"""Docstring of the some_class.py module"""
"""Second Docstring"""
from .another_path.another_class import AnotherClass
from .another_path.another_class import AnotherClass as k
from enum import Enum
import mypy
import math as mathematics
from docstring_parser import *

a = AnotherClass
another_attribute = [a, 1, mathematics, "Some String"]
this_a_dict = {"a": a, "b": 2}
b: int = True
c: int | bool = "str"
a_2, a_3 = (123456, "I am a String")
a_4 = a_5 = ["I am some", "kind of list"]


def get_another_class(param_1: str = "first param", param_2: a | None = None) -> a:
    """method docstring"""
    """Second method Docstring"""
    param_1
    param_2
    return a()


class SomeClass(mathematics, k):
    """Class docstring"""
    """Second class Docstring"""
    attr_1: int = 1
    attr_2, attr_3 = (False, True)
    attr_4 = attr_5 = ["Some", "list"]

    def __init__(self):
        self.attr_2: bool = True

    def some_function(self, param_1: bool) -> bool:
        """Function Docstring
        param_1: bool
        """
        self.attr_2 = param_1
        return a()

    @staticmethod
    def static_function(param_1: bool = True):
        """Function Docstring"""
        return param_1


class SomeEnum(Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    FORTH = FIFTH = "forth and fifth"
    SIXTH, SEVENTH = ("sixth", "seventh")
