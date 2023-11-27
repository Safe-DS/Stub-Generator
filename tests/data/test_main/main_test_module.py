"""Docstring of the some_class.py module."""
# noinspection PyUnresolvedReferences
import math as mathematics

# noinspection PyUnresolvedReferences
import mypy

# noinspection PyUnresolvedReferences
from docstring_parser import *

from .another_path.another_module import AnotherClass
from .another_path.another_module import AnotherClass as _AcImportAlias

AcDoubleAlias = _AcImportAlias
ac_alias = AnotherClass


# Todo Frage: Ist bei den Stubs param_2 optional? Wird None als default value unterstützt?
# noinspection PyUnusedLocal
def global_func(param_1: str = "first param", param_2: ac_alias | None = None) -> ac_alias:
    """Docstring 1.

    Docstring 2.
    """


def _private_global_func() -> _AcImportAlias | AcDoubleAlias | ac_alias:
    pass


class ModuleClass(AcDoubleAlias):
    """Summary of the description.

    Full description
    """
    attr_1: int = 3

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
