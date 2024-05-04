from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

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
            case EnumType.__name__:
                return EnumType.from_dict(d)
            case BoundaryType.__name__:
                return BoundaryType.from_dict(d)
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
class EnumType(AbstractType):
    values: frozenset[str] = field(default_factory=frozenset)
    full_match: str = field(default="", compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> EnumType:
        return EnumType(d["values"])

    @classmethod
    def from_string(cls, string: str) -> EnumType | None:
        def remove_backslash(e: str) -> str:
            e = e.replace(r"\"", '"')
            return e.replace(r"\'", "'")

        enum_match = re.search(r"{(.*?)}", string)
        if enum_match:
            quotes = "'\""
            values = set()
            enum_str = enum_match.group(1)
            value = ""
            inside_value = False
            curr_quote = None
            for i, char in enumerate(enum_str):
                if char in quotes and (i == 0 or (i > 0 and enum_str[i - 1] != "\\")):
                    if not inside_value:
                        inside_value = True
                        curr_quote = char
                    elif inside_value:
                        if curr_quote == char:
                            inside_value = False
                            curr_quote = None
                            values.add(remove_backslash(value))
                            value = ""
                        else:
                            value += char
                elif inside_value:
                    value += char

            return EnumType(frozenset(values), enum_match.group(0))

        return None

    def update(self, enum: EnumType) -> EnumType:
        values = set(self.values)
        values.update(enum.values)
        return EnumType(frozenset(values))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.__class__.__name__, "values": set(self.values)}


@dataclass(frozen=True)
class BoundaryType(AbstractType):
    NEGATIVE_INFINITY: ClassVar = "NegativeInfinity"
    INFINITY: ClassVar = "Infinity"

    base_type: str
    min: float | int | str
    max: float | int | str
    min_inclusive: bool
    max_inclusive: bool

    full_match: str = field(default="", compare=False)

    @classmethod
    def _is_inclusive(cls, bracket: str) -> bool:
        if bracket in ("(", ")"):
            return False
        if bracket in ("[", "]"):
            return True
        raise ValueError(f"{bracket} is not one of []()")

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> BoundaryType:
        return BoundaryType(
            d["base_type"],
            d["min"],
            d["max"],
            d["min_inclusive"],
            d["max_inclusive"],
        )

    @classmethod
    def from_string(cls, string: str) -> BoundaryType | None:
        pattern = r"""(?P<base_type>float|int)?[ ]  # optional base type of either float or int
                    (in|of)[ ](the[ ])?(range|interval)[ ](of[ ])?
                    # 'in' or 'of', optional 'the', 'range' or 'interval', optional 'of'
                    `?(?P<min_bracket>[\[(])(?P<min>[-+]?\d+(.\d*)?|negative_infinity),[ ]  # left side of the range
                    (?P<max>[-+]?\d+(.\d*)?|infinity)(?P<max_bracket>[\])])`?"""  # right side of the range
        match = re.search(pattern, string, re.VERBOSE)

        if match is not None:
            base_type = match.group("base_type")
            if base_type is None:
                base_type = "float"

            min_value: str | int | float = match.group("min")
            if min_value != "negative_infinity":
                if base_type == "int":
                    min_value = int(min_value)
                else:
                    min_value = float(min_value)
            else:
                min_value = BoundaryType.NEGATIVE_INFINITY

            max_value: str | int | float = match.group("max")
            if max_value != "infinity":
                if base_type == "int":
                    max_value = int(max_value)
                else:
                    max_value = float(max_value)
            else:
                max_value = BoundaryType.INFINITY

            min_bracket = match.group("min_bracket")
            max_bracket = match.group("max_bracket")
            min_inclusive = BoundaryType._is_inclusive(min_bracket)
            max_inclusive = BoundaryType._is_inclusive(max_bracket)

            return BoundaryType(
                base_type=base_type,
                min=min_value,
                max=max_value,
                min_inclusive=min_inclusive,
                max_inclusive=max_inclusive,
                full_match=match.group(0),
            )

        return None

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, BoundaryType):
            eq = (
                self.base_type == __o.base_type
                and self.min == __o.min
                and self.min_inclusive == __o.min_inclusive
                and self.max == __o.max
            )
            if eq:
                if self.max == BoundaryType.INFINITY:
                    return True
                return self.max_inclusive == __o.max_inclusive
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.__class__.__name__,
            "base_type": self.base_type,
            "min": self.min,
            "max": self.max,
            "min_inclusive": self.min_inclusive,
            "max_inclusive": self.max_inclusive,
        }


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


# ############################## Utilities ############################## #
# def _dismantel_type_string_structure(type_structure: str) -> list:
#     current_type = ""
#     result = []
#
#     while True:
#         i = 0
#         for i, char in enumerate(type_structure):
#             if char == "[":
#                 try:
#                     brackets_content, remaining_content = _parse_type_string_bracket_content(type_structure[i + 1:])
#                 except TypeParsingError as parsing_error:
#                     raise TypeParsingError(
#                         f"Missing brackets in the following string: \n{type_structure}") from parsing_error
#
#                 result.append(current_type + "[" + brackets_content + "]")
#                 type_structure = remaining_content
#                 current_type = ""
#                 break
#             elif char == ",":
#                 if current_type:
#                     result.append(current_type)
#                     current_type = ""
#             else:
#                 current_type += char
#
#         if len(type_structure) == 0 or i + 1 == len(type_structure):
#             break
#
#     if current_type:
#         result.append(current_type)
#
#     return result
#
#
# def _parse_type_string_bracket_content(substring: str) -> tuple[str, str]:
#     brackets_content = ""
#     bracket_count = 0
#     for i, char in enumerate(substring):
#         if char == "[":
#             bracket_count += 1
#         elif char == "]" and bracket_count:
#             bracket_count -= 1
#         elif char == "]" and not bracket_count:
#             return brackets_content, substring[i + 1:]
#
#         brackets_content += char
#     raise TypeParsingError("")
#
#
# # T0do Return mypy\types -> Type class
# def create_type(type_string: str, description: str) -> AbstractType:
#     if not type_string:
#         return NamedType("None", "builtins.None")
#
#     type_string = type_string.replace(" ", "")
#
#     # t0do Replace pipes with Union
#     # if "|" in type_string:
#     #     type_string = _replace_pipes_with_union(type_string)
#
#     # Structures, which only take one type argument
#     one_arg_structures = {"Final": FinalType, "Optional": OptionalType}
#     for key in one_arg_structures:
#         regex = r"^" + key + r"\[(.*)]$"
#         match = re.match(regex, type_string)
#         if match:
#             content = match.group(1)
#             return one_arg_structures[key](create_type(content, description))
#
#     # List-like structures, which take multiple type arguments
#     mult_arg_structures = {"List": ListType, "Set": SetType, "Tuple": TupleType, "Union": UnionType}
#     for key in mult_arg_structures:
#         regex = r"^" + key + r"\[(.*)]$"
#         match = re.match(regex, type_string)
#         if match:
#             content = match.group(1)
#             content_elements = _dismantel_type_string_structure(content)
#             return mult_arg_structures[key]([
#                 create_type(element, description)
#                 for element in content_elements
#             ])
#
#     match = re.match(r"^Literal\[(.*)]$", type_string)
#     if match:
#         content = match.group(1)
#         contents = content.replace(" ", "").split(",")
#         literals = []
#         for element in contents:
#             try:
#                 value = ast.literal_eval(element)
#             except (SyntaxError, ValueError):
#                 value = element[1:-1]
#             literals.append(value)
#         return LiteralType(literals)
#
#     # Misc. special structures
#     match = re.match(r"^Dict\[(.*)]$", type_string)
#     if match:
#         content = match.group(1)
#         content_elements = _dismantel_type_string_structure(content)
#         if len(content_elements) != 2:
#             raise TypeParsingError(f"Could not parse Dict from the following string: \n{type_string}")
#         return DictType(
#             create_type(content_elements[0], description),
#             create_type(content_elements[1], description),
#         )
#
#     # raise TypeParsingError(f"Could not parse type for the following type string:\n{type_string}")
#     type_ = _create_enum_boundry_type(type_string, description)
#     if type_ is not None:
#         return type_
#     return NamedType(name=type_string, qname=)
#
#
# # t0do übernehmen in create_type -> Tests schlagen nun fehl
# def _create_enum_boundry_type(type_string: str, description: str) -> AbstractType | None:
#     types: list[AbstractType] = []
#
#     # Collapse whitespaces
#     type_string = re.sub(r"\s+", " ", type_string)
#
#     # Get boundary from description
#     boundary = BoundaryType.from_string(description)
#     if boundary is not None:
#         types.append(boundary)
#
#     # Find all enums and remove them from doc_string
#     enum_array_matches = re.findall(r"\{.*?}", type_string)
#     type_string = re.sub(r"\{.*?}", " ", type_string)
#     for enum in enum_array_matches:
#         enum_type = EnumType.from_string(enum)
#         if enum_type is not None:
#             types.append(enum_type)
#
#     # Remove default value from doc_string
#     type_string = re.sub("default=.*", " ", type_string)
#
#     # Create a list with all values and types
#     # ") or (" must be replaced by a very unlikely string ("&%&") so that it is not removed when filtering out.
#     # The string will be replaced by ") or (" again after filtering out.
#     type_string = re.sub(r"\) or \(", "&%&", type_string)
#     type_string = re.sub(r" ?, ?or ", ", ", type_string)
#     type_string = re.sub(r" or ", ", ", type_string)
#     type_string = re.sub("&%&", ") or (", type_string)
#
#     brackets = 0
#     build_string = ""
#     for c in type_string:
#         if c == "(":
#             brackets += 1
#         elif c == ")":
#             brackets -= 1
#
#         if brackets > 0:
#             build_string += c
#             continue
#
#         if brackets == 0 and c != ",":
#             build_string += c
#         elif brackets == 0 and c == ",":
#             # remove leading and trailing whitespaces
#             build_string = build_string.strip()
#             if build_string != "":
#                 named = NamedType.from_string(build_string)
#                 types.append(named)
#                 build_string = ""
#
#     build_string = build_string.strip()
#
#     # Append the last remaining entry
#     if build_string != "":
#         named = NamedType.from_string(build_string)
#         types.append(named)
#
#     if len(types) == 1:
#         return types[0]
#     if len(types) == 0:
#         return None
#     return UnionType(types)
#
#
# class TypeParsingError(Exception):
#     def __init__(self, message: str):
#         self.message = message
#
#     def __str__(self) -> str:
#         return f"TypeParsingException: {self.message}"
