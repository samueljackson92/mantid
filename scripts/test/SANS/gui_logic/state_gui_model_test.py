from __future__ import (absolute_import, division, print_function)
import unittest
import mantid
from sans.gui_logic.models.state_gui_model import StateGuiModel
from sans.user_file.user_file_common import OtherId, event_binning_string_values
from sans.common.enums import ReductionDimensionality


class StateGuiModelTest(unittest.TestCase):
    # ------------------------------------------------------------------------------------------------------------------
    # Event slices
    # ------------------------------------------------------------------------------------------------------------------
    def test_that_if_no_slice_event_is_present_an_empty_string_is_returned(self):
        state_gui_model = StateGuiModel({"test": 1})
        self.assertTrue(state_gui_model.event_slices == "")

    def test_that_slice_event_can_be_retrieved_if_it_exists(self):
        state_gui_model = StateGuiModel({OtherId.event_slices: [event_binning_string_values(value="test")]})
        self.assertTrue(state_gui_model.event_slices == "test")

    def test_that_slice_event_can_be_updated(self):
        state_gui_model = StateGuiModel({OtherId.event_slices: [event_binning_string_values(value="test")]})
        state_gui_model.event_slices = "test2"
        self.assertTrue(state_gui_model.event_slices == "test2")

    # ------------------------------------------------------------------------------------------------------------------
    # Reduction dimensionality
    # ------------------------------------------------------------------------------------------------------------------
    def test_that_is_1D_reduction_by_default(self):
        state_gui_model = StateGuiModel({"test": [1]})
        self.assertTrue(state_gui_model.reduction_dimensionality is ReductionDimensionality.OneDim)

    def test_that_an_set_to_2D_reduction(self):
        state_gui_model = StateGuiModel({"test": [1]})
        state_gui_model.reduction_dimensionality = ReductionDimensionality.TwoDim
        self.assertTrue(state_gui_model.reduction_dimensionality is ReductionDimensionality.TwoDim)

    def test_that_raises_when_not_setting_with_reduction_dim_enum(self):
        def red_dim_wrapper():
            state_gui_model = StateGuiModel({"test": [1]})
            state_gui_model.reduction_dimensionality = "string"
        self.assertRaises(ValueError, red_dim_wrapper)

    def test_that_can_update_reduction_dimensionality(self):
        state_gui_model = StateGuiModel({OtherId.reduction_dimensionality: [ReductionDimensionality.OneDim]})
        self.assertTrue(state_gui_model.reduction_dimensionality is ReductionDimensionality.OneDim)
        state_gui_model.reduction_dimensionality = ReductionDimensionality.TwoDim
        self.assertTrue(state_gui_model.reduction_dimensionality is ReductionDimensionality.TwoDim)

    # ------------------------------------------------------------------------------------------------------------------
    # Reduction mode
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # Reduction mode
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # Zero error free saving
    # ------------------------------------------------------------------------------------------------------------------
    def test_that_can_zero_error_free_saving_is_default(self):
        state_gui_model = StateGuiModel({"test": [1]})
        self.assertTrue(state_gui_model.zero_error_free)

    def test_that_can_zero_error_free_saving_can_be_changed(self):
        state_gui_model = StateGuiModel({OtherId.save_as_zero_error_free: [True]})
        state_gui_model.zero_error_free = False
        self.assertFalse(state_gui_model.zero_error_free)

if __name__ == '__main__':
    unittest.main()


