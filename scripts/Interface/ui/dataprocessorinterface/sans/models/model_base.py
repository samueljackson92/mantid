#pylint: disable=too-few-public-methods, invalid-name

""" Fundamental classes and Descriptors for the State mechanism."""
from __future__ import (absolute_import, division, print_function)
import copy
from functools import (partial)


# ---------------------------------------------------------------
# Validator functions
# ---------------------------------------------------------------
def is_not_none(value):
    return value is not None


def is_positive(value):
    return value >= 0


def is_positive_or_none(value):
    return value is None or value >= 0


def all_list_elements_are_of_specific_type_and_not_empty(value, comparison_type,
                                                         additional_comparison=lambda x: True, type_check=isinstance):
    """
    Ensures that all elements of a list are of a specific type and that the list is not empty

    @param value: the list to check
    @param comparison_type: the expected type of the elements of the list.
    @param additional_comparison: additional comparison lambda.
    @param type_check: the method which performs type checking.
    @return: True if the list is not empty and all types are as expected, else False.
    """
    is_of_type = True
    for element in value:
        # Perform type check
        if not type_check(element, comparison_type):
            is_of_type = False
        # Perform additional check
        if not additional_comparison(element):
            is_of_type = False

    if not value:
        is_of_type = False
    return is_of_type


def all_list_elements_are_of_instance_type_and_not_empty(value, comparison_type, additional_comparison=lambda x: True):
    """
    Ensures that all elements of a list are of a certain INSTANCE type and that the list is not empty.
    """
    return all_list_elements_are_of_specific_type_and_not_empty(value=value, comparison_type=comparison_type,
                                                                additional_comparison=additional_comparison,
                                                                type_check=isinstance)


def all_list_elements_are_of_class_type_and_not_empty(value, comparison_type, additional_comparison=lambda x: True):
    """
    Ensures that all elements of a list are of a certain INSTANCE type and that the list is not empty.
    """
    return all_list_elements_are_of_specific_type_and_not_empty(value=value, comparison_type=comparison_type,
                                                                additional_comparison=additional_comparison,
                                                                type_check=issubclass)


def all_list_elements_are_float_and_not_empty(value):
    typed_comparison = partial(all_list_elements_are_of_instance_type_and_not_empty, comparison_type=float)
    return typed_comparison(value)


def all_list_elements_are_string_and_not_empty(value):
    typed_comparison = partial(all_list_elements_are_of_instance_type_and_not_empty, comparison_type=str)
    return typed_comparison(value)


def all_list_elements_are_int_and_not_empty(value):
    typed_comparison = partial(all_list_elements_are_of_instance_type_and_not_empty, comparison_type=int)
    return typed_comparison(value)


def all_list_elements_are_int_and_positive_and_not_empty(value):
    typed_comparison = partial(all_list_elements_are_of_instance_type_and_not_empty, comparison_type=int,
                               additional_comparison=lambda x: x >= 0)
    return typed_comparison(value)


def validator_sub_state(sub_state):
    is_valid = True
    try:
        sub_state.validate()
    except ValueError:
        is_valid = False
    return is_valid


# -------------------------------------------------------
# Parameters
# -------------------------------------------------------
class ModelParameter(object):
    """
    The ModelParameter descriptor allows the user to store/handle a type-checked value with an additional
    validator option, e.g. one can restrict the held parameter to be only a positive value.
    """
    __counter = 0

    def __init__(self, parameter_type, validator=lambda x: True):
        cls = self.__class__
        prefix = cls.__name__
        # pylint: disable=protected-access
        index = cls.__counter
        cls.__counter += 1
        # Name which is used to store value in the instance. This will be unique and not accessible via the standard
        # attribute access, since the developer/user cannot apply the hash symbol in their code (it is valid though
        # when writing into the __dict__). Note that the name which we generate here will be altered (via a
        # class decorator) in the classes which actually use the ModelParameter descriptor, to make it more readable.
        self.name = '_{0}#{1}'.format(prefix, index)
        self.parameter_type = parameter_type
        self.value = None
        self.validator = validator

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            if hasattr(instance, self.name):
                return getattr(instance, self.name)
            else:
                return None

    def __set__(self, instance, value):
        # Convert value to the desired type
        try:
            copied_value = copy.deepcopy(value)
            converted_value = self.parameter_type(copied_value)
            self._type_check(converted_value)
            setattr(instance, self.name, converted_value)
        except:
            raise ValueError("Trying to set {0} with an invalid value of {1}".format(self.name, str(value)))
        # Perform a type check
        self._type_check(value)
        if self.validator(value):
            # The descriptor should be holding onto its own data and return a deepcopy of the data.
            copied_value = copy.deepcopy(value)
            setattr(instance, self.name, copied_value)
        else:
            raise ValueError("Trying to set {0} with an invalid value of {1}".format(self.name, str(value)))

    def __delete__(self):
        raise AttributeError("Cannot delete the attribute {0}".format(self.name))

    def _type_check(self, value):
        if not isinstance(value, self.parameter_type):
            raise TypeError("Trying to set {0} which expects a value of type {1}."
                            " Got a value of {2} which is of type: {3}".format(self.name, str(self.parameter_type),
                                                                               str(value), str(type(value))))


# ---------------------------------------------------
# Various standard cases of the ModelParameter
# ---------------------------------------------------
class StringParameter(ModelParameter):
    def __init__(self):
        super(StringParameter, self).__init__(str, is_not_none)


class BoolParameter(ModelParameter):
    def __init__(self):
        super(BoolParameter, self).__init__(bool, is_not_none)


class FloatParameter(ModelParameter):
    def __init__(self):
        super(FloatParameter, self).__init__(float, is_not_none)


class PositiveFloatParameter(ModelParameter):
    def __init__(self):
        super(PositiveFloatParameter, self).__init__(float, is_positive)


class PositiveIntegerParameter(ModelParameter):
    def __init__(self):
        super(PositiveIntegerParameter, self).__init__(int, is_positive)
