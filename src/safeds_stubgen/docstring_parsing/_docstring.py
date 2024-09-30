from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING
from safeds_stubgen.api_analyzer._extract_boundary_values import extract_boundary
from safeds_stubgen.api_analyzer._extract_valid_values import extract_valid_literals
from safeds_stubgen.api_analyzer._types import BoundaryType

if TYPE_CHECKING:
    from typing import Any

    from safeds_stubgen.api_analyzer import AbstractType


@dataclass(frozen=True)
class ClassDocstring:
    description: str = ""
    full_docstring: str = ""
    examples: list[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class FunctionDocstring:
    description: str = ""
    full_docstring: str = ""
    examples: list[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(unsafe_hash=True)  # unsafe hash so that we wont have to call the extractors before init
class ParameterDocstring:
    type: AbstractType | None = None
    default_value: str = ""
    type_string: str = ""
    description: str = ""
    boundaries: frozenset[BoundaryType] | None = None
    valid_values: frozenset[str] | None = None

    def __init__(self, type: AbstractType | None = None, default_value: str = "", type_string: str = "", description: str = ""):
        self.type = type # from annotation
        self.default_value = default_value
        self.type_string = type_string
        self.description = description
        self.boundaries = frozenset(extract_boundary(description, type_string))
        self.valid_values = frozenset(extract_valid_literals(description, type_string))

    def to_dict(self) -> dict[str, Any]:  # custom to dict function, as sets are not JSON serializable
        boundaries = list(self.boundaries) if self.boundaries is not None else []
        valid_values = sorted(self.valid_values) if self.valid_values is not None else []
        type = self.type.to_dict() if self.type is not None else {}
        return {
            "type": type,
            "default_value": self.default_value,
            "type_string": self.type_string,
            "description": self.description,
            "boundaries": sorted(map(lambda boundary: boundary.to_dict(), boundaries), key=(lambda boundary_dict: boundary_dict["min"] + boundary_dict["max"])),
            "valid_values": valid_values
        }


@dataclass(frozen=True)
class AttributeDocstring:
    type: AbstractType | None = None
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ResultDocstring:
    type: AbstractType | None = None
    description: str = ""
    name: str = ""
