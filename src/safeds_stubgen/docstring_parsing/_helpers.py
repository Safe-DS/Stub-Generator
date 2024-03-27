from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from docstring_parser import Docstring

from griffe.docstrings.dataclasses import (
    DocstringAttribute,
    DocstringParameter,
    DocstringSection,
    DocstringSectionAttributes,
    DocstringSectionParameters,
)
from mypy import nodes


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
