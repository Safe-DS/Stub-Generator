from __future__ import annotations

import re
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
        docstring_obj = parse_docstring(docstring, style=DP_DocstringStyle.NUMPYDOC)

        return ClassDocstring(
            description=get_description(docstring_obj),
            full_docstring=docstring,
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = get_full_docstring(function_node)
        docstring_obj = self.__get_cached_numpydoc_string(function_node, docstring)

        return FunctionDocstring(
            description=get_description(docstring_obj),
            full_docstring=docstring,
        )

    def get_parameter_documentation(
        self,
        function_node: nodes.FuncDef,
        parameter_name: str,
        parameter_assigned_by: ParameterAssignment,
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
        all_parameters_numpydoc: list[DocstringParam] = function_numpydoc.params
        matching_parameters_numpydoc = [
            it
            for it in all_parameters_numpydoc
            if it.args[0] == "param" and _is_matching_parameter_numpydoc(it, parameter_name, parameter_assigned_by)
        ]

        if len(matching_parameters_numpydoc) == 0:
            # If we have a constructor we have to check both, the class and then the constructor (see issue
            # https://github.com/Safe-DS/Library-Analyzer/issues/10)
            if function_node.name == "__init__":
                docstring_constructor = get_full_docstring(function_node)
                # Find matching parameter docstrings
                function_numpydoc = parse_docstring(docstring_constructor, style=DP_DocstringStyle.NUMPYDOC)
                all_parameters_numpydoc = function_numpydoc.params

                # Overwrite previous matching_parameters_numpydoc list
                matching_parameters_numpydoc = [
                    it
                    for it in all_parameters_numpydoc
                    if _is_matching_parameter_numpydoc(it, parameter_name, parameter_assigned_by)
                ]

            if len(matching_parameters_numpydoc) == 0:
                return ParameterDocstring(type="", default_value="", description="")

        last_parameter_numpydoc = matching_parameters_numpydoc[-1]
        type_, default_value = _get_type_and_default_value(last_parameter_numpydoc)
        return ParameterDocstring(
            type=type_,
            default_value=default_value,
            description=last_parameter_numpydoc.description or "",
        )

    def get_attribute_documentation(
        self,
        parent_class: Class,
        attribute_name: str,
    ) -> AttributeDocstring:
        # Find matching attribute docstrings
        function_numpydoc = self.__get_cached_numpydoc_string(parent_class, parent_class.docstring.full_docstring)
        all_attributes_numpydoc: list[DocstringParam] = function_numpydoc.params
        matching_attributes_numpydoc = [
            it
            for it in all_attributes_numpydoc
            if it.args[0] == "attribute" and _is_matching_attribute_numpydoc(it, attribute_name)
        ]

        # If the class has a constructor we have to check both the class and then the constructor
        # (see issue https://github.com/Safe-DS/Library-Analyzer/issues/10)
        if len(matching_attributes_numpydoc) == 0:
            # Find matching attribute docstrings
            function_numpydoc = parse_docstring(
                parent_class.constructor_fulldocstring,
                style=DP_DocstringStyle.NUMPYDOC,
            )
            all_attributes_numpydoc = function_numpydoc.params

            # Overwrite previous matching_attributes_numpydoc list
            matching_attributes_numpydoc = [
                it for it in all_attributes_numpydoc if _is_matching_attribute_numpydoc(it, attribute_name)
            ]

            if len(matching_attributes_numpydoc) == 0:
                return AttributeDocstring(type="", default_value="", description="")

        last_attribute_numpydoc = matching_attributes_numpydoc[-1]
        type_, default_value = _get_type_and_default_value(last_attribute_numpydoc)
        return AttributeDocstring(
            type=type_,
            default_value=default_value,
            description=last_attribute_numpydoc.description or "",
        )

    def get_result_documentation(self, function_node: nodes.FuncDef) -> ResultDocstring:
        docstring = get_full_docstring(function_node)

        # Find matching parameter docstrings
        function_numpydoc = self.__get_cached_numpydoc_string(function_node, docstring)
        function_result = function_numpydoc.returns

        if function_result is None:
            return ResultDocstring()

        return ResultDocstring(
            type=function_result.type_name or "",
            description=function_result.description or "",
        )

    def __get_cached_numpydoc_string(self, node: nodes.FuncDef | Class, docstring: str) -> Docstring:
        """
        Return the NumpyDocString for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function `get_parameter_documentation` when parsing sklearn. Afterwards, it was only 2.113s.
        """
        if self.__cached_node is not node or node.name == "__init__":
            self.__cached_node = node
            self.__cached_docstring = parse_docstring(docstring, style=DP_DocstringStyle.NUMPYDOC)

        if self.__cached_docstring is None:  # pragma: no cover
            raise ValueError("Expected a docstring, got None instead.")
        return self.__cached_docstring


def _is_matching_parameter_numpydoc(
    parameter_docstring_obj: DocstringParam,
    parameter_name: str,
    parameter_assigned_by: ParameterAssignment,
) -> bool:
    """Return whether the given docstring object applies to the parameter with the given name."""
    from safeds_stubgen.api_analyzer import ParameterAssignment

    if parameter_assigned_by == ParameterAssignment.POSITIONAL_VARARG:
        lookup_name = f"*{parameter_name}"
    elif parameter_assigned_by == ParameterAssignment.NAMED_VARARG:
        lookup_name = f"**{parameter_name}"
    else:
        lookup_name = parameter_name

    # Numpydoc allows multiple parameters to be documented at once. See
    # https://numpydoc.readthedocs.io/en/latest/format.html#parameters for more information.
    return any(name.strip() == lookup_name for name in parameter_docstring_obj.arg_name.split(","))


def _is_matching_attribute_numpydoc(parameter_docstring_obj: DocstringParam, parameter_name: str) -> bool:
    return any(name.strip() == parameter_name for name in parameter_docstring_obj.arg_name.split(","))


def _get_type_and_default_value(
    parameter_docstring_obj: DocstringParam,
) -> tuple[str, str]:
    """Return the type and default value for the given NumpyDoc."""
    type_name = parameter_docstring_obj.type_name or ""
    parts = re.split(r",\s*optional|,\s*default\s*[:=]?", type_name)

    if len(parts) != 2:
        return type_name.strip(), parameter_docstring_obj.default or ""

    return parts[0].strip(), parts[1].strip()
