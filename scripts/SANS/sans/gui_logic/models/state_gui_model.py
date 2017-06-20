from sans.user_file.user_file_common import (OtherId, DetectorId, LimitsId, SetId, event_binning_string_values, set_scales_entry)
from sans.common.enums import (ReductionDimensionality, ISISReductionMode, RangeStepType)
from sans.user_file.user_file_common import simple_range


class StateGuiModel(object):
    def __init__(self, user_file_items):
        super(StateGuiModel, self).__init__()
        self._user_file_items = user_file_items

    @property
    def settings(self):
        return self._user_file_items

    def get_simple_element(self, element_id, default_value):
        return self.get_simple_element_with_attribute(element_id, default_value)

    def set_simple_element(self, element_id, value, expected_types):
        is_valid = any([value is expected_type for expected_type in expected_types])

        if is_valid:
            if element_id in self._user_file_items:
                del self._user_file_items[element_id]
            new_state_entries = {element_id: [value]}
            self._user_file_items.update(new_state_entries)
        else:
            raise ValueError("A reduction mode was expected, got instead {}".format(value))

    def get_simple_element_with_attribute(self, element_id, default_value, attribute=None):
        if element_id in self._user_file_items:
            element = self._user_file_items[element_id][-1]
            return getattr(element, attribute) if attribute else element
        else:
            return default_value

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
    # Wavelength properties
    # ------------------------------------------------------------------------------------------------------------------
    def _update_wavelength(self, min=None, max=None, step=None, step_type=None):
        if LimitsId.wavelength in self._user_file_items:
            settings = self._user_file_items[LimitsId.wavelength]
        else:
            # If the entry does not already exist, then add it. The -1. is an illegal input which should get overriden
            # and if not we want it to fail.
            settings = [simple_range(start=-1., stop=-1., step=-1., step_type=RangeStepType.Lin)]
            self._user_file_items.update({LimitsId.reduction_mode: settings})
        self._apply_wavelength_settings(min, "start", settings)
        self._apply_wavelength_settings(max, "stop", settings)
        self._apply_wavelength_settings(step, "step", settings)
        self._apply_wavelength_settings(step_type, "step_type", settings)

    @staticmethod
    def _apply_wavelength_settings(element, attribute, settings):
        if element:
            for setting in settings:
                setattr(setting, attribute, element)


    @property
    def wavelength_step_type(self):
        return self.get_simple_element_with_attribute(element_id=LimitsId.wavelength, default_value=RangeStepType.Lin,
                                                      attribute="step_type")

    @wavelength_step_type.setter
    def wavelength_step_type(self, value):
        self._update_wavelength(step_type=value)

    @property
    def wavelength_min(self):
        return self.get_simple_element_with_attribute(element_id=LimitsId.wavelength,
                                                      default_value="",
                                                      attribute="start")

    @wavelength_min.setter
    def wavelength_min(self, value):
        self._update_wavelength(min=value)

    @property
    def wavelength_max(self):
        return self.get_simple_element_with_attribute(element_id=LimitsId.wavelength,
                                                      default_value="",
                                                      attribute="stop")

    @wavelength_max.setter
    def wavelength_max(self, value):
        self._update_wavelength(max=value)

    @property
    def wavelength_step(self):
        return self.get_simple_element_with_attribute(element_id=LimitsId.wavelength,
                                                      default_value="",
                                                      attribute="step")

    @wavelength_step.setter
    def wavelength_step(self, value):
        self._update_wavelength(step=value)

    # ------------------------------------------------------------------------------------------------------------------
    # Scale properties
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def absolute_scale(self):
        return self.get_simple_element_with_attribute(element_id=SetId.scales,
                                                      default_value="",
                                                      attribute="s")

    @absolute_scale.setter
    def absolute_scale(self, value):
        if isinstance(value, float) and value > 0:
            if SetId.scales in self._user_file_items:
                settings = self._user_file_items[SetId.scales]
            else:
                settings = [set_scales_entry(s=100., a=0., b=0., c=0., d=0.)]
                self._user_file_items.update({SetId.scales: settings})
            for setting in settings:
                setting.s = value

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
