"""API-Analyzer for the Safe-DS stubs generator."""
from __future__ import annotations

from ._api import (
    API,
    Attribute,
    Class,
    Enum,
    Function,
    Parameter,
    ParameterAssignment,
    QualifiedImport,
    Result,
    WildcardImport,
)
from ._generate_stubs import StubsGenerator
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
    "Enum",
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
    "QualifiedImport",
    "Result",
    "SetType",
    "StubsGenerator",
    "TupleType",
    "UnionType",
    "WildcardImport",
]
