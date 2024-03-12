from typing import TypeVar, Generic, Sequence, Collection, Mapping, Any

T = TypeVar('T')


class GenericTypeVar(Generic[T]):
    type_var = TypeVar("type_var")

    def __init__(self, items: list[T]): ...

    def type_var_class_method(self, a: T) -> T: ...


class GenericTypeVar2(Generic[T]):
    type_var = TypeVar("type_var")

    def type_var_class_method2(self, a: T) -> T: ...


class SequenceTypeVar(Sequence[T]):
    type_var = TypeVar("type_var")

    def __init__(self, items: list[T]): ...

    def type_var_class_method(self, a: T) -> T: ...


class SequenceTypeVar2(Sequence[T]):
    type_var = TypeVar("type_var")

    def type_var_class_method2(self, a: T) -> T: ...


class CollectionTypeVar(Collection[T]):
    type_var = TypeVar("type_var")

    def __init__(self, items: list[T]): ...

    def type_var_class_method(self, a: T) -> T: ...


class CollectionTypeVar2(Collection[T]):
    type_var = TypeVar("type_var")

    def type_var_class_method2(self, a: T) -> T: ...


class MappingTypeVar(Mapping[str, Any]):
    def __init__(self, data: Mapping[str, Any] | None = None): ...


class MappingTypeVar2:
    def __init__(self, data: Mapping[str, Sequence[Any]]): ...


class MappingTypeVar3(Mapping[str, Collection[T]]):
    def __init__(self, data: Mapping[str, Collection[T]] | None): ...


_type_var = TypeVar("_type_var")
def type_var_func(a: list[_type_var]) -> list[_type_var]: ...


_type_var1 = TypeVar("_type_var1")
_type_var2 = TypeVar("_type_var2")
def multiple_type_var(a: _type_var1, b: _type_var2) -> list[_type_var1 | _type_var2]: ...


T_in = TypeVar("T_in", bound=int)
def type_var_fun_invariance_with_bound(a: list[T_in]) -> T_in: ...
