from typing import Self

from tests.data.main_package.another_path.another_module import yetAnotherClass


class ClassModuleEmptyClassA:
    ...


class ClassModuleClassB(ClassModuleEmptyClassA):
    def __init__(self, a: int, b: ClassModuleEmptyClassA | None): ...

    def f(self): ...


class ClassModuleClassC(ClassModuleEmptyClassA, ClassModuleClassB, yetAnotherClass):
    attr_1: int
    attr_2: int

    def f1(self):
        def f1_2(): ...


class ClassModuleClassD:
    class ClassModuleNestedClassE:
        nested_attr_1: None
        _nested_attr_2: None

        def class_e_func(self): ...

        class _ClassModulePrivateDoubleNestedClassF:
            def _class_f_func(self): ...


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
