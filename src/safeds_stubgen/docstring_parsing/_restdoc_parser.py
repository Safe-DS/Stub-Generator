from __future__ import annotations

from typing import TYPE_CHECKING

from docstring_parser import Docstring, DocstringParam
from docstring_parser import DocstringStyle as DP_DocstringStyle
from docstring_parser import parse as parse_docstring

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
    from mypy import nodes

    from safeds_stubgen.api_analyzer import Class, ParameterAssignment


class RestDocParser(AbstractDocstringParser):
    """Parses documentation in the Restdoc format.

    See https://spring.io/projects/spring-restdocs#samples for more information.
    This class is not thread-safe. Each thread should create its own instance.
    """

    def __init__(self) -> None:
        self.__cached_node: nodes.FuncDef | Class | None = None
        self.__cached_docstring: Docstring | None = None

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        docstring = get_full_docstring(class_node)
        docstring_obj = parse_docstring(docstring, style=DP_DocstringStyle.REST)

        return ClassDocstring(
            description=get_description(docstring_obj),
            full_docstring=docstring,
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = get_full_docstring(function_node)
        docstring_obj = self.__get_cached_restdoc_string(function_node, docstring)

        return FunctionDocstring(
            description=get_description(docstring_obj),
            full_docstring=docstring,
        )

    def get_parameter_documentation(
        self,
        function_node: nodes.FuncDef,
        parameter_name: str,
        parameter_assigned_by: ParameterAssignment,  # noqa: ARG002
        parent_class: Class | None,
    ) -> ParameterDocstring:
        from safeds_stubgen.api_analyzer import Class

        # For constructors the parameters are described in the class
        if function_node.name == "__init__" and isinstance(parent_class, Class):
            docstring = parent_class.docstring.full_docstring
        else:
            docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_restdoc = self.__get_cached_restdoc_string(function_node, docstring)
        all_parameters_restdoc: list[DocstringParam] = function_restdoc.params
        matching_parameters_restdoc = [it for it in all_parameters_restdoc if it.arg_name == parameter_name]

        if len(matching_parameters_restdoc) == 0:
            return ParameterDocstring()

        last_parameter_docstring_obj = matching_parameters_restdoc[-1]
        return ParameterDocstring(
            type=last_parameter_docstring_obj.type_name or "",
            default_value=last_parameter_docstring_obj.default or "",
            description=last_parameter_docstring_obj.description or "",
        )

    def get_attribute_documentation(
        self,
        parent_class: Class,
        attribute_name: str,
    ) -> AttributeDocstring:
        # ReST docstrings do not differentiate between parameter and attributes, therefore the parameter and attribute
        #  functions are quite similiar

        # Find matching attribute docstrings
        class_restdoc = self.__get_cached_restdoc_string(parent_class, parent_class.docstring.full_docstring)
        all_attributes_restdoc: list[DocstringParam] = class_restdoc.params
        matching_attributes_restdoc = [it for it in all_attributes_restdoc if it.arg_name == attribute_name]

        if len(matching_attributes_restdoc) == 0:
            return AttributeDocstring()

        last_attribute_docstring_obj = matching_attributes_restdoc[-1]
        return AttributeDocstring(
            type=last_attribute_docstring_obj.type_name or "",
            default_value=last_attribute_docstring_obj.default or "",
            description=last_attribute_docstring_obj.description or "",
        )

    def get_result_documentation(self, function_node: nodes.FuncDef) -> ResultDocstring:
        docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_restdoc = self.__get_cached_restdoc_string(function_node, docstring)
        function_returns = function_restdoc.returns

        if function_returns is None:
            return ResultDocstring()

        return ResultDocstring(
            type=function_returns.type_name or "",
            description=function_returns.description or "",
        )

    def __get_cached_restdoc_string(self, node: nodes.FuncDef | Class, docstring: str) -> Docstring:
        """
        Return the RestDocString for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function get_parameter_documentation when parsing sklearn. Afterward, it was only 2.113s.
        """
        if self.__cached_node is not node or node.name == "__init__":
            self.__cached_node = node
            self.__cached_docstring = parse_docstring(docstring, style=DP_DocstringStyle.REST)

        if self.__cached_docstring is None:  # pragma: no cover
            raise ValueError("Expected a docstring, got None instead.")
        return self.__cached_docstring
