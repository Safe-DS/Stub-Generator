"""Docstring of the some_class.py module"""
import math as mathematics
# noinspection PyUnresolvedReferences
from enum import Enum
# noinspection PyUnresolvedReferences
from enum import Enum as _Enum
from typing import *

# noinspection PyUnresolvedReferences
import mypy
# noinspection PyUnresolvedReferences
from docstring_parser import *

from .another_path.another_module import AnotherClass
from .another_path.another_module import AnotherClass as _AcImportAlias

AcDoubleAlias = _AcImportAlias
ac_alias = AnotherClass


def global_func(param_1: str = "first param", param_2: ac_alias | None = None) -> ac_alias:
    """Docstring 1
    Docstring 2
    """
    return ac_alias()


def _private_global_func() -> _AcImportAlias | AcDoubleAlias | ac_alias:
    return AnotherClass()


class SomeClass(mathematics, AcDoubleAlias):
    """Summary of the description
    Full description
    """
    dict_attr_2: dict[str | int, None | _AcImportAlias]

    type_hint_public: int
    _type_hint_private: int

    no_type_hint_public = 1
    _no_type_hint_private = 1

    object_attr: _AcImportAlias
    object_attr_2: AcDoubleAlias | mathematics

    tuple_attr_1: tuple
    tuple_attr_2: tuple[str | int]
    tuple_attr_3: tuple[str, int]

    list_attr_1: list
    list_attr_2: list[str | _AcImportAlias]
    list_attr_3: list[str, AcDoubleAlias]
    list_attr_4: list[str, _AcImportAlias | int]

    dict_attr_1: dict
    dict_attr_2: dict[str | int, None | _AcImportAlias]
    dict_attr_3: dict[str, int]

    bool_attr: bool
    none_attr: None
    flaot_attr: float
    int_or_bool_attr: int | bool
    str_attr_with_none_value: str = None

    mulit_attr_1, _mulit_attr_2_private = (123456, "I am a String")
    mulit_attr_3 = _mulit_attr_4_private = ["I am some", "kind of list"]

    no_hint = 123  # is_new_def == True and node.is_inferred == True
    yes_hint: float = "str"  # is_new_def == True and node.is_inferred == False
    override_in_init: int  # is_new_def == True and node.is_inferred == False

    def __init__(self, init_param_1):
        """Summary of the init description
        Full init description
        """
        self.init_attr: bool
        self._init_attr_private: float = "I'm a string"
        self.override_in_init: str
        no_class_attr: bool

    def _some_function(self, param_1: bool, param_2: ac_alias) -> ac_alias:
        """Function Docstring
        param_1: bool
        """
        self.attr_2 = param_1
        return ac_alias()

    @staticmethod
    def static_function(param_1: bool, param_2: int | bool = 123456) -> tuple[bool, int]:
        """Function Docstring"""
        return param_1, param_2

    def test_position(self, param1, /, param2: bool, param3=1, *, param4=AcDoubleAlias(), param5: int = 1) -> Any:
        """Function Docstring"""
        self.something = param2 + param3
        return param1 + self.something - param5

    @staticmethod
    def multiple_results(param_1: int) -> Any | tuple[int, str]:
        """Function Docstring"""
        if param_1 == 1:
            return 99
        elif param_1 == 2:
            return False
        elif param_1 == 3:
            return None
        elif param_1 == 4:
            return 2.324
        elif param_1 == 5:
            return "some string"
        elif param_1 == 6:
            return _AcImportAlias()
        elif param_1 == 7:
            return [1, 2, 3, 4, 5]
        elif param_1 == 8:
            return {1: 1, 2: 2}
        elif param_1 == 9:
            return [x for x in [1, 2, 3]]
        elif param_1 == 10:
            return {1, 2, 3}
        elif param_1 == 11:
            return _AcImportAlias
        elif param_1 == 12:
            return True, _AcImportAlias(), 33
        return

    class NestedClass(_AcImportAlias, mypy):
        def nested_class_function(self, param_1: int) -> set[bool | None]:
            pass


class _PrivateClass:
    public_attr_in_private_class = 0

    def __init__(self):
        self.public_init_attr_in_private_class: int = 0

    def public_func_in_private_class(self):
        pass

    class NestedPrivateClass:
        nested_class_attr = 0

        @staticmethod
        def static_nested_private_class_function():
            pass

        class NestedNestedPrivateClass:
            pass


class TestEnum(Enum):
    """Enum Docstring
    Full Docstring Description
    """
    ONE = "first"
    TWO = (2, 2)
    THREE = 3
    FOUR = FIVE = "forth and fifth"
    SIX, SEVEN = ("sixth", 7)
    EIGHT, NINE = "89"
    TEN = _AcImportAlias()


class EmptyEnum(_Enum):
    """Nothing's here"""


class AnotherTestEnum(_Enum, Enum):
    ELEVEN = 11
