from __future__ import annotations

from typing import TYPE_CHECKING

from docstring_parser import Docstring, DocstringParam, DocstringStyle
from docstring_parser import parse as parse_docstring
from mypy import nodes

from ._abstract_docstring_parser import AbstractDocstringParser
from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)
from ._helpers import get_description, get_full_docstring

if TYPE_CHECKING:
    from safeds_stubgen.api_analyzer import Class, ParameterAssignment


class RestDocParser(AbstractDocstringParser):
    """Parses documentation in the Restdoc format.

    See https://spring.io/projects/spring-restdocs#samples for more information.
    This class is not thread-safe. Each thread should create its own instance.
    """

    def __init__(self) -> None:
        self.__cached_function_node: nodes.FuncDef | None = None
        self.__cached_docstring: DocstringParam | None = None

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        docstring = get_full_docstring(class_node)
        docstring_obj = parse_docstring(docstring, style=DocstringStyle.REST)

        return ClassDocstring(
            description=get_description(docstring_obj),
            full_docstring=docstring,
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = get_full_docstring(function_node)
        docstring_obj = self.__get_cached_function_restdoc_string(function_node, docstring)

        return FunctionDocstring(
            description=get_description(docstring_obj),
            full_docstring=docstring,
        )

    def get_parameter_documentation(
        self,
        function_node: nodes.FuncDef,
        parameter_name: str,
        parameter_assigned_by: ParameterAssignment,  # noqa: ARG002
        parent_class: Class,
    ) -> ParameterDocstring:
        from safeds_stubgen.api_analyzer import Class

        # For constructors (__init__ functions) the parameters are described on the class
        if function_node.name == "__init__" and isinstance(parent_class, Class):
            docstring = parent_class.docstring.full_docstring
        else:
            docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_restdoc = self.__get_cached_function_restdoc_string(function_node, docstring)
        all_parameters_restdoc: list[DocstringParam] = function_restdoc.params
        matching_parameters_restdoc = [
            it for it in all_parameters_restdoc
            if it.arg_name == parameter_name
        ]

        if len(matching_parameters_restdoc) == 0:
            return ParameterDocstring()

        last_parameter_docstring_obj = matching_parameters_restdoc[-1]
        return ParameterDocstring(
            type=last_parameter_docstring_obj.type_name or "",
            default_value=last_parameter_docstring_obj.default or "",
            description=last_parameter_docstring_obj.description,
        )

    def get_attribute_documentation(
        self,
        class_node: nodes.ClassDef,
        attribute_name: str,
    ) -> AttributeDocstring:
        # ReST docstrings do not differentiate between parameter and attributes,
        # therefore we recycle the parameter function
        from safeds_stubgen.api_analyzer import ParameterAssignment, get_classdef_definitions, Class

        function_node = None
        for definition in get_classdef_definitions(class_node):
            if isinstance(definition, nodes.FuncDef) and definition.name == "__init__":
                function_node = definition

        if function_node is not None:
            # ParameterAssignment and parent are unimportant in this case
            class_docs = self.get_class_documentation(class_node)
            fake_parent = Class(
                id="", name="", superclasses=[], is_public=True, docstring=class_docs
            )

            documentation = self.get_parameter_documentation(
                function_node=function_node,
                parameter_name=attribute_name,
                parameter_assigned_by=ParameterAssignment.POSITION_OR_NAME,
                parent_class=fake_parent,
            )

            return AttributeDocstring(
                type=documentation.type,
                default_value=documentation.default_value,
                description=documentation.description,
            )
        return AttributeDocstring()

    def get_result_documentation(self, function_node: nodes.FuncDef, parent_class: Class) -> ResultDocstring:
        from safeds_stubgen.api_analyzer import Class

        if function_node.name == "__init__" and isinstance(parent_class, Class):
            docstring = parent_class.docstring.full_docstring
        else:
            docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_restdoc = self.__get_cached_function_restdoc_string(function_node, docstring)
        function_returns = function_restdoc.returns

        if function_returns is None:
            return ResultDocstring()

        return ResultDocstring(
            type=function_returns.type_name or "",
            description=function_returns.description or "",
        )

    def __get_cached_function_restdoc_string(self, function_node: nodes.FuncDef, docstring: str) -> Docstring:
        """
        Return the RestDocString for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function get_parameter_documentation when parsing sklearn. Afterward, it was only 2.113s.
        """
        if self.__cached_function_node is not function_node:
            self.__cached_function_node = function_node
            self.__cached_docstring = parse_docstring(docstring, style=DocstringStyle.REST)

        return self.__cached_docstring
