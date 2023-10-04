class ClassWithDocumentation:
    """
    Lorem ipsum.

    Dolor sit amet.
    """

    def __init__(self, p: int) -> None:
        pass


class ClassWithoutDocumentation:
    pass


def function_with_documentation(p: int) -> None:  # noqa: ARG001
    """
    Lorem ipsum.

    Dolor sit amet.
    """


def function_without_documentation(p: int) -> None:  # noqa: ARG001
    pass
