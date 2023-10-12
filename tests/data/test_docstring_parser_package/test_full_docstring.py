class ClassWithMultiLineDocumentation:
    """
    Lorem ipsum.

    Dolor sit amet.
    """


class ClassWithSingleLineDocumentation:
    """Lorem ipsum."""


class ClassWithoutDocumentation:
    pass


def function_with_multi_line_documentation() -> None:
    """
    Lorem ipsum.

    Dolor sit amet.
    """


def function_with_single_line_documentation() -> None:
    """Lorem ipsum."""


def function_without_documentation() -> None:
    pass
