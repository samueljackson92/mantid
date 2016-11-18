import unittest
import mantid

from mantid.kernel import (PropertyManagerProperty, PropertyManager)
from mantid.api import Algorithm

from SANS2.State.SANSState import (SANSStateISIS, SANSState)
from SANS2.State.SANSStateData import (SANSStateDataISIS, SANSStateData)
from SANS2.State.SANSStateMove import (SANSStateMoveLOQ)
from SANS2.State.SANSStateReduction import (SANSStateReductionISIS)
from SANS2.State.SANSStateSliceEvent import (SANSStateSliceEventISIS)
from SANS2.State.SANSStateMask import (SANSStateMaskISIS)
from SANS2.State.SANSStateWavelength import (SANSStateWavelengthISIS)
from SANS2.State.SANSStateSave import (SANSStateSaveISIS)
from SANS2.State.SANSStateNormalizeToMonitor import (SANSStateNormalizeToMonitorLOQ)
from SANS2.State.SANSStateScale import (SANSStateScaleISIS)
from SANS2.State.SANSStateCalculateTransmission import (SANSStateCalculateTransmissionLOQ)
from SANS2.State.SANSStateWavelengthAndPixelAdjustment import (SANSStateWavelengthAndPixelAdjustmentISIS)
from SANS2.State.SANSStateAdjustment import (SANSStateAdjustmentISIS)
from SANS2.State.SANSStateConvertToQ import (SANSStateConvertToQISIS)
from SANS2.Common.SANSConstants import SANSConstants
from SANS2.Common.SANSEnumerations import (ISISReductionMode, ReductionDimensionality, FitModeForMerge,
                                           RangeStepType, RebinType, SampleShape)


class SANSStateTest(unittest.TestCase):
    def test_that_is_sans_state_object(self):
        state = SANSStateISIS()
        self.assertTrue(isinstance(state, SANSState))

    def test_that_can_set_and_get_values(self):
        # Arrange
        state = SANSStateISIS()

        # Add the different descriptors of the SANSState here:
        data_state = SANSStateDataISIS()
        data_state.sample_scatter = "sample_scat"
        state.data = data_state

        # Move
        move_state = SANSStateMoveLOQ()
        move_state.detectors[SANSConstants.high_angle_bank].detector_name = "test"
        move_state.detectors[SANSConstants.high_angle_bank].detector_name_short = "test"
        move_state.detectors[SANSConstants.low_angle_bank].detector_name = "test"
        move_state.detectors[SANSConstants.low_angle_bank].detector_name_short = "test"
        state.move = move_state

        # Reduction
        reduction_state = SANSStateReductionISIS()
        reduction_state.reduction_mode = ISISReductionMode.Merged
        reduction_state.dimensionality = ReductionDimensionality.TwoDim
        reduction_state.merge_shift = 12.65
        reduction_state.merge_scale = 34.6
        reduction_state.merge_fit_mode = FitModeForMerge.ShiftOnly
        state.reduction = reduction_state

        # Event Slice
        slice_state = SANSStateSliceEventISIS()
        slice_state.start_time = [12.3, 123.4, 34345.0]
        slice_state.end_time = [12.5, 200., 40000.0]
        state.slice = slice_state

        # Mask
        mask_state = SANSStateMaskISIS()
        mask_state.radius_min = 10.0
        mask_state.radius_max = 20.0
        state.mask = mask_state

        # Wavelength conversion
        wavelength_state = SANSStateWavelengthISIS()
        wavelength_state.wavelength_low = 10.0
        wavelength_state.wavelength_high = 20.0
        wavelength_state.wavelength_step = 2.0
        wavelength_state.wavelength_step_type = RangeStepType.Lin
        wavelength_state.rebin_type = RebinType.Rebin
        state.wavelength = wavelength_state

        # Save state
        save_state = SANSStateSaveISIS()
        save_state.file_name = "test_file_name"
        state.save = save_state

        # Scale state
        scale_state = SANSStateScaleISIS()
        scale_state.shape = SampleShape.Cuboid
        scale_state.thickness = 1.0
        scale_state.width = 2.0
        scale_state.height = 3.0
        scale_state.scale = 4.0
        state.scale = scale_state
        
        # Adjustment state
        normalize_to_monitor_state = SANSStateNormalizeToMonitorLOQ()
        normalize_to_monitor_state.rebin_type = RebinType.Rebin
        normalize_to_monitor_state.wavelength_low = 1.0
        normalize_to_monitor_state.wavelength_high = 2.0
        normalize_to_monitor_state.wavelength_step = 1.0
        normalize_to_monitor_state.wavelength_step_type = RangeStepType.Lin
        normalize_to_monitor_state.background_TOF_general_start = 1.0
        normalize_to_monitor_state.background_TOF_general_stop = 2.0
        normalize_to_monitor_state.background_TOF_monitor_start = {"1": 12, "2": 13}
        normalize_to_monitor_state.background_TOF_monitor_stop = {"1": 15, "2": 18}
        normalize_to_monitor_state.incident_monitor = 12

        calculate_transmission_state = SANSStateCalculateTransmissionLOQ()
        calculate_transmission_state.transmission_monitor = 3
        calculate_transmission_state.incident_monitor = 1
        calculate_transmission_state.rebin_type = RebinType.Rebin
        calculate_transmission_state.wavelength_low = 1.0
        calculate_transmission_state.wavelength_high = 2.0
        calculate_transmission_state.wavelength_step = 1.0
        calculate_transmission_state.wavelength_step_type = RangeStepType.Lin
        calculate_transmission_state.background_TOF_general_start = 1.0
        calculate_transmission_state.background_TOF_general_stop = 2.0
        calculate_transmission_state.background_TOF_monitor_start = {"1": 12, "2": 13}
        calculate_transmission_state.background_TOF_monitor_stop = {"1": 15, "2": 18}

        wavelength_and_pixel_state = SANSStateWavelengthAndPixelAdjustmentISIS()
        wavelength_and_pixel_state.wavelength_low = 1.0
        wavelength_and_pixel_state.wavelength_high = 10.0
        wavelength_and_pixel_state.wavelength_step = 2.0
        wavelength_and_pixel_state.wavelength_step_type = RangeStepType.Lin

        adjustment_state = SANSStateAdjustmentISIS()
        adjustment_state.normalize_to_monitor = normalize_to_monitor_state
        adjustment_state.calculate_transmission = calculate_transmission_state
        adjustment_state.wavelength_and_pixel_adjustment = wavelength_and_pixel_state
        adjustment_state.wide_angle_correction = False
        state.adjustment = adjustment_state

        convert_to_q_state = SANSStateConvertToQISIS()
        convert_to_q_state.reduction_dimensionality = ReductionDimensionality.OneDim
        convert_to_q_state.use_gravity = False
        convert_to_q_state.radius_cutoff = 0.002
        convert_to_q_state.wavelength_cutoff = 1.
        convert_to_q_state.q_min = 1.
        convert_to_q_state.q_max = 2.
        convert_to_q_state.q_step = 0.1
        convert_to_q_state.q_step_type = RangeStepType.Lin
        convert_to_q_state.use_q_resolution = False
        state.convert_to_q = convert_to_q_state

        # Assert
        try:
            state.validate()
            is_valid = True
        except ValueError:
            is_valid = False
        self.assertTrue(is_valid)

    def test_that_invalid_types_for_parameters_raise_type_error(self):
        # Arrange
        state = SANSStateISIS()

        # Act + Assert
        try:
            state.data = ["sdf"]
            is_valid = True
        except TypeError:
            is_valid = False
        self.assertFalse(is_valid)

    def test_that_descriptor_validators_work(self):
        # Arrange
        state = SANSStateISIS()

        # We are not setting sample_scatter on the SANSStateDataISIS making it invalid
        data = SANSStateDataISIS()

        # Act + Assert
        try:
            state.data = data
            is_valid = True
        except ValueError:
            is_valid = False
        self.assertFalse(is_valid)

    def test_that_sans_state_holds_a_copy_of_the_substates_and_not_only_a_reference(self):
        # Arrange
        state = SANSStateISIS()
        data = SANSStateDataISIS()
        ws_name_1 = "sample_scat"
        ws_name_2 = "sample_scat2"
        data.sample_scatter = ws_name_1
        state.data = data

        # Act
        data.sample_scatter = ws_name_2

        # Assert
        stored_name = state.data.sample_scatter
        self.assertTrue(stored_name == ws_name_1)

    def test_that_property_manager_can_be_generated_from_state_object(self):
        class FakeAlgorithm(Algorithm):
            def PyInit(self):
                self.declareProperty(PropertyManagerProperty("Args"))

            def PyExec(self):
                pass
        # Arrange
        state = SANSStateISIS()

        # Prepare state data
        data_state = SANSStateDataISIS()
        ws_name_sample = "SANS2D00001234"
        ws_name_can = "SANS2D00001234"
        period = 3

        data_state.sample_scatter = ws_name_sample
        data_state.sample_scatter_period = period
        data_state.can_scatter = ws_name_can
        data_state.can_scatter_period = period

        state.data = data_state

        # Prepare the move
        move_state = SANSStateMoveLOQ()
        test_value = 12.4
        test_name = "test_name"
        move_state.detectors[SANSConstants.low_angle_bank].x_translation_correction = test_value
        move_state.detectors[SANSConstants.high_angle_bank].y_translation_correction = test_value
        move_state.detectors[SANSConstants.high_angle_bank].detector_name = test_name
        move_state.detectors[SANSConstants.high_angle_bank].detector_name_short = test_name
        move_state.detectors[SANSConstants.low_angle_bank].detector_name = test_name
        move_state.detectors[SANSConstants.low_angle_bank].detector_name_short = test_name
        state.move = move_state

        # Prepare the reduction
        reduction_state = SANSStateReductionISIS()
        reduction_state.reduction_mode = ISISReductionMode.Merged
        reduction_state.dimensionality = ReductionDimensionality.TwoDim
        reduction_state.merge_shift = 12.65
        reduction_state.merge_scale = 34.6
        reduction_state.merge_fit_mode = FitModeForMerge.ShiftOnly
        state.reduction = reduction_state

        # Prepare the event Slice
        slice_state = SANSStateSliceEventISIS()
        slice_state.start_time = [12.3, 123.4, 34345.0]
        slice_state.end_time = [12.5, 200., 40000.0]
        state.slice = slice_state

        # Prepare the mask
        mask_state = SANSStateMaskISIS()
        mask_state.radius_min = 10.0
        mask_state.radius_max = 20.0
        state.mask = mask_state

        # Wavelength conversion
        wavelength_state = SANSStateWavelengthISIS()
        wavelength_state.wavelength_low = 10.0
        wavelength_state.wavelength_high = 20.0
        wavelength_state.wavelength_step = 2.0
        wavelength_state.wavelength_step_type = RangeStepType.Lin
        wavelength_state.rebin_type = RebinType.Rebin
        state.wavelength = wavelength_state

        # Save state
        save_state = SANSStateSaveISIS()
        save_state.file_name = "test_file_name"
        state.save = save_state

        # Scale state
        scale_state = SANSStateScaleISIS()
        scale_state.shape = SampleShape.Cuboid
        scale_state.thickness = 1.0
        scale_state.width = 2.0
        scale_state.height = 3.0
        scale_state.scale = 4.0
        state.scale = scale_state

        # Adjustment state
        normalize_to_monitor_state = SANSStateNormalizeToMonitorLOQ()
        normalize_to_monitor_state.rebin_type = RebinType.Rebin
        normalize_to_monitor_state.wavelength_low = 1.0
        normalize_to_monitor_state.wavelength_high = 2.0
        normalize_to_monitor_state.wavelength_step = 1.0
        normalize_to_monitor_state.wavelength_step_type = RangeStepType.Lin
        normalize_to_monitor_state.background_TOF_general_start = 1.0
        normalize_to_monitor_state.background_TOF_general_stop = 2.0
        normalize_to_monitor_state.background_TOF_monitor_start = {"1": 12, "2": 13}
        normalize_to_monitor_state.background_TOF_monitor_stop = {"1": 15, "2": 18}
        normalize_to_monitor_state.incident_monitor = 12

        calculate_transmission_state = SANSStateCalculateTransmissionLOQ()
        calculate_transmission_state.transmission_monitor = 3
        calculate_transmission_state.incident_monitor = 1
        calculate_transmission_state.rebin_type = RebinType.Rebin
        calculate_transmission_state.wavelength_low = 1.0
        calculate_transmission_state.wavelength_high = 2.0
        calculate_transmission_state.wavelength_step = 1.0
        calculate_transmission_state.wavelength_step_type = RangeStepType.Lin
        calculate_transmission_state.background_TOF_general_start = 1.0
        calculate_transmission_state.background_TOF_general_stop = 2.0
        calculate_transmission_state.background_TOF_monitor_start = {"1": 12, "2": 13}
        calculate_transmission_state.background_TOF_monitor_stop = {"1": 15, "2": 18}

        wavelength_and_pixel_state = SANSStateWavelengthAndPixelAdjustmentISIS()
        wavelength_and_pixel_state.wavelength_low = 1.0
        wavelength_and_pixel_state.wavelength_high = 10.0
        wavelength_and_pixel_state.wavelength_step = 2.0
        wavelength_and_pixel_state.wavelength_step_type = RangeStepType.Lin

        adjustment_state = SANSStateAdjustmentISIS()
        adjustment_state.normalize_to_monitor = normalize_to_monitor_state
        adjustment_state.calculate_transmission = calculate_transmission_state
        adjustment_state.wavelength_and_pixel_adjustment = wavelength_and_pixel_state
        state.adjustment = adjustment_state

        convert_to_q_state = SANSStateConvertToQISIS()
        convert_to_q_state.reduction_dimensionality = ReductionDimensionality.OneDim
        convert_to_q_state.use_gravity = False
        convert_to_q_state.radius_cutoff = 0.002
        convert_to_q_state.wavelength_cutoff = 1.
        convert_to_q_state.q_min = 1.
        convert_to_q_state.q_max = 2.
        convert_to_q_state.q_step = 0.1
        convert_to_q_state.q_step_type = RangeStepType.Lin
        convert_to_q_state.use_q_resolution = False
        state.convert_to_q = convert_to_q_state

        # Act
        serialized = state.property_manager

        fake = FakeAlgorithm()
        fake.initialize()
        fake.setProperty("Args", serialized)
        property_manager = fake.getProperty("Args").value

        # Assert
        state_2 = SANSStateISIS()
        state_2.property_manager = property_manager

        self.assertTrue(state_2.data.sample_scatter == ws_name_sample)
        self.assertTrue(state_2.data.sample_scatter_period == period)
        self.assertTrue(state_2.data.can_scatter == ws_name_can)
        self.assertTrue(state_2.data.can_scatter_period == period)

        self.assertTrue(state_2.move.detectors[SANSConstants.low_angle_bank].x_translation_correction == test_value)
        self.assertTrue(state_2.move.detectors[SANSConstants.high_angle_bank].y_translation_correction == test_value)
        self.assertTrue(state_2.move.detectors[SANSConstants.high_angle_bank].detector_name == test_name)
        self.assertTrue(state_2.move.detectors[SANSConstants.high_angle_bank].detector_name_short == test_name)

        self.assertTrue(state_2.reduction.reduction_mode is ISISReductionMode.Merged)
        self.assertTrue(state_2.reduction.dimensionality is ReductionDimensionality.TwoDim)
        self.assertTrue(state_2.reduction.merge_shift == 12.65)
        self.assertTrue(state_2.reduction.merge_scale == 34.6)
        self.assertTrue(state_2.reduction.merge_fit_mode == FitModeForMerge.ShiftOnly)

        self.assertTrue(len(state_2.slice.start_time) == 3)
        self.assertTrue(len(state_2.slice.end_time) == 3)
        self.assertTrue(state_2.slice.start_time[1] == 123.4)

        self.assertTrue(state_2.mask.radius_min == 10.)
        self.assertTrue(state_2.mask.radius_max == 20.)

        self.assertTrue(state_2.wavelength.wavelength_low == 10.0)
        self.assertTrue(state_2.wavelength.wavelength_high == 20.0)
        self.assertTrue(state_2.wavelength.wavelength_step == 2.0)
        self.assertTrue(state_2.wavelength.wavelength_step_type is RangeStepType.Lin)
        self.assertTrue(state_2.wavelength.rebin_type is RebinType.Rebin)

        self.assertTrue(state_2.save.file_name == "test_file_name")

        self.assertTrue(state_2.scale.thickness == 1.0)
        self.assertTrue(state_2.scale.width == 2.0)
        self.assertTrue(state_2.scale.height == 3.0)
        self.assertTrue(state_2.scale.scale == 4.0)
        self.assertTrue(state_2.scale.shape is SampleShape.Cuboid)

        # Adjustment state
        self.assertTrue(state_2.adjustment.normalize_to_monitor.rebin_type is RebinType.Rebin)
        self.assertTrue(state_2.adjustment.normalize_to_monitor.wavelength_low == 1.0)
        self.assertTrue(state_2.adjustment.normalize_to_monitor.wavelength_high == 2.0)
        self.assertTrue(state_2.adjustment.normalize_to_monitor.wavelength_step == 1.0)
        self.assertTrue(state_2.adjustment.normalize_to_monitor.background_TOF_monitor_start == {"1": 12, "2": 13})
        self.assertTrue(state_2.adjustment.calculate_transmission.transmission_monitor == 3)
        self.assertTrue(state_2.adjustment.wavelength_and_pixel_adjustment.wavelength_low == 1.0)
        # ConvertToQ state
        self.assertTrue(state_2.convert_to_q.reduction_dimensionality is
                        ReductionDimensionality.OneDim)
        self.assertFalse(state_2.convert_to_q.use_q_resolution)
        self.assertTrue(state_2.convert_to_q.q_min == 1.)
        self.assertTrue(state_2.convert_to_q.q_step_type is RangeStepType.Lin)
        self.assertTrue(state_2.convert_to_q.wavelength_cutoff == 1.)


if __name__ == '__main__':
    unittest.main()
