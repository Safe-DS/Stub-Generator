from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from safeds_stubgen.api_analyzer import AbstractType


@dataclass(frozen=True)
class ClassDocstring:
    description: str = ""
    full_docstring: str = ""
    example: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class FunctionDocstring:
    description: str = ""
    full_docstring: str = ""
    example: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ParameterDocstring:
    type: AbstractType | None = None
    default_value: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


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
