from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


class AbstractType(metaclass=ABCMeta):
    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AbstractType:
        match d["kind"]:
            case UnknownType.__name__:
                return UnknownType.from_dict(d)
            case NamedType.__name__:
                return NamedType.from_dict(d)
            case NamedSequenceType.__name__:
                return NamedSequenceType.from_dict(d)
            case ListType.__name__:
                return ListType.from_dict(d)
            case DictType.__name__:
                return DictType.from_dict(d)
            case SetType.__name__:
                return SetType.from_dict(d)
            case LiteralType.__name__:
                return LiteralType.from_dict(d)
            case FinalType.__name__:
                return FinalType.from_dict(d)
            case TupleType.__name__:
                return TupleType.from_dict(d)
            case UnionType.__name__:
                return UnionType.from_dict(d)
            case CallableType.__name__:
                return CallableType.from_dict(d)
            case TypeVarType.__name__:
                return TypeVarType.from_dict(d)
            case _:
                raise ValueError(f"Cannot parse {d['kind']} value.")

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class UnknownType(AbstractType):
    @classmethod
    def from_dict(cls, _: dict[str, Any]) -> UnknownType:
        return UnknownType()

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.__class__.__name__}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnknownType):  # pragma: no cover
            return NotImplemented
        return True


@dataclass(frozen=True)
class NamedType(AbstractType):
    name: str
    qname: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> NamedType:
        return NamedType(d["name"], d["qname"])

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.__class__.__name__, "name": self.name, "qname": self.qname}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NamedType):  # pragma: no cover
            return NotImplemented
        return self.name == other.name and self.qname == other.qname

    def __hash__(self) -> int:
        return hash((self.name, self.qname))


@dataclass(frozen=True)
class NamedSequenceType(AbstractType):
    name: str
    qname: str
    types: Sequence[AbstractType]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> NamedSequenceType:
        types = []
        for element in d["types"]:
            type_ = AbstractType.from_dict(element)
            if type_ is not None:
                types.append(type_)
        return NamedSequenceType(name=d["name"], qname=d["qname"], types=types)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.__class__.__name__,
            "name": self.name,
            "qname": self.qname,
            "types": [t.to_dict() for t in self.types],
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NamedSequenceType):  # pragma: no cover
            return NotImplemented
        return Counter(self.types) == Counter(other.types) and self.name == other.name and self.qname == other.qname

    def __hash__(self) -> int:
        return hash(frozenset([self.name, self.qname, *self.types]))


@dataclass(frozen=True)
class UnionType(AbstractType):
    types: Sequence[AbstractType]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> UnionType:
        types = []
        for element in d["types"]:
            type_ = AbstractType.from_dict(element)
            if type_ is not None:
                types.append(type_)
        return UnionType(types)

    def to_dict(self) -> dict[str, Any]:
        type_list = []
        for t in self.types:
            type_list.append(t.to_dict())

        return {"kind": self.__class__.__name__, "types": type_list}

    def __hash__(self) -> int:
        return hash(frozenset(self.types))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnionType):  # pragma: no cover
            return NotImplemented
        return Counter(self.types) == Counter(other.types)


@dataclass(frozen=True)
class ListType(AbstractType):
    types: Sequence[AbstractType]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ListType:
        types = []
        for element in d["types"]:
            type_ = AbstractType.from_dict(element)
            if type_ is not None:
                types.append(type_)
        return ListType(types)

    def to_dict(self) -> dict[str, Any]:
        type_list = [t.to_dict() for t in self.types]

        return {"kind": self.__class__.__name__, "types": type_list}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ListType):  # pragma: no cover
            return NotImplemented
        return Counter(self.types) == Counter(other.types)

    def __hash__(self) -> int:
        return hash(frozenset(self.types))


@dataclass(frozen=True)
class DictType(AbstractType):
    key_type: AbstractType
    value_type: AbstractType

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DictType:
        return DictType(AbstractType.from_dict(d["key_type"]), AbstractType.from_dict(d["value_type"]))

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.__class__.__name__,
            "key_type": self.key_type.to_dict(),
            "value_type": self.value_type.to_dict(),
        }

    def __hash__(self) -> int:
        return hash(frozenset([self.key_type, self.value_type]))


@dataclass(frozen=True)
class CallableType(AbstractType):
    parameter_types: Sequence[AbstractType]
    return_type: AbstractType

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CallableType:
        params = []
        for param in d["parameter_types"]:
            type_ = AbstractType.from_dict(param)
            if type_ is not None:
                params.append(type_)

        return CallableType(params, AbstractType.from_dict(d["return_type"]))

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.__class__.__name__,
            "parameter_types": [t.to_dict() for t in self.parameter_types],
            "return_type": self.return_type.to_dict(),
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CallableType):  # pragma: no cover
            return NotImplemented
        return Counter(self.parameter_types) == Counter(other.parameter_types) and self.return_type == other.return_type

    def __hash__(self) -> int:
        return hash(frozenset([*self.parameter_types, self.return_type]))


@dataclass(frozen=True)
class SetType(AbstractType):
    types: Sequence[AbstractType]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SetType:
        types = []
        for element in d["types"]:
            type_ = AbstractType.from_dict(element)
            if type_ is not None:
                types.append(type_)
        return SetType(types)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.__class__.__name__,
            "types": [t.to_dict() for t in self.types],
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SetType):  # pragma: no cover
            return NotImplemented
        return Counter(self.types) == Counter(other.types)

    def __hash__(self) -> int:
        return hash(frozenset(self.types))


@dataclass(frozen=True)
class LiteralType(AbstractType):
    literals: list[str | int | float | bool]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LiteralType:
        return LiteralType(d["literals"])

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.__class__.__name__, "literals": self.literals}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LiteralType):  # pragma: no cover
            return NotImplemented
        return Counter(self.literals) == Counter(other.literals)

    def __hash__(self) -> int:
        return hash(frozenset(self.literals))


@dataclass(frozen=True)
class FinalType(AbstractType):
    type_: AbstractType

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> FinalType:
        return FinalType(AbstractType.from_dict(d["type"]))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.__class__.__name__, "type": self.type_.to_dict()}

    def __hash__(self) -> int:
        return hash(frozenset([self.type_]))


@dataclass(frozen=True)
class TupleType(AbstractType):
    types: Sequence[AbstractType]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TupleType:
        types = []
        for element in d["types"]:
            type_ = AbstractType.from_dict(element)
            if type_ is not None:
                types.append(type_)
        return TupleType(types)

    def to_dict(self) -> dict[str, Any]:
        type_list = [t.to_dict() for t in self.types]

        return {"kind": self.__class__.__name__, "types": type_list}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TupleType):  # pragma: no cover
            return NotImplemented
        return Counter(self.types) == Counter(other.types)

    def __hash__(self) -> int:
        return hash(frozenset(self.types))


@dataclass(frozen=True)
class TypeVarType(AbstractType):
    name: str
    upper_bound: AbstractType | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TypeVarType:
        return TypeVarType(d["name"], d["upper_bound"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.__class__.__name__,
            "name": self.name,
            "upper_bound": self.upper_bound.to_dict() if self.upper_bound is not None else None,
        }

    def __hash__(self) -> int:
        return hash(frozenset([self.name, self.upper_bound]))
