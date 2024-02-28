from typing import TypeVar, Generic

T = TypeVar('T')


class TypeVarClass(Generic[T]):
    type_var = TypeVar("type_var")

    def __init__(self, items: list[T]): ...

    def type_var_class_method(self, a: T) -> T: ...


class TypeVarClass2(Generic[T]):
    type_var = TypeVar("type_var")

    def type_var_class_method2(self, a: T) -> T: ...


_type_var = TypeVar("_type_var")
def type_var_func(a: list[_type_var]) -> list[_type_var]: ...


_type_var1 = TypeVar("_type_var1")
_type_var2 = TypeVar("_type_var2")
def multiple_type_var(a: _type_var1, b: _type_var2) -> list[_type_var1 | _type_var2]: ...
