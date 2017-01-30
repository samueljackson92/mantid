"""Set of general purpose functions which are related to the SANSState approach."""

from copy import deepcopy
from sans.common.enums import (ReductionDimensionality, ISISReductionMode, OutputParts, DetectorType)
from sans.common.constants import (ALL_PERIODS, EMPTY_NAME, REDUCED_CAN_TAG)
from sans.common.general_functions import (add_to_sample_log, get_ads_workspace_references)
from sans.common.log_tagger import (has_hash, get_hash_value, set_hash)
from sans.common.xml_parsing import (get_monitor_names_from_idf_file, get_named_elements_from_ipf_file)


def is_pure_none_or_not_none(elements_to_check):
    """
    Checks a list of elements contains None entries and non-None entries

    @param elements_to_check: a list with entries to check
    @return: True if the list contains either only None or only non-None elements, else False
    """
    are_all_none_or_all_not_none = True

    if len(elements_to_check) == 0:
        return are_all_none_or_all_not_none
    return all(element is not None for element in elements_to_check) or  \
           all(element is None for element in elements_to_check)  # noqa


def is_not_none_and_first_larger_than_second(elements_to_check):
    """
    This function checks if both are not none and then checks if the first element is smaller than the second element.

    @param elements_to_check: a list with two entries. The first is the lower bound and the second entry is the upper
                              bound
    @return: False if at least one input is None or if both are not None and the first element is smaller than the
             second else True
    """
    is_invalid = True
    if len(elements_to_check) != 2:
        return is_invalid
    if any(element is None for element in elements_to_check):
        is_invalid = False
        return is_invalid
    if elements_to_check[0] < elements_to_check[1]:
        is_invalid = False
    return is_invalid


def one_is_none(elements_to_check):
    return any(element is None for element in elements_to_check)


def validation_message(error_message, instruction, variables):
    """
    Generates a validation message for the SANSState.

    @param error_message: A message describing the error.
    @param instruction: A message describing what to do to fix the error
    @param variables: A dictionary which contains the variable names and values which are involved in the error.
    @return: a formatted validation message string.
    """
    message = ""
    for key, value in sorted(variables.items()):
        message += "{0}: {1}\n".format(key, value)
    message += instruction
    return {error_message: message}


def get_state_hash_for_can_reduction(state, partial_type=None):
    """
    Creates a hash for a (modified) state object.

    Note that we need to modify the state object to exclude elements which are not relevant for the can reduction.
    This is primarily the setting of the sample workspaces. This is the only place where we directly alter the value
    of a state object
    @param state: a SANSState object.
    @param partial_type: if it is a partial type, then it needs to be specified here.
    @return: the hash of the state
    """
    def remove_sample_related_information(full_state):
        state_to_hash = deepcopy(full_state)
        state_to_hash.data.sample_scatter = EMPTY_NAME
        state_to_hash.data.sample_scatter_period = ALL_PERIODS
        state_to_hash.data.sample_transmission = EMPTY_NAME
        state_to_hash.data.sample_transmission_period = ALL_PERIODS
        state_to_hash.data.sample_direct = EMPTY_NAME
        state_to_hash.data.sample_direct_period = ALL_PERIODS
        state_to_hash.data.sample_scatter_run_number = 1
        return state_to_hash
    new_state = remove_sample_related_information(state)
    new_state_serialized = new_state.property_manager

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


def get_reduced_can_workspace_from_ads(state, output_parts):
    """
    Get the reduced can workspace from the ADS if it exists else nothing

    @param state: a SANSState object.
    @param output_parts: if true then search also for the partial workspaces
    @return: a reduced can object or None.
    """
    # Get the standard reduced can workspace
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


def set_detector_names(state, ipf_path):
    """
    Sets the detectors names on a State object which has a `detector` map entry, e.g. StateMask

    @param state: the state object
    @param ipf_path: the path to the Instrument Parameter File
    """
    lab_keyword = DetectorType.to_string(DetectorType.LAB)
    hab_keyword = DetectorType.to_string(DetectorType.HAB)
    detector_names = {lab_keyword: "low-angle-detector-name",
                      hab_keyword: "high-angle-detector-name"}
    detector_names_short = {lab_keyword: "low-angle-detector-short-name",
                            hab_keyword: "high-angle-detector-short-name"}

    names_to_search = []
    names_to_search.extend(detector_names.values())
    names_to_search.extend(detector_names_short.values())

    found_detector_names = get_named_elements_from_ipf_file(ipf_path, names_to_search, str)

    for detector_type in state.detectors:
        try:
            detector_name_tag = detector_names[detector_type]
            detector_name_short_tag = detector_names_short[detector_type]
            detector_name = found_detector_names[detector_name_tag]
            detector_name_short = found_detector_names[detector_name_short_tag]
        except KeyError:
            continue

        state.detectors[detector_type].detector_name = detector_name
        state.detectors[detector_type].detector_name_short = detector_name_short


def set_monitor_names(state, idf_path):
    monitor_names = get_monitor_names_from_idf_file(idf_path)
    state.monitor_names = monitor_names
