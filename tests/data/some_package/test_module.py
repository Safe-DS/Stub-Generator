"""Docstring of the some_class.py module"""
import math as mathematics
from enum import Enum
from typing import *

# noinspection PyUnresolvedReferences
import mypy
# noinspection PyUnresolvedReferences
from docstring_parser import *

from .another_path.another_module import AnotherClass
from .another_path.another_module import AnotherClass as k

s = k
a = AnotherClass


def global_func(param_1: str = "first param", param_2: a | None = None) -> a:
    """method docstring"""
    return a()


class SomeClass(mathematics, s):
    """Class docstring"""
    no_type_hint_public = 1
    _no_type_hint_private = 1

    type_hint_public: int
    _type_hint_private: int

    object_attr: k
    object_attr_2: s | mathematics

    tuple_attr_1: tuple
    tuple_attr_2: tuple[str | int]
    tuple_attr_3: tuple[str, int]

    list_attr_1: list
    list_attr_2: list[str | k]
    list_attr_3: list[str, s]
    list_attr_4: list[str, k | int]

    dict_attr_1: dict
    dict_attr_2: dict[str | int, None | k]
    dict_attr_3: dict[str, int]

    bool_attr: bool
    none_attr: None
    flaot_attr: float
    int_or_bool_attr: int | bool
    str_attr_with_none_value: str = None

    mulit_attr_1, _mulit_attr_2_private = (123456, "I am a String")
    mulit_attr_3 = _mulit_attr_4_private = ["I am some", "kind of list"]

    override_in_init: int

    def __init__(self):
        self.init_attr: bool
        self._init_attr_private: float
        self.override_in_init: str

    def _some_function(self, param_1: bool, param_2: a) -> a:
        """Function Docstring
        param_1: bool
        """
        self.attr_2 = param_1
        return a()

    @staticmethod
    def static_function(param_1: bool, param_2: int = 123456) -> tuple[bool, int]:
        """Function Docstring"""
        return param_1, param_2

    def test_position(self, param1, /, param2: bool, param3, *, param4, param5: int = 1) -> Any:
        """Function Docstring"""
        self.something = param2 + param3
        return param1 + self.something + param4 - param5

    @staticmethod
    def multiple_results(param_1: int) -> Any:
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
            return k()
        elif param_1 == 7:
            return [1, 2, 3, 4, 5]
        elif param_1 == 8:
            return {1: 1, 2: 2}
        elif param_1 == 9:
            return [x for x in [1, 2, 3]]
        elif param_1 == 10:
            return {1, 2, 3}
        elif param_1 == 11:
            return k
        elif param_1 == 12:
            return True, k(), 33
        return

    class NestedClass(k, mypy):
        def nested_class_function(self):
            pass


class _PrivateClass:
    public_attr_in_private_class = 0

    def __init__(self):
        self.public_init_attr_in_private_class: int = 0

    def public_func_in_private_class(self):
        pass

    class NestedPrivateClass:
        nested_class_attr = 0

        def nested_private_class_function(self):
            pass

class SomeEnum(Enum):
    ONE = "first"
    TWO = (2, 2)
    THREE = 3
    FOUR = FIVE = "forth and fifth"
    SIX, SEVEN = ("sixth", 7)
    EIGHT, NINE = "89"
    TEN = k()
