"""Test module for docstring tests.

A module for testing the various docstring types.
"""
from enum import Enum


class ClassWithDocumentation:
    """
    Lorem ipsum. Code::

        pass

    Dolor sit amet.
    """


class ClassWithoutDocumentation:
    pass


def function_with_documentation() -> None:
    """
    Lorem ipsum. Code::

        pass

    Dolor sit amet.
    """


def function_without_documentation() -> None:
    pass


class ClassWithParameters:
    """Lorem ipsum.

    Dolor sit amet.

    Args:
        p (int): foo. Defaults to 1.
    """

    def __init__(self, p) -> None:
        pass


def function_with_parameters(no_type_no_default, type_no_default, with_default, *args, **kwargs) -> None:
    """Lorem ipsum.

    Dolor sit amet.

    Args:
        no_type_no_default: no type and no default.
        type_no_default (int): type but no default.
        with_default (int): foo. Defaults to 2.
        *args (int): foo: *args
        **kwargs (int): foo: **kwargs
    """


def function_with_attributes_and_parameters(q) -> None:
    """Lorem ipsum.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 2.

    Args:
        q (int): foo. Defaults to 2.
    """


class ClassWithAttributes:
    """Lorem ipsum.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 1.
        q (int): foo. Defaults to 1.
    """
    p: int
    q = 1


def function_with_return_value_and_type() -> bool:
    """Lorem ipsum.

    Dolor sit amet.

    Returns:
        bool: this will be the return value.
    """


def function_with_return_value_no_type() -> None:
    """Lorem ipsum.

    Dolor sit amet.

    Returns:
        None
    """


def function_without_return_value():
    """Lorem ipsum.

    Dolor sit amet.
    """


class ClassWithMethod:
    def method_with_docstring(self, a) -> bool:
        """
        Lorem ipsum.

        Dolor sit amet.

        Args:
            a (int): foo

        Returns:
            bool: this will be the return value.
        """

    @property
    def property_method_with_docstring(self):
        """
        Lorem ipsum.

        Dolor sit amet.

        Returns:
            bool: this will be the return value.
        """


class EnumDocstring(Enum):
    """
    Lorem ipsum.

    Dolor sit amet.
    """
