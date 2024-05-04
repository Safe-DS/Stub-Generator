from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from safeds_stubgen.docstring_parsing import (
        AttributeDocstring,
        ClassDocstring,
        FunctionDocstring,
        ParameterDocstring,
        ResultDocstring,
    )

    from ._types import AbstractType, TypeVarType

API_SCHEMA_VERSION = 1


def ensure_file_exists(file: Path) -> None:
    """
    Create a file and all parent directories if they don't exist already.

    Parameters
    ----------
    file:
        The file path.
    """
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)


class API:
    def __init__(self, distribution: str, package: str, version: str) -> None:
        self.distribution: str = distribution
        self.package: str = package
        self.version: str = version
        self.modules: dict[str, Module] = {}
        self.classes: dict[str, Class] = {}
        self.functions: dict[str, Function] = {}
        self.results: dict[str, Result] = {}
        self.enums: dict[str, Enum] = {}
        self.enum_instances: dict[str, EnumInstance] = {}
        self.attributes_: dict[str, Attribute] = {}
        self.parameters_: dict[str, Parameter] = {}
        self.reexport_map: dict[str, set[Module]] = defaultdict(set)

    def add_module(self, module: Module) -> None:
        self.modules[module.id] = module

    def add_class(self, class_: Class) -> None:
        self.classes[class_.id] = class_

    def add_function(self, function: Function) -> None:
        self.functions[function.id] = function

    def add_enum(self, enum: Enum) -> None:
        self.enums[enum.id] = enum

    def add_results(self, results: list[Result]) -> None:
        for result in results:
            self.results[result.id] = result

    def add_enum_instance(self, enum_instance: EnumInstance) -> None:
        self.enum_instances[enum_instance.id] = enum_instance

    def add_attribute(self, attribute: Attribute) -> None:
        self.attributes_[attribute.id] = attribute

    def add_parameter(self, parameter: Parameter) -> None:
        self.parameters_[parameter.id] = parameter

    def to_json_file(self, path: Path) -> None:
        ensure_file_exists(path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": API_SCHEMA_VERSION,
            "distribution": self.distribution,
            "package": self.package,
            "version": self.version,
            "modules": [module.to_dict() for module in sorted(self.modules.values(), key=lambda it: it.id)],
            "classes": [class_.to_dict() for class_ in sorted(self.classes.values(), key=lambda it: it.id)],
            "functions": [function.to_dict() for function in sorted(self.functions.values(), key=lambda it: it.id)],
            "results": [result.to_dict() for result in sorted(self.results.values(), key=lambda it: it.id)],
            "enums": [enum.to_dict() for enum in sorted(self.enums.values(), key=lambda it: it.id)],
            "enum_instances": [
                enum_instance.to_dict() for enum_instance in sorted(self.enum_instances.values(), key=lambda it: it.id)
            ],
            "attributes": [
                attribute.to_dict() for attribute in sorted(self.attributes_.values(), key=lambda it: it.id)
            ],
            "parameters": [
                parameter.to_dict() for parameter in sorted(self.parameters_.values(), key=lambda it: it.id)
            ],
        }


class Module:
    def __init__(
        self,
        id_: str,
        name: str,
        docstring: str = "",
        qualified_imports: list[QualifiedImport] | None = None,
        wildcard_imports: list[WildcardImport] | None = None,
    ):
        self.id: str = id_
        self.name: str = name
        self.docstring: str = docstring
        self.qualified_imports: list[QualifiedImport] = qualified_imports or []
        self.wildcard_imports: list[WildcardImport] = wildcard_imports or []
        self.classes: list[Class] = []
        self.global_functions: list[Function] = []
        self.enums: list[Enum] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "docstring": self.docstring,
            "qualified_imports": [import_.to_dict() for import_ in self.qualified_imports],
            "wildcard_imports": [import_.to_dict() for import_ in self.wildcard_imports],
            "classes": [class_.id for class_ in self.classes],
            "functions": [function.id for function in self.global_functions],
            "enums": [enum.id for enum in self.enums],
        }

    def add_class(self, class_: Class) -> None:
        self.classes.append(class_)

    def add_function(self, function: Function) -> None:
        self.global_functions.append(function)

    def add_enum(self, enum: Enum) -> None:
        self.enums.append(enum)


@dataclass
class QualifiedImport:
    qualified_name: str
    alias: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "qualified_name": self.qualified_name,
            "alias": self.alias,
        }


@dataclass
class WildcardImport:
    module_name: str

    def to_dict(self) -> dict[str, Any]:
        return {"module_name": self.module_name}


@dataclass
class Class:
    id: str
    name: str
    superclasses: list[str]
    is_public: bool
    docstring: ClassDocstring
    constructor: Function | None = None
    constructor_fulldocstring: str = ""
    inherits_from_exception: bool = False
    reexported_by: list[Module] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)
    methods: list[Function] = field(default_factory=list)
    classes: list[Class] = field(default_factory=list)
    type_parameters: list[TypeParameter] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "docstring": self.docstring.to_dict(),
            "is_public": self.is_public,
            "superclasses": self.superclasses,
            "constructor": self.constructor.to_dict() if self.constructor is not None else None,
            "inherits_from_exception": self.inherits_from_exception,
            "reexported_by": [module.id for module in self.reexported_by],
            "attributes": [attribute.id for attribute in self.attributes],
            "methods": [method.id for method in self.methods],
            "classes": [class_.id for class_ in self.classes],
            "type_parameters": [type_parameter.to_dict() for type_parameter in self.type_parameters],
        }

    @property
    def is_abstract(self) -> bool:
        return "abc.ABC" in self.superclasses

    def add_method(self, method: Function) -> None:
        self.methods.append(method)

    def add_class(self, class_: Class) -> None:
        self.classes.append(class_)

    def add_constructor(self, constructor: Function) -> None:
        self.constructor = constructor

    def add_attribute(self, attribute: Attribute) -> None:
        self.attributes.append(attribute)


@dataclass(frozen=True)
class Attribute:
    id: str
    name: str
    is_public: bool
    is_static: bool
    type: AbstractType | None
    docstring: AttributeDocstring

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "docstring": self.docstring.to_dict(),
            "is_public": self.is_public,
            "is_static": self.is_static,
            "type": self.type.to_dict() if self.type is not None else None,
        }


@dataclass
class Function:
    id: str
    name: str
    docstring: FunctionDocstring
    is_public: bool
    is_static: bool
    is_class_method: bool
    is_property: bool
    result_docstrings: list[ResultDocstring]
    type_var_types: list[TypeVarType] = field(default_factory=list)
    results: list[Result] = field(default_factory=list)
    reexported_by: list[Module] = field(default_factory=list)
    parameters: list[Parameter] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "docstring": self.docstring.to_dict(),
            "is_public": self.is_public,
            "is_static": self.is_static,
            "is_class_method": self.is_class_method,
            "is_property": self.is_property,
            "results": [result.id for result in self.results],
            "reexported_by": [module.id for module in self.reexported_by],
            "parameters": [parameter.id for parameter in self.parameters],
        }


@dataclass(frozen=True)
class Parameter:
    id: str
    name: str
    is_optional: bool
    # We do not support default values that aren't core classes or classes definied in the package we analyze.
    default_value: str | bool | int | float | None
    assigned_by: ParameterAssignment
    docstring: ParameterDocstring
    type: AbstractType | None

    @property
    def is_required(self) -> bool:
        return self.default_value is None

    @property
    def is_variadic(self) -> bool:
        return self.assigned_by in (
            ParameterAssignment.POSITIONAL_VARARG,
            ParameterAssignment.NAMED_VARARG,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "docstring": self.docstring.to_dict(),
            "is_optional": self.is_optional,
            "default_value": self.default_value,
            "assigned_by": self.assigned_by.name,
            "type": self.type.to_dict() if self.type is not None else None,
        }


class ParameterAssignment(PythonEnum):
    """
    How arguments are assigned to parameters. The parameters must appear exactly in this order in a parameter list.

    IMPLICIT parameters appear on instance methods (usually called "self") and on class methods (usually called "cls").
    POSITION_ONLY parameters precede the "/" in a parameter list. NAME_ONLY parameters follow the "*" or the
    POSITIONAL_VARARGS parameter ("*args"). Between the "/" and the "*" the POSITION_OR_NAME parameters reside. Finally,
    the parameter list might optionally include a NAMED_VARARG parameter ("**kwargs").
    """

    IMPLICIT = "IMPLICIT"
    POSITION_ONLY = "POSITION_ONLY"
    POSITION_OR_NAME = "POSITION_OR_NAME"
    POSITIONAL_VARARG = "POSITIONAL_VARARG"
    NAME_ONLY = "NAME_ONLY"
    NAMED_VARARG = "NAMED_VARARG"


@dataclass(frozen=True)
class TypeParameter:
    name: str
    type: AbstractType | None
    variance: VarianceKind

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.to_dict() if self.type is not None else None,
            "variance_type": self.variance.name,
        }


class VarianceKind(PythonEnum):
    CONTRAVARIANT = "CONTRAVARIANT"
    COVARIANT = "COVARIANT"
    INVARIANT = "INVARIANT"


@dataclass(frozen=True)
class Result:
    id: str
    name: str
    type: AbstractType | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.to_dict() if self.type is not None else None,
        }


@dataclass
class Enum:
    id: str
    name: str
    docstring: ClassDocstring
    instances: list[EnumInstance] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "docstring": self.docstring.to_dict(),
            "instances": [instance.id for instance in self.instances],
        }

    def add_enum_instance(self, enum_instance: EnumInstance) -> None:
        self.instances.append(enum_instance)


@dataclass(frozen=True)
class EnumInstance:
    id: str
    name: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
        }
