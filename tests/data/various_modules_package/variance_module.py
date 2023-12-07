from typing import Generic, TypeVar, Literal


class A:
    ...


_T_co = TypeVar("_T_co", covariant=True, bound=str)
_T_con = TypeVar("_T_con", contravariant=True, bound=A)
_T_in = TypeVar("_T_in", int, Literal[1, 2])


class VarianceClassAll(Generic[_T_co, _T_con, _T_in]):
    ...


class VarianceClassOnlyInvariance(Generic[_T_in]):
    ...
