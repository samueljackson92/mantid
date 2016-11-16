import os
import unittest
import mantid


from SANS2.UserFile.UserFileStateDirector import UserFileStateDirectorISIS
from SANS2.Common.SANSEnumerations import (SANSFacility, ISISReductionMode, RangeStepType, RebinType,
                                           DataType, convert_reduction_data_type_to_string, FitType,
                                           convert_detector_type_to_string, DetectorType)
from SANS2.Common.SANSConfigurations import SANSConfigurations
from SANS2.State.StateBuilder.SANSStateDataBuilder import get_data_builder
from SANS2.UserFile.UserFileCommon import *

from SANS2.Common.SANSConstants import SANSConstants
from UserFileTestHelper import create_user_file, sample_user_file


# -----------------------------------------------------------------
# --- Tests -------------------------------------------------------
# -----------------------------------------------------------------
class UserFileStateDirectorISISTest(unittest.TestCase):
    def _assert_move(self, state):
        move = state.move
        # Check the elements which were set on move
        self.assertTrue(move.sample_offset == 53.0/1000.)

        # Detector specific
        lab = move.detectors[SANSConstants.low_angle_bank]
        hab = move.detectors[SANSConstants.high_angle_bank]
        self.assertTrue(lab.x_translation_correction == -16.0/1000.)
        self.assertTrue(lab.z_translation_correction == 47.0/1000.)
        self.assertTrue(hab.x_translation_correction == -44.0/1000.)
        self.assertTrue(hab.y_translation_correction == -20.0/1000.)
        self.assertTrue(hab.z_translation_correction == 47.0/1000.)
        self.assertTrue(hab.rotation_correction == 0.0)

        # SANS2D-specific
        self.assertTrue(move.monitor_4_offset == -70.0/1000.)

    def _assert_mask(self, state):
        mask = state.mask
        self.assertTrue(mask.radius_min == 12/1000.)
        self.assertTrue(mask.radius_max == 15/1000.)
        self.assertTrue(mask.clear is True)
        self.assertTrue(mask.clear_time is True)
        self.assertTrue(mask.detectors[SANSConstants.low_angle_bank].single_horizontal_strip_mask == [0])
        self.assertTrue(mask.detectors[SANSConstants.low_angle_bank].single_vertical_strip_mask == [0, 191])
        self.assertTrue(mask.detectors[SANSConstants.high_angle_bank].single_horizontal_strip_mask == [0])
        self.assertTrue(mask.detectors[SANSConstants.high_angle_bank].single_vertical_strip_mask == [0, 191])
        self.assertTrue(mask.detectors[SANSConstants.low_angle_bank].range_horizontal_strip_start == [190, 167])
        self.assertTrue(mask.detectors[SANSConstants.low_angle_bank].range_horizontal_strip_stop == [191, 172])
        self.assertTrue(mask.detectors[SANSConstants.high_angle_bank].range_horizontal_strip_start == [190, 156])
        self.assertTrue(mask.detectors[SANSConstants.high_angle_bank].range_horizontal_strip_stop == [191, 159])

    def _assert_reduction(self, state):
        reduction = state.reduction
        self.assertTrue(reduction.reduction_mode is ISISReductionMode.Lab)

    def _assert_scale(self, state):
        scale = state.scale
        self.assertTrue(scale.scale == 0.074)

    def _assert_wavelength(self, state):
        wavelength = state.wavelength
        self.assertTrue(wavelength.wavelength_low == 1.5)
        self.assertTrue(wavelength.wavelength_high == 12.5)
        self.assertTrue(wavelength.wavelength_step == 0.125)
        self.assertTrue(wavelength.wavelength_step_type is RangeStepType.Lin)

    def _assert_convert_to_q(self, state):
        convert_to_q = state.convert_to_q
        self.assertTrue(convert_to_q.wavelength_cutoff == 8.0)
        self.assertTrue(convert_to_q.radius_cutoff == 0.2)
        self.assertTrue(convert_to_q.q_min == .001)
        self.assertTrue(convert_to_q.q_max == .2)
        self.assertTrue(convert_to_q.q_step == .001)
        self.assertTrue(convert_to_q.q_step_type is RangeStepType.Lin)
        self.assertTrue(convert_to_q.q_step2 == .08)
        self.assertTrue(convert_to_q.q_step_type2 is RangeStepType.Log)
        self.assertTrue(convert_to_q.use_gravity)

        self.assertTrue(convert_to_q.use_q_resolution)
        self.assertTrue(convert_to_q.q_resolution_a1 == 13./1000.)
        self.assertTrue(convert_to_q.q_resolution_a2 == 14./1000.)
        self.assertTrue(convert_to_q.q_resolution_delta_r == 11./1000.)
        self.assertTrue(convert_to_q.moderator_file == "moderator_rkh_file.txt")
        self.assertTrue(convert_to_q.q_resolution_collimation_length == 12.)

    def _assert_adjustment(self, state):
        adjustment = state.adjustment

        # Normalize to monitor settings
        normalize_to_monitor = adjustment.normalize_to_monitor
        self.assertTrue(normalize_to_monitor.prompt_peak_correction_min == 1000)
        self.assertTrue(normalize_to_monitor.prompt_peak_correction_max == 2000)
        self.assertTrue(normalize_to_monitor.rebin_type is RebinType.InterpolatingRebin)
        self.assertTrue(normalize_to_monitor.wavelength_low == 1.5)
        self.assertTrue(normalize_to_monitor.wavelength_high == 12.5)
        self.assertTrue(normalize_to_monitor.wavelength_step == 0.125)
        self.assertTrue(normalize_to_monitor.wavelength_step_type is RangeStepType.Lin)
        self.assertTrue(normalize_to_monitor.background_TOF_general_start == 3500)
        self.assertTrue(normalize_to_monitor.background_TOF_general_stop == 4500)
        self.assertTrue(normalize_to_monitor.background_TOF_monitor_start["1"] == 35000)
        self.assertTrue(normalize_to_monitor.background_TOF_monitor_stop["1"] == 65000)
        self.assertTrue(normalize_to_monitor.background_TOF_monitor_start["2"] == 85000)
        self.assertTrue(normalize_to_monitor.background_TOF_monitor_stop["2"] == 98000)
        self.assertTrue(normalize_to_monitor.incident_monitor == 1)

        # Calculate Transmission
        calculate_transmission = adjustment.calculate_transmission
        self.assertTrue(calculate_transmission.prompt_peak_correction_min == 1000)
        self.assertTrue(calculate_transmission.prompt_peak_correction_max == 2000)
        self.assertTrue(calculate_transmission.default_transmission_monitor == 3)
        self.assertTrue(calculate_transmission.default_incident_monitor == 2)
        self.assertTrue(calculate_transmission.incident_monitor == 1)
        self.assertTrue(calculate_transmission.transmission_radius_on_detector == 0.007)  # This is in mm
        self.assertTrue(calculate_transmission.transmission_roi_files == ["test.xml", "test2.xml"])
        self.assertTrue(calculate_transmission.transmission_mask_files == ["test3.xml", "test4.xml"])
        self.assertTrue(calculate_transmission.transmission_monitor == 4)
        self.assertTrue(calculate_transmission.rebin_type is RebinType.InterpolatingRebin)
        self.assertTrue(calculate_transmission.wavelength_low == 1.5)
        self.assertTrue(calculate_transmission.wavelength_high == 12.5)
        self.assertTrue(calculate_transmission.wavelength_step == 0.125)
        self.assertTrue(calculate_transmission.wavelength_step_type is RangeStepType.Lin)
        self.assertFalse(calculate_transmission.use_full_wavelength_range)
        self.assertTrue(calculate_transmission.wavelength_full_range_low ==
                        SANSConfigurations.SANS2D.wavelength_full_range_low)
        self.assertTrue(calculate_transmission.wavelength_full_range_high ==
                        SANSConfigurations.SANS2D.wavelength_full_range_high)
        self.assertTrue(calculate_transmission.background_TOF_general_start == 3500)
        self.assertTrue(calculate_transmission.background_TOF_general_stop == 4500)
        self.assertTrue(calculate_transmission.background_TOF_monitor_start["1"] == 35000)
        self.assertTrue(calculate_transmission.background_TOF_monitor_stop["1"] == 65000)
        self.assertTrue(calculate_transmission.background_TOF_monitor_start["2"] == 85000)
        self.assertTrue(calculate_transmission.background_TOF_monitor_stop["2"] == 98000)
        self.assertTrue(calculate_transmission.background_TOF_roi_start == 123)
        self.assertTrue(calculate_transmission.background_TOF_roi_stop == 466)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Sample)].fit_type is FitType.Log)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Sample)].wavelength_low == 1.5)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Sample)].wavelength_high == 12.5)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Sample)].polynomial_order == 0)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Can)].fit_type is FitType.Log)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Can)].wavelength_low == 1.5)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Can)].wavelength_high == 12.5)
        self.assertTrue(calculate_transmission.fit[
                            convert_reduction_data_type_to_string(DataType.Can)].polynomial_order == 0)

        # Wavelength and Pixel Adjustment
        wavelength_and_pixel_adjustment = adjustment.wavelength_and_pixel_adjustment
        self.assertTrue(wavelength_and_pixel_adjustment.wavelength_low == 1.5)
        self.assertTrue(wavelength_and_pixel_adjustment.wavelength_high == 12.5)
        self.assertTrue(wavelength_and_pixel_adjustment.wavelength_step == 0.125)
        self.assertTrue(wavelength_and_pixel_adjustment.wavelength_step_type is RangeStepType.Lin)
        self.assertTrue(wavelength_and_pixel_adjustment.adjustment_files[
                            convert_detector_type_to_string(DetectorType.Lab)].wavelength_adjustment_file ==
                            "DIRECTM1_15785_12m_31Oct12_v12.dat")
        self.assertTrue(wavelength_and_pixel_adjustment.adjustment_files[
                            convert_detector_type_to_string(DetectorType.Hab)].wavelength_adjustment_file ==
                            "DIRECTM1_15785_12m_31Oct12_v12.dat")

        # Assert wide angle correction
        self.assertTrue(state.adjustment.wide_angle_correction)

    def test_state_can_be_created_from_valid_user_file_with_data_information(self):
        # Arrange
        data_builder = get_data_builder(SANSFacility.ISIS)
        data_builder.set_sample_scatter("SANS2D00022024")
        data_builder.set_sample_scatter_period(3)
        data_state = data_builder.build()

        director = UserFileStateDirectorISIS(data_state)
        user_file_path = create_user_file(sample_user_file)

        director.set_user_file(user_file_path)
        # TODO: Add manual settings

        state = director.construct()

        # Assert
        self._assert_move(state)
        self._assert_mask(state)
        self._assert_reduction(state)
        self._assert_wavelength(state)
        self._assert_scale(state)
        self._assert_adjustment(state)
        self._assert_convert_to_q(state)

        # clean up
        if os.path.exists(user_file_path):
            os.remove(user_file_path)


if __name__ == "__main__":
    unittest.main()
