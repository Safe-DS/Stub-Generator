class ClassWithDocumentation:
    """
    Lorem ipsum. Code::

        pass

    Dolor sit amet.
    """  # noqa: D400


class ClassWithoutDocumentation:
    pass


def function_with_documentation() -> None:
    """
    Lorem ipsum. Code::

        pass

    Dolor sit amet.
    """  # noqa: D400


def function_without_documentation() -> None:
    pass


class ClassWithParameters:
    """Lorem ipsum.

    Dolor sit amet.

    Args:
        p (int): foo. Defaults to 1.
    """

    def __init__(self) -> None:
        pass


def function_with_parameters() -> None:
    """Lorem ipsum.

    Dolor sit amet.

    Args:
        no_type_no_default: no type and no default.
        type_no_default (int): type but no default.
        with_default (int): foo. Defaults to 2.
        *args (int): foo: *args
        **kwargs (int): foo: **kwargs
    """


def function_with_attributes_and_parameters() -> None:
    """Lorem ipsum.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 2.

    Args:
        q (int): foo. Defaults to 2.

    """  # noqa: D406, D407


class ClassWithAttributes:
    """Lorem ipsum.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 1.
    """  # noqa: D406, D407


def function_with_return_value_and_type() -> None:
    """Lorem ipsum.

    Dolor sit amet.

    Returns:
        int: this will be the return value.
    """  # noqa: D406, D407


def function_with_return_value_no_type() -> None:
    """Lorem ipsum.

    Dolor sit amet.

    Returns:
        int
    """  # noqa: D406, D407


def function_without_return_value() -> None:
    """Lorem ipsum.

    Dolor sit amet.
    """
