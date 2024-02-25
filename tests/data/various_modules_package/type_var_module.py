from typing import TypeVar


class TypeVarClass:
    type_var = TypeVar("type_var")


_type_var = TypeVar("_type_var")
def type_var_func(a: list[_type_var]) -> list[_type_var]: ...


def type_var_func2[T](a: T) -> T: ...


_type_var1 = TypeVar("_type_var1")
_type_var2 = TypeVar("_type_var2")
def multiple_type_var(a: _type_var1, b: _type_var2) -> list[_type_var1 | _type_var2]: ...


def multiple_type_var2[T, U](a: T, b: U) -> T | U: ...
