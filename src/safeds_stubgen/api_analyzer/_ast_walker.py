from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mypy.nodes import AssignmentStmt, ClassDef, Decorator, FuncDef, MypyFile

from ._mypy_helpers import get_classdef_definitions, get_funcdef_definitions, get_mypyfile_definitions

_EnterAndLeaveFunctions = tuple[
    Callable[[MypyFile | ClassDef | FuncDef | AssignmentStmt], None] | None,
    Callable[[MypyFile | ClassDef | FuncDef | AssignmentStmt], None] | None,
]


class ASTWalker:
    """A walker visiting an abstract syntax tree in preorder.

    The following methods get called:

    * enter_<class_name> on entering a node, where class name is the class of the node in lower case.
    * leave_<class_name> on leaving a node, where class name is the class of the node in lower case.
    """

    def __init__(self, handler: Any) -> None:
        self._handler = handler
        self._cache: dict[str, _EnterAndLeaveFunctions] = {}

    def walk(self, tree: MypyFile) -> None:
        self.__walk(tree, set())

    def __walk(self, node: MypyFile | ClassDef | Decorator | FuncDef | AssignmentStmt, visited_nodes: set) -> None:
        # It's possible to get decorator data but for now we'll ignore them and just get the func
        if isinstance(node, Decorator):
            node = node.func

        if node in visited_nodes:
            raise AssertionError("Node visited twice")
        visited_nodes.add(node)

        self.__enter(node)

        definitions: list = []
        if isinstance(node, MypyFile):
            definitions = get_mypyfile_definitions(node)
        elif isinstance(node, ClassDef):
            definitions = get_classdef_definitions(node)
        elif isinstance(node, FuncDef):
            definitions = get_funcdef_definitions(node)

        # Skip other types, since we either get them through the ast_visitor, some other way or
        # don't need to parse them
        child_nodes = [
            _def
            for _def in definitions
            if _def.__class__.__name__
            in {
                "AssignmentStmt",
                "FuncDef",
                "ClassDef",
                "Decorator",
            }
        ]

        for child_node in child_nodes:
            # Ignore global variables and function attributes if the function is an __init__
            if isinstance(child_node, AssignmentStmt):
                if isinstance(node, MypyFile):
                    continue
                if isinstance(node, FuncDef) and node.name != "__init__":
                    continue

            self.__walk(child_node, visited_nodes)
        self.__leave(node)

    def __enter(self, node: MypyFile | ClassDef | FuncDef | AssignmentStmt) -> None:
        method = self.__get_callbacks(node)[0]
        if method is not None:
            method(node)

    def __leave(self, node: MypyFile | ClassDef | FuncDef | AssignmentStmt) -> None:
        method = self.__get_callbacks(node)[1]
        if method is not None:
            method(node)

    def __get_callbacks(self, node: MypyFile | ClassDef | FuncDef | AssignmentStmt) -> _EnterAndLeaveFunctions:
        class_ = node.__class__
        class_name = class_.__name__.lower()

        # Handle special cases
        if class_name == "classdef":
            if not hasattr(node, "base_type_exprs"):  # pragma: no cover
                raise AttributeError("Expected classdef node to have attribute 'base_type_exprs'.")

            for superclass in node.base_type_exprs:
                if hasattr(superclass, "fullname") and superclass.fullname in ("enum.Enum", "enum.IntEnum"):
                    class_name = "enumdef"
        elif class_name == "mypyfile":
            class_name = "moduledef"

        # Get class methods
        methods = self._cache.get(class_name, None)
        if methods is None:
            handler = self._handler
            enter_method = getattr(handler, f"enter_{class_name}", getattr(handler, "enter_default", None))
            leave_method = getattr(handler, f"leave_{class_name}", getattr(handler, "leave_default", None))
            self._cache[class_name] = (enter_method, leave_method)
        else:
            enter_method, leave_method = methods

        return enter_method, leave_method
