"""
Test module for Numpy docstring tests.

A module for testing the various docstring types.
"""
from typing import Any, Optional, Callable, Mapping
from enum import Enum
from tests.data.various_modules_package.another_path.another_module import AnotherClass
from tests.data.various_modules_package.type_var_module import SequenceTypeVar, SequenceTypeVar2


class ClassWithDocumentation:
    """
    ClassWithDocumentation. Code::

        pass

    Dolor sit amet.
    """


class ClassWithoutDocumentation:
    pass


def function_with_documentation() -> None:
    """
    function_with_documentation. Code::

        pass

    Dolor sit amet.
    """


def function_without_documentation() -> None:
    pass


class ClassWithParameters:
    """
    ClassWithParameters.

    Dolor sit amet.

    Parameters
    ----------
    p : int, default=1
        foo
    grouped_parameter_1, grouped_parameter_2 : int, default=4
        foo: grouped_parameter_1 and grouped_parameter_2
    """

    def __init__(self, p, grouped_parameter_1, grouped_parameter_2) -> None:
        pass


def function_with_parameters(
    no_type_no_default, type_no_default, optional_unknown_default, with_default_syntax_1, with_default_syntax_2,
    with_default_syntax_3, grouped_parameter_1, grouped_parameter_2, *args, **kwargs
) -> None:
    """
    function_with_parameters.

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
    **kwargs : dict[str, int]
        foo: **kwargs
    """


class ClassAndConstructorWithParameters:
    """
    ClassAndConstructorWithParameters

    Dolor sit amet.

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


class ClassAndConstructorWithAttributes:
    """
    ClassAndConstructorWithParameters

    Dolor sit amet.

    Attributes
    ----------
    x : str
        Lorem ipsum 1.
    z : int, default=5
        Lorem ipsum 3.
    """
    x: str
    z: int
    y: str

    def __init__(self) -> None:
        """
        Attributes
        ----------
        y : str
            Lorem ipsum 2.
        z : str
            Lorem ipsum 4.
        """
        self.y: str
        self.z: str


class ClassWithParametersAndAttributes:
    """
    ClassWithParametersAndAttributes.

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
    ClassWithAttributes.

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
    no_type_no_default = ""
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
    function_with_result_value_and_type.

    Dolor sit amet.

    Returns
    -------
    bool
        this will be the return value
    """


def function_with_named_result() -> bool:
    """
    function_with_named_result.

    Dolor sit amet.

    Returns
    -------
    named_result : bool
        this will be the return value
    """


def function_with_multiple_results() -> (int, bool):
    """
    function_with_named_result.

    Dolor sit amet.

    Returns
    -------
    first_result : int
        first result
    second_result : bool
        second result
    """
    if ClassWithAttributes:
        return 1
    return True


def function_without_result_value():
    """
    function_without_result_value.

    Dolor sit amet.
    """


class ClassWithMethod:
    def method_with_docstring(self, a) -> bool:
        """
        method_with_docstring.

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
        property_method_with_docstring.

        Dolor sit amet.

        Returns
        -------
        named_result : bool
            this will be the return value
        """


class EnumDocstring(Enum):
    """
    EnumDocstring.

    Dolor sit amet.
    """


class ClassWithVariousParameterTypes:
    """
    Parameters
    ----------
    no_type
    optional_type : int, optional
    none_type : None
    int_type : int
    bool_type : bool
    str_type : str
    float_type : float
    multiple_types : int, bool
    list_type_1 : list
    list_type_2 : list[str]
    list_type_3 : list[int, bool]
    list_type_4 : list[list[int]]
    set_type_1 : set
    set_type_2 : set[str]
    set_type_3 : set[int, bool]
    set_type_4 : set[list[int]]
    tuple_type_1 : tuple
    tuple_type_2 : tuple[str]
    tuple_type_3 : tuple[int, bool]
    tuple_type_4 : tuple[list[int]]
    any_type : Any
    optional_type_2 : Optional[int]
    class_type : ClassWithAttributes
    imported_type : AnotherClass
    """

    def __init__(
        self, no_type, optional_type, none_type, int_type, bool_type, str_type, float_type, multiple_types, list_type_1,
        list_type_2, list_type_3, list_type_4, list_type_5, set_type_1, set_type_2, set_type_3, set_type_4, set_type_5,
        tuple_type_1, tuple_type_2, tuple_type_3, tuple_type_4, any_type: Any,
        optional_type_2: Optional[int], class_type, imported_type
    ) -> None:
        pass


class ClassWithVariousAttributeTypes:
    """
    Attributes
    ----------
    no_type
    optional_type : int, optional
    none_type : None
    int_type : int
    bool_type : bool
    str_type : str
    float_type : float
    multiple_types : int, bool
    list_type_1 : list
    list_type_2 : list[str]
    list_type_3 : list[int, bool]
    list_type_4 : list[list[int]]
    set_type_1 : set
    set_type_2 : set[str]
    set_type_3 : set[int, bool]
    set_type_4 : set[list[int]]
    tuple_type_1 : tuple
    tuple_type_2 : tuple[str]
    tuple_type_3 : tuple[int, bool]
    tuple_type_4 : tuple[list[int]]
    any_type : Any
    optional_type_2 : Optional[int]
    class_type : ClassWithAttributes
    imported_type : AnotherClass
    callable_type : Callable[[int], str]
    mapping_type : Mapping[int, str]
    bool_op_type : int or str or bool
    list_type_5 : [int]
  """
    no_type = ""
    optional_type = ""
    none_type = ""
    int_type = ""
    bool_type = ""
    str_type = ""
    float_type = ""
    multiple_types = ""
    list_type_1 = ""
    list_type_2 = ""
    list_type_3 = ""
    list_type_4 = ""
    set_type_1 = ""
    set_type_2 = ""
    set_type_3 = ""
    set_type_4 = ""
    tuple_type_1 = ""
    tuple_type_2 = ""
    tuple_type_3 = ""
    tuple_type_4 = ""
    any_type: Any
    optional_type_2: Optional[int]
    class_type: ClassWithAttributes
    imported_type: AnotherClass
    callable_type: Callable[[int], str]
    mapping_type: Mapping[int, str]
    bool_op_type: int | str | bool
    list_type_5: list[int]


def uninferable_return_doc():
    """
    uninferable_return_doc.

    Dolor sit amet.

    Returns
    -------
    'True' is something happens, else 'False'.
    """


def infer_types():
    """
    property_method_with_docstring.

    Dolor sit amet.

    Returns
    -------
    first_result : bool
        This is the first result
    second_result : str
        This is the second result
    """
    return True, "Another value"


def infer_types2(a, b):
    """
    property_method_with_docstring.

    Dolor sit amet.

    Parameters
    ----------
    a : str
        The first parameter
    b : bool
        The second parameter

    Returns
    -------
    func_result : str | bool | int
        This is the result
    """
    if b:
        return "A value"
    if a:
        return int
    return True


def infer_types3(a, b):
    """
    property_method_with_docstring.

    Dolor sit amet.

    Parameters
    ----------
    a : str
        The first parameter
    b : bool
        The second parameter

    Returns
    -------
    func_result : str
        This is the result
    func_result_2 : int
        This is the second result
    """
    if b:
        return "A value"
    if a:
        return int
    return True


class NumpyClassWithExamples:
    """
    NumpyClassWithExamples.

    Dolor sit amet.

    Examples
    --------
    >>> from tests.data.docstring_parser_package.numpydoc import NumpyClassWithExamples
    This text should be ignored
    >>> class_ = (
    ...     NumpyClassWithExamples
    ... )
    This text should be ignored, too.
    """

    def numpy_func_with_examples(self):
        """
        Examples
        --------
        >>> from tests.data.docstring_parser_package.numpydoc import NumpyClassWithExamples
        >>> func = (
        ...     NumpyClassWithExamples.numpy_func_with_examples
        ... )
        >>> func()
        This text should be ignored.
        """


def numpy_sequence_types(a: SequenceTypeVar[list]) -> SequenceTypeVar2[int]:
    """
    numpy_sequence_types.

    Dolor sit amet.

    Parameters
    ----------
    a: SequenceTypeVar[list]

    Returns
    -------
    named_result : SequenceTypeVar2[int]
        this will be the return value
    """
    pass


def numpy_named_result_without_type() -> str:
    """
    numpy_named_result_without_type

    Returns
    -------
    named_result :
        this will be the return value
    """
    return "result"


def numpy_named_result_without_type_inferred():
    """
    numpy_named_result_without_type_inferred

    Returns
    -------
    named_result :
        this will be the return value
    """
    return "result"


class ClassWithExample:
    """
    Examples
    --------
    >>> print(1+1)
    2

    >>> x = 2 - 1
    >>> print(x)
    1
    """


def function_with_example() -> None:
    """
    Examples
    --------
    >>> print(1+1)
    2

    >>> x = 2 - 1
    >>> print(x)
    1
    """


def numpy_named_result_with_more_hints_than_docstring_types() -> tuple[int, str]:
    """
    numpy_named_result_without_type_inferred

    Returns
    -------
    named_result : int
        this will be the return value
    """
    ...
