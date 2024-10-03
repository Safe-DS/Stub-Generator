from typing import Self, overload, no_type_check
from . import unknown_source

from tests.data.main_package.another_path.another_module import yetAnotherClass


class ClassModuleEmptyClassA:
    ...


class ClassModuleClassB(ClassModuleEmptyClassA):
    b_attr_1: int
    b_attr_2: dict = {}

    def __init__(self, a: int, b: ClassModuleEmptyClassA | None):
        self.b_attr_1 = self.b_attr_2['index'] = 0

    def __enter__(self):
        return self

    @no_type_check
    def _apply(self, f, *args, **kwargs):
        pass

    def f(self): ...


class ClassModuleClassC(ClassModuleEmptyClassA, ClassModuleClassB, yetAnotherClass):
    attr_1: int
    attr_2: int

    def f1(self):
        def f1_2(): ...


class ClassModuleClassD:
    class ClassModuleNestedClassE:
        """Docstring of the nested class E."""
        nested_attr_1: None
        _nested_attr_2: None

        def class_e_func(self):
            """Docstring of func of nested class E"""
            ...

        class _ClassModulePrivateDoubleNestedClassF:
            def _class_f_func(self): ...

    class _PrivateNestedClass:
        ...


class _ClassModulePrivateClassG:
    _attr_1: float
    _attr_2: bool


class InheritFromException(ValueError):
    ...


class InheritFromException2(Exception, InheritFromException, ClassModuleClassB):
    ...


class SelfTypes1:
    def self_result1(self) -> Self:
        pass


class SelfTypes2(SelfTypes1):
    def self_result2(self) -> Self:
        pass

    def infer_self_result2(self):
        return self


class ClassWithOverloadedFunction:
    @overload
    def overloaded_function(
        self,
        parameter_1: int,
        *,
        parameter_2: float = ...,
    ) -> bool: ...

    @overload
    def overloaded_function(
        self,
        parameter_1: str,
        *,
        parameter_2: bool,
    ) -> bool | None: ...

    def overloaded_function(
        self,
        parameter_1: int,
        *,
        parameter_2: bool = True,
    ) -> bool | None:
        return None


class ClassWithOverloadedFunction2:
    @property
    def stale(self):
        return self._stale

    @stale.setter
    def stale(self, val):
        self._stale = val


class ClassWithImportedSuperclasses(unknown_source.UnknownClass):
    pass
