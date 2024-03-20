"""
Test module for docstring tests.

A module for testing the various docstring types.
"""
from typing import Any, Optional
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
    """
    Lorem ipsum.

    Dolor sit amet.

    Parameters
    ----------
    p : int, default=1
        foo
    """

    def __init__(self, p) -> None:
        pass


def function_with_parameters(
    no_type_no_default, type_no_default, optional_unknown_default, with_default_syntax_1, with_default_syntax_2,
    with_default_syntax_3, grouped_parameter_1, grouped_parameter_2, *args, **kwargs
) -> None:
    """
    Lorem ipsum.

    Dolor sit amet.

    Parameters
    ----------
    no_type_no_default
        foo: no_type_no_default. Code::

            pass
    type_no_default : int
        foo: type_no_default
    optional_unknown_default : int, optional
        foo: optional_unknown_default
    with_default_syntax_1 : int, default 1
        foo: with_default_syntax_1
    with_default_syntax_2 : int, default: 2
        foo: with_default_syntax_2
    with_default_syntax_3 : int, default=3
        foo: with_default_syntax_3
    grouped_parameter_1, grouped_parameter_2 : int, default=4
        foo: grouped_parameter_1 and grouped_parameter_2
    *args : int
        foo: *args
    **kwargs : int
        foo: **kwargs
    """


class ClassAndConstructorWithParameters:
    """
    Parameters
    ----------
    x : str
        Lorem ipsum 1.
    z : int, default=5
        Lorem ipsum 3.
    """

    def __init__(self, x, y, z) -> None:
        """
        Parameters
        ----------
        y : str
            Lorem ipsum 2.
        z : str
            Lorem ipsum 4.
        """


class ClassWithParametersAndAttributes:
    """
    Lorem ipsum.

    Dolor sit amet.

    Parameters
    ----------
    x : int, default=1
        foo

    Attributes
    ----------
    p : int, default=1
        foo
    q : int, default=1
        foo
    """
    p: int
    q = 1

    def __init__(self, x) -> None:
        pass


class ClassWithAttributes:
    """
    Lorem ipsum.

    Dolor sit amet.

    Attributes
    ----------
    no_type_no_default
        foo: no_type_no_default. Code::

            pass
    type_no_default : int
        foo: type_no_default
    optional_unknown_default : int, optional
        foo: optional_unknown_default
    with_default_syntax_1 : int, default 1
        foo: with_default_syntax_1
    with_default_syntax_2 : int, default: 2
        foo: with_default_syntax_2
    with_default_syntax_3 : int, default=3
        foo: with_default_syntax_3
    grouped_attribute_1, grouped_attribute_2 : int, default=4
        foo: grouped_attribute_1 and grouped_attribute_2
    """
    no_type_no_default: Any
    type_no_default: int
    optional_unknown_default: Optional[int]
    with_default_syntax_1 = 1
    with_default_syntax_2: int
    with_default_syntax_3: int = 3
    grouped_attribute_1, grouped_attribute_2 = 4, 4

    def __init__(self) -> None:
        pass


def function_with_result_value_and_type() -> bool:
    """
    Lorem ipsum.

    Dolor sit amet.

    Returns
    -------
    bool
        this will be the return value
    """


def function_with_named_result() -> bool:
    """
    Lorem ipsum.

    Dolor sit amet.

    Returns
    -------
    named_result : bool
        this will be the return value
    """


def function_without_result_value():
    """
    Lorem ipsum.

    Dolor sit amet.
    """


class ClassWithMethod:
    def method_with_docstring(self, a) -> bool:
        """
        Lorem ipsum.

        Dolor sit amet.

        Parameters
        ----------
        a: str

        Returns
        -------
        named_result : bool
            this will be the return value
        """

    @property
    def property_method_with_docstring(self) -> bool:
        """
        Lorem ipsum.

        Dolor sit amet.

        Returns
        -------
        named_result : bool
            this will be the return value
        """


class EnumDocstring(Enum):
    """
    Lorem ipsum.

    Dolor sit amet.
    """
