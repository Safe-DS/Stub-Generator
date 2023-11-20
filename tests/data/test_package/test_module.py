"""Docstring of the some_class.py module."""
# noinspection PyUnresolvedReferences
import math as mathematics
from typing import *

# noinspection PyUnresolvedReferences
import mypy

# noinspection PyUnresolvedReferences
from docstring_parser import *

from .another_path.another_module import AnotherClass
from .another_path.another_module import AnotherClass as _AcImportAlias

AcDoubleAlias = _AcImportAlias
ac_alias = AnotherClass


# noinspection PyUnusedLocal
def global_func(param_1: str = "first param", param_2: ac_alias | None = None) -> ac_alias:
    """Docstring 1.

    Docstring 2.
    """


def _private_global_func() -> _AcImportAlias | AcDoubleAlias | ac_alias:
    pass


class SomeClass(AcDoubleAlias):
    """Summary of the description.

    Full description
    """

    type_hint_public: int
    _type_hint_private: int

    no_type_hint_public = 1
    _no_type_hint_private = 1

    object_attr: _AcImportAlias
    object_attr_2: AcDoubleAlias

    tuple_attr_1: tuple
    tuple_attr_2: tuple[str | int]
    tuple_attr_3: tuple[str, int]

    list_attr_1: list
    list_attr_2: list[str | _AcImportAlias]
    list_attr_3: list[str, AcDoubleAlias]
    list_attr_4: list[str, _AcImportAlias | int]

    dict_attr_1: dict
    dict_attr_2: dict[str, int]
    dict_attr_3: dict[str | int, None | _AcImportAlias]

    bool_attr: bool
    none_attr: None
    flaot_attr: float
    int_or_bool_attr: int | bool
    str_attr_with_none_value: str = None

    multi_attr_1, _multi_attr_2_private = (123456, "I am a String")
    multi_attr_3 = _multi_attr_4_private = ["I am some", "kind of list"]

    # noinspection PyUnusedLocal
    def __init__(self, init_param_1):
        """Summary of the init description.

        Full init description.
        """
        self.init_attr: bool
        # noinspection PyTypeChecker
        self._init_attr_private: float = "I'm a string"
        no_class_attr: bool

    def _some_function(self, param_1: ac_alias, param_2: bool = False) -> ac_alias:
        """Function Docstring.

        param_2: bool.
        """

    @staticmethod
    def static_function(param_1: bool = True, param_2: int | bool = 123456) -> tuple[bool, int]:
        """Function Docstring."""

    def test_position(self, param1, /, param2: bool, param3=1, *, param4=AcDoubleAlias(), param5: int = 1) -> Any:
        """Function Docstring."""

    @staticmethod
    def test_params(*args, **kwargs):
        pass

    @staticmethod
    def multiple_results(param_1: int) -> Any | tuple[int, str]:
        """Function Docstring."""

    def no_return_1(self):
        pass

    def no_return_2(self) -> None:
        pass

    @classmethod
    def class_method(cls) -> None:
        pass

    @classmethod
    def class_method_params(cls, param_1: int) -> bool:
        pass

    class NestedClass(_AcImportAlias):
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


class InferMyTypes:
    infer_attr = 1

    def __init__(self, init_param=1):
        self.init_infer = 3

    @staticmethod
    def infer_function(infer_param=1, infer_param_2: int = "Something"):
        if infer_param_2:
            return False
        elif infer_param:
            if infer_param:
                return 12
            else:
                return bool

        match infer_param:
            case 1:
                if 4:
                    return InferMyTypes
            case _:
                return None

        while infer_param_2:
            if infer_param_2:
                return 1.23
            else:
                infer_param_2 = 0

        with open("no path", "r") as _:
            if infer_param_2:
                return "Some String"

        for _ in (1, 2):
            if infer_param_2:
                return SomeClass

        return int


_T_co = TypeVar("_T_co", covariant=True, bound=str)
_T_con = TypeVar("_T_con", contravariant=True, bound=SomeClass)
_T_in = TypeVar("_T_in", int, Literal[1, 2])


class VarianceClassAll(Generic[_T_co, _T_con, _T_in]):
    ...


class VarianceClassOnlyInvariance(Generic[_T_in]):
    ...
