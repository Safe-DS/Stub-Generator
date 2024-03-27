from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from griffe.dataclasses import Docstring
from griffe.dataclasses import Docstring as GriffeDocstring
from griffe.docstrings.dataclasses import (
    DocstringAttribute,
    DocstringParameter,
    DocstringSection,
    DocstringSectionAttributes,
    DocstringSectionParameters,
    DocstringSectionReturns,
    DocstringSectionText,
)
from griffe.enumerations import Parser

from ._abstract_docstring_parser import AbstractDocstringParser
from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)
from ._helpers import get_full_docstring, remove_newline_from_text

if TYPE_CHECKING:
    from mypy import nodes

    from safeds_stubgen.api_analyzer import Class


class DocstringParser(AbstractDocstringParser):
    def __init__(self, parser: Parser):
        self.parser = parser
        self.__cached_node: nodes.FuncDef | Class | None = None
        self.__cached_docstring: list[DocstringSection] | None = None

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        docstring = get_full_docstring(class_node)

        griffe_doc = GriffeDocstring(value=docstring, parser=self.parser)
        description = ""
        for docstring_section in griffe_doc.parse(parser=self.parser):
            if isinstance(docstring_section, DocstringSectionText):
                description = docstring_section.value
                break

        return ClassDocstring(
            description=remove_newline_from_text(description),
            full_docstring=remove_newline_from_text(docstring),
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = get_full_docstring(function_node)
        griffe_docstring = self.__get_cached_docstring(function_node, docstring)

        description = ""
        for docstring_section in griffe_docstring:
            if isinstance(docstring_section, DocstringSectionText):
                description = docstring_section.value
                break

        return FunctionDocstring(
            description=remove_newline_from_text(description),
            full_docstring=remove_newline_from_text(docstring),
        )

    def get_parameter_documentation(
        self,
        function_node: nodes.FuncDef,
        parameter_name: str,
        parent_class: Class | None,
    ) -> ParameterDocstring:
        from safeds_stubgen.api_analyzer import Class

        # For constructors (__init__ functions) the parameters are described on the class
        if function_node.name == "__init__" and isinstance(parent_class, Class):
            docstring = parent_class.docstring.full_docstring
        else:
            docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_doc = self.__get_cached_docstring(function_node, docstring)
        matching_parameters = self._get_matching_docstrings(function_doc, parameter_name, "param")

        # For numpy, if we have a constructor we have to check both, the class and then the constructor (see issue
        # https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if self.parser == Parser.numpy and len(matching_parameters) == 0 and function_node.name == "__init__":
            # Get constructor docstring
            docstring_constructor = get_full_docstring(function_node)
            griffe_docstring = GriffeDocstring(value=docstring_constructor, parser=self.parser)

            # Find matching parameter docstrings
            function_doc = griffe_docstring.parse(self.parser)
            matching_parameters = self._get_matching_docstrings(function_doc, parameter_name, "param")

        if len(matching_parameters) == 0:
            return ParameterDocstring()

        last_parameter = matching_parameters[-1]

        if not isinstance(last_parameter, DocstringParameter):  # pragma: no cover
            raise TypeError(f"Expected parameter docstring, got {type(last_parameter)}.")

        annotation = "" if not last_parameter.annotation else str(last_parameter.annotation)

        return ParameterDocstring(
            type=annotation,
            default_value=last_parameter.default or "",
            description=remove_newline_from_text(last_parameter.description) or "",
        )

    def get_attribute_documentation(
        self,
        parent_class: Class,
        attribute_name: str,
    ) -> AttributeDocstring:
        # Find matching attribute docstrings
        function_doc = self.__get_cached_docstring(parent_class, parent_class.docstring.full_docstring)
        if self.parser == Parser.sphinx:
            # ReST does not differentiate between attribute and parameter
            matching_attributes = self._get_matching_docstrings(function_doc, attribute_name, "param")
        else:
            matching_attributes = self._get_matching_docstrings(function_doc, attribute_name, "attr")

        # For Numpydoc, if the class has a constructor we have to check both the class and then the constructor
        # (see issue https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if self.parser == Parser.numpy and len(matching_attributes) == 0:
            griffe_docstring = GriffeDocstring(value=parent_class.constructor_fulldocstring, parser=self.parser)

            # Find matching parameter docstrings
            function_doc = griffe_docstring.parse(self.parser)
            matching_attributes = self._get_matching_docstrings(function_doc, attribute_name, "attr")

        if len(matching_attributes) == 0:
            return AttributeDocstring()

        last_attribute = matching_attributes[-1]
        annotation = "" if not last_attribute.annotation else str(last_attribute.annotation)
        return AttributeDocstring(
            type=annotation,
            default_value=last_attribute.value or "",
            description=remove_newline_from_text(last_attribute.description),
        )

    def get_result_documentation(self, function_node: nodes.FuncDef) -> ResultDocstring:
        docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_doc = self.__get_cached_docstring(function_node, docstring)

        all_returns = None
        for docstring_section in function_doc:
            if isinstance(docstring_section, DocstringSectionReturns):
                all_returns = docstring_section
                break

        if not all_returns:
            return ResultDocstring()

        annotation = "" if not all_returns.value[0].annotation else str(all_returns.value[0].annotation)
        return ResultDocstring(
            type=annotation,
            description=remove_newline_from_text(all_returns.value[0].description),
        )

    @staticmethod
    def _get_matching_docstrings(
        function_doc: list[DocstringSection],
        name: str,
        type_: Literal["attr", "param"],
    ) -> list[DocstringAttribute | DocstringParameter]:
        all_docstrings = None
        for docstring_section in function_doc:
            if (type_ == "attr" and isinstance(docstring_section, DocstringSectionAttributes)) or (
                type_ == "param" and isinstance(docstring_section, DocstringSectionParameters)
            ):
                all_docstrings = docstring_section
                break

        if all_docstrings:
            name = name.lstrip("*")
            return [it for it in all_docstrings.value if it.name.lstrip("*") == name]

        return []

    def __get_cached_docstring(self, node: nodes.FuncDef | Class, docstring: str) -> list[DocstringSection]:
        """
        Return the Docstring for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function get_parameter_documentation when parsing sklearn. Afterward, it was only 2.113s.
        """
        if self.__cached_node is not node or node.name == "__init__":
            self.__cached_node = node
            griffe_docstring = Docstring(value=docstring, parser=self.parser)
            self.__cached_docstring = griffe_docstring.parse(parser=self.parser)

        if self.__cached_docstring is None:  # pragma: no cover
            raise ValueError("Expected a docstring, got None instead.")
        return self.__cached_docstring
