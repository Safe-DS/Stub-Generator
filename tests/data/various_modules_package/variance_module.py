from typing import Generic, TypeVar, Literal


class A:
    ...


_T_in = TypeVar("_T_in")
_T_co = TypeVar("_T_co", covariant=True)
_T_con = TypeVar("_T_con", contravariant=True)


class VarianceClassOnlyCovarianceNoBound(Generic[_T_co]):
    ...


class VarianceClassOnlyVarianceNoBound(Generic[_T_in]):
    ...


class VarianceClassOnlyContravarianceNoBound(Generic[_T_con]):
    ...


_T_co2 = TypeVar("_T_co2", covariant=True, bound=str)
_T_con2 = TypeVar("_T_con2", contravariant=True, bound=A)
_T_in2 = TypeVar("_T_in2", int, Literal[1, 2])


class VarianceClassAll(Generic[_T_co2, _T_con2, _T_in2]):
    ...
