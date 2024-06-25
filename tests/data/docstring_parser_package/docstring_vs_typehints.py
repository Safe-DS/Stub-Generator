class DocVsHintsClassWithParameter:
    """
    ClassWithParametersAndAttributes.

    Dolor sit amet.

    Parameters
    ----------
    x : int, default=1
        foo
    """

    def __init__(self, x, y: str = "Some String") -> None:
        pass


def doc_vs_hints_function_with_parameters_and_return(x, y: str = "Some String"):
    """
    function_with_result_value_and_type.

    Dolor sit amet.

    Parameters
    ----------
    x : int, default=1

    Returns
    -------
    named_result : bool
        this will be the return value
    """


class DocVsHintsClassWithContrastingParameter:
    """
    ClassWithParametersAndAttributes.

    Dolor sit amet.

    Parameters
    ----------
    x : int, default=1
        foo
    """

    def __init__(self, x: str = "Some String") -> None:
        pass


def doc_vs_hints_function_with_contrasting_parameter_and_return(x: str = "Some String") -> int:
    """
    function_with_result_value_and_type.

    Dolor sit amet.

    Parameters
    ----------
    x : int, default=1

    Returns
    -------
    named_result : bool
        this will be the return value
    """


def doc_vs_hints_function_with_multiple_contrasting_return() -> tuple[int, str]:
    """
    function_with_result_value_and_type.

    Dolor sit amet.

    Returns
    -------
    first_result : float
        first float value instead of int
    second_result : bool
        second bool value instead of str
    """
