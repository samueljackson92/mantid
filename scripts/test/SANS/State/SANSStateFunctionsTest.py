import unittest
import mantid

from SANS2.State.SANSStateFunctions import (get_output_workspace_name, is_pure_none_or_not_none, one_is_none,
                                            validation_message, is_not_none_and_first_larger_than_second)
from SANS2.State.StateDirector.TestDirector import TestDirector
from SANS2.State.SANSStateData import SANSStateData
from SANS2.Common.SANSType import (ReductionDimensionality, ISISReductionMode)


class SANSStateFunctionsTest(unittest.TestCase):
    @staticmethod
    def _get_state():
        test_director = TestDirector()
        state = test_director.construct()

        state.data.sample_scatter_run_number = 12345
        state.data.sample_scatter_period = SANSStateData.ALL_PERIODS

        state.reduction.dimensionality = ReductionDimensionality.OneDim

        state.wavelength.wavelength_low = 12.0
        state.wavelength.wavelength_high = 34.0

        state.mask.phi_min = 12.0
        state.mask.phi_max = 56.0

        state.slice.start_time = [4.56778]
        state.slice.end_time = [12.373938]
        return state

    def test_that_unknown_reduction_mode_raises(self):
        # Arrange
        state = SANSStateFunctionsTest._get_state()

        # Act + Assert
        try:
            get_output_workspace_name(state, ISISReductionMode.All)
            did_raise = False
        except RuntimeError:
            did_raise = True
        self.assertTrue(did_raise)

    def test_that_creates_correct_workspace_name_for_1D(self):
        # Arrange
        state = SANSStateFunctionsTest._get_state()
        # Act
        output_workspace = get_output_workspace_name(state, ISISReductionMode.Lab)
        # Assert
        self.assertTrue("12345rear_1D12.0_34.0Phi12.0_56.0_t4.57_T12.37" == output_workspace)

    def test_that_detects_if_all_entries_are_none_or_not_none_as_true(self):
        self.assertFalse(is_pure_none_or_not_none(["test", None, "test"]))
        self.assertTrue(is_pure_none_or_not_none([None, None, None]))
        self.assertTrue(is_pure_none_or_not_none(["test", "test", "test"]))
        self.assertTrue(is_pure_none_or_not_none([]))

    def test_that_detects_if_one_is_none(self):
        self.assertTrue(one_is_none(["test", None, "test"]))
        self.assertFalse(one_is_none([]))
        self.assertFalse(one_is_none(["test", "test", "test"]))

    def test_test_that_can_detect_when_first_is_larger_than_second(self):
        self.assertTrue(is_not_none_and_first_larger_than_second([1, 2, 3]))
        self.assertTrue(is_not_none_and_first_larger_than_second([2, 1]))
        self.assertFalse(is_not_none_and_first_larger_than_second([1, 2]))

    def test_that_produces_correct_validation_message(self):
        # Arrange
        error_message = "test message."
        instruction = "do this."
        variables = {"var1": 12,
                     "var2": "test"}
        # Act
        val_message = validation_message(error_message, instruction, variables)
        # Assert
        expected_text = "var1: 12\n" \
                        "var2: test\n" \
                        "" + instruction
        self.assertTrue(val_message.keys()[0] == error_message)
        self.assertTrue(val_message[error_message] == expected_text)


if __name__ == '__main__':
    unittest.main()
