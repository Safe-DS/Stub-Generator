from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from pathlib import Path

    from safeds_stubgen.docstring_parsing import AttributeDocstring, ClassDocstring, FunctionDocstring, ParameterDocstring, ResultDocstring

    from ._types import AbstractType

API_SCHEMA_VERSION = 1


def ensure_file_exists(file: Path) -> None:
    """
    Create a file and all parent directories if they don't exist already.

    Parameters
    ----------
    file: Path
        The file path.
    """
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)


def parent_id(id_: str) -> str:
    return "/".join(id_.split("/")[:-1])


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

    def is_public_class(self, class_id: str) -> bool:
        return class_id in self.classes and self.classes[class_id].is_public

    def is_public_function(self, function_id: str) -> bool:
        return function_id in self.functions and self.functions[function_id].is_public

    def class_count(self) -> int:
        return len(self.classes)

    def public_class_count(self) -> int:
        return len([it for it in self.classes.values() if it.is_public])

    def function_count(self) -> int:
        return len(self.functions)

    def public_function_count(self) -> int:
        return len([it for it in self.functions.values() if it.is_public])

    def parameter_count(self) -> int:
        return len(self.parameters())

    def parameters(self) -> dict[str, Parameter]:
        if self.parameters_ is not None:
            return self.parameters_
        parameters_: dict[str, Parameter] = {}

        for function in self.functions.values():
            for parameter in function.parameters:
                parameter_id = f"{function.id}/{parameter.name}"
                parameters_[parameter_id] = parameter
        self.parameters_ = parameters_
        return parameters_

    def attributes(self) -> dict[str, Attribute]:
        if self.attributes_ is not None:
            return self.attributes_
        attributes_: dict[str, Attribute] = {}

        for class_ in self.classes.values():
            for attribute in class_.attributes:
                attribute_id = f"{class_.id}/{attribute.name}"
                attributes_[attribute_id] = attribute
        self.attributes_ = attributes_

        return attributes_

    def results(self) -> dict[str, Result]:
        if self.results != {}:
            return self.results
        results_: dict[str, Result] = {}

        for function in self.functions.values():
            for result in function.results:
                result_id = f"{function.id}/{result.name}"
                results_[result_id] = result
        self.results = results_
        return results_

    def get_default_value(self, parameter_id: str) -> str | None:
        function_id = parent_id(parameter_id)

        if function_id not in self.functions:
            return None

        for parameter in self.functions[function_id].parameters:
            if parameter.id == parameter_id:
                return parameter.default_value

        return None

    def get_public_api(self) -> API:
        result = API(self.distribution, self.package, self.version)

        for module in self.modules.values():
            result.add_module(module)

        for class_ in self.classes.values():
            if class_.is_public:
                copy = Class(
                    id=class_.id,
                    name=class_.name,
                    superclasses=class_.superclasses,
                    is_public=class_.is_public,
                    reexported_by=class_.reexported_by,
                    docstring=class_.docstring,
                    constructor=class_.constructor,
                    attributes=class_.attributes,
                    methods=class_.methods,
                    classes=class_.classes,
                )
                for method in class_.methods:
                    if self.is_public_function(method.id):
                        copy.add_method(method)
                result.add_class(copy)

        for function in self.functions.values():
            if function.is_public:
                result.add_function(function)

        return result

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
            "modules": [
                module.to_dict()
                for module in sorted(self.modules.values(), key=lambda it: it.id)
            ],
            "classes": [
                class_.to_dict()
                for class_ in sorted(self.classes.values(), key=lambda it: it.id)
            ],
            "functions": [
                function.to_dict()
                for function in sorted(self.functions.values(), key=lambda it: it.id)
            ],
            "results": [
                result.to_dict()
                for result in sorted(self.results.values(), key=lambda it: it.id)
            ],
            "enums": [
                enum.to_dict()
                for enum in sorted(self.enums.values(), key=lambda it: it.id)
            ],
            "enum_instances": [
                enum_instance.to_dict()
                for enum_instance in sorted(self.enum_instances.values(), key=lambda it: it.id)
            ],
            "attributes": [
                attribute.to_dict()
                for attribute in sorted(self.attributes_.values(), key=lambda it: it.id)
            ],
            "parameters": [
                parameter.to_dict()
                for parameter in sorted(self.parameters_.values(), key=lambda it: it.id)
            ],
        }


class Module:
    def __init__(
        self, id_: str, name: str, docstring: str = "", qualified_imports=None, wildcard_imports=None,
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
    superclasses: list[Class]
    is_public: bool
    docstring: ClassDocstring
    constructor: Function | None = None
    constructor_fulldocstring: str = ""
    reexported_by: list[Module] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)
    methods: list[Function] = field(default_factory=list)
    classes: list[Class] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "superclasses": self.superclasses,
            "is_public": self.is_public,
            "description": self.docstring.description,
            "constructor": self.constructor.to_dict() if self.constructor is not None else None,
            "reexported_by": [module.id for module in self.reexported_by],
            "attributes": [attribute.id for attribute in self.attributes],
            "methods": [method.id for method in self.methods],
            "classes": [class_.id for class_ in self.classes],
        }

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
            "is_public": self.is_public,
            "is_static": self.is_static,
            "type": self.type.to_dict() if self.type is not None else None,
            "docstring": self.docstring.to_dict(),
        }


@dataclass
class Function:
    id: str
    name: str
    docstring: FunctionDocstring
    is_public: bool
    is_static: bool
    results: list[Result] = field(default_factory=list)
    reexported_by: list[Module] = field(default_factory=list)
    parameters: list[Parameter] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.docstring.description,
            "is_public": self.is_public,
            "is_static": self.is_static,
            "results": [result.id for result in self.results],
            "reexported_by": [module.id for module in self.reexported_by],
            "parameters": [parameter.id for parameter in self.parameters],
        }


@dataclass(frozen=True)
class Parameter:
    id: str
    name: str
    is_optional: bool
    default_value: str | bool | int | float | None
    assigned_by: ParameterAssignment
    docstring: ParameterDocstring
    type: AbstractType

    @property
    def is_required(self) -> bool:
        return self.default_value is None

    @property
    def is_variadic(self) -> bool:
        return self.assigned_by in (
            ParameterAssignment.POSITIONAL_VARARG, ParameterAssignment.NAMED_VARARG,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "is_optional": self.is_optional,
            "default_value": self.default_value,
            "assigned_by": self.assigned_by.name,
            "docstring": self.docstring.to_dict(),
            "type": self.type.to_dict(),
        }


class ParameterAssignment(Enum):
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
class Result:
    id: str
    name: str
    type: AbstractType | None
    docstring: ResultDocstring | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.to_dict() if self.type is not None else None,
            "docstring": self.docstring.to_dict() if self.docstring is not None else None,
        }


@dataclass
class Enum:
    id: str
    name: str
    docstring: ClassDocstring
    instances: list[EnumInstance] = field(default_factory=list)

    def to_dict(self):
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

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


ApiElement: TypeAlias = Module | Class | Attribute | Function | Parameter | Result
