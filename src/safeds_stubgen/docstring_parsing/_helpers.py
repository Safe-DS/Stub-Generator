from __future__ import annotations

import inspect

from mypy import nodes


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
