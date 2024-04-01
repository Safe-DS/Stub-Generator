from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.enumerations import Parser

from ._docstring_parser import DocstringParser
from ._docstring_style import DocstringStyle
from ._plaintext_docstring_parser import PlaintextDocstringParser

if TYPE_CHECKING:
    from pathlib import Path

    from ._abstract_docstring_parser import AbstractDocstringParser


def create_docstring_parser(style: DocstringStyle, package_path: Path) -> AbstractDocstringParser:
    if style == DocstringStyle.GOOGLE:
        return DocstringParser(parser=Parser.google, package_path=package_path)
    elif style == DocstringStyle.NUMPYDOC:
        return DocstringParser(parser=Parser.numpy, package_path=package_path)
    elif style == DocstringStyle.REST:
        return DocstringParser(parser=Parser.sphinx, package_path=package_path)
    else:
        return PlaintextDocstringParser()
