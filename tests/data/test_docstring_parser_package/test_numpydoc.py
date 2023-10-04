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
    """
    Lorem ipsum.

    Dolor sit amet.

    Parameters
    ----------
    p : int, default=1
        foo
    """

    def __init__(self) -> None:
        pass


def function_with_parameters() -> None:
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


class ClassAndFunctionWithParameters:
    """
    Parameters
    ----------
    x: str
        Lorem ipsum 1.
    z: int, default=5
        Lorem ipsum 3.
    """  # noqa: D205

    def __init__(self, x, y, z) -> None:
        """
        Parameters
        ----------
        y: str
            Lorem ipsum 2.
        z: str
            Lorem ipsum 4.
        """  # noqa: D205


class ClassWithParametersAndAttributes:
    """
    Lorem ipsum.

    Dolor sit amet.

    Parameters
    ----------
    p : int, default=1
        foo

    Attributes
    ----------
    q : int, default=1
        foo
    """

    def __init__(self) -> None:
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

    def __init__(self) -> None:
        pass


def function_with_result_value_and_type() -> None:
    """
    Lorem ipsum.

    Dolor sit amet.

    Returns
    -------
    int
        this will be the return value
    """


def function_without_result_value() -> None:
    """
    Lorem ipsum.

    Dolor sit amet.
    """
