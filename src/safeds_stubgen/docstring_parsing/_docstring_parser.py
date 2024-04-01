from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from griffe import load
from griffe.docstrings.dataclasses import DocstringAttribute, DocstringParameter
from griffe.enumerations import DocstringSectionKind, Parser

from ._abstract_docstring_parser import AbstractDocstringParser
from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)
from ._helpers import remove_newline_from_text

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring, Object
    from griffe.docstrings.dataclasses import DocstringSection
    from mypy import nodes
    from pathlib import Path
    from safeds_stubgen.api_analyzer import Class


class DocstringParser(AbstractDocstringParser):
    def __init__(self, parser: Parser, package_path: Path):
        while True:
            try:
                self.griffe_build = load(package_path, docstring_parser=parser)
                break
            except KeyError:
                package_path = package_path.parent

        self.parser = parser
        self.__cached_node: nodes.FuncDef | Class | None = None
        self.__cached_docstring: list[DocstringSection] | None = None

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        griffe_node = self._get_griffe_node(class_node.fullname)

        if griffe_node is None:  # pragma: no cover
            raise TypeError(f"Expected a griffe node for {class_node.fullname}, got None.")

        description = ""
        docstring = ""
        if griffe_node.docstring is not None:
            docstring = griffe_node.docstring.value

            for docstring_section in griffe_node.docstring.parsed:
                if docstring_section.kind == DocstringSectionKind.text:
                    description = docstring_section.value
                    break

        return ClassDocstring(
            description=remove_newline_from_text(description),
            full_docstring=remove_newline_from_text(docstring),
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = ""
        description = ""
        griffe_docstring = self.__get_cached_docstring(function_node.fullname)
        if griffe_docstring is not None:
            docstring = griffe_docstring.value
            for docstring_section in griffe_docstring.parsed:
                if docstring_section.kind == DocstringSectionKind.text:
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
        # For constructors (__init__ functions) the parameters are described on the class
        if function_node.name == "__init__" and parent_class is not None:
            parent_qname = parent_class.id.replace("/", ".")
            griffe_docstring = self.__get_cached_docstring(parent_qname)
        else:
            griffe_docstring = self.__get_cached_docstring(function_node.fullname)

        # Find matching parameter docstrings
        matching_parameters = []
        if griffe_docstring is not None:
            matching_parameters = self._get_matching_docstrings(griffe_docstring, parameter_name, "param")

        # For numpy, if we have a constructor we have to check both, the class and then the constructor (see issue
        # https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if self.parser == Parser.numpy and len(matching_parameters) == 0 and function_node.name == "__init__":
            # Get constructor docstring & find matching parameter docstrings
            constructor_docstring = self.__get_cached_docstring(function_node.fullname)
            if constructor_docstring is not None:
                matching_parameters = self._get_matching_docstrings(constructor_docstring, parameter_name, "param")

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
        parent_class_qname: str,
        attribute_name: str,
    ) -> AttributeDocstring:
        parent_class_qname = parent_class_qname.replace("/", ".")

        # Find matching attribute docstrings
        parent_qname = parent_class_qname
        griffe_docstring = self.__get_cached_docstring(parent_qname)
        if griffe_docstring is None:
            matching_attributes = []
        elif self.parser == Parser.sphinx:
            # ReST does not differentiate between parameterd and attributes
            matching_attributes = self._get_matching_docstrings(griffe_docstring, attribute_name, "param")
        else:
            matching_attributes = self._get_matching_docstrings(griffe_docstring, attribute_name, "attr")

        # For Numpydoc, if the class has a constructor we have to check both the class and then the constructor
        # (see issue https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if self.parser == Parser.numpy and len(matching_attributes) == 0:
            constructor_qname = f"{parent_class_qname}.__init__"
            constructor_docstring = self.__get_cached_docstring(constructor_qname)

            # Find matching parameter docstrings
            if constructor_docstring is not None:
                matching_attributes = self._get_matching_docstrings(constructor_docstring, attribute_name, "attr")

        if len(matching_attributes) == 0:
            return AttributeDocstring()

        last_attribute = matching_attributes[-1]
        annotation = "" if not last_attribute.annotation else str(last_attribute.annotation)
        return AttributeDocstring(
            type=annotation,
            description=remove_newline_from_text(last_attribute.description),
        )

    # Todo handle multiple results
    def get_result_documentation(self, function_qname: str) -> ResultDocstring:
        # Find matching parameter docstrings
        griffe_docstring = self.__get_cached_docstring(function_qname)

        if griffe_docstring is None:
            return ResultDocstring()

        all_returns = None
        for docstring_section in griffe_docstring.parsed:
            if docstring_section.kind == DocstringSectionKind.returns:
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
        function_doc: Docstring,
        name: str,
        type_: Literal["attr", "param"],
    ) -> list[DocstringAttribute | DocstringParameter]:
        all_docstrings = None
        for docstring_section in function_doc.parsed:
            section_kind = docstring_section.kind
            if (type_ == "attr" and section_kind == DocstringSectionKind.attributes) or (
                type_ == "param" and section_kind == DocstringSectionKind.parameters
            ):
                all_docstrings = docstring_section
                break

        if all_docstrings:
            name = name.lstrip("*")
            return [it for it in all_docstrings.value if it.name.lstrip("*") == name]

        return []

    def _get_griffe_node(self, qname: str) -> Object | None:
        node_qname_parts = qname.split(".")
        griffe_node = self.griffe_build
        for part in node_qname_parts:
            if griffe_node.name == part:
                continue

            if part in griffe_node.modules:
                griffe_node = griffe_node.modules[part]
            elif part in griffe_node.classes:
                griffe_node = griffe_node.classes[part]
            elif part in griffe_node.functions:
                griffe_node = griffe_node.functions[part]
            elif part in griffe_node.attributes:
                griffe_node = griffe_node.attributes[part]
            elif part == "__init__" and griffe_node.is_class:
                return None
            else:
                raise ValueError(f"Something went wrong while searching for the docstring for {qname}. Please make sure"
                                 " that all directories with python files have an __init__.py file.")

        return griffe_node

    def __get_cached_docstring(self, qname: str) -> Docstring | None:
        """
        Return the Docstring for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function get_parameter_documentation when parsing sklearn. Afterward, it was only 2.113s.
        """
        if self.__cached_node != qname or qname.endswith("__init__"):
            self.__cached_node = qname

            griffe_node = self._get_griffe_node(qname)
            if griffe_node is not None:
                griffe_docstring = griffe_node.docstring
                self.__cached_docstring = griffe_docstring
            else:
                self.__cached_docstring = None

        return self.__cached_docstring
