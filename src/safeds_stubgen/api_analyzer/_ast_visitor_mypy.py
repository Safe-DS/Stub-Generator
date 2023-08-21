# TODO Vgl. mit dem alten _ast_visitor.py


import re

import astroid

from ._api import (
    API,
    Class,
    Function,
    Module,
    # QualifiedImport,
    # WildcardImport,
)
from ._names import parent_qualified_name

# from ._file_filters import _is_init_file
from ._get_parameter_list import get_parameter_list
from ..docstring_parsing._abstract_docstring_parser import AbstractDocstringParser


class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.reexported: dict[str, list[str]] = {}
        self.api: API = api
        self.__declaration_stack: list[Module | Class | Function] = []

    def __get_id(self, name: str) -> str:
        segments = [self.api.package]
        segments += [it.name for it in self.__declaration_stack]
        segments += [name]

        return "/".join(segments)

    def __get_function_id(self, name: str, decorators: list[str]) -> str:
        def is_getter() -> bool:
            return "property" in decorators

        def is_setter() -> bool:
            return any(re.search("^[^.]*.setter$", decorator) for decorator in decorators)

        def is_deleter() -> bool:
            return any(re.search("^[^.]*.deleter$", decorator) for decorator in decorators)

        result = self.__get_id(name)

        if is_getter():
            result += "@getter"
        elif is_setter():
            result += "@setter"
        elif is_deleter():
            result += "@deleter"

        return result

    # todo module_node ist der ganze ast vom file.py?
    def enter_module(self, mypy_ast) -> None:
        # imports: list[Import] = []
        # from_imports: list[FromImport] = []
        # visited_global_nodes: set[astroid.NodeNG] = set()
        id_ = f"{self.api.package}/{mypy_ast.fullname}"

        # # todo Brauchen ggf. imports und fromimports nicht mehr
        # # todo for def in defs
        # for definition in mypy_ast.definitions:
        #     definitions = global_node_list[0]
        #
        #     # For some reason from-imports get visited as often as there are imported names, leading to duplicates
        #     if global_node in visited_global_nodes:
        #         continue
        #     visited_global_nodes.add(global_node)
        #
        #     # todo get Imports
        #     if isinstance(definition, astroid.Import):
        #         for name, alias in definition.names:
        #             imports.append(Import(name, alias))
        #
        #     # Todo get ImportFroms
        #     if isinstance(definition, astroid.ImportFrom):
        #         base_import_path = definition.relative_to_absolute_name(definition.modname, definition.level)

        # Remember module, so we can later add classes and global functions
        module = Module(
            id_,
            mypy_ast.fullname
        )
        self.__declaration_stack.append(module)

    def leave_module(self, _: astroid.Module) -> None:
        module = self.__declaration_stack.pop()
        if not isinstance(module, Module):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        self.api.add_module(module)

    def enter_classdef(self, class_node: astroid.ClassDef) -> None:
        id_ = self.__get_id(class_node.name)
        name = class_node.qname()

        # Remember class, so we can later add methods
        class_ = Class(
            id=id_,
            name=name,
            superclasses=class_node.basenames,
            is_public=self.is_public(class_node.name, name),
            reexported_by=self.reexported.get(name, []),
            docstring=self.docstring_parser.get_class_documentation(class_node),
            # Todo
            constructor=None,
            attributes=[],
            methods=[],
            classes=[]
        )
        self.__declaration_stack.append(class_)

    def leave_classdef(self, _: astroid.ClassDef) -> None:
        class_ = self.__declaration_stack.pop()
        if not isinstance(class_, Class):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested classes for now
            if isinstance(parent, Module):
                self.api.add_class(class_)
                parent.add_class(class_)

    def enter_functiondef(self, function_node: astroid.FunctionDef) -> None:
        qname = function_node.qname()

        decorators: astroid.Decorators | None = function_node.decorators
        if decorators is not None:
            decorator_names = [decorator.as_string() for decorator in decorators.nodes]
        else:
            decorator_names = []

        is_public = self.is_public(function_node.name, qname)
        is_static = self.is_static(function_node.name, qname)

        function_id = self.__get_function_id(function_node.name, decorator_names)
        function = Function(
            id=function_id,
            name=qname,
            reexported_by=self.reexported.get(qname, []),
            docstring=self.docstring_parser.get_function_documentation(function_node),
            is_public=is_public,
            is_static=is_static,
            parameters=get_parameter_list(
                self.docstring_parser,
                function_node,
                function_id,
                qname,
                is_public,
            ),
            # Todo
            results=[],
        )
        self.__declaration_stack.append(function)

    # Todo
    def is_static(self, name: str, qualified_name: str) -> bool:
        return True

    def is_public(self, name: str, qualified_name: str) -> bool:
        if name.startswith("_") and not name.endswith("__"):
            return False

        if qualified_name in self.reexported:
            return True

        # Containing class is re-exported (always false if the current API element is not a method)
        if isinstance(self.__declaration_stack[-1], Class) and parent_qualified_name(qualified_name) in self.reexported:
            return True

        # The slicing is necessary so __init__ functions are not excluded (already handled in the first condition).
        return all(not it.startswith("_") for it in qualified_name.split(".")[:-1])


def is_public_module(module_name: str) -> bool:
    return all(not it.startswith("_") for it in module_name.split("."))


def trim_code(code: str | None, from_line_no: int, to_line_no: int, encoding: str) -> str:
    if code is None:
        return ""
    if isinstance(code, bytes):
        code = code.decode(encoding)
    lines = code.split("\n")
    return "\n".join(lines[from_line_no - 1 : to_line_no])
