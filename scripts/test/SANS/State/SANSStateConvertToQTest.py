import unittest
import mantid
from mantid.kernel import (PropertyManagerProperty, PropertyManager)
from mantid.api import Algorithm
from SANS2.State.SANSStateConvertToQ import (SANSStateConvertToQ, SANSStateConvertToQISIS)
from SANS2.Common.SANSEnumerations import (ReductionDimensionality, RangeStepType)


class SANSStateConvertToQTest(unittest.TestCase):
    def test_that_is_sans_state_data_object(self):
        state = SANSStateConvertToQISIS()
        self.assertTrue(isinstance(state, SANSStateConvertToQ))

    def test_that_can_set_and_get_values(self):
        # Arrange
        state = SANSStateConvertToQISIS()

        # Act + Assert
        state.reduction_dimensionality = ReductionDimensionality.OneDim
        state.use_gravity = False
        state.gravity_extra_length = 12.8
        state.radius_cutoff = 1.
        state.wavelength_cutoff = 34.
        state.q_min = 23.
        state.q_max = 234.
        state.q_step = 34.
        state.q_step_type = RangeStepType.Lin

        try:
            state.validate()
            is_valid = True
        except ValueError:
            is_valid = False
        self.assertTrue(is_valid)

    def test_that_invalid_types_for_parameters_raise_type_error(self):
        # Arrange
        state = SANSStateConvertToQISIS()

        # Act + Assert
        try:
            state.use_gravity = "w234234"
            is_valid = True
        except TypeError:
            is_valid = False
        self.assertFalse(is_valid)

    def test_that_invalid_list_values_raise_value_error(self):
        # Arrange
        state = SANSStateConvertToQISIS()

        # Act + Assert
        try:
            state.q_step = -1.0
            is_valid = True
        except ValueError:
            is_valid = False
        self.assertFalse(is_valid)

    def test_that_q_min_smaller_than_q_max_raises(self):
        # Arrange
        state = SANSStateConvertToQISIS()
        state.q_min = 12.
        state.q_max = 11.
        # Act + Assert
        try:
            state.validate()
            is_valid = True
        except ValueError:
            is_valid = False
        self.assertFalse(is_valid)

    def test_that_incomplete_q_information_raises(self):
        # Arrange
        state = SANSStateConvertToQISIS()
        state.q_min = 12.
        # Act + Assert
        try:
            state.validate()
            is_valid = True
        except ValueError:
            is_valid = False
        self.assertFalse(is_valid)

    def test_that_dict_can_be_generated_from_state_object_and_property_manager_read_in(self):
        class FakeAlgorithm(Algorithm):
            def PyInit(self):
                self.declareProperty(PropertyManagerProperty("Args"))

            def PyExec(self):
                pass

        # Arrange
        state = SANSStateConvertToQISIS()

        state.reduction_dimensionality = ReductionDimensionality.OneDim
        state.use_gravity = False
        state.gravity_extra_length = 12.8
        state.radius_cutoff = 1.
        state.wavelength_cutoff = 34.
        state.q_min = 23.
        state.q_max = 234.
        state.q_step = 34.
        state.q_step_type = RangeStepType.Lin

        # Act
        serialized = state.property_manager
        fake = FakeAlgorithm()
        fake.initialize()
        fake.setProperty("Args", serialized)
        property_manager = fake.getProperty("Args").value

        # Assert
        self.assertTrue(type(serialized) == dict)
        self.assertTrue(type(property_manager) == PropertyManager)
        state_2 = SANSStateConvertToQISIS()
        state_2.property_manager = property_manager

        self.assertTrue(state_2.reduction_dimensionality is ReductionDimensionality.OneDim)
        self.assertFalse(state_2.use_gravity)
        self.assertTrue(state_2.gravity_extra_length == 12.8)
        self.assertTrue(state_2.radius_cutoff == 1.)
        self.assertTrue(state_2.wavelength_cutoff == 34.)
        self.assertTrue(state_2.q_min == 23.)
        self.assertTrue(state_2.q_max == 234.)
        self.assertTrue(state_2.q_step == 34.)
        self.assertTrue(state_2.q_step_type is RangeStepType.Lin)


if __name__ == '__main__':
    unittest.main()
