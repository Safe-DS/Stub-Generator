"""
Test module for ReST docstring tests.

A module for testing the various docstring types.
"""
from enum import Enum


class ClassWithDocumentation:
    """
    ClassWithDocumentation. Code::

        pass

    Dolor sit amet.
    """


class ClassWithoutDocumentation:
    pass


def function_with_documentation() -> None:
    """
    function_with_documentation. Code::

        pass

    Dolor sit amet.
    """


def function_without_documentation() -> None:
    pass


class ClassWithParameters:
    """
    ClassWithParameters.

    Dolor sit amet.

    :param p: foo defaults to 1
    :type p: int
    """

    def __init__(self, p) -> None:
        pass


def function_with_parameters(no_type_no_default, type_no_default, with_default, *args, **kwargs) -> None:
    """
    function_with_parameters.

    Dolor sit amet.

    :param no_type_no_default: no type and no default
    :param type_no_default: type but no default
    :type type_no_default: int
    :param with_default: foo that defaults to 2
    :type with_default: int
    :param *args: foo: *args
    :type *args: int
    :param **kwargs: foo: **kwargs
    :type **kwargs: int
    """


def function_with_return_value_and_type() -> bool:
    """
    function_with_return_value_and_type.

    Dolor sit amet.

    :return: return value
    :rtype: bool
    """


def function_with_return_value_no_type() -> None:
    """
    function_with_return_value_no_type.

    Dolor sit amet.

    :return: return value
    """


def function_without_return_value():
    """
    function_without_return_value.

    Dolor sit amet.
    """


class ClassWithMethod:
    def method_with_docstring(self, a) -> bool:
        """
        method_with_docstring.

        Dolor sit amet.

        :param a: type but no default
        :type a: int

        :return: return value
        :rtype: bool
        """

    @property
    def property_method_with_docstring(self) -> bool:
        """
        property_method_with_docstring.

        Dolor sit amet.

        :return: return value
        :rtype: bool
        """


class EnumDocstring(Enum):
    """
    EnumDocstring.

    Dolor sit amet.
    """
