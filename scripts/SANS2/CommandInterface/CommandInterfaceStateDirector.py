from SANS2.Common.SANSType import (sans_type, ReductionDimensionality, DetectorType)
from SANS2.UserFile.UserFileStateDirector import UserFileStateDirectorISIS
from SANS2.State.StateBuilder.SANSStateDataBuilder import get_data_builder
from SANS2.UserFile.UserFileParser import (UserFileParser, set_mask_entries)
from SANS2.UserFile.UserFileReader import (UserFileReader)

# ----------------------------------------------------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------------------------------------------------

# ------------------
# IDs for commands. We use here sans_type since enum is not available in the current Python configuration.
# ------------------
@sans_type("sample_scatter", "sample_transmission", "sample_direct", "can_scatter", "can_transmission", "can_direct")
class DataCommandId(object):
    pass


@sans_type("clear", "one_dim", "two_dim",  # Null Parameter commands
           "user_file", "mask", "sample_offset", "detector", "event_slices",  # Single parameter commands
           "flood_file", "wavelength_correction_file",  # Single parameter commands
           "monitor_spectrum", "transmission_spectrum", "gravity",  # Double parameter commands
           "centre",   # Three parameter commands
           "trans_fit", "phi_limit", "mask_radius", "wavelength_limit", "qxy_limit", # Four parameter commands
           "front_detector_rescale"  # Six parameter commands
           )
class NParameterCommandId(object):
    pass


class Command(object):
    def __init__(self, command_id):
        super(Command, self).__init__()
        self.command_id = command_id


class DataCommand(Command):
    """
    A command which is associated with setting data information.
    """
    def __init__(self, command_id, file_name, period=None):
        super(DataCommand, self).__init__(command_id)
        self.file_name = file_name
        self.period = period


class NParameterCommand(Command):
    """
    A command which has n parameters in a list.
    """
    def __init__(self, command_id, values):
        super(NParameterCommand, self).__init__(command_id)
        self.values = values


class FitData(object):
    """
    Describes the fit mode. This is not part of the SANSType module since we only need it here. It is slightly
    inconsistent but it is very localized.
    """
    class Sample(object):
        pass

    class Can(object):
        pass

    class Both(object):
        pass


# ----------------------------------------------------------------------------------------------------------------------
# Command Interface State Director

# Explanation of the implementation
#
# Previously the ISISCommandInterface just executed commands one after another. Settings were stored in the reduction
# singleton. Once in a while the reduction singleton was reset.
#
# Here we need to have state director which builds the SANS state out of these legacy commands. Note that before we
# can process any of the commands we need to find the data entries, since they drive the reduction.
# All other commands should be setting the SANSState in order.
# ----------------------------------------------------------------------------------------------------------------------


class CommandInterfaceStateDirector(object):
    def __init__(self, facility):
        super(CommandInterfaceStateDirector, self).__init__()
        self._commands = []
        self._user_file_state_director = None
        self._parsed_data = {}
        self._facility = facility
        self._method_map = None
        self._set_up_method_map()

    def add_command(self, command):
        self._commands.append(command)

    def clear_commands(self):
        self._commands = []

    def process_commands(self):
        """
        Here we process the commands that have been set. This would be triggered by a command which requests a reduction

        The execution strategy is:
        1. Find the data entries and great a SANSStateData object out of them
        2. Go sequentially through the commands in a FIFO manner (except for the data entries)
        3. Clear commands
        4. Returns the constructed state
        @returns a list of valid SANSState object which can be used for data reductions or raises an exception.
        """
        # 1. Get a SANSStateData object.
        data_state = self._get_data_state()

        # 2. Go through
        state = self._process_command_queue(data_state)

        # 3. Clear commands
        self._commands = []
        self._user_file_state_director = None
        self._parsed_data = {}

        # 4. Provide the state
        return state

    def _get_data_state(self):
        # Get the data commands
        data_commands = self._extract_data_commands()

        # Build the state data
        data_builder = get_data_builder(self._facility)
        self._set_data_element(data_builder.set_sample_scatter, data_builder.set_sample_scatter_period,
                               DataCommandId.sample_scatter, data_commands)
        self._set_data_element(data_builder.set_sample_transmission, data_builder.set_sample_transmission_period,
                               DataCommandId.sample_transmission, data_commands)
        self._set_data_element(data_builder.set_sample_direct, data_builder.set_sample_direct_period,
                               DataCommandId.sample_direct, data_commands)
        
        self._set_data_element(data_builder.set_can_scatter, data_builder.set_can_scatter_period,
                               DataCommandId.can_scatter, data_commands)
        self._set_data_element(data_builder.set_can_transmission, data_builder.set_can_transmission_period,
                               DataCommandId.can_transmission, data_commands)
        self._set_data_element(data_builder.set_can_direct, data_builder.set_can_direct_period,
                               DataCommandId.can_direct, data_commands)

        return data_builder.build()

    def _extract_data_commands(self):
        """
        Grabs and removes the data commands from the command queue.

        @return: a list of data commands
        """
        # Grab the data commands
        data_commands = [element for element in self._commands if isinstance(element, DataCommand)]
        # Remove the data commands from the old list
        for element in data_commands:
            self._commands.remove(element)
        return data_commands

    def _set_data_element(self, data_builder_file_setter, data_builder_period_setter, command_id, commands):
        """
        Sets a data element (e.g. sample scatter file and sample scatter period) on the data builder.

        @param data_builder_file_setter: a handle to the correct setter for the file on the data builder.
        @param data_builder_period_setter: a handle to the correct setter for the period on the data builder.
        @param command_id: the command id
        @param commands: a list of commands.
        """
        data_elements = self._get_elements_with_key(command_id, commands)

        # If there is no element, then there is nothing to do
        if len(data_elements) == 0:
            return

        # If there is more than one element, then that is not right
        if len(data_elements) > 1:
            raise RuntimeError("Specified too many data elements for {0}".format(command_id))

        data_element = data_elements[0]
        file_name = data_element.file_name
        period = data_element.period
        data_builder_file_setter(file_name)
        data_builder_period_setter(period)

    @staticmethod
    def _get_elements_with_key(command_id, command_list):
        """
        Get all elements in the command list with a certain id

        @param command_id: the id of the command.
        @param command_list: a list of commands.
        @return: a list of commands which match the id.
        """
        return [element for element in command_list if element.command_id is command_id]

    def _process_command_queue(self, data_state):
        """
        Process the command queue sequentially as FIFO structure

        @param data_state: the data state.
        @return: a SANSState object.
        """
        self._user_file_state_director = UserFileStateDirectorISIS(data_state)

        for command in self._commands:
            command_id = command.command_id
            process_function = self._method_map[command_id]
            process_function(command, self._user_file_state_director)
        return self._user_file_state_director.construct()

    def _set_up_method_map(self):
        """
        Sets up a mapping between command ids and the adequate processing methods which can handle the command.
        """
        self._method_map = {NParameterCommandId.user_file: self._process_user_file,
                            NParameterCommandId.mask: self._process_mask,
                            NParameterCommandId.monitor_spectrum: self._process_monitor_spectrum,
                            NParameterCommandId.transmission_spectrum: self._process_transmission_spectrum,
                            NParameterCommandId.one_dim: self._process_one_dim,
                            NParameterCommandId.two_dim: self._process_two_dim,
                            NParameterCommandId.sample_offset: self._process_sample_offset,
                            NParameterCommandId.detector: self._process_detector,
                            NParameterCommandId.gravity: self._process_gravity,
                            NParameterCommandId.centre: self._process_centre,
                            NParameterCommandId.trans_fit: self._process_trans_fit,
                            NParameterCommandId.front_detector_rescale: self._process_front_detector_rescale,
                            NParameterCommandId.event_slices: self._process_event_slices,
                            NParameterCommandId.flood_file: self._process_flood_file,
                            NParameterCommandId.phi_limit: self._process_phi_limit,
                            NParameterCommandId.wavelength_correction_file: self._process_wavelength_correction_file,
                            NParameterCommandId.mask_radius: self._process_mask_radius,
                            NParameterCommandId.wavelength_limit: self._process_wavelength_limit,
                            NParameterCommandId.qxy_limit: self._process_qxy_limit}

    @staticmethod
    def _process_user_file(command, user_file_state_director):
        """
        Processes a user file and retains the

        @param command: the command with the user file path
        @param user_file_state_director: the user file state director
        @return:
        """
        file_name = command.values[0]
        user_file_state_director.set_user_file(file_name)

    @staticmethod
    def _process_mask(command, user_file_state_director):
        """
        We need to process a mask line as specified in the user file.
        """
        mask_command = command.values[0]
        # Strip the MASK/ bit from the command
        user_file_parser = UserFileParser()
        parsed_output = user_file_parser.parse_line(mask_command)
        # Note that we need to provide the parsed output as a list
        if not isinstance(parsed_output, list):
            parsed_output = [parsed_output]
        set_mask_entries(director=user_file_state_director, user_file_items=parsed_output)

    @staticmethod
    def _process_monitor_spectrum(command, user_file_state_director):
        incident_monitor = command.values[0]
        rebin_type = command.values[1]
        user_file_state_director.set_normalize_to_monitor_builder_incident_monitor(incident_monitor)
        user_file_state_director.set_normalize_to_monitor_builder_rebin_type(rebin_type)

    @staticmethod
    def _process_transmission_spectrum(command, user_file_state_director):
        incident_monitor = command.values[0]
        rebin_type = command.values[1]
        user_file_state_director.set_calculate_transmission_builder_incident_monitor(incident_monitor)
        user_file_state_director.set_calculate_transmission_builder_rebin_type(rebin_type)

    @staticmethod
    def _process_one_dim(command, user_file_state_director):
        _ = command
        user_file_state_director.set_reduction_builder_reduction_dimensionality(ReductionDimensionality.OneDim)
        user_file_state_director.set_convert_to_q_builder_reduction_dimensionality(ReductionDimensionality.OneDim)

    @staticmethod
    def _process_two_dim(command, user_file_state_director):
        _ = command
        user_file_state_director.set_reduction_builder_reduction_dimensionality(ReductionDimensionality.TwoDim)
        user_file_state_director.set_convert_to_q_builder_reduction_dimensionality(ReductionDimensionality.TwoDim)

    @staticmethod
    def _process_sample_offset(command, user_file_state_director):
        sample_offset = command.values[0]
        user_file_state_director.set_move_builder_sample_offset(sample_offset)

    @staticmethod
    def _process_detector(command, user_file_state_director):
        pass

    @staticmethod
    def _process_gravity(command, user_file_state_director):
        use_gravity = command.values[0]
        extra_length = command.values[1]
        user_file_state_director.set_convert_to_q_builder_use_gravity(use_gravity)
        user_file_state_director.set_convert_to_q_builder_gravity_extra_length(extra_length)

    @staticmethod
    def _process_centre(command, user_file_state_director):
        pos1 = command.values[0]
        pos2 = command.values[1]
        detector_type = command.values[2]

        # We need to convert the positions correctly, this is driven by the data. What is defined as the
        # x coordinate can be for example an angle for LARMOR, hence we need to ensure that the input is handled
        # correctly
        pos1 = user_file_state_director.convert_pos1(pos1)
        pos2 = user_file_state_director.convert_pos1(pos2)

        if detector_type is DetectorType.Lab:
            user_file_state_director.set_move_builder_LAB_sample_centre_pos1(pos1)
            user_file_state_director.set_move_builder_LAB_sample_centre_pos2(pos2)
        elif detector_type is DetectorType.Hab:
            user_file_state_director.set_move_builder_HAB_sample_centre_pos1(pos1)
            user_file_state_director.set_move_builder_HAB_sample_centre_pos2(pos2)

    @staticmethod
    def _process_trans_fit(command, user_file_state_director):
        fit_data = command.values[0]
        wavelength_low = command.values[1]
        wavelength_high = command.values[2]
        fit_type = command.values[3]
        polynomial_order = command.values[4]

        if fit_data is FitData.Both:
            data_to_fit = [FitData.Sample, FitData.Can]
        else:
            data_to_fit = [fit_data]

        # Set the fit configuration on the Sample
        if FitData.Sample in data_to_fit:
            user_file_state_director.set_calculate_transmission_builder_Sample_fit_type(fit_type)
            if polynomial_order is not None:
                user_file_state_director.set_calculate_transmission_builder_Sample_polynomial_order(polynomial_order)
            user_file_state_director.set_calculate_transmission_builder_Sample_wavelength_low(wavelength_low)
            user_file_state_director.set_calculate_transmission_builder_Sample_wavelength_high(wavelength_high)

        # Set the fit configuration on the Can
        if FitData.Can in data_to_fit:
            user_file_state_director.set_calculate_transmission_builder_Can_fit_type(fit_type)
            if polynomial_order is not None:
                user_file_state_director.set_calculate_transmission_builder_Can_polynomial_order(polynomial_order)
            user_file_state_director.set_calculate_transmission_builder_Can_wavelength_low(wavelength_low)
            user_file_state_director.set_calculate_transmission_builder_Can_wavelength_high(wavelength_high)

    @staticmethod
    def _process_front_detector_rescale(command, user_file_state_director):
        # scale, shift,
        # fitScale, fitShift,
        # qMin, qMax])
        # TODO implement this
        pass

    @staticmethod
    def _process_event_slices(command, user_file_state_director):
        event_slices = command.values
        # TODO implement this

    @staticmethod
    def _process_flood_file(command, user_file_state_director):
        file_name = command.values[0]
        detector_type = command.values[1]
        if detector_type is DetectorType.Lab:
            user_file_state_director.set_wavelength_and_pixel_adjustment_builder_LAB_pixel_adjustment_file(file_name)
        elif detector_type is DetectorType.Hab:
            user_file_state_director.set_wavelength_and_pixel_adjustment_builder_HAB_pixel_adjustment_file(file_name)

    @staticmethod
    def _process_phi_limit(command, user_file_state_director):
        phi_min = command.values[0]
        phi_max = command.values[1]
        use_phi_mirror = command.values[2]
        user_file_state_director.set_mask_builder_phi_min(phi_min)
        user_file_state_director.set_mask_builder_phi_max(phi_max)
        user_file_state_director.set_mask_builder_use_mask_phi_mirror(use_phi_mirror)

    @staticmethod
    def _process_wavelength_correction_file(command, user_file_state_director):
        detector_type = command.values[0]
        file_name = command.values[1]
        if detector_type is DetectorType.Lab:
            user_file_state_director.set_wavelength_and_pixel_adjustment_builder_LAB_wavelength_adjustment_file(
                file_name)
        elif detector_type is DetectorType.Hab:
            user_file_state_director.set_wavelength_and_pixel_adjustment_builder_HAB_wavelength_adjustment_file(
                file_name)

    @staticmethod
    def _process_mask_radius(command, user_file_state_director):
        radius_min = command.values[0]
        radius_max = command.values[1]
        user_file_state_director.set_mask_builder_radius_min(radius_min)
        user_file_state_director.set_mask_builder_radius_max(radius_max)

    @staticmethod
    def _process_wavelength_limit(command, user_file_state_director):
        wavelength_low = command.values[0]
        wavelength_high = command.values[1]
        wavelength_step = command.values[2]
        wavelength_step_type = command.values[3]

        # We need to set this in several locations. In:
        # 1. SANSStateWavelength
        # 2. SANSStateNormalizeToMonitor
        # 3. SANSStateCalculateTransmission
        # 4. SANStateWavelengthAndPixel
        user_file_state_director.set_wavelength_builder_wavelength_low(wavelength_low)
        user_file_state_director.set_wavelength_builder_wavelength_high(wavelength_high)
        user_file_state_director.set_wavelength_builder_wavelength_step(wavelength_step)
        user_file_state_director.set_wavelength_builder_wavelength_step_type(wavelength_step_type)

        user_file_state_director.set_normalize_to_monitor_builder_wavelength_low(wavelength_low)
        user_file_state_director.set_normalize_to_monitor_builder_wavelength_high(wavelength_high)
        user_file_state_director.set_normalize_to_monitor_builder_wavelength_step(wavelength_step)
        user_file_state_director.set_normalize_to_monitor_builder_wavelength_step_type(wavelength_step_type)

        user_file_state_director.set_calculate_transmission_builder_wavelength_low(wavelength_low)
        user_file_state_director.set_calculate_transmission_builder_wavelength_high(wavelength_high)
        user_file_state_director.set_calculate_transmission_builder_wavelength_step(wavelength_step)
        user_file_state_director.set_calculate_transmission_builder_wavelength_step_type(wavelength_step_type)

        user_file_state_director.set_wavelength_and_pixel_adjustment_builder_wavelength_low(wavelength_low)
        user_file_state_director.set_wavelength_and_pixel_adjustment_builder_wavelength_high(wavelength_high)
        user_file_state_director.set_wavelength_and_pixel_adjustment_builder_wavelength_step(wavelength_step)
        user_file_state_director.set_wavelength_and_pixel_adjustment_builder_wavelength_step_type(wavelength_step_type)

    @staticmethod
    def _process_qxy_limit(command, user_file_state_director):
        _ = command.values[0]
        qmax = command.values[1]
        step = command.values[2]
        step_type = command.values[3]
        user_file_state_director.set_convert_to_q_builder_q_xy_max(qmax)
        user_file_state_director.set_convert_to_q_builder_q_xy_step(step)
        user_file_state_director.set_convert_to_q_builder_q_xy_step_type(step_type)
