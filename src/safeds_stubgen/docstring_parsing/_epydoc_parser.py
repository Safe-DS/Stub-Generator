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


class EpydocParser(AbstractDocstringParser):
    """Parses documentation in the Epydoc format.

    See https://epydoc.sourceforge.net/epytext.html for more information.
    This class is not thread-safe. Each thread should create its own instance.
    """

    def __init__(self) -> None:
        self.__cached_node: nodes.FuncDef | None = None
        self.__cached_docstring: Docstring | None = None

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        docstring = get_full_docstring(class_node)
        docstring_obj = parse_docstring(docstring, style=DP_DocstringStyle.EPYDOC)

        return ClassDocstring(
            description=get_description(docstring_obj),
            full_docstring=docstring,
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = get_full_docstring(function_node)
        docstring_obj = self.__get_cached_epydoc_string(function_node, docstring)

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

        # For constructors (__init__ functions) the parameters are described on the class
        if function_node.name == "__init__" and isinstance(parent_class, Class):
            docstring = parent_class.docstring.full_docstring
        else:
            docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_epydoc = self.__get_cached_epydoc_string(function_node, docstring)
        all_parameters_epydoc: list[DocstringParam] = function_epydoc.params
        matching_parameters_epydoc = [it for it in all_parameters_epydoc if it.arg_name == parameter_name]

        if len(matching_parameters_epydoc) == 0:
            return ParameterDocstring()

        last_parameter_docstring_obj = matching_parameters_epydoc[-1]
        return ParameterDocstring(
            type=last_parameter_docstring_obj.type_name or "",
            default_value=last_parameter_docstring_obj.default or "",
            description=last_parameter_docstring_obj.description or "",
        )

    # Todo Epydoc: Attribute handling not yet implemented in docstring_parser library
    def get_attribute_documentation(
        self,
        parent_class: Class,  # noqa: ARG002
        attribute_name: str,  # noqa: ARG002
    ) -> AttributeDocstring:
        return AttributeDocstring()

    def get_result_documentation(self, function_node: nodes.FuncDef) -> ResultDocstring:
        docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_epydoc = self.__get_cached_epydoc_string(function_node, docstring)
        function_returns = function_epydoc.returns

        if function_returns is None:
            return ResultDocstring()

        return ResultDocstring(
            type=function_returns.type_name or "",
            description=function_returns.description or "",
        )

    def __get_cached_epydoc_string(self, node: nodes.FuncDef, docstring: str) -> Docstring:
        """
        Return the EpydocString for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function get_parameter_documentation when parsing sklearn. Afterwards, it was only 2.113s.
        """
        if self.__cached_node is not node or node.name == "__init__":
            self.__cached_node = node
            self.__cached_docstring = parse_docstring(docstring, style=DP_DocstringStyle.EPYDOC)

        if self.__cached_docstring is None:  # pragma: no cover
            raise ValueError("Expected a docstring, got None instead.")
        return self.__cached_docstring
