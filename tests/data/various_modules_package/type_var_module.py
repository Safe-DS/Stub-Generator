from typing import TypeVar


class TypeVarClass:
    type_var = TypeVar("type_var")


_type_var = TypeVar("_type_var")
def type_var_func(type_var_list: list[_type_var]) -> list[_type_var]: ...


def type_var_func2[T](a: T) -> T: ...
