from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeAlias

from mypy.types import ProperType

from safeds_stubgen.docstring_parsing import ClassDocstring, FunctionDocstring, ParameterDocstring, \
    ResultDocstring
from ._types import AbstractType, create_type

if TYPE_CHECKING:
    from pathlib import Path

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
        self.attributes_: dict[str, Attribute] | None = None
        self.parameters_: dict[str, Parameter] | None = None
        self.results_: dict[str, Result] | None = None
        self.enums: dict[str, Enum] | None = None

    def add_module(self, module: Module) -> None:
        self.modules[module.id] = module

    def add_class(self, class_: Class) -> None:
        self.classes[class_.id] = class_

    def add_function(self, function: Function) -> None:
        self.functions[function.id] = function

    def add_enum(self, enum: Enum) -> None:
        self.enums[enum.id] = enum

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
        if self.results_ is not None:
            return self.results_
        results_: dict[str, Result] = {}

        for function in self.functions.values():
            for result in function.results:
                result_id = f"{function.id}/{result.name}"
                results_[result_id] = result
        self.results_ = results_
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
                    classes=class_.classes
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
            ] if self.modules is not None else [],
            "classes": [
                class_.to_dict()
                for class_ in sorted(self.classes.values(), key=lambda it: it.id)
            ] if self.classes is not None else [],
            "functions": [
                function.to_dict()
                for function in sorted(self.functions.values(), key=lambda it: it.id)
            ] if self.functions is not None else [],
            "enums": [
                enum.to_dict()
                for enum in sorted(self.enums.values(), key=lambda it: it.id)
            ] if self.enums is not None else [],
        }


# Todo new: added global_attribute
class Module:
    def __init__(
        self, id_: str, name: str, docstring: str = "", qualified_imports=None, wildcard_imports=None,
        global_attributes=None
    ):
        self.id: str = id_
        self.name: str = name
        self.docstring: str = docstring
        self.qualified_imports: list[QualifiedImport] = qualified_imports or []
        self.wildcard_imports: list[WildcardImport] = wildcard_imports or []
        self.global_attributes: list[Attribute] = global_attributes or []
        self.classes: list[Class] = []
        self.global_functions: list[Function] = []
        self.enums: list[Enum] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "docstring": self.docstring,
            "qualified_imports": [import_.qualified_name for import_ in self.qualified_imports],
            "wildcard_imports": [import_.module_name for import_ in self.wildcard_imports],
            "global_attributes": [attribute.id for attribute in self.global_attributes],
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


# Todo Was ist mit selective imports? Ich hab diese erstmal zu den QualifiedImport hinzugefügt (siehe ast visitor)
# Todo Import können auch in Klassen und Funktionen vorkommen -> to handle?
@dataclass
class QualifiedImport:
    qualified_name: str
    alias: str | None

    def __init__(self, qualified_name: str, alias: str | None = ""):
        self.qualified_name = qualified_name
        self.alias = alias or ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "qualified_name": self.qualified_name,
            "alias": self.alias
        }


@dataclass
class WildcardImport:
    module_name: str

    def __init__(self, module_name: str):
        self.module_name = module_name

    def to_dict(self) -> dict[str, Any]:
        return {"module_name": self.module_name}


@dataclass
class Class:
    id: str
    name: str
    superclasses: list[Class]
    is_public: bool
    reexported_by: list[Module]
    docstring: ClassDocstring
    constructor: Function | None = None
    attributes: list[Attribute] = field(default_factory=list)
    methods: list[Function] = field(default_factory=list)
    classes: list[Class] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "qname": self.name,
            "superclasses": self.superclasses,
            "is_public": self.is_public,
            "reexported_by": self.reexported_by,
            "description": self.docstring.description,
            "constructor": self.constructor,
            "attributes": [attribute.id for attribute in self.attributes],
            "methods": [method.id for method in self.methods],
            "classes": [class_.id for class_ in self.classes]
        }

    def add_method(self, method: Function) -> None:
        self.methods.append(method)

    def add_class(self, class_: Class) -> None:
        self.classes.append(class_)


@dataclass(frozen=True)
class Attribute:
    id: str
    name: str
    type: ProperType | None
    is_public: bool = False
    description: str = ""
    is_static: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "types": _get_types(self.type),
            "is_public": self.is_public,
            "description": self.description,
            "is_static": self.is_static
        }


@dataclass(frozen=True)
class Function:
    id: str
    name: str
    reexported_by: list[str]
    docstring: FunctionDocstring
    is_public: bool
    is_static: bool
    parameters: list[Parameter]
    results: list[Result]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "reexported_by": self.reexported_by,
            "description": self.docstring.description,
            "is_public": self.is_public,
            "is_static": self.is_static,
            "parameters": [parameter.id for parameter in self.parameters],
            "results": [result.id for result in self.results],
        }


# Todo assignment kann man auch von mypy bekommen
# Todo Dataclass?
class Parameter:
    def __init__(
        self,
        id_: str,
        name: str,
        default_value: Expression | None,
        assigned_by: ParameterAssignment,
        docstring: ParameterDocstring,
        type_: AbstractType | None,
    ) -> None:
        self.id: str = id_
        self.name: str = name
        self.default_value: Expression | None = default_value
        self.assigned_by: ParameterAssignment = assigned_by
        self.docstring = docstring
        # Todo wie mit type_ arbeiten?
        self.type: AbstractType | None = create_type(docstring.type, docstring.description)

    def is_optional(self) -> bool:
        return self.default_value is not None

    def is_required(self) -> bool:
        return self.default_value is None

    # Todo
    def is_variadic(self): ...

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "default_value": self.default_value,
            "assigned_by": self.assigned_by.name,
            "docstring": self.docstring.to_dict(),
            "type": self.type.to_dict() if self.type is not None else {},
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
    name: str | None
    type_: AbstractType | None
    docstring: ResultDocstring

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type_,
            "docstring": self.docstring.to_dict(),
        }


class Enum:
    id: str
    name: str
    description: str
    instances: list[EnumInstance] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "instances": [instance.id for instance in self.instances],
        }


class EnumInstance:
    id: str


class Expression:
    id: str
    value: str


# Todo
def _get_types(type: ProperType | None):
    return None


# Todo
def dict_to_stub(): ...


# Todo
def dict_to_json(): ...


ApiElement: TypeAlias = Module | Class | Attribute | Function | Parameter | Result
