"""Test module for Google docstring tests.

A module for testing the various docstring types.
"""
from enum import Enum
from typing import Optional, Any, Callable, Mapping
from tests.data.various_modules_package.another_path.another_module import AnotherClass


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
    """ClassWithParameters.

    Dolor sit amet.

    Args:
        p (int): foo. Defaults to 1.
    """

    def __init__(self, p) -> None:
        pass


def function_with_parameters(no_type_no_default, optional_type, type_no_default, with_default, *args, **kwargs) -> None:
    """function_with_parameters.

    Dolor sit amet.

    Args:
        no_type_no_default: no type and no default.
        optional_type (int, optional): optional type.
        type_no_default (int): type but no default.
        with_default (int): foo. Defaults to 2.
        *args (int): foo: *args
        **kwargs (dict[str, int]): foo: **kwargs
    """


def function_with_attributes_and_parameters(q) -> None:
    """function_with_attributes_and_parameters.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 2.

    Args:
        q (int): foo. Defaults to 2.
    """
    p: int = 2


class ClassWithAttributes:
    """ClassWithAttributes.

    Dolor sit amet.

    Attributes:
        p (int): foo. Defaults to 1.
        q (int): foo. Defaults to 1.
        optional_unknown_default (int, optional): foo.
    """
    p: int
    q = 1
    optional_unknown_default = None


def function_with_return_value_and_type() -> bool:
    """function_with_return_value_and_type.

    Dolor sit amet.

    Returns:
        bool: this will be the return value.
    """


def function_with_return_value_no_type() -> None:
    """function_with_return_value_no_type.

    Dolor sit amet.

    Returns:
        None
    """


def function_with_multiple_results() -> (int, bool):
    """
    function_with_named_result.

    Dolor sit amet.

    Returns:
        int: first result
        bool: second result
    """


def function_without_return_value():
    """function_without_return_value.

    Dolor sit amet.
    """


class ClassWithMethod:
    def method_with_docstring(self, a) -> bool:
        """
        method_with_docstring.

        Dolor sit amet.

        Args:
            a (int): foo

        Returns:
            bool: this will be the return value.
        """

    @property
    def property_method_with_docstring(self) -> bool:
        """
        property_method_with_docstring.

        Dolor sit amet.

        Returns:
            bool: this will be the return value.
        """


class EnumDocstring(Enum):
    """
    EnumDocstring.

    Dolor sit amet.
    """


class ClassWithVariousParameterTypes:
    """
    Args:
        no_type:
        optional_type (int, optional):
        none_type (None):
        int_type (int):
        bool_type (bool):
        str_type (str):
        float_type (float):
        byte_type (bytes):
        multiple_types (int, bool):
        list_type_1 (list):
        list_type_2 (list[str]):
        list_type_3 (list[int, bool]):
        list_type_4 (list[list[int]]):
        set_type_1 (set):
        set_type_2 (set[str]):
        set_type_3 (set[int, bool]):
        set_type_4 (set[list[int]]):
        tuple_type_1 (tuple):
        tuple_type_2 (tuple[str]):
        tuple_type_3 (tuple[int, bool]):
        tuple_type_4 (tuple[list[int]]):
        any_type (Any):
        optional_type_2 (Optional[int]):
        class_type (ClassWithAttributes):
        imported_type (AnotherClass):
   """

    def __init__(
        self, no_type, optional_type, none_type, int_type, bool_type, str_type, float_type, byte_type, multiple_types,
        list_type_1, list_type_2, list_type_3, list_type_4, list_type_5, set_type_1, set_type_2, set_type_3, set_type_4,
        set_type_5, tuple_type_1, tuple_type_2, tuple_type_3, tuple_type_4, any_type: Any,
        optional_type_2: Optional[int], class_type, imported_type
    ) -> None:
        pass


class ClassWithVariousAttributeTypes:
    """
    Attributes:
        no_type:
        optional_type (int, optional):
        none_type (None):
        int_type (int):
        bool_type (bool):
        str_type (str):
        float_type (float):
        multiple_types (int, bool):
        list_type_1 (list):
        list_type_2 (list[str]):
        list_type_3 (list[int, bool]):
        list_type_4 (list[list[int]]):
        set_type_1 (set):
        set_type_2 (set[str]):
        set_type_3 (set[int, bool]):
        set_type_4 (set[list[int]]):
        tuple_type_1 (tuple):
        tuple_type_2 (tuple[str]):
        tuple_type_3 (tuple[int, bool]):
        tuple_type_4 (tuple[list[int]]):
        any_type (Any):
        optional_type_2 (Optional[int]):
        class_type (ClassWithAttributes):
        imported_type (AnotherClass):
        callable_type (Callable[[int], str]):
        mapping_type (Mapping[int, str]):
        bool_op_type (int or str or bool):
        list_type_5 ([int]):
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

    Returns:
        'True' is something happens, else 'False'.
    """


def google_multiple_text_parts(a, b):
    """
    Nihil possimus iusto autem aut. Laboriosam ut ipsum veritatis.
    Excepturi voluptatem beatae nam voluptas.

    Est aliquid numquam at error quis laborum et perferendis.

    Args:
        a: First arg
        b: Second arg
    Throws:
        RuntimeError
    Returns:
        Nothing

    Illum amet velit et qui.
    """
    ...


def infer_types():
    """
    property_method_with_docstring.

    Dolor sit amet.

    Returns:
        str: This is the first result
        int: This is the second result
    """
    return "Some value", 2


def infer_types2(a, b):
    """
    property_method_with_docstring.

    Dolor sit amet.

    Args:
        a (int): The first parameter
        b (bool): The second parameter

    Returns:
        str | bool: This is the result
    """
    if a or b:
        return "A value"
    return True
