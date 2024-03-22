"""
Test module for full docstring tests.

A module for testing the various docstring types.
"""


class ClassWithMultiLineDocumentation:
    """
    ClassWithMultiLineDocumentation.

    Dolor sit amet.
    """


class ClassWithSingleLineDocumentation:
    """ClassWithSingleLineDocumentation."""


class ClassWithoutDocumentation:
    pass


def function_with_multi_line_documentation() -> None:
    """
    function_with_multi_line_documentation.

    Dolor sit amet.
    """


def function_with_single_line_documentation() -> None:
    """function_with_single_line_documentation."""


def function_without_documentation() -> None:
    pass
