import unittest
import mantid
import os
from SANS2.Common.SANSType import (ISISReductionMode, DetectorType, RangeStepType, FitType)
from SANS2.UserFile.UserFileReader import UserFileReader
from SANS2.UserFile.UserFileCommon import *
from UserFileTestHelper import create_user_file, sample_user_file


# -----------------------------------------------------------------
# --- Tests -------------------------------------------------------
# -----------------------------------------------------------------
class UserFileReaderTest(unittest.TestCase):
    def test_that_can_read_user_file(self):
        # Arrange
        user_file_path = create_user_file(sample_user_file)
        reader = UserFileReader(user_file_path)

        # Act
        output = reader.read_user_file()

        # Assert
        expected_values = {user_file_limits_wavelength: [simple_range(start=1.5, stop=12.5, step=0.125,
                                                                      step_type=RangeStepType.Lin)],
                           user_file_limits_q: [complex_range(.001, .001, .0126, .08, .2,
                                                              step_type1=RangeStepType.Lin,
                                                              step_type2=RangeStepType.Log)],
                           user_file_limits_qxy: [simple_range(0, 0.05, 0.001, RangeStepType.Lin)],
                           user_file_back_single_monitors: [back_single_monitor_entry(1, 35000, 65000),
                                                            back_single_monitor_entry(2, 85000, 98000)],
                           user_file_det_reduction_mode: [ISISReductionMode.Lab],
                           user_file_gravity_on_off: [True],
                           user_file_fit_general: [fit_general(start=1.5, stop=12.5, fit_type=FitType.Log,
                                                               data_type=None, polynomial_order=0)],
                           user_file_mask_vertical_single_strip_mask: [single_entry_with_detector(191,
                                                                                                  DetectorType.Lab),
                                                                       single_entry_with_detector(191,
                                                                                                  DetectorType.Hab),
                                                                       single_entry_with_detector(0, DetectorType.Lab),
                                                                       single_entry_with_detector(0, DetectorType.Hab)],
                           user_file_mask_horizontal_single_strip_mask: [single_entry_with_detector(0,
                                                                                                  DetectorType.Lab),
                                                                         single_entry_with_detector(0,
                                                                                                    DetectorType.Hab)],
                           user_file_mask_horizontal_range_strip_mask: [range_entry_with_detector(190, 191,
                                                                                                  DetectorType.Lab),
                                                                        range_entry_with_detector(167, 172,
                                                                                                  DetectorType.Lab),
                                                                        range_entry_with_detector(190, 191,
                                                                                                  DetectorType.Hab),
                                                                        range_entry_with_detector(156, 159,
                                                                                                  DetectorType.Hab)
                                                                        ],
                           user_file_mask_time: [range_entry_with_detector(17500, 22000, None)],
                           user_file_mon_direct: [monitor_file("DIRECTM1_15785_12m_31Oct12_v12.dat", DetectorType.Lab),
                                                  monitor_file("DIRECTM1_15785_12m_31Oct12_v12.dat", DetectorType.Hab)],
                           user_file_mon_spectrum: [monitor_spectrum(1, True, True), monitor_spectrum(1, False, True)],
                           user_file_set_centre: [position_entry(155.45, -169.6, DetectorType.Lab)],
                           user_file_set_scales: [set_scales_entry(0.074, 1.0, 1.0, 1.0, 1.0)],
                           user_file_sample_offset: [53],
                           user_file_det_correction_x: [single_entry_with_detector(-16.0, DetectorType.Lab),
                                                        single_entry_with_detector(-44.0, DetectorType.Hab)],
                           user_file_det_correction_y: [single_entry_with_detector(-20.0, DetectorType.Hab)],
                           user_file_det_correction_z: [single_entry_with_detector(47.0, DetectorType.Lab),
                                                        single_entry_with_detector(47.0, DetectorType.Hab)],
                           user_file_det_correction_rotation: [single_entry_with_detector(0.0, DetectorType.Hab)],
                           user_file_limits_events_binning: [rebin_string_values(rebin_values=[7000.0, 500.0,
                                                                                               60000.0])],
                           user_file_mask_clear_detector_mask: [True],
                           user_file_mask_clear_time_mask : [True],
                           user_file_limits_radius: [range_entry(12, 15)],
                           user_file_trans_spec_shift: [-70],
                           user_file_print: ["for changer"],
                           user_file_back_all_monitors: [range_entry(start=3500, stop=4500)],
                           user_file_fit_monitor_times: [range_entry(start=1000, stop=2000)],
                           user_file_trans_spec: [4],
                           user_file_back_trans: [range_entry(start=123, stop=466)],
                           user_file_trans_radius: [7.0],
                           user_file_trans_roi: ["test.xml", "test2.xml"],
                           user_file_trans_mask: ["test3.xml", "test4.xml"],
                           user_file_sample_path: [True],
                           user_file_limits_radius_cut: [200],
                           user_file_limits_wavelength_cut: [8.0],
                           user_file_q_resolution_on: [True],
                           user_file_q_resolution_delta_r: [11.],
                           user_file_q_resolution_collimation_length: [12.],
                           user_file_q_resolution_a1: [13.],
                           user_file_q_resolution_a2: [14.],
                           user_file_q_resolution_moderator: ["moderator_rkh_file.txt"]
                           }

        self.assertTrue(len(expected_values) == len(output))
        for key, value in expected_values.items():
            self.assertTrue(key in output)
            self.assertTrue(len(output[key]) == len(value))
            self.assertTrue(sorted(output[key]) == sorted(value))

        # clean up
        if os.path.exists(user_file_path):
            os.remove(user_file_path)

if __name__ == "__main__":
    unittest.main()
