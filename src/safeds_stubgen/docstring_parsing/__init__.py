"""Parsing docstrings into a common format."""

from ._create_docstring_parser import create_docstring_parser
from ._docstring_style import DocstringStyle

__all__ = [
    "create_docstring_parser",
    "DocstringStyle",
]
