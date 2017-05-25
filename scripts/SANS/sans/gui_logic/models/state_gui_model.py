from sans.user_file.user_file_common import OtherId, DetectorId, event_binning_string_values
from sans.common.enums import ReductionDimensionality, ISISReductionMode


class StateGuiModel(object):
    def __init__(self, user_file_items):
        super(StateGuiModel, self).__init__()
        self._user_file_items = user_file_items

    @property
    def settings(self):
        return self._user_file_items

    def get_simple_element(self, element_id, default_value,):
        if element_id in self._user_file_items:
            return self._user_file_items[element_id]
        else:
            return default_value

    def set_simple_element(self, element_id, value, expected_types):
        is_valid = any([value is expected_type for expected_type in expected_types])

        if is_valid:
            if element_id in self._user_file_items:
                del self._user_file_items[element_id]
            new_state_entries = {element_id: [value]}
            self._user_file_items.update(new_state_entries)
        else:
            raise ValueError("A reduction mode was expected, got instead {}".format(value))

    # ------------------------------------------------------------------------------------------------------------------
    # Event slices
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def event_slices(self):
        if OtherId.event_slices in self._user_file_items:
            return self._user_file_items[OtherId.event_slices][-1].value
        else:
            return ""

    @event_slices.setter
    def event_slices(self, value):
        if not value:
            return
        if OtherId.event_slices in self._user_file_items:
            del self._user_file_items[OtherId.event_slices]
        new_state_entries = {OtherId.event_slices: [event_binning_string_values(value=value)]}
        self._user_file_items.update(new_state_entries)

    # ------------------------------------------------------------------------------------------------------------------
    # Reduction dimensionality
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def reduction_dimensionality(self):
        if OtherId.reduction_dimensionality in self._user_file_items:
            return self._user_file_items[OtherId.reduction_dimensionality][-1]
        else:
            return ReductionDimensionality.OneDim

    @reduction_dimensionality.setter
    def reduction_dimensionality(self, value):
        if value is ReductionDimensionality.OneDim or value is ReductionDimensionality.TwoDim:
            if OtherId.reduction_dimensionality in self._user_file_items:
                del self._user_file_items[OtherId.reduction_dimensionality]
            new_state_entries = {OtherId.reduction_dimensionality: [value]}
            self._user_file_items.update(new_state_entries)
        else:
            raise ValueError("A reduction dimensionality was expected, got instead {}".format(value))

    # ------------------------------------------------------------------------------------------------------------------
    # Reduction Mode
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def reduction_mode(self):
        if DetectorId.reduction_mode in self._user_file_items:
            return self._user_file_items[DetectorId.reduction_mode][-1]
        else:
            return ISISReductionMode.LAB

    @reduction_mode.setter
    def reduction_mode(self, value):
        if value is ISISReductionMode.LAB or value is ISISReductionMode.HAB or\
                        value is ISISReductionMode.Merged or ISISReductionMode.All:
            if DetectorId.reduction_mode in self._user_file_items:
                del self._user_file_items[DetectorId.reduction_mode]
            new_state_entries = {DetectorId.reduction_mode: [value]}
            self._user_file_items.update(new_state_entries)
        else:
            raise ValueError("A reduction mode was expected, got instead {}".format(value))

    # ------------------------------------------------------------------------------------------------------------------
    # Reduction Mode
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def wavelength_rebin_type(self):
        return self.get_simple_element(element_id=DetectorId.reduction_mode, default_value=ISISReductionMode.LAB)

    @wavelength_rebin_type.setter
    def wavelength_rebin_type(self, value):
        if value is ISISReductionMode.LAB or value is ISISReductionMode.HAB or\
                        value is ISISReductionMode.Merged or ISISReductionMode.All:
            if DetectorId.reduction_mode in self._user_file_items:
                del self._user_file_items[DetectorId.reduction_mode]
            new_state_entries = {DetectorId.reduction_mode: [value]}
            self._user_file_items.update(new_state_entries)
        else:
            raise ValueError("A reduction mode was expected, got instead {}".format(value))

    # ------------------------------------------------------------------------------------------------------------------
    # Save Options
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def zero_error_free(self):
        if OtherId.save_as_zero_error_free in self._user_file_items:
            return self._user_file_items[OtherId.save_as_zero_error_free][-1]
        else:
            # Turn on zero error free saving by default
            return True

    @zero_error_free.setter
    def zero_error_free(self, value):
        if value is None:
            return
        if OtherId.save_as_zero_error_free in self._user_file_items:
            del self._user_file_items[OtherId.save_as_zero_error_free]
        new_state_entries = {OtherId.save_as_zero_error_free: [value]}
        self._user_file_items.update(new_state_entries)

    @property
    def save_format(self):
        return True

    @save_format.setter
    def save_format(self, value):
        pass
