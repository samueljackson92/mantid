import unittest
import mantid

from sans.state.reduction_mode import (StateReductionMode, get_reduction_mode_builder)
from sans.state.data import get_data_builder
from sans.common.sans_type import (ISISReductionMode, ReductionDimensionality, FitModeForMerge,
                                   SANSFacility, SANSInstrument)
from sans.common.constants import SANSConstants


# ----------------------------------------------------------------------------------------------------------------------
# State
# ----------------------------------------------------------------------------------------------------------------------
class StateReductionModeTest(unittest.TestCase):
    def test_that_converter_methods_work(self):
        # Arrange
        state = StateReductionMode()

        state.reduction_mode = ISISReductionMode.Merged
        state.dimensionality = ReductionDimensionality.TwoDim
        state.merge_shift = 12.65
        state.merge_scale = 34.6
        state.merge_fit_mode = FitModeForMerge.ShiftOnly

        state.detector_names[SANSConstants.low_angle_bank] = "Test1"
        state.detector_names[SANSConstants.high_angle_bank] = "Test2"

        # Assert
        merge_strategy = state.get_merge_strategy()
        self.assertTrue(merge_strategy[0] is ISISReductionMode.Lab)
        self.assertTrue(merge_strategy[1] is ISISReductionMode.Hab)

        all_reductions = state.get_all_reduction_modes()
        self.assertTrue(len(all_reductions) == 2)
        self.assertTrue(all_reductions[0] is ISISReductionMode.Lab)
        self.assertTrue(all_reductions[1] is ISISReductionMode.Hab)

        result_lab = state.get_detector_name_for_reduction_mode(ISISReductionMode.Lab)
        self.assertTrue(result_lab == "Test1")
        result_hab = state.get_detector_name_for_reduction_mode(ISISReductionMode.Hab)
        self.assertTrue(result_hab == "Test2")

        self.assertRaises(RuntimeError, state.get_detector_name_for_reduction_mode, "non_sense")


# ----------------------------------------------------------------------------------------------------------------------
# Builder
# ----------------------------------------------------------------------------------------------------------------------
class StateReductionModeBuilderTest(unittest.TestCase):
    def test_that_reduction_state_can_be_built(self):
        # Arrange
        facility = SANSFacility.ISIS
        data_builder = get_data_builder(facility)
        data_builder.set_sample_scatter("LOQ74044")
        data_info = data_builder.build()

        # Act
        builder = get_reduction_mode_builder(data_info)
        self.assertTrue(builder)

        mode = ISISReductionMode.Merged
        dim = ReductionDimensionality.OneDim
        builder.set_reduction_mode(mode)
        builder.set_reduction_dimensionality(dim)

        merge_shift = 324.2
        merge_scale = 3420.98
        fit_mode = FitModeForMerge.Both
        builder.set_merge_fit_mode(fit_mode)
        builder.set_merge_shift(merge_shift)
        builder.set_merge_scale(merge_scale)

        state = builder.build()

        # Assert
        self.assertTrue(state.reduction_mode is mode)
        self.assertTrue(state.reduction_dimensionality is dim)
        self.assertTrue(state.merge_fit_mode == fit_mode)
        self.assertTrue(state.merge_shift == merge_shift)
        self.assertTrue(state.merge_scale == merge_scale)
        detector_names = state.detector_names
        self.assertTrue(detector_names[SANSConstants.low_angle_bank] == "main-detector-bank")


if __name__ == '__main__':
    unittest.main()