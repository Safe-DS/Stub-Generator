from __future__ import annotations

from typing import TYPE_CHECKING

from ._abstract_docstring_parser import AbstractDocstringParser
from ._docstring import (
    AttributeDocstring,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)
from ._helpers import get_full_docstring

if TYPE_CHECKING:
    from mypy import nodes


class PlaintextDocstringParser(AbstractDocstringParser):
    """Parses documentation in any format. Should not be used if there is another parser for the specific format."""

    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        docstring = get_full_docstring(class_node)

        return ClassDocstring(
            description=docstring,
            full_docstring=docstring,
        )

    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        docstring = get_full_docstring(function_node)

        return FunctionDocstring(
            description=docstring,
            full_docstring=docstring,
        )

    def get_parameter_documentation(
        self,
        function_qname: str,  # noqa: ARG002
        parameter_name: str,  # noqa: ARG002
        parent_class_qname: str,  # noqa: ARG002
    ) -> ParameterDocstring:
        return ParameterDocstring()

    def get_attribute_documentation(
        self,
        parent_class_qname: str,  # noqa: ARG002
        attribute_name: str,  # noqa: ARG002
    ) -> AttributeDocstring:
        return AttributeDocstring()

    def get_result_documentation(
        self,
        function_qname: str,  # noqa: ARG002
    ) -> list[ResultDocstring]:
        return []
