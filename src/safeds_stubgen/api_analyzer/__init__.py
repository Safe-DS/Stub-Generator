"""API-Analyzer for the Safe-DS stubs generator."""
from __future__ import annotations

from ._api import API, Attribute, Class, Function, Parameter, ParameterAssignment
from ._get_api import get_api
from ._mypy_helpers import get_classdef_definitions, get_funcdef_definitions, get_mypyfile_definitions
from ._package_metadata import distribution, distribution_version, package_root
from ._types import (
    AbstractType,
    BoundaryType,
    DictType,
    EnumType,
    FinalType,
    ListType,
    LiteralType,
    NamedType,
    OptionalType,
    SetType,
    TupleType,
    UnionType,
)

__all__ = [
    "AbstractType",
    "API",
    "Attribute",
    "BoundaryType",
    "Class",
    "DictType",
    "distribution",
    "distribution_version",
    "EnumType",
    "FinalType",
    "Function",
    "get_api",
    "get_classdef_definitions",
    "get_funcdef_definitions",
    "get_mypyfile_definitions",
    "ListType",
    "LiteralType",
    "NamedType",
    "OptionalType",
    "package_root",
    "Parameter",
    "ParameterAssignment",
    "SetType",
    "TupleType",
    "UnionType",
]
