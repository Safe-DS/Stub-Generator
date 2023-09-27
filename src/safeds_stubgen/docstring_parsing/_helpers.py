import inspect

from docstring_parser import Docstring
from mypy import nodes


def get_full_docstring(declaration: nodes.ClassDef | nodes.FuncDef) -> str:
    """
    Return the full docstring of the given declaration.

    If no docstring is available, an empty string is returned. Indentation is cleaned up.
    """
    # Todo fix for new mypy syntax
    doc_node = declaration.doc_node
    if doc_node is None:
        return ""
    return inspect.cleandoc(doc_node.value)


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
