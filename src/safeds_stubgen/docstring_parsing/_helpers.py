from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable
    from docstring_parser import Docstring
    from safeds_stubgen.api_analyzer import Class

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
from mypy import nodes

from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)


def remove_newline_from_text(text: str) -> str:
    return text.rstrip("\n").strip("\n")


def get_full_docstring(declaration: nodes.ClassDef | nodes.FuncDef) -> str:
    """
    Return the full docstring of the given declaration.

    If no docstring is available, an empty string is returned. Indentation is cleaned up.
    """
    from safeds_stubgen.api_analyzer import get_classdef_definitions, get_funcdef_definitions

    if isinstance(declaration, nodes.ClassDef):
        definitions = get_classdef_definitions(declaration)
    elif isinstance(declaration, nodes.FuncDef):
        definitions = get_funcdef_definitions(declaration)
    else:  # pragma: no cover
        raise TypeError("Declaration is of wrong type.")

    full_docstring = ""
    for definition in definitions:
        if isinstance(definition, nodes.ExpressionStmt) and isinstance(definition.expr, nodes.StrExpr):
            full_docstring = definition.expr.value

    return inspect.cleandoc(full_docstring)


def get_description(docstring_obj: Docstring) -> str:
    """
    Return the concatenated short and long description of the given docstring object.

    If these parts are blank, an empty string is returned.
    """
    summary: str = docstring_obj.short_description or ""
    extended_summary: str = docstring_obj.long_description or ""

    result = ""
    result += summary.rstrip()
    result += "\n\n"
    result += extended_summary.rstrip()
    return result.strip()


def create_class_docstring(class_node: nodes.ClassDef, parser: Parser) -> ClassDocstring:
    docstring = get_full_docstring(class_node)

    griffe_doc = GriffeDocstring(value=docstring, parser=parser)
    description = ""
    for docstring_section in griffe_doc.parse(parser=parser):
        if isinstance(docstring_section, DocstringSectionText):
            description = docstring_section.value
            break

    return ClassDocstring(
        description=remove_newline_from_text(description),
        full_docstring=remove_newline_from_text(docstring),
    )


def create_function_docstring(function_node: nodes.FuncDef, cache_function: Callable) -> FunctionDocstring:
    docstring = get_full_docstring(function_node)
    griffe_docstring = cache_function(function_node, docstring)

    description = ""
    for docstring_section in griffe_docstring:
        if isinstance(docstring_section, DocstringSectionText):
            description = docstring_section.value
            break

    return FunctionDocstring(
        description=remove_newline_from_text(description),
        full_docstring=remove_newline_from_text(docstring),
    )


def create_parameter_docstring(
    function_node: nodes.FuncDef,
    parameter_name: str,
    parent_class: Class | None,
    cache_function: Callable[[nodes.FuncDef | Class, str], list[DocstringSection]],
    parser: Parser
) -> ParameterDocstring:
    from safeds_stubgen.api_analyzer import Class

    # For constructors (__init__ functions) the parameters are described on the class
    if function_node.name == "__init__" and isinstance(parent_class, Class):
        docstring = parent_class.docstring.full_docstring
    else:
        docstring = get_full_docstring(function_node)

    # Find matching parameter docstrings
    function_doc = cache_function(function_node, docstring)
    matching_parameters: list[DocstringParameter] = _get_matching_docstrings(function_doc, parameter_name, "param")

    # For numpy, if we have a constructor we have to check both, the class and then the constructor (see issue
    # https://github.com/Safe-DS/Library-Analyzer/issues/10)
    if parser == Parser.numpy and len(matching_parameters) == 0 and function_node.name == "__init__":
        # Get constructor docstring
        docstring_constructor = get_full_docstring(function_node)
        griffe_docstring = GriffeDocstring(value=docstring_constructor, parser=parser)

        # Find matching parameter docstrings
        function_doc = griffe_docstring.parse(parser)
        matching_parameters: list[DocstringParameter] = _get_matching_docstrings(function_doc, parameter_name, "param")

    if len(matching_parameters) == 0:
        return ParameterDocstring()

    last_parameter = matching_parameters[-1]
    return ParameterDocstring(
        type=last_parameter.annotation or "",
        default_value=last_parameter.default or "",
        description=remove_newline_from_text(last_parameter.description) or "",
    )


def _get_matching_docstrings(
    function_doc: list[DocstringSection],
    name: str,
    type_: Literal["attr", "param"]
) -> list[DocstringAttribute] | list[DocstringParameter]:
    all_docstrings = None
    for docstring_section in function_doc:
        if ((type_ == "attr" and isinstance(docstring_section, DocstringSectionAttributes)) or
                (type_ == "param" and isinstance(docstring_section, DocstringSectionParameters))):
            all_docstrings = docstring_section
            break

    if all_docstrings:
        name = name.lstrip("*")
        return [it for it in all_docstrings.value if it.name.lstrip("*") == name]

    return []


def create_attribute_docstring(
    attribute_name: str,
    parent_class: Class | None,
    cache_function: Callable[[nodes.FuncDef | Class, str], list[DocstringSection]],
    parser: Parser
) -> AttributeDocstring:
    # Find matching attribute docstrings
    function_doc = cache_function(parent_class, parent_class.docstring.full_docstring)
    matching_attributes = _get_matching_docstrings(function_doc, attribute_name, "attr")

    # For Numpydoc, if the class has a constructor we have to check both the class and then the constructor
    # (see issue https://github.com/Safe-DS/Library-Analyzer/issues/10)
    if parser == Parser.numpy and len(matching_attributes) == 0:
        griffe_docstring = GriffeDocstring(value=parent_class.constructor_fulldocstring, parser=parser)

        # Find matching parameter docstrings
        function_doc = griffe_docstring.parse(parser)
        matching_attributes = _get_matching_docstrings(function_doc, attribute_name, "attr")

    if len(matching_attributes) == 0:
        return AttributeDocstring()

    last_attribute = matching_attributes[-1]
    return AttributeDocstring(
        type=last_attribute.annotation or "",
        default_value=last_attribute.value or "",
        description=remove_newline_from_text(last_attribute.description),
    )


def create_result_docstring(
    function_node: nodes.FuncDef,
    cache_function: Callable[[nodes.FuncDef | Class, str], list[DocstringSection]],
):
    docstring = get_full_docstring(function_node)

    # Find matching parameter docstrings
    function_doc = cache_function(function_node, docstring)

    all_returns = None
    for docstring_section in function_doc:
        if isinstance(docstring_section, DocstringSectionReturns):
            all_returns = docstring_section
            break

    if not all_returns:
        return ResultDocstring()

    return ResultDocstring(
        type=all_returns.value[0].annotation or "",
        description=remove_newline_from_text(all_returns.value[0].description),
    )
