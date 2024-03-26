from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.dataclasses import Docstring
from griffe.enumerations import Parser

from ._abstract_docstring_parser import AbstractDocstringParser
from ._helpers import (
    create_attribute_docstring,
    create_class_docstring,
    create_function_docstring,
    create_parameter_docstring,
    create_result_docstring,
)

if TYPE_CHECKING:
    from griffe.docstrings.dataclasses import DocstringSection
    from ._docstring import (
        AttributeDocstring,
        ClassDocstring,
        FunctionDocstring,
        ParameterDocstring,
        ResultDocstring,
    )
    from mypy import nodes

    from safeds_stubgen.api_analyzer import Class


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
        return create_class_docstring(class_node=class_node, parser=Parser.numpy)

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        return create_function_docstring(function_node=function_node, cache_function=self.__get_cached_numpydoc_string)

    def get_parameter_documentation(
        self,
        function_node: nodes.FuncDef,
        parameter_name: str,
        parent_class: Class | None,
    ) -> ParameterDocstring:
        return create_parameter_docstring(
            function_node=function_node,
            parameter_name=parameter_name,
            parent_class=parent_class,
            cache_function=self.__get_cached_numpydoc_string,
            parser=Parser.numpy
        )

    def get_attribute_documentation(self, parent_class: Class, attribute_name: str) -> AttributeDocstring:
        return create_attribute_docstring(
            attribute_name=attribute_name,
            parent_class=parent_class,
            cache_function=self.__get_cached_numpydoc_string,
            parser=Parser.numpy
        )

    def get_result_documentation(self, function_node: nodes.FuncDef) -> ResultDocstring:
        return create_result_docstring(function_node=function_node, cache_function=self.__get_cached_numpydoc_string)

    def __get_cached_numpydoc_string(self, node: nodes.FuncDef | Class, docstring: str) -> list[DocstringSection]:
        """
        Return the NumpyDocString for the given function node.

        It is only recomputed when the function node differs from the previous one that was passed to this function.
        This avoids reparsing the docstring for the function itself and all of its parameters.

        On Lars's system this caused a significant performance improvement: Previously, 8.382s were spent inside the
        function `get_parameter_documentation` when parsing sklearn. Afterward, it was only 2.113s.
        """
        if self.__cached_node is not node or node.name == "__init__":
            self.__cached_node = node
            griffe_docstring = Docstring(value=docstring, parser=Parser.numpy)
            self.__cached_docstring = griffe_docstring.parse(parser=Parser.numpy)

        if self.__cached_docstring is None:  # pragma: no cover
            raise ValueError("Expected a docstring, got None instead.")
        return self.__cached_docstring
