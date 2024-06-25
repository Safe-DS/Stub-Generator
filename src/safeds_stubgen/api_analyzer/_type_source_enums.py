from __future__ import annotations

from enum import Enum


class TypeSourcePreference(Enum):
    CODE = "code"
    DOCSTRING = "docstring"

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_string(key: str) -> TypeSourcePreference:
        try:
            return TypeSourcePreference[key.upper()]
        except KeyError as err:
            raise ValueError(f"Unknown preference type: {key}") from err


class TypeSourceWarning(Enum):
    WARN = "warn"
    IGNORE = "ignore"

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_string(key: str) -> TypeSourceWarning:
        try:
            return TypeSourceWarning[key.upper()]
        except KeyError as err:
            raise ValueError(f"Unknown warning type: {key}") from err
