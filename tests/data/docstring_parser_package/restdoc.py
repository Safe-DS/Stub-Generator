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

    :param p: foo defaults to 1
    :type p: int
    """

    def __init__(self) -> None:
        pass


def function_with_parameters() -> None:
    """
    Lorem ipsum.

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


def function_with_return_value_and_type() -> None:
    """
    Lorem ipsum.

    Dolor sit amet.

    :return: return value
    :rtype: bool
    """


def function_with_return_value_no_type() -> None:
    """
    Lorem ipsum.

    Dolor sit amet.

    :return: return value
    """


def function_without_return_value() -> None:
    """
    Lorem ipsum.

    Dolor sit amet.
    """
