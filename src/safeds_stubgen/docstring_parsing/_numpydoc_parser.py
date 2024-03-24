from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.dataclasses import Docstring
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

    from safeds_stubgen.api_analyzer import Class, ParameterAssignment


class NumpyDocParser(AbstractDocstringParser):
    """
    Parse documentation in the NumpyDoc format.

    Notes
    -----
    This class is not thread-safe. Each thread should create its own instance.

    References
    ----------
    ... [1] https://numpydoc.readthedocs.io/en/latest/format.html
    """

    def __init__(self) -> None:
        self.__cached_node: nodes.FuncDef | Class | None = None
        self.__cached_docstring: Docstring | None = None

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        docstring = get_full_docstring(class_node)

        griffe_doc = Docstring(value=docstring, parser=Parser.numpy)
        description = ""
        for docstring_section in griffe_doc.parse("numpy"):
            if isinstance(docstring_section, DocstringSectionText):
                description = docstring_section.value
                break

        return ClassDocstring(
            description=remove_newline_from_text(description),
            full_docstring=remove_newline_from_text(docstring),
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = get_full_docstring(function_node)

        griffe_doc = Docstring(value=docstring, parser=Parser.numpy)
        description = ""
        for docstring_section in griffe_doc.parse("numpy"):
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
        function_numpydoc = self.__get_cached_numpydoc_string(function_node, docstring)
        all_parameters_numpydoc = None
        for docstring_section in function_numpydoc:
            if isinstance(docstring_section, DocstringSectionParameters):
                all_parameters_numpydoc = docstring_section
                break

        matching_parameters_numpydoc: list[DocstringParameter] = []
        if all_parameters_numpydoc:
            matching_parameters_numpydoc = [
                it for it in all_parameters_numpydoc.value if it.name.lstrip("*") == parameter_name
            ]

        if len(matching_parameters_numpydoc) == 0:
            # If we have a constructor we have to check both, the class and then the constructor (see issue
            # https://github.com/Safe-DS/Library-Analyzer/issues/10)
            if function_node.name == "__init__":
                docstring_constructor = get_full_docstring(function_node)
                griffe_docstring = Docstring(value=docstring_constructor, parser=Parser.numpy)

                # Find matching parameter docstrings
                function_numpydoc = griffe_docstring.parse("numpy")
                all_parameters_numpydoc = None
                for docstring_section in function_numpydoc:
                    if isinstance(docstring_section, DocstringSectionParameters):
                        all_parameters_numpydoc = docstring_section
                        break

                # Overwrite previous matching_parameters_numpydoc list
                if all_parameters_numpydoc:
                    matching_parameters_numpydoc = [
                        it for it in all_parameters_numpydoc.value if it.name == parameter_name
                    ]

            if len(matching_parameters_numpydoc) == 0:
                return ParameterDocstring(type="", default_value="", description="")

        last_parameter_numpydoc = matching_parameters_numpydoc[-1]
        return ParameterDocstring(
            type=last_parameter_numpydoc.annotation or "",
            default_value=last_parameter_numpydoc.default or "",
            description=remove_newline_from_text(last_parameter_numpydoc.description),
        )

    def get_attribute_documentation(
        self,
        parent_class: Class,
        attribute_name: str,
    ) -> AttributeDocstring:
        # Find matching attribute docstrings
        function_numpydoc = self.__get_cached_numpydoc_string(parent_class, parent_class.docstring.full_docstring)

        all_attributes_numpydoc = None
        for docstring_section in function_numpydoc:
            if isinstance(docstring_section, DocstringSectionAttributes):
                all_attributes_numpydoc = docstring_section
                break

        matching_attributes_numpydoc: list[DocstringAttribute] = []
        if all_attributes_numpydoc:
            matching_attributes_numpydoc = [
                it for it in all_attributes_numpydoc.value if it.name == attribute_name
            ]

        # If the class has a constructor we have to check both the class and then the constructor
        # (see issue https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if len(matching_attributes_numpydoc) == 0:
            griffe_docstring = Docstring(parent_class.constructor_fulldocstring, parser=Parser.numpy)

            # Find matching parameter docstrings
            function_numpydoc = griffe_docstring.parse("numpy")
            all_attributes_numpydoc = []
            for docstring_section in function_numpydoc:
                if isinstance(docstring_section, DocstringSectionAttributes):
                    all_attributes_numpydoc = docstring_section
                    break

            # Overwrite previous matching_parameters_numpydoc list
            matching_attributes_numpydoc = [it for it in all_attributes_numpydoc if it.name == attribute_name]

            if len(matching_attributes_numpydoc) == 0:
                return AttributeDocstring(type="", default_value="", description="")

        last_attribute_numpydoc = matching_attributes_numpydoc[-1]
        return AttributeDocstring(
            type=last_attribute_numpydoc.annotation or "",
            default_value=last_attribute_numpydoc.value or "",
            description=remove_newline_from_text(last_attribute_numpydoc.description),
        )

    def get_result_documentation(self, function_node: nodes.FuncDef) -> ResultDocstring:
        docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_numpydoc = self.__get_cached_numpydoc_string(function_node, docstring)

        all_returns = None
        for docstring_section in function_numpydoc:
            if isinstance(docstring_section, DocstringSectionReturns):
                all_returns = docstring_section
                break

        if not all_returns:
            return ResultDocstring()

        return ResultDocstring(
            type=all_returns.value[0].annotation or "",
            description=remove_newline_from_text(all_returns.value[0].description),
        )

    def __get_cached_numpydoc_string(self, node: nodes.FuncDef | Class, docstring: str) -> list[DocstringSection]:
        """
        Return the NumpyDocString for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function `get_parameter_documentation` when parsing sklearn. Afterward, it was only 2.113s.
        """
        if self.__cached_node is not node or node.name == "__init__":
            self.__cached_node = node
            griffe_docstring = Docstring(value=docstring, parser=Parser.numpy)
            self.__cached_docstring = griffe_docstring.parse(parser=Parser.numpy)

        if self.__cached_docstring is None:  # pragma: no cover
            raise ValueError("Expected a docstring, got None instead.")
        return self.__cached_docstring
