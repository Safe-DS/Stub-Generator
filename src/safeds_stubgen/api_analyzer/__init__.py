"""API-Analyzer for the Safe-DS stubs generator."""
from __future__ import annotations

from ._api import API, Attribute, Class, Function, Parameter, ParameterAssignment
from ._get_api import get_api
from ._mypy_helpers import get_classdef_definitions, get_funcdef_definitions, get_mypyfile_definitions
from ._package_metadata import distribution, distribution_version, package_root
from ._types import (
    BoundaryType,
    EnumType,
    NamedType,
)

__all__ = [
    "API",
    "Attribute",
    "BoundaryType",
    "Class",
    "distribution",
    "distribution_version",
    "EnumType",
    "Function",
    "get_api",
    "get_classdef_definitions",
    "get_funcdef_definitions",
    "get_mypyfile_definitions",
    "NamedType",
    "package_root",
    "Parameter",
    "ParameterAssignment",
]
