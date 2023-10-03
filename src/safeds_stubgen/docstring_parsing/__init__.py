"""Parsing docstrings into a common format."""

from ._abstract_docstring_parser import AbstractDocstringParser
from ._create_docstring_parser import create_docstring_parser
from ._docstring import AttributeDocstring, ClassDocstring, FunctionDocstring, ParameterDocstring, ResultDocstring
from ._docstring_style import DocstringStyle
from ._epydoc_parser import EpydocParser
from ._googledoc_parser import GoogleDocParser
from ._numpydoc_parser import NumpyDocParser
from ._plaintext_docstring_parser import PlaintextDocstringParser
from ._restdoc_parser import RestDocParser

__all__ = [
    "AbstractDocstringParser",
    "AttributeDocstring",
    "ClassDocstring",
    "create_docstring_parser",
    "DocstringStyle",
    "EpydocParser",
    "FunctionDocstring",
    "GoogleDocParser",
    "NumpyDocParser",
    "ParameterDocstring",
    "PlaintextDocstringParser",
    "RestDocParser",
    "ResultDocstring",
]
