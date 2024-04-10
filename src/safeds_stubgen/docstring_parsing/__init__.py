"""Parsing docstrings into a common format."""

from ._abstract_docstring_parser import AbstractDocstringParser
from ._create_docstring_parser import create_docstring_parser
from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)
from ._docstring_parser import DocstringParser
from ._docstring_style import DocstringStyle
from ._plaintext_docstring_parser import PlaintextDocstringParser

__all__ = [
    "AbstractDocstringParser",
    "AttributeDocstring",
    "ClassDocstring",
    "create_docstring_parser",
    "DocstringParser",
    "DocstringStyle",
    "FunctionDocstring",
    "ParameterDocstring",
    "PlaintextDocstringParser",
    "ResultDocstring",
]
