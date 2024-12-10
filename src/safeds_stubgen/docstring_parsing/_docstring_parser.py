from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from _griffe import models as griffe_models
from griffe import load
from griffe import Docstring
from griffe import DocstringAttribute, DocstringParameter
from griffe import parse_docstring_annotation
from griffe import DocstringSectionKind, Parser
from griffe import Expr, ExprAttribute, ExprBinOp, ExprBoolOp, ExprList, ExprName, ExprSubscript, ExprTuple
from griffe.docstrings.utils import parse_annotation

# noinspection PyProtectedMember
import safeds_stubgen.api_analyzer._types as sds_types

from ._abstract_docstring_parser import AbstractDocstringParser
from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)

if TYPE_CHECKING:
    from pathlib import Path
    from mypy import nodes


class DocstringParser(AbstractDocstringParser):
    def __init__(self, parser: Parser, package_path: Path):
        self.parser = parser

        while True:
            # If a package has no __init__.py file Griffe can't parse it, therefore we check the parent
            try:
                griffe_build = load(package_path, docstring_parser=parser)
                break
            except KeyError:
                package_path = package_path.parent

        self.griffe_index: dict[str, griffe_models.Object] = {}
        self._recursive_griffe_indexer(griffe_build)

    def _recursive_griffe_indexer(self, griffe_build: griffe_models.Object | griffe_models.Alias) -> None:
        for member in griffe_build.all_members.values():
            if isinstance(
                member,
                griffe_models.Class | griffe_models.Function | griffe_models.Attribute | griffe_models.Alias
            ):
                self.griffe_index[member.path] = member

            if isinstance(member, griffe_models.Module | griffe_models.Class):
                self._recursive_griffe_indexer(member)

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        griffe_node = self.griffe_index[class_node.fullname] if class_node.fullname in self.griffe_index else None

        if griffe_node is None:  # pragma: no cover
            msg = (
                f"Something went wrong while searching for the docstring for {class_node.fullname}. Please make sure"
                " that all directories with python files have an __init__.py file.",
            )
            logging.warning(msg)

        description = ""
        docstring = ""
        examples = []
        if griffe_node is not None and griffe_node.docstring is not None:
            docstring = griffe_node.docstring.value.strip("\n")

            try:
                for docstring_section in griffe_node.docstring.parsed:
                    if docstring_section.kind == DocstringSectionKind.text:
                        description = docstring_section.value.strip("\n")
                    elif docstring_section.kind == DocstringSectionKind.examples:
                        for example_data in docstring_section.value:
                            examples.append(example_data[1].strip("\n"))
            except IndexError as _:  # pragma: no cover
                msg = f"There was an error while parsing the following docstring:\n{docstring}."
                logging.warning(msg)

        return ClassDocstring(
            description=description,
            full_docstring=docstring,
            examples=examples,
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = ""
        description = ""
        examples = []
        griffe_docstring = self._get_griffe_docstring(function_node.fullname)
        if griffe_docstring is not None:
            docstring = griffe_docstring.value.strip("\n")

            try:
                for docstring_section in griffe_docstring.parsed:
                    if docstring_section.kind == DocstringSectionKind.text:
                        if description:
                            description += "\n\n"
                        description += docstring_section.value.strip("\n")
                    elif docstring_section.kind == DocstringSectionKind.examples:
                        for example_data in docstring_section.value:
                            examples.append(example_data[1].strip("\n"))
            except IndexError as _:  # pragma: no cover
                msg = f"There was an error while parsing the following docstring:\n{docstring}."
                logging.warning(msg)

        return FunctionDocstring(
            description=description,
            full_docstring=docstring,
            examples=examples,
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
            griffe_docstring = self._get_griffe_docstring(parent_qname)
        else:
            griffe_docstring = self._get_griffe_docstring(function_qname)

        # Find matching parameter docstrings
        matching_parameters = []
        if griffe_docstring is not None:
            matching_parameters = self._get_matching_docstrings(griffe_docstring, parameter_name, "param")

        # For numpy, if we have a constructor we have to check both, the class and then the constructor (see issue
        # https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if self.parser == Parser.numpy and len(matching_parameters) == 0 and function_name == "__init__":
            # Get constructor docstring & find matching parameter docstrings
            constructor_docstring = self._get_griffe_docstring(function_qname)
            if constructor_docstring is not None:
                matching_parameters = self._get_matching_docstrings(constructor_docstring, parameter_name, "param")

        if len(matching_parameters) == 0:
            return ParameterDocstring()

        last_parameter = matching_parameters[-1]

        if not isinstance(last_parameter, DocstringParameter):  # pragma: no cover
            raise TypeError(f"Expected parameter docstring, got {type(last_parameter)}.")

        if griffe_docstring is None:  # pragma: no cover
            griffe_docstring = griffe_models.Docstring("")

        annotation = last_parameter.annotation
        if annotation is None:
            type_ = None
        else:
            type_ = self._griffe_annotation_to_api_type(annotation, griffe_docstring)

        default_value = ""
        if last_parameter.default:
            default_value = str(last_parameter.default)

        type_string = ""
        if isinstance(last_parameter.annotation, Expr):
           type_string = last_parameter.annotation.canonical_name
        if isinstance(last_parameter.annotation, str):
            type_string = last_parameter.annotation
        return ParameterDocstring(
            type=type_,  # type from docstring
            default_value=default_value,
            type_string=type_string,
            description=last_parameter.description.strip("\n") or "",
        )

    def get_attribute_documentation(self, parent_class_qname: str, attribute_name: str) -> AttributeDocstring:
        parent_class_qname = parent_class_qname.replace("/", ".")

        # Find matching attribute docstrings
        parent_qname = parent_class_qname
        griffe_docstring = self._get_griffe_docstring(parent_qname)
        if griffe_docstring is None:
            matching_attributes = []
            griffe_docstring = griffe_models.Docstring("")
        else:
            matching_attributes = self._get_matching_docstrings(griffe_docstring, attribute_name, "attr")

        # For Numpydoc, if the class has a constructor we have to check both the class and then the constructor
        # (see issue https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if self.parser == Parser.numpy and len(matching_attributes) == 0:
            constructor_qname = f"{parent_class_qname}.__init__"
            constructor_docstring = self._get_griffe_docstring(constructor_qname)

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
        
        type_string = ""
        if isinstance(last_attribute.annotation, Expr):
           type_string = last_attribute.annotation.canonical_name
        if isinstance(last_attribute.annotation, str):
            type_string = last_attribute.annotation
        return AttributeDocstring(
            type=type_,
            type_string=type_string,
            description=last_attribute.description.strip("\n"),
        )

    def get_result_documentation(self, function_qname: str) -> list[ResultDocstring]:
        # Find matching parameter docstrings
        griffe_docstring = self._get_griffe_docstring(function_qname)

        if griffe_docstring is None:
            return []

        all_returns = None
        try:
            for docstring_section in griffe_docstring.parsed:
                if docstring_section.kind == DocstringSectionKind.returns:
                    all_returns = docstring_section
                    break
        except IndexError as _:  # pragma: no cover
            msg = f"There was an error while parsing the following docstring:\n{griffe_docstring.value}."
            logging.warning(msg)
            return []

        if not all_returns:
            return []

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

            type_ = None
            if annotation:
                type_ = self._griffe_annotation_to_api_type(annotation, griffe_docstring)

            results = [
                ResultDocstring(
                    type=type_,
                    description=return_value.description.strip("\n"),
                ),
            ]

        return results

    @staticmethod
    def _get_matching_docstrings(
        function_doc: griffe_models.Docstring,
        name: str,
        type_: Literal["attr", "param"],
    ) -> list[DocstringAttribute | DocstringParameter]:
        all_docstrings = None
        try:
            for docstring_section in function_doc.parsed:
                section_kind = docstring_section.kind
                if (type_ == "attr" and section_kind == DocstringSectionKind.attributes) or (
                    type_ == "param" and section_kind == DocstringSectionKind.parameters
                ):
                    all_docstrings = docstring_section
                    break
        except IndexError as _:  # pragma: no cover
            msg = f"There was an error while parsing the following docstring:\n{function_doc.value}."
            logging.warning(msg)
            return []

        if all_docstrings:
            name = name.lstrip("*")
            return [it for it in all_docstrings.value if it.name.lstrip("*") == name]

        return []

    def _griffe_annotation_to_api_type(
        self,
        annotation: Expr | str,
        docstring: griffe_models.Docstring,
    ) -> sds_types.AbstractType | None:
        if isinstance(annotation, ExprName | ExprAttribute):
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
            elif annotation.canonical_path == "bytes":
                return sds_types.NamedType(name="bytes", qname="builtins.bytes")
            elif annotation.canonical_path == "list":
                return sds_types.ListType(types=[])
            elif annotation.canonical_path == "tuple":
                return sds_types.TupleType(types=[])
            elif annotation.canonical_path == "set":
                return sds_types.SetType(types=[])
            return sds_types.NamedType(name=annotation.canonical_name, qname=annotation.canonical_path)
        elif isinstance(annotation, ExprSubscript):
            any_type = sds_types.NamedType(name="Any", qname="typing.Any")
            slices = annotation.slice
            types: list[sds_types.AbstractType] = []
            if isinstance(slices, ExprTuple):
                for slice_ in slices.elements:
                    new_type = self._griffe_annotation_to_api_type(slice_, docstring)
                    if new_type is not None:
                        types.append(new_type)
            else:
                type_ = self._griffe_annotation_to_api_type(slices, docstring)
                if type_ is not None:
                    types.append(type_)

            if annotation.canonical_path in {"list", "collections.abc.Sequence", "collections.abc.Iterator"}:
                return sds_types.ListType(types=types)
            elif annotation.canonical_path == "tuple":
                return sds_types.TupleType(types=types)
            elif annotation.canonical_path == "set":
                return sds_types.SetType(types=types)
            elif annotation.canonical_path in {"collections.abc.Callable", "typing.Callable"}:
                param_type = types[0] if len(types) >= 1 else [any_type]
                if not isinstance(param_type, sds_types.AbstractType):  # pragma: no cover
                    msg = f"Expected AbstractType object, received {type(param_type)}. Added unknown type instead."
                    logging.warning(msg)
                    return sds_types.UnknownType()
                parameter_types = param_type.types if isinstance(param_type, sds_types.ListType) else [param_type]
                return_type = types[1] if len(types) >= 2 else any_type
                return sds_types.CallableType(parameter_types=parameter_types, return_type=return_type)
            elif annotation.canonical_path in {"dict", "collections.abc.Mapping", "typing.Mapping"}:
                key_type = types[0] if len(types) >= 1 else any_type
                value_type = types[1] if len(types) >= 2 else any_type
                return sds_types.DictType(key_type=key_type, value_type=value_type)
            elif annotation.canonical_path == "typing.Optional":
                types.append(sds_types.NamedType(name="None", qname="builtins.None"))
                return sds_types.UnionType(types=types)
            else:
                return sds_types.NamedSequenceType(
                    name=annotation.canonical_name,
                    qname=annotation.canonical_path,
                    types=types,
                )
        elif isinstance(annotation, ExprList):
            elements = []
            for element in annotation.elements:
                annotation_element = self._griffe_annotation_to_api_type(element, docstring)
                if annotation_element is not None:
                    elements.append(annotation_element)
            return sds_types.ListType(types=elements)
        elif isinstance(annotation, ExprBoolOp):
            types = []
            for value in annotation.values:
                value_type_ = self._griffe_annotation_to_api_type(value, docstring)
                if value_type_ is not None:
                    types.append(value_type_)
            return sds_types.UnionType(types=types)
        elif isinstance(annotation, ExprTuple):
            elements = []
            # Todo Remove the "optional" related part of the code once issue #99 is solved.
            has_optional = False
            for element_ in annotation.elements:
                if not isinstance(element_, str) and element_.canonical_path == "optional":
                    has_optional = True
                else:
                    new_element = self._griffe_annotation_to_api_type(element_, docstring)
                    if new_element is not None:
                        elements.append(new_element)
            if has_optional:
                elements.append(sds_types.NamedType(name="None", qname="builtins.None"))
                return sds_types.UnionType(elements)
            return sds_types.TupleType(elements)
        elif isinstance(annotation, str):
            new_annotation = self._remove_default_from_griffe_annotation(annotation)
            parsed_annotation = parse_docstring_annotation(new_annotation, docstring)
            if parsed_annotation in (new_annotation, annotation):
                if parsed_annotation == "None":
                    return sds_types.NamedType(name="None", qname="builtins.None")
                else:
                    return None
            else:
                return self._griffe_annotation_to_api_type(parsed_annotation, docstring)
        elif isinstance(annotation, ExprBinOp):
            type_ = self._griffe_annotation_to_api_type(annotation.right, docstring)
            types = [type_] if type_ is not None else []
            left_bin = annotation.left
            if isinstance(left_bin, ExprBinOp):
                while isinstance(left_bin, ExprBinOp):
                    right_type = self._griffe_annotation_to_api_type(left_bin.right, docstring)
                    if right_type is not None:  # pragma: no cover
                        types.append(right_type)
                    left_bin = left_bin.left
            left_type = self._griffe_annotation_to_api_type(left_bin, docstring)
            if left_type is not None:
                types.append(left_type)
            return sds_types.UnionType(types=types)
        else:  # pragma: no cover
            msg = f"Can't parse unexpected type from docstring: {annotation}. Added unknown type instead."
            logging.warning(msg)
            return sds_types.UnknownType()

    def _remove_default_from_griffe_annotation(self, annotation: str) -> str:
        if self.parser == Parser.numpy:
            return annotation.split(", default")[0]
        return annotation

    def _get_griffe_docstring(self, qname: str) -> griffe_models.Docstring | None:
        griffe_node = self.griffe_index[qname] if qname in self.griffe_index else None

        if griffe_node is not None:
            return griffe_node.docstring

        msg = (
            f"Something went wrong while searching for the docstring for {qname}. Please make sure"
            " that all directories with python files have an __init__.py file.",
        )
        logging.warning(msg)
        return None
