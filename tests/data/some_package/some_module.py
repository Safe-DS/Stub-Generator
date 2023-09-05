"""Docstring of the some_class.py module"""
import math as mathematics
from enum import Enum
from typing import Any

# noinspection PyUnresolvedReferences
import mypy
# noinspection PyUnresolvedReferences
from docstring_parser import *

from .another_path.another_class import AnotherClass
from .another_path.another_class import AnotherClass as k

s = k
a = AnotherClass

attr_1: int = 1
attr_2, attr_3 = (False, True)
attr_4 = attr_5 = ["Some", "list"]


def get_another_class(param_1: str = "first param", param_2: a | None = None) -> a:
    """method docstring"""
    return a()


class SomeClass(mathematics, s):
    """Class docstring"""
    a1 = k()
    a1_5 = (1, "B")
    a3: a = k()
    _a_list = [a, 1, mathematics, "Some String"]
    a_list_2: list[a | int | mathematics | str] = [a(), 1, mathematics, "Some String"]
    this_a_dict = {"a": a, "b": 2}
    _b: str = True
    c: int | bool = "str"
    a_2, a_3 = (123456, "I am a String")
    _a_4 = a_5 = ["I am some", "kind of list"]

    def __init__(self):
        self.init_attr_1: bool = True
        init_attr_2: int = 42
        self.init_attr_3, init_attr_4 = (123456, "I am a String")
        self.init_attr_5 = init_attr_6 = ["I am some", "kind of list"]

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


class _PrivateClass:
    def __init__(self):
        pass

    def function_in_private_class(self):
        pass


class SomeEnum(Enum):
    ONE = "first"
    TWO = (2, 2)
    THREE = 3
    FOUR = FIVE = "forth and fifth"
    SIX, SEVEN = ("sixth", 7)
    EIGHT, NINE = "89"
    TEN = k()
