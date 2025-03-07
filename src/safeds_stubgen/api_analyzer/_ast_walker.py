from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mypy.nodes import AssignmentStmt, ClassDef, Decorator, FuncDef, MypyFile, OverloadedFuncDef

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
        # We ignore decorators and just take their inner functions, since we can get decorator information from the
        # function node too
        if isinstance(node, Decorator):
            node = node.func
        elif isinstance(node, OverloadedFuncDef):
            node = node.impl

        if node in visited_nodes:  # pragma: no cover
            raise AssertionError("Node visited twice")
        visited_nodes.add(node)

        self.__enter(node)

        # Search nodes for more child nodes. Skip other not specified types, since we either get them through the
        # ast_visitor, some other way or don't need to parse them at all
        child_nodes = []
        if isinstance(node, MypyFile):
            definitions = get_mypyfile_definitions(node)
            child_nodes = [
                _def for _def in definitions if _def.__class__.__name__ in {"FuncDef", "ClassDef", "Decorator"}
            ]
        elif isinstance(node, ClassDef):
            definitions = get_classdef_definitions(node)
            child_nodes = [
                _def
                for _def in definitions
                if _def.__class__.__name__
                in {"AssignmentStmt", "FuncDef", "ClassDef", "Decorator", "OverloadedFuncDef"}
            ]
        elif isinstance(node, FuncDef) and node.name == "__init__":
            definitions = get_funcdef_definitions(node)
            child_nodes = [_def for _def in definitions if _def.__class__.__name__ == "AssignmentStmt"]

        for child_node in child_nodes:
            # The '__mypy-replace' name is a mypy placeholer which we don't want to parse.
            if getattr(child_node, "name", "") == "__mypy-replace":  # pragma: no cover
                continue

            # Overloaded Functions can either have one implementation (impl) or can have multiple (items)
            if isinstance(child_node, OverloadedFuncDef):
                if child_node.impl is not None:
                    self.__walk(child_node.impl, visited_nodes)
                else:
                    for child_node_impl in child_node.items:
                        self.__walk(child_node_impl, visited_nodes)
            else:
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
