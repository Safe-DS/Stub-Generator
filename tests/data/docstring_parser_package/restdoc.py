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


class ClassWithVariousParameterTypes:
    """
    Parameters
    ----------
    :param no_type:
    :param optional_type:
    :type optional_type: int, optional
    :param none_type:
    :type none_type: None
    :param int_type:
    :type int_type: int
    :param bool_type:
    :type bool_type: bool
    :param str_type:
    :type str_type: str
    :param float_type:
    :type float_type: float
    :param multiple_types:
    :type multiple_types: int, bool
    :param list_type_1:
    :type list_type_1: list
    :param list_type_2:
    :type list_type_2: list[str]
    :param list_type_3:
    :type list_type_3: list[int, bool]
    :param list_type_4:
    :type list_type_4: list[list[int]]
    :param set_type_1:
    :type set_type_1: set
    :param set_type_2:
    :type set_type_2: set[str]
    :param set_type_3:
    :type set_type_3: set[int, bool]
    :param set_type_4:
    :type set_type_4: set[list[int]]
    :param tuple_type_1:
    :type tuple_type_1: tuple
    :param tuple_type_2:
    :type tuple_type_2: tuple[str]
    :param tuple_type_3:
    :type tuple_type_3: tuple[int, bool]
    :param tuple_type_4:
    :type tuple_type_4: tuple[list[int]]
    """

    def __init__(
        self, no_type, optional_type, none_type, int_type, bool_type, str_type, float_type, multiple_types, list_type_1,
        list_type_2, list_type_3, list_type_4, list_type_5, set_type_1, set_type_2, set_type_3, set_type_4, set_type_5,
        tuple_type_1, tuple_type_2, tuple_type_3, tuple_type_4, tuple_type_5
    ) -> None:
        pass
