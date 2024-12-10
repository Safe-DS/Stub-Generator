"""API-Analyzer for the Safe-DS stubs generator."""

from __future__ import annotations

from ._api import (
    API,
    Attribute,
    Class,
    Enum,
    Function,
    Module,
    Parameter,
    ParameterAssignment,
    QualifiedImport,
    Result,
    UnknownValue,
    VarianceKind,
    WildcardImport,
)
from safeds_stubgen.api_analyzer._extract_boundary_values import extract_boundary
from safeds_stubgen.api_analyzer._extract_valid_values import extract_valid_literals
from ._ast_visitor import result_name_generator
from ._get_api import get_api
from ._mypy_helpers import get_classdef_definitions, get_funcdef_definitions, get_mypyfile_definitions
from ._package_metadata import distribution, distribution_version
from ._type_source_enums import TypeSourcePreference, TypeSourceWarning
from ._types import (
    AbstractType,
    CallableType,
    DictType,
    FinalType,
    ListType,
    LiteralType,
    NamedSequenceType,
    NamedType,
    SetType,
    TupleType,
    TypeVarType,
    UnionType,
    UnknownType,
)

__all__ = [
    "AbstractType",
    "API",
    "Attribute",
    "CallableType",
    "Class",
    "DictType",
    "distribution",
    "distribution_version",
    "Enum",
    "EnumType",
    "extract_boundary",
    "extract_valid_literals",
    "FinalType",
    "Function",
    "get_api",
    "get_classdef_definitions",
    "get_funcdef_definitions",
    "get_mypyfile_definitions",
    "ListType",
    "LiteralType",
    "Module",
    "NamedSequenceType",
    "NamedType",
    "Parameter",
    "ParameterAssignment",
    "QualifiedImport",
    "Result",
    "result_name_generator",
    "SetType",
    "TupleType",
    "TypeSourcePreference",
    "TypeSourceWarning",
    "TypeVarType",
    "UnionType",
    "UnknownType",
    "UnknownValue",
    "VarianceKind",
    "WildcardImport",
]
