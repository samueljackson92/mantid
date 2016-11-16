# pylint: disable=too-few-public-methods

"""State describing the conversion to momentum transfer"""

import json
from SANS2.State.SANSStateBase import (SANSStateBase, sans_parameters, BoolParameter, PositiveFloatParameter,
                                       ClassTypeParameter, StringParameter)
from SANS2.Common.SANSEnumerations import (ReductionDimensionality, RangeStepType)
from SANS2.Common.SANSFunctions import is_pure_none_or_not_none


# ------------------------------------------------
# SANSStateConvertToQ
# ------------------------------------------------
class SANSStateConvertToQ(object):
    pass


@sans_parameters
class SANSStateConvertToQISIS(SANSStateBase, SANSStateConvertToQ):
    reduction_dimensionality = ClassTypeParameter(ReductionDimensionality)
    use_gravity = BoolParameter()
    gravity_extra_length = PositiveFloatParameter()
    radius_cutoff = PositiveFloatParameter()
    wavelength_cutoff = PositiveFloatParameter()

    # 1D settings
    # The complex binning instructions require a second step and a mid point, which produces:
    #   start -> step -> mid -> step2 -> stop
    # The simple form is:
    #   start -> step -> stop
    q_min = PositiveFloatParameter()
    q_max = PositiveFloatParameter()
    q_step = PositiveFloatParameter()
    q_step_type = ClassTypeParameter(RangeStepType)
    q_step2 = PositiveFloatParameter()
    q_step_type2 = ClassTypeParameter(RangeStepType)
    q_mid = PositiveFloatParameter()

    # 2D settings
    q_xy_max = PositiveFloatParameter()
    q_xy_step = PositiveFloatParameter()
    q_xy_step_type = ClassTypeParameter(RangeStepType)

    # -----------------------
    # Q Resolution specific
    # ---------------------
    use_q_resolution = BoolParameter()
    q_resolution_collimation_length = PositiveFloatParameter()
    q_resolution_delta_r = PositiveFloatParameter()
    moderator_file = StringParameter()

    # Circular aperture settings
    q_resolution_a1 = PositiveFloatParameter()
    q_resolution_a2 = PositiveFloatParameter()

    # Rectangular aperture settings
    q_resolution_h1 = PositiveFloatParameter()
    q_resolution_h2 = PositiveFloatParameter()
    q_resolution_w1 = PositiveFloatParameter()
    q_resolution_w2 = PositiveFloatParameter()

    def __init__(self):
        super(SANSStateConvertToQISIS, self).__init__()
        self.reduction_dimensionality = ReductionDimensionality.OneDim
        self.use_gravity = False
        self.gravity_extra_length = 0.0
        self.use_q_resolution = False

    def validate(self):
        is_invalid = {}

        # 1D Q settings
        if not is_pure_none_or_not_none([self.q_min, self.q_max]):
            is_invalid.update({"q_min or q_max": "Either only q_min {0} or the q_max {1} was set. Either none are set "
                                                 "or both.".format(self.q_min, self.q_max)})
        if (self.q_min is not None and self.q_max is not None) and self.q_min > self.q_max:
            is_invalid.update({"q_min or q_max": "The q_min value {0} was larger than the q_max value"
                                                 " {1}.".format(self.q_min, self.q_max)})

        if self.reduction_dimensionality is ReductionDimensionality.OneDim:
            if self.q_min is None or self.q_max is None:
                is_invalid.update({"q_min or q_max or q_step or q_step_type": "Not all q entries were set for a "
                                                    "1D reduction.".format(self.q_min, self.q_max)})

        if self.reduction_dimensionality is ReductionDimensionality.TwoDim:
            if self.q_xy_max is None or self.q_xy_step is None:
                is_invalid.update({"q_xy_max or q_xy_step": "Not all q entries were set for a 2D "
                                                            "reduction".format(self.q_min, self.q_max)})

        # Q Resolution settings
        if self.use_q_resolution:
            if not is_pure_none_or_not_none([self.q_resolution_a1, self.q_resolution_a2]):
                is_invalid.update({"q_resolution_a1 or q_resolution_a2": "The q_resolution_a2 value {0} was larger "
                            "than the q_resolution_a2 value {1}.".format(self.q_resolution_a1, self.q_resolution_a2)})
            if not is_pure_none_or_not_none([self.q_resolution_a1, self.q_resolution_a2]):
                is_invalid.update({"q_resolution_a1 or q_resolution_a2": "The q_resolution_a2 value {0} was larger "
                                                                         "than the q_resolution_a2 value {1}."
                                                                         "".format(self.q_resolution_a1,
                                                                                   self.q_resolution_a2)})
            if not is_pure_none_or_not_none([self.q_resolution_h1, self.q_resolution_h2, self.q_resolution_w1,
                                             self.q_resolution_w2]):
                is_invalid.update({"q_resolution_hX or q_resolution_wX": "Not all entries for rectangular apertures "
                                                                         "were specified."})
            if all(element is None for element in [self.q_resolution_a1, self.q_resolution_a2, self.q_resolution_w1,
                                                   self.q_resolution_w2, self.q_resolution_h1, self.q_resolution_h2]):
                is_invalid.update({"q_resolution_hX or q_resolution_wX or q_resolution_aX": "The aperture is undefined."
                                   " You either have to specify a rectangular or a circular aperture."})
            if self.moderator_file is None:
                is_invalid.update({"moderator_file": "A moderator file is required for the q resolution calculation."})

        if is_invalid:
            raise ValueError("SANSStateMoveDetectorISIS: The provided inputs are illegal. "
                             "Please see: {0}".format(json.dumps(is_invalid)))


# -----------------------------------------------
# SANSStateConvertToQ setup for other facilities/techniques/scenarios.
# Needs to derive from SANSStateConvertToQ and SANSStateBase and fulfill its contract.
# -----------------------------------------------
