from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


@dataclass(frozen=True)
class ClassDocstring:
    description: str = ""
    full_docstring: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class FunctionDocstring:
    description: str = ""
    full_docstring: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ParameterDocstring:
    type: str = ""
    default_value: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class AttributeDocstring:
    type: str = ""
    default_value: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ResultDocstring:
    type: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)
