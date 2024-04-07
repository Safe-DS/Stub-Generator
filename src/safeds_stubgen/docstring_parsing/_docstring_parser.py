from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from griffe import load
from griffe.dataclasses import Docstring
from griffe.docstrings.dataclasses import DocstringAttribute, DocstringParameter
from griffe.docstrings.utils import parse_annotation
from griffe.enumerations import DocstringSectionKind, Parser
from griffe.expressions import Expr, ExprName, ExprSubscript, ExprTuple

# noinspection PyProtectedMember
import safeds_stubgen.api_analyzer._types as sds_types

from ._abstract_docstring_parser import AbstractDocstringParser
from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
    ResultDocstrings,
)

if TYPE_CHECKING:
    from pathlib import Path

    from griffe.dataclasses import Object
    from mypy import nodes

    from safeds_stubgen.api_analyzer import AbstractType


class DocstringParser(AbstractDocstringParser):
    def __init__(self, parser: Parser, package_path: Path):
        while True:
            try:
                self.griffe_build = load(package_path, docstring_parser=parser)
                break
            except KeyError:
                package_path = package_path.parent

        self.parser = parser
        self.__cached_node: str | None = None
        self.__cached_docstring: Docstring | None = None

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        griffe_node = self._get_griffe_node(class_node.fullname)

        if griffe_node is None:  # pragma: no cover
            raise TypeError(f"Expected a griffe node for {class_node.fullname}, got None.")

        description = ""
        docstring = ""
        if griffe_node.docstring is not None:
            docstring = griffe_node.docstring.value.strip("\n")

            for docstring_section in griffe_node.docstring.parsed:
                if docstring_section.kind == DocstringSectionKind.text:
                    description = docstring_section.value.strip("\n")
                    break

        return ClassDocstring(
            description=description,
            full_docstring=docstring,
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = ""
        description = ""
        griffe_docstring = self.__get_cached_docstring(function_node.fullname)
        if griffe_docstring is not None:
            docstring = griffe_docstring.value.strip("\n")
            for docstring_section in griffe_docstring.parsed:
                if docstring_section.kind == DocstringSectionKind.text:
                    description = docstring_section.value.strip("\n")
                    break

        return FunctionDocstring(
            description=description,
            full_docstring=docstring,
        )

    def get_parameter_documentation(
        self,
        function_qname: str,
        parameter_name: str,
        parent_class_qname: str,
    ) -> ParameterDocstring:
        function_name = function_qname.split(".")[-1]

        # For constructors (__init__ functions) the parameters are described on the class
        if function_name == "__init__" and parent_class_qname:
            parent_qname = parent_class_qname.replace("/", ".")
            griffe_docstring = self.__get_cached_docstring(parent_qname)
        else:
            griffe_docstring = self.__get_cached_docstring(function_qname)

        # Find matching parameter docstrings
        matching_parameters = []
        if griffe_docstring is not None:
            matching_parameters = self._get_matching_docstrings(griffe_docstring, parameter_name, "param")

        # For numpy, if we have a constructor we have to check both, the class and then the constructor (see issue
        # https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if self.parser == Parser.numpy and len(matching_parameters) == 0 and function_name == "__init__":
            # Get constructor docstring & find matching parameter docstrings
            constructor_docstring = self.__get_cached_docstring(function_qname)
            if constructor_docstring is not None:
                matching_parameters = self._get_matching_docstrings(constructor_docstring, parameter_name, "param")

        if len(matching_parameters) == 0:
            return ParameterDocstring()

        last_parameter = matching_parameters[-1]

        if not isinstance(last_parameter, DocstringParameter):  # pragma: no cover
            raise TypeError(f"Expected parameter docstring, got {type(last_parameter)}.")

        if griffe_docstring is None:  # pragma: no cover
            griffe_docstring = Docstring("")

        annotation = last_parameter.annotation
        if annotation is None:
            type_ = None
        else:
            type_ = self._griffe_annotation_to_api_type(annotation, griffe_docstring)

        return ParameterDocstring(
            type=type_,
            default_value=last_parameter.default or "",
            description=last_parameter.description.strip("\n") or "",
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
            griffe_docstring = Docstring("")
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

        annotation = last_attribute.annotation
        if annotation is None:
            type_ = None
        else:
            type_ = self._griffe_annotation_to_api_type(annotation, griffe_docstring)

        return AttributeDocstring(
            type=type_,
            description=last_attribute.description.strip("\n"),
        )

    def get_result_documentation(self, function_qname: str) -> ResultDocstrings:
        # Find matching parameter docstrings
        griffe_docstring = self.__get_cached_docstring(function_qname)

        if griffe_docstring is None:
            return ResultDocstrings(docstrings=[])

        all_returns = None
        for docstring_section in griffe_docstring.parsed:
            if docstring_section.kind == DocstringSectionKind.returns:
                all_returns = docstring_section
                break

        if not all_returns:
            return ResultDocstrings(docstrings=[])

        # Multiple results are handled differently for numpy, since there we can define multiple named results.
        if self.parser == Parser.numpy:
            results = [
                ResultDocstring(
                    type=self._griffe_annotation_to_api_type(result.annotation, griffe_docstring),
                    description=result.description.strip("\n"),
                    name=result.name or "",
                )
                for result in all_returns.value
            ]
        else:
            return_value = all_returns.value[0]
            # If a GoogleDoc result docstring only has a type and no name Griffe parses it wrong and saves the
            # type as the name...
            if self.parser == Parser.google and return_value.annotation is None:
                annotation = return_value.name
            else:
                annotation = return_value.annotation

            results = [
                ResultDocstring(
                    type=self._griffe_annotation_to_api_type(annotation, griffe_docstring),
                    description=return_value.description.strip("\n"),
                ),
            ]

        return ResultDocstrings(docstrings=results)

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

    def _griffe_annotation_to_api_type(self, annotation: Expr | str, docstring: Docstring) -> AbstractType:
        if isinstance(annotation, ExprName):
            if annotation.canonical_path == "typing.Any":
                return sds_types.NamedType(name="Any", qname="typing.Any")
            elif annotation.canonical_path == "int":
                return sds_types.NamedType(name="int", qname="builtins.int")
            elif annotation.canonical_path == "bool":
                return sds_types.NamedType(name="bool", qname="builtins.bool")
            elif annotation.canonical_path == "float":
                return sds_types.NamedType(name="float", qname="builtins.float")
            elif annotation.canonical_path == "str":
                return sds_types.NamedType(name="str", qname="builtins.str")
            elif annotation.canonical_path == "list":
                return sds_types.ListType(types=[])
            elif annotation.canonical_path == "tuple":
                return sds_types.TupleType(types=[])
            elif annotation.canonical_path == "set":
                return sds_types.SetType(types=[])
            else:
                return sds_types.NamedType(name=annotation.canonical_name, qname=annotation.canonical_path)
        elif isinstance(annotation, ExprSubscript):
            slices = annotation.slice
            if isinstance(slices, ExprTuple):
                types = []
                for slice_ in slices.elements:
                    new_type = self._griffe_annotation_to_api_type(slice_, docstring)
                    types.append(new_type)
            else:
                types = []
                type_ = self._griffe_annotation_to_api_type(slices, docstring)
                if type_ is not None:
                    types.append(type_)

            if annotation.canonical_path == "list":
                return sds_types.ListType(types=types)
            elif annotation.canonical_path == "tuple":
                return sds_types.TupleType(types=types)
            elif annotation.canonical_path == "set":
                return sds_types.SetType(types=types)
            elif annotation.canonical_path == "typing.Optional":
                types.append(sds_types.NamedType(name="None", qname="builtins.None"))
                return sds_types.UnionType(types=types)
            else:  # pragma: no cover
                raise TypeError(f"Can't parse unexpected type from docstring {annotation.canonical_path}.")
        elif isinstance(annotation, ExprTuple):
            elements = []
            # Todo Remove the "optional" related part of the code once issue #99 is solved.
            has_optional = False
            for element in annotation.elements:
                if not isinstance(element, str) and element.canonical_path == "optional":
                    has_optional = True
                else:
                    new_element = self._griffe_annotation_to_api_type(element, docstring)
                    if new_element is None:  # pragma: no cover
                        continue
                    elements.append(new_element)
            if has_optional:
                elements.append(sds_types.NamedType(name="None", qname="builtins.None"))
                return sds_types.UnionType(elements)
            else:
                return sds_types.TupleType(elements)
        elif isinstance(annotation, str):
            new_annotation = self._remove_default_from_griffe_annotation(annotation)
            parsed_annotation = parse_annotation(new_annotation, docstring)
            if parsed_annotation in (new_annotation, annotation):
                if parsed_annotation == "None":
                    return sds_types.NamedType(name="None", qname="builtins.None")
                else:  # pragma: no cover
                    raise TypeError(
                        f"Can't parse unexpected type from docstring {parsed_annotation}. We received a "
                        f"str type, but we expected a Griffe object.",
                    )
            else:
                return self._griffe_annotation_to_api_type(parsed_annotation, docstring)
        else:  # pragma: no cover
            raise TypeError(
                f"Can't parse unexpected type from docstring: {annotation}. This case is not handled by us"
                f"(yet), please report this.",
            )

    def _remove_default_from_griffe_annotation(self, annotation: str) -> str:
        if self.parser == Parser.numpy:
            return annotation.split(", default")[0]
        return annotation

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
            else:  # pragma: no cover
                raise ValueError(
                    f"Something went wrong while searching for the docstring for {qname}. Please make sure"
                    " that all directories with python files have an __init__.py file.",
                )

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
