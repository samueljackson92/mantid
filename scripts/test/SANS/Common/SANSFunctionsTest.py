import unittest
import mantid

from mantid.kernel import (V3D, Quat)
from SANS2.Common.SANSFunctions import (quaternion_to_angle_and_axis, create_unmanaged_algorithm, add_to_sample_log,
                                        convert_bank_name_to_detector_type_isis, parse_event_slice_setting,
                                        get_bins_for_rebin_setting, get_range_lists_from_bin_list,
                                        get_ranges_from_event_slice_setting, get_ranges_for_rebin_array)
from SANS2.Common.SANSType import (DetectorType, RangeStepType)


class SANSFunctionsTest(unittest.TestCase):
    @staticmethod
    def _create_sample_workspace():
        sample_name = "CreateSampleWorkspace"
        sample_options = {"OutputWorkspace": "dummy"}
        sample_alg = create_unmanaged_algorithm(sample_name, **sample_options)
        sample_alg.execute()
        return sample_alg.getProperty("OutputWorkspace").value

    def _do_test_quaternion(self, angle, axis, expected_axis=None):
        # Act
        quaternion = Quat(angle, axis)
        converted_angle, converted_axis = quaternion_to_angle_and_axis(quaternion)

        # Assert
        if expected_axis is not None:
            axis = expected_axis
        self.assertAlmostEqual(angle, converted_angle)
        self.assertAlmostEqual(axis[0], converted_axis[0])
        self.assertAlmostEqual(axis[1], converted_axis[1])
        self.assertAlmostEqual(axis[2], converted_axis[2])

    def test_that_quaternion_can_be_converted_to_axis_and_angle_for_regular(self):
        # Arrange
        angle = 23.0
        axis = V3D(0.0, 1.0, 0.0)
        self._do_test_quaternion(angle, axis)

    def test_that_quaternion_can_be_converted_to_axis_and_angle_for_0_degree(self):
        # Arrange
        angle = 0.0
        axis = V3D(1.0, 0.0, 0.0)
        # There shouldn't be an axis for angle 0
        expected_axis = V3D(0.0, 0.0, 0.0)
        self._do_test_quaternion(angle, axis, expected_axis)

    def test_that_quaternion_can_be_converted_to_axis_and_angle_for_180_degree(self):
        # Arrange
        angle = 180.0
        axis = V3D(0.0, 1.0, 0.0)
        # There shouldn't be an axis for angle 0
        self._do_test_quaternion(angle, axis)

    def test_that_sample_log_is_added(self):
        # Arrange
        workspace = SANSFunctionsTest._create_sample_workspace()
        log_name = "TestName"
        log_value = "TestValue"
        log_type = "String"

        # Act
        add_to_sample_log(workspace, log_name, log_value, log_type)

        # Assert
        run = workspace.run()
        self.assertTrue(run.hasProperty(log_name))
        self.assertTrue(run.getProperty(log_name).value == log_value)

    def test_that_sample_log_raises_for_non_string_type_arguments(self):
        # Arrange
        workspace = SANSFunctionsTest._create_sample_workspace()
        log_name = "TestName"
        log_value = 123
        log_type = "String"

        # Act + Assert
        try:
            add_to_sample_log(workspace, log_name, log_value, log_type)
            did_raise = False
        except TypeError:
            did_raise = True
        self.assertTrue(did_raise)

    def test_that_sample_log_raises_for_wrong_type_selection(self):
        # Arrange
        workspace = SANSFunctionsTest._create_sample_workspace()
        log_name = "TestName"
        log_value = "test"
        log_type = "sdfsdfsdf"

        # Act + Assert
        try:
            add_to_sample_log(workspace, log_name, log_value, log_type)
            did_raise = False
        except ValueError:
            did_raise = True
        self.assertTrue(did_raise)

    def test_that_can_convert_detector_name_to_correct_detector_type_when_valid(self):
        self.assertTrue(convert_bank_name_to_detector_type_isis(" main-detector-bank") is DetectorType.Lab)
        self.assertTrue(convert_bank_name_to_detector_type_isis("rEAR-detector") is DetectorType.Lab)
        self.assertTrue(convert_bank_name_to_detector_type_isis("dEtectorBench  ") is DetectorType.Lab)
        self.assertTrue(convert_bank_name_to_detector_type_isis("front-detector") is DetectorType.Hab)
        self.assertTrue(convert_bank_name_to_detector_type_isis("Hab") is DetectorType.Hab)
        self.assertTrue(convert_bank_name_to_detector_type_isis("front") is DetectorType.Hab)
        self.assertTrue(convert_bank_name_to_detector_type_isis("rear") is DetectorType.Lab)
        self.assertTrue(convert_bank_name_to_detector_type_isis("main") is DetectorType.Lab)

    def test_that_raises_when_detector_name_is_not_known(self):
        self.assertRaises(RuntimeError, convert_bank_name_to_detector_type_isis, "rear-detector-bank")
        self.assertRaises(RuntimeError, convert_bank_name_to_detector_type_isis, "detectorBenc")
        self.assertRaises(RuntimeError, convert_bank_name_to_detector_type_isis, "frontd")

    def test_that_can_parse_event_slices_when_they_are_valid(self):
        slice_string = "1:2:4.5, 4-6.6, 34:79:87, <5, >3.2"
        parsed_ranges = parse_event_slice_setting(slice_string)
        self.assertTrue(parsed_ranges[0] == [1, 3])
        self.assertTrue(parsed_ranges[1] == [3, 4.5])
        self.assertTrue(parsed_ranges[2] == [4, 6.6])
        self.assertTrue(parsed_ranges[3] == [34, 87])
        self.assertTrue(parsed_ranges[4] == [-1, 5])
        self.assertTrue(parsed_ranges[5] == [3.2, -1])

    def test_that_raises_when_min_is_larger_than_max(self):
        self.assertRaises(ValueError, parse_event_slice_setting, "4:2:2.5")
        self.assertRaises(ValueError, parse_event_slice_setting, "10.4-2.3")

    def test_that_raises_when_unknown_search_string_appears(self):
        self.assertRaises(ValueError, parse_event_slice_setting, "4:2.5")
        self.assertRaises(ValueError, parse_event_slice_setting, "4:2-2.5, 1:4")

    def test_that_gets_range_list_for_event_slice_string(self):
        lower, upper = get_ranges_from_event_slice_setting("1:2:4.5, 4-6.6, 34:79:87, <5, >3.2")
        self.assertTrue(lower[0] == 1.)
        self.assertTrue(lower[1] == 3.)
        self.assertTrue(lower[2] == 4.)
        self.assertTrue(lower[3] == 34.)
        self.assertTrue(lower[4] == -1)
        self.assertTrue(lower[5] == 3.2)
        self.assertTrue(upper[0] == 3.)
        self.assertTrue(upper[1] == 4.5)
        self.assertTrue(upper[2] == 6.6)
        self.assertTrue(upper[3] == 87.)
        self.assertTrue(upper[4] == 5.)
        self.assertTrue(upper[5] == -1)

    def test_that_can_parse_a_linear_rebin_string_correctly(self):
        bins = get_bins_for_rebin_setting(2., 10., 3., RangeStepType.Lin)
        self.assertTrue(bins[0] == 2.)
        self.assertTrue(bins[1] == 5.)
        self.assertTrue(bins[2] == 8.)
        self.assertTrue(bins[3] == 10.)

    def test_that_can_parse_a_log_rebin_string_correctly(self):
        bins = get_bins_for_rebin_setting(2., 100., 2., RangeStepType.Log)
        # We expect
        # 1  --> 2.
        # 2  --> 2. + 2.*2 == 6
        # 3  --> 6. + 6.*2 == 18.
        # 4  --> 18. + 18.*2 == 54.
        # 5  --> 54. + 54.*2 > 100. ==> 100.
        self.assertTrue(bins[0] == 2.)
        self.assertTrue(bins[1] == 6.)
        self.assertTrue(bins[2] == 18.)
        self.assertTrue(bins[3] == 54.)
        self.assertTrue(bins[4] == 100.)

    def test_that_gets_range_lists_correctly_from_bin_list(self):
        bin_list = [1, 2, 3, 4, 5]
        lower, upper = get_range_lists_from_bin_list(bin_list)
        self.assertTrue(len(lower) == len(bin_list)-1)
        self.assertTrue(len(upper) == len(bin_list)-1)
        self.assertTrue(lower[0] == bin_list[0])
        self.assertTrue(upper[0] == bin_list[1])

    def test_that_gets_range_lists_correctly_from_rebin_array(self):
        rebin_array = [2, 3, 10]
        lower, upper = get_ranges_for_rebin_array(rebin_array)
        self.assertTrue(len(lower) == 3)
        self.assertTrue(len(upper) == 3)
        self.assertTrue(lower[0] == 2)
        self.assertTrue(upper[0] == 5)
        self.assertTrue(lower[2] == 8)
        self.assertTrue(upper[2] == 10)


if __name__ == '__main__':
    unittest.main()
