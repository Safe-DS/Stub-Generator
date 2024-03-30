from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.enumerations import Parser

from ._docstring_parser import DocstringParser
from ._docstring_style import DocstringStyle
from ._plaintext_docstring_parser import PlaintextDocstringParser

if TYPE_CHECKING:
    from ._abstract_docstring_parser import AbstractDocstringParser


def create_docstring_parser(style: DocstringStyle) -> AbstractDocstringParser:
    if style == DocstringStyle.GOOGLE:
        return DocstringParser(Parser.google)
    elif style == DocstringStyle.NUMPYDOC:
        return DocstringParser(Parser.numpy)
    elif style == DocstringStyle.REST:
        return DocstringParser(Parser.sphinx)
    else:
        return PlaintextDocstringParser()
