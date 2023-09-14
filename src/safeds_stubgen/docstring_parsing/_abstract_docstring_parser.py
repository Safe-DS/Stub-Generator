from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import astroid

    from ._docstring import (
        ClassDocstring,
        FunctionDocstring,
        ParameterDocstring,
    )

    from safeds_stubgen.api_analyzer import ParameterAssignment


class AbstractDocstringParser(ABC):
    @abstractmethod
    def get_class_documentation(self, class_node: astroid.ClassDef) -> ClassDocstring:
        pass

    @abstractmethod
    def get_function_documentation(self, function_node: astroid.FunctionDef) -> FunctionDocstring:
        pass

    @abstractmethod
    def get_parameter_documentation(
        self,
        function_node: astroid.FunctionDef,
        parameter_name: str,
        parameter_assigned_by: ParameterAssignment,
    ) -> ParameterDocstring:
        pass