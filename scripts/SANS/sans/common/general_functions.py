""" The elements of this module contain various general-purpose functions for the SANS reduction framework."""

# pylint: disable=invalid-name

from __future__ import (absolute_import, division, print_function)
from math import (acos, sqrt, degrees)
import re
from copy import deepcopy
import json
from mantid.api import AlgorithmManager, AnalysisDataService
from sans.common.constants import (SANS_FILE_TAG, ALL_PERIODS, REDUCED_WORKSPACE_NAME_IN_LOGS,
                                   REDUCED_WORKSPACE_NAME_BY_USER_IN_LOGS, REDUCED_WORKSPACE_BASE_NAME_IN_LOGS,
                                   SANS2D, LOQ, LARMOR, ALL_PERIODS, EMPTY_NAME, REDUCED_CAN_TAG)
from sans.common.log_tagger import (get_tag, has_tag, set_tag, has_hash, get_hash_value, set_hash)
from sans.common.enums import (DetectorType, RangeStepType, ReductionDimensionality, ISISReductionMode, OutputParts)


# -------------------------------------------
# Free functions
# -------------------------------------------
def get_log_value(run, log_name, log_type):
    """
    Find a log value.

    There are two options here. Either the log is a scalar or a vector. In the case of a scalar there is not much
    left to do. In the case of a vector we select the first element whose time_stamp is after the start time of the run
    @param run: a Run object.
    @param log_name: the name of the log entry
    @param log_type: the expected type fo the log entry
    @return: the log entry
    """
    try:
        # Scalar case
        output = log_type(run.getLogData(log_name).value)
    except TypeError:
        # We must be dealing with a vectorized case, ie a time series
        log_property = run.getLogData(log_name)
        number_of_entries = len(log_property.value)

        # If we have only one item, then there is nothing left to do
        output = None
        if number_of_entries == 1:
            output = log_type(run.getLogData(log_name).value[0])
        else:
            # Get the first entry which is past the start time log
            start_time = run.startTime()
            times = log_property.times
            values = log_property.value

            has_found_value = False
            for index in range(0, number_of_entries):
                if times[index] > start_time:
                    # Not fully clear why we take index - 1, but this follows the old implementation rules
                    value_index = index if index == 0 else index - 1
                    has_found_value = True
                    output = log_type(values[value_index])
                    break

            # Not fully clear why we take index - 1, but this follows the old implementation rules
            if not has_found_value:
                output = float(values[number_of_entries - 1])
    return output


def get_single_valued_logs_from_workspace(workspace, log_names, log_types, convert_from_millimeter_to_meter=False):
    """
    Gets non-array valued entries from the sample logs.

    :param workspace: the workspace with the sample log.
    :param log_names: the log names which are to be extracted.
    :param log_types: the types of log entries, ie strings or numeric
    :param convert_from_millimeter_to_meter:
    :return: the log results
    """
    assert len(log_names) == len(log_types)
    # Find the desired log names.
    run = workspace.getRun()
    log_results = {}
    for log_name, log_type in zip(log_names, log_types):
        log_value = get_log_value(run, log_name, log_type)
        log_results.update({log_name: log_value})
    if convert_from_millimeter_to_meter:
        for key in log_results.keys():
            log_results[key] /= 1000.
    return log_results


def create_unmanaged_algorithm(name, **kwargs):
    """
    Creates an unmanaged child algorithm and initializes it.

    :param name: the name of the algorithm
    :param kwargs: settings for the algorithm
    :return: an initialized algorithm instance.
    """
    alg = AlgorithmManager.createUnmanaged(name)
    alg.initialize()
    alg.setChild(True)
    for key, value in kwargs.items():
        alg.setProperty(key, value)
    return alg


def quaternion_to_angle_and_axis(quaternion):
    """
    Converts a quaternion to an angle + an axis

    The conversion from a quaternion to an angle + axis is explained here:
    http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToAngle/
    """
    angle = 2*acos(quaternion[0])
    s_parameter = sqrt(1 - quaternion[0]*quaternion[0])

    axis = []
    # If the the angle is zero, then it does not make sense to have an axis
    if s_parameter < 1e-8:
        axis.append(quaternion[1])
        axis.append(quaternion[2])
        axis.append(quaternion[3])
    else:
        axis.append(quaternion[1]/s_parameter)
        axis.append(quaternion[2]/s_parameter)
        axis.append(quaternion[3]/s_parameter)
    return degrees(angle), axis


def get_charge_and_time(workspace):
    """
    Gets the total charge and time from a workspace

    :param workspace: the workspace from which we extract the charge and time.
    :return: the charge, the time
    """
    run = workspace.getRun()
    charges = run.getLogData('proton_charge')
    total_charge = sum(charges.value)
    time_passed = (charges.times[-1] - charges.times[0]).total_microseconds()
    time_passed /= 1e6
    return total_charge, time_passed


def add_to_sample_log(workspace, log_name, log_value, log_type):
    """
    Adds a sample log to the workspace

    :param workspace: the workspace to whcih the sample log is added
    :param log_name: the name of the log
    :param log_value: the value of the log in string format
    :param log_type: the log value type which can be String, Number, Number Series
    """
    if log_type not in ["String", "Number", "Number Series"]:
        raise ValueError("Tryint go add {0} to the sample logs but it was passed "
                         "as an unknown type of {1}".format(log_value, log_type))
    if not isinstance(log_value, str):
        raise TypeError("The value which is added to the sample logs needs to be passed as a string,"
                        " but it is passed as {0}".format(type(log_value)))

    add_log_name = "AddSampleLog"
    add_log_options = {"Workspace": workspace,
                       "LogName": log_name,
                       "LogText": log_value,
                       "LogType": log_type}
    add_log_alg = create_unmanaged_algorithm(add_log_name, **add_log_options)
    add_log_alg.execute()


def append_to_sans_file_tag(workspace, to_append):
    """
    Appends a string to the existing sans file tag.

    :param workspace: the workspace which contains the sample logs with the sans file tag.
    :param to_append: the additional tag
    """
    if has_tag(SANS_FILE_TAG, workspace):
        value = get_tag(SANS_FILE_TAG, workspace)
        value += to_append
        set_tag(SANS_FILE_TAG, value, workspace)


def get_ads_workspace_references():
    """
    Gets a list of handles of available workspaces on the ADS

    @return: the workspaces on the ADS.
    """
    for workspace_name in AnalysisDataService.getObjectNames():
        yield AnalysisDataService.retrieve(workspace_name)


def convert_bank_name_to_detector_type_isis(detector_name):
    """
    Converts a detector name of an isis detector to a detector type.

    The current translation is
    SANS2D: rear-detector -> LAB
            front-detector -> HAB
            but also allowed rear, front
    LOQ:    main-detector-bank -> LAB
            HAB                -> HAB
            but also allowed main
    LARMOR: DetectorBench      -> LAB

    @param detector_name: a string with a valid detector name
    @return: a detector type depending on the input string, or a runtime exception.
    """
    detector_name = detector_name.upper()
    detector_name = detector_name.strip()
    if detector_name == "REAR-DETECTOR" or detector_name == "MAIN-DETECTOR-BANK" or detector_name == "DETECTORBENCH" \
            or detector_name == "REAR" or detector_name == "MAIN":
        detector_type = DetectorType.LAB
    elif detector_name == "FRONT-DETECTOR" or detector_name == "HAB" or detector_name == "FRONT":
        detector_type = DetectorType.HAB
    else:
        raise RuntimeError("There is not detector type conversion for a detector with the "
                           "name {0}".format(detector_name))
    return detector_type


# ----------------------------------------------------------------------------------------------------------------------
#  Functions for bins, ranges and slices
# ----------------------------------------------------------------------------------------------------------------------
def parse_event_slice_setting(string_to_parse):
    """
    Create a list of boundaries from a string defining the slices.
    Valid syntax is:
      * From 8 to 9 > '8-9' --> return [[8,9]]
      * From 8 to 9 and from 10 to 12 > '8-9, 10-12' --> return [[8,9],[10,12]]
      * From 5 to 10 in steps of 1 > '5:1:10' --> return [[5,6],[6,7],[7,8],[8,9],[9,10]]
      * From 5 > '>5' --> return [[5, -1]]
      * Till 5 > '<5' --> return [[-1,5]]

    Any combination of these syntax separated by comma is valid.
    A special mark is used to signal no limit: -1,
    As, so, for an empty string, it will return: None.

    It does not accept negative values.
    """

    def _does_match(compiled_regex, line):
        return compiled_regex.match(line) is not None

    def _extract_simple_slice(line):
        start, stop = line.split("-")
        start = float(start)
        stop = float(stop)
        if start > stop:
            raise ValueError("Parsing event slices. It appears that the start value {0} is larger than the stop "
                             "value {1}. Make sure that this is not the case.")
        return [start, stop]

    def float_range(start, stop, step):
        while start < stop:
            yield start
            start += step

    def _extract_slice_range(line):
        split_line = line.split(":")
        start = float(split_line[0])
        step = float(split_line[1])
        stop = float(split_line[2])
        if start > stop:
            raise ValueError("Parsing event slices. It appears that the start value {0} is larger than the stop "
                             "value {1}. Make sure that this is not the case.")

        elements = list(float_range(start, stop, step))
        # We are missing the last element
        elements.append(stop)

        # We generate ranges with [[element[0], element[1]], [element[1], element[2]], ...]
        ranges = zip(elements[:-1], elements[1:])
        return [[e1, e2] for e1, e2 in ranges]

    def _extract_full_range(line, range_marker_pattern):
        is_lower_bound = ">" in line
        line = re.sub(range_marker_pattern, "", line)
        value = float(line)
        if is_lower_bound:
            return [value, -1]
        else:
            return [-1, value]

    # Check if the input actually exists.
    if not string_to_parse:
        return None

    number = r'(\d+(?:\.\d+)?(?:[eE][+-]\d+)?)'  # float without sign
    simple_slice_pattern = re.compile("\\s*" + number + "\\s*" r'-' + "\\s*" + number + "\\s*")
    slice_range_pattern = re.compile("\\s*" + number + "\\s*" + r':' + "\\s*" + number + "\\s*"
                                     + r':' + "\\s*" + number)
    full_range_pattern = re.compile("\\s*" + "(<|>)" + "\\s*" + number + "\\s*")

    range_marker = re.compile("[><]")

    slice_settings = string_to_parse.split(',')
    all_ranges = []
    for slice_setting in slice_settings:
        slice_setting = slice_setting.replace(' ', '')
        # We can have three scenarios
        # 1. Simple Slice:     X-Y
        # 2. Slice range :     X:Y:Z
        # 3. Slice full range: >X or <X
        if _does_match(simple_slice_pattern, slice_setting):
            all_ranges.append(_extract_simple_slice(slice_setting))
        elif _does_match(slice_range_pattern, slice_setting):
            all_ranges.extend(_extract_slice_range(slice_setting))
        elif _does_match(full_range_pattern, slice_setting):
            all_ranges.append(_extract_full_range(slice_setting, range_marker))
        else:
            raise ValueError("The provided event slice configuration {0} cannot be parsed because "
                             "of {1}".format(slice_settings, slice_setting))
    return all_ranges


def get_ranges_from_event_slice_setting(string_to_parse):
    parsed_elements = parse_event_slice_setting(string_to_parse)
    if not parsed_elements:
        return
    # We have the elements in the form [[a, b], [c, d], ...] but want [a, c, ...] and [b, d, ...]
    lower = [element[0] for element in parsed_elements]
    upper = [element[1] for element in parsed_elements]
    return lower, upper


def get_bins_for_rebin_setting(min_value, max_value, step_value, step_type):
    """
    Creates a list of bins for the rebin setting.

    @param min_value: the minimum value
    @param max_value: the maximum value
    @param step_value: the step value
    @param step_type: the step type, ie if linear or logarithmic
    @return: a list of bin values
    """
    lower_bound = min_value
    bins = []
    while lower_bound < max_value:

        bins.append(lower_bound)
        # We can either have linear or logarithmic steps. The logarithmic step depends on the lower bound.
        if step_type is RangeStepType.Lin:
            step = step_value
        else:
            step = lower_bound*step_value

        # Check if the step will bring us out of bounds. If so, then set the new upper value to the max_value
        upper_bound = lower_bound + step
        upper_bound = upper_bound if upper_bound < max_value else max_value

        # Now we advance the lower bound
        lower_bound = upper_bound
    # Add the last lower_bound
    bins.append(lower_bound)
    return bins


def get_range_lists_from_bin_list(bin_list):
    return bin_list[:-1], bin_list[1:]


def get_ranges_for_rebin_setting(min_value, max_value, step_value, step_type):
    """
    Creates two lists of lower and upper bounds for the

    @param min_value: the minimum value
    @param max_value: the maximum value
    @param step_value: the step value
    @param step_type: the step type, ie if linear or logarithmic
    @return: two ranges lists, one for the lower and one for the upper bounds.
    """
    bins = get_bins_for_rebin_setting(min_value, max_value, step_value, step_type)
    return get_range_lists_from_bin_list(bins)


def get_ranges_for_rebin_array(rebin_array):
    """
    Converts a rebin string into min, step (+ step_type), max

    @param rebin_array: a simple rebin array, ie min, step, max
    @return: two ranges lists, one for the lower and one for the upper bounds.
    """
    min_value = rebin_array[0]
    step_value = rebin_array[1]
    max_value = rebin_array[2]
    step_type = RangeStepType.Lin if step_value >= 0. else RangeStepType.Log
    step_value = abs(step_value)
    return get_ranges_for_rebin_setting(min_value, max_value, step_value, step_type)


# ----------------------------------------------------------------------------------------------------------------------
# Functions related to workspace names
# ----------------------------------------------------------------------------------------------------------------------
def get_output_workspace_name(state, reduction_mode):
    """
    Creates the name of the output workspace from a state object.

    The name of the output workspace is:
    1. The short run number
    2. If specific period is being reduced: 'p' + number
    3. Short detector name of the current reduction or "merged"
    4. The reduction dimensionality: "_" + dimensionality
    5. A wavelength range: wavelength_low + "_" + wavelength_high
    6. In case of a 1D reduction, then add phi limits
    7. If we are dealing with an actual slice limit, then specify it: "_tXX_TYY" Note that the time set to
       two decimals
    :param state: a SANSState object
    :param reduction_mode: which reduction is being looked at
    :return: the name of the reduced workspace, and the base name fo the reduced workspace
    """
    # 1. Short run number
    data = state.data
    short_run_number = data.sample_scatter_run_number
    short_run_number_as_string = str(short_run_number)

    # 2. Multiperiod
    if state.data.sample_scatter_period != ALL_PERIODS:
        period = data.sample_scatter_period
        period_as_string = "p"+str(period)
    else:
        period_as_string = ""

    # 3. Detector name
    move = state.move
    detectors = move.detectors
    if reduction_mode is ISISReductionMode.Merged:
        detector_name_short = "merged"
    elif reduction_mode is ISISReductionMode.HAB:
        detector_name_short = detectors[DetectorType.to_string(DetectorType.HAB)].detector_name_short
    elif reduction_mode is ISISReductionMode.LAB:
        detector_name_short = detectors[DetectorType.to_string(DetectorType.LAB)].detector_name_short
    else:
        raise RuntimeError("SANSStateFunctions: Unknown reduction mode {0} cannot be used to "
                           "create an output name".format(reduction_mode))

    # 4. Dimensionality
    reduction = state.reduction
    if reduction.reduction_dimensionality is ReductionDimensionality.OneDim:
        dimensionality_as_string = "_1D"
    else:
        dimensionality_as_string = "_2D"

    # 5. Wavelength range
    wavelength = state.wavelength
    wavelength_range_string = "_" + str(wavelength.wavelength_low) + "_" + str(wavelength.wavelength_high)

    # 6. Phi Limits
    mask = state.mask
    if reduction.reduction_dimensionality is ReductionDimensionality.OneDim:
        if mask.phi_min and mask.phi_max and (abs(mask.phi_max - mask.phi_min) != 180.0):
            phi_limits_as_string = 'Phi' + str(mask.phi_min) + '_' + str(mask.phi_max)
        else:
            phi_limits_as_string = ""
    else:
        phi_limits_as_string = ""

    # 7. Slice limits
    slice_state = state.slice
    start_time = slice_state.start_time
    end_time = slice_state.end_time
    if start_time and end_time:
        start_time_as_string = '_t%.2f' % start_time[0]
        end_time_as_string = '_T%.2f' % end_time[0]
    else:
        start_time_as_string = ""
        end_time_as_string = ""

    # Piece it all together
    output_workspace_name = (short_run_number_as_string + period_as_string + detector_name_short +
                             dimensionality_as_string + wavelength_range_string + phi_limits_as_string +
                             start_time_as_string + end_time_as_string)
    output_workspace_base_name = (short_run_number_as_string + detector_name_short + dimensionality_as_string +
                                  wavelength_range_string + phi_limits_as_string)
    return output_workspace_name, output_workspace_base_name


def add_workspace_name(workspace, state, reduction_mode):
    """
    Adds the default reduced workspace name to the sample logs as well as the base name and a a user specified name,
    if one was specified.

    :param workspace: The output workspace
    :param state: a SANSState object
    :param reduction_mode: the reduction mode, i.e. LAB, HAB, MERGED of the particular data set. If it is HAB it can
                           still be part of an overall MERGED request.
    """
    reduced_workspace_name, reduced_workspace_base_name = get_output_workspace_name(state, reduction_mode)
    add_to_sample_log(workspace, REDUCED_WORKSPACE_NAME_IN_LOGS, reduced_workspace_name, "String")
    add_to_sample_log(workspace, REDUCED_WORKSPACE_BASE_NAME_IN_LOGS, reduced_workspace_base_name, "String")


def get_output_workspace_name_from_workspace_log(workspace, log_name):
    run = workspace.run()
    if not run.hasProperty(log_name):
        raise RuntimeError("The workspace sample logs don't contain an entry for {0}.".format(log_name))
    return run.getProperty(log_name).value


def get_output_workspace_name_from_workspace(workspace):
    """
    Gets the name of the reduced workspace from the logs.

    @param workspace: a matrix workspace
    @return: the name of the workspace
    """
    return get_output_workspace_name_from_workspace_log(workspace, REDUCED_WORKSPACE_NAME_IN_LOGS)


def get_output_workspace_base_name_from_workspace(workspace):
    """
    Gets the base name of the reduced workspace. This can be the same as the name, but is different for
    multi-period files, it will not contain the _X of the name of the multi-period file.

    @param workspace: a matrix workspace
    @return: the base name of the workspace
    """
    return get_output_workspace_name_from_workspace_log(workspace, REDUCED_WORKSPACE_BASE_NAME_IN_LOGS)


def get_output_user_specified_name_from_workspace(workspace):
    """
    Gets a user specified name from the workspace logs.

    @param workspace: a matrix workspace.
    @return: the user specified output workspace name.
    """
    return get_output_workspace_name_from_workspace_log(workspace, REDUCED_WORKSPACE_NAME_BY_USER_IN_LOGS)


def get_base_name_from_multi_period_name(workspace_name):
    """
    Gets a base name from a multiperiod name. The multiperiod name is NAME_xxx and the base name is NAME

    @param workspace_name: a workspace name string
    @return: the base name
    """
    multi_period_workspace_form = "_[0-9]+$"
    if re.search(multi_period_workspace_form, workspace_name) is not None:
        return re.sub(multi_period_workspace_form, "", workspace_name)
    else:
        raise RuntimeError("The workspace name {0} seems to not be part of a "
                           "multi-period workspace.".format(workspace_name))


def sanitise_instrument_name(instrument_name):
    """
    Sanitises instrument names which have been obtained from an instrument on a workspace.

    Unfortunately the instrument names are sometimes truncated or extended. This is possible since they are strings
    and not types.
    @param instrument_name: a instrument name string
    @return: a sanitises instrument name string
    """
    instrument_name_upper = instrument_name.upper()
    if re.search(LOQ, instrument_name_upper):
        instrument_name = LOQ
    elif re.search(SANS2D, instrument_name_upper):
        instrument_name = SANS2D
    elif re.search(LARMOR, instrument_name_upper):
        instrument_name = LARMOR
    return instrument_name


# ----------------------------------------------------------------------------------------------------------------------
# Hashing + ADS
# ----------------------------------------------------------------------------------------------------------------------
def get_state_hash_for_can_reduction(state, partial_type=None):
    """
    Creates a hash for a (modified) state object.

    Note that we need to modify the state object to exclude elements which are not relevant for the can reduction.
    This is primarily the setting of the sample workspaces. This is the only place where we directly alter the value
    of a state object in the entire reduction workflow. Note that we are not changing the
    @param state: a SANSState object.
    @param partial_type: if it is a partial type, then it needs to be specified here.
    @return: the hash of the state
    """
    def remove_sample_related_information(full_state):
        state_to_hash = deepcopy(full_state)

        # Data
        state_to_hash.data.sample_scatter = EMPTY_NAME
        state_to_hash.data.sample_scatter_period = ALL_PERIODS
        state_to_hash.data.sample_transmission = EMPTY_NAME
        state_to_hash.data.sample_transmission_period = ALL_PERIODS
        state_to_hash.data.sample_direct = EMPTY_NAME
        state_to_hash.data.sample_direct_period = ALL_PERIODS
        state_to_hash.data.sample_scatter_run_number = 1

        # Save
        state_to_hash.save.user_specified_output_name = ""

        return state_to_hash
    new_state = remove_sample_related_information(state)
    new_state_serialized = new_state.property_manager
    new_state_serialized = json.dumps(new_state_serialized, sort_keys=True, indent=4)

    # If we are dealing with a partial output workspace, then mark it as such
    if partial_type is OutputParts.Count:
        state_string = str(new_state_serialized) + "counts"
    elif partial_type is OutputParts.Norm:
        state_string = str(new_state_serialized) + "norm"
    else:
        state_string = str(new_state_serialized)
    return str(get_hash_value(state_string))


def get_workspace_from_ads_based_on_hash(hash_value):
    for workspace in get_ads_workspace_references():
        if has_hash(REDUCED_CAN_TAG, hash_value, workspace):
            return workspace


def does_workspace_exist_on_ads(workspace):
    """
    Checks if the workspace exists on the ADS based on a (potentially stored hash value)
    @param workspace: workspace to check
    @return: true if it is on the ADS else false
    """
    workspace_exists = False
    if has_tag(REDUCED_CAN_TAG, workspace):
        has_value = get_tag(REDUCED_CAN_TAG, workspace)
        ws_reference_from_ads = get_workspace_from_ads_based_on_hash(has_value)
        if ws_reference_from_ads is not None:
            workspace_exists = True
    return workspace_exists


def get_reduced_can_workspace_from_ads(state, output_parts):
    """
    Get the reduced can workspace from the ADS if it exists else nothing

    @param state: a SANSState object.
    @param output_parts: if true then search also for the partial workspaces
    @return: a reduced can object or None.
    """
    # Get the standard reduced can workspace)
    hashed_state = get_state_hash_for_can_reduction(state)
    reduced_can = get_workspace_from_ads_based_on_hash(hashed_state)
    reduced_can_count = None
    reduced_can_norm = None
    if output_parts:
        hashed_state_count = get_state_hash_for_can_reduction(state, OutputParts.Count)
        reduced_can_count = get_workspace_from_ads_based_on_hash(hashed_state_count)
        hashed_state_norm = get_state_hash_for_can_reduction(state, OutputParts.Norm)
        reduced_can_norm = get_workspace_from_ads_based_on_hash(hashed_state_norm)
    return reduced_can, reduced_can_count, reduced_can_norm


def write_hash_into_reduced_can_workspace(state, workspace, partial_type=None):
    """
    Writes the state hash into a reduced can workspace.

    @param state: a SANSState object.
    @param workspace: a reduced can workspace
    @param partial_type: if it is a partial type, then it needs to be specified here.
    """
    hashed_state = get_state_hash_for_can_reduction(state, partial_type=partial_type)
    set_hash(REDUCED_CAN_TAG, hashed_state, workspace)
