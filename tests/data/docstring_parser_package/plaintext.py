"""Test module for docstring tests.

A module for testing the various docstring types.
"""


class ClassWithDocumentation:
    """
    Lorem ipsum.

    Dolor sit amet.
    """

    def __init__(self, p: int) -> None:
        pass


class ClassWithoutDocumentation:
    pass


def function_with_documentation(p: int) -> None:
    """
    Lorem ipsum.

    Dolor sit amet.
    """


def function_without_documentation(p: int) -> None:
    pass
