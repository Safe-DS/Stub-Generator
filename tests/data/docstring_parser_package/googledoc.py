"""Test module for Google docstring tests.

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
    """ClassWithParameters.

    Dolor sit amet.

    Args:
        p (int): foo. Defaults to 1.
    """

    def __init__(self, p) -> None:
        pass


def function_with_parameters(no_type_no_default, type_no_default, with_default, *args, **kwargs) -> None:
    """function_with_parameters.

    Dolor sit amet.

    Args:
        no_type_no_default: no type and no default.
        type_no_default (int): type but no default.
        with_default (int): foo. Defaults to 2.
        *args (int): foo: *args
        **kwargs (int): foo: **kwargs
    """


def function_with_attributes_and_parameters(q) -> None:
    """function_with_attributes_and_parameters.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 2.

    Args:
        q (int): foo. Defaults to 2.
    """


class ClassWithAttributes:
    """ClassWithAttributes.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 1.
        q (int): foo. Defaults to 1.
    """
    p: int
    q = 1


def function_with_return_value_and_type() -> bool:
    """function_with_return_value_and_type.

    Dolor sit amet.

    Returns:
        bool: this will be the return value.
    """


def function_with_return_value_no_type() -> None:
    """function_with_return_value_no_type.

    Dolor sit amet.

    Returns:
        None
    """


def function_without_return_value():
    """function_without_return_value.

    Dolor sit amet.
    """


class ClassWithMethod:
    def method_with_docstring(self, a) -> bool:
        """
        method_with_docstring.

        Dolor sit amet.

        Args:
            a (int): foo

        Returns:
            bool: this will be the return value.
        """

    @property
    def property_method_with_docstring(self) -> bool:
        """
        property_method_with_docstring.

        Dolor sit amet.

        Returns:
            bool: this will be the return value.
        """


class EnumDocstring(Enum):
    """
    EnumDocstring.

    Dolor sit amet.
    """
