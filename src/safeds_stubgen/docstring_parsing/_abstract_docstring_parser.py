from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy import nodes

    from safeds_stubgen.api_analyzer import Class, ParameterAssignment

    from ._docstring import (
        AttributeDocstring,
        ClassDocstring,
        FunctionDocstring,
        ParameterDocstring,
        ResultDocstring,
    )


class AbstractDocstringParser(ABC):
    @abstractmethod
    def get_class_documentation(self, class_node: nodes.ClassDef) -> ClassDocstring:
        pass  # pragma: no cover

    @abstractmethod
    def get_function_documentation(self, function_node: nodes.FuncDef) -> FunctionDocstring:
        pass  # pragma: no cover

    @abstractmethod
    def get_parameter_documentation(
        self,
        function_node: nodes.FuncDef,
        parameter_name: str,
        parameter_assigned_by: ParameterAssignment,
        parent_class: Class | None,
    ) -> ParameterDocstring:
        pass  # pragma: no cover

    @abstractmethod
    def get_attribute_documentation(
        self,
        parent_class: Class,
        attribute_name: str,
    ) -> AttributeDocstring:
        pass  # pragma: no cover

    @abstractmethod
    def get_result_documentation(self, function_node: nodes.FuncDef) -> ResultDocstring:
        pass  # pragma: no cover
