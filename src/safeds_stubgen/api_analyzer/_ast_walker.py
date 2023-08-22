from collections.abc import Callable
from typing import Any

from mypy import nodes
from mypy.nodes import FuncDef, ClassDef

_EnterAndLeaveFunctions = tuple[
    Callable[[nodes.Statement], None] | None,
    Callable[[nodes.Statement], None] | None,
]


class ASTWalker:
    """A walker visiting an abstract syntax tree in preorder.

    The following methods get called:

    * enter_<class_name> on entering a node, where class name is the class of the node in lower case.
    * leave_<class_name> on leaving a node, where class name is the class of the node in lower case.
    """

    def __init__(self, handler: Any) -> None:
        self._handler = handler
        self._cache: dict[type, _EnterAndLeaveFunctions] = {}

    def walk(self, tree: nodes.MypyFile) -> None:
        self.__walk(tree, set(), True)

    def __walk(self, node, visited_nodes: set, is_module: bool = False) -> None:
        if node in visited_nodes:
            raise AssertionError("Node visited twice")
        visited_nodes.add(node)

        self.__enter(node, is_module)

        if isinstance(node, FuncDef):
            definitions = node.body.body
        elif isinstance(node, ClassDef):
            definitions = node.defs.body
        else:
            definitions = node.defs

        child_nodes = [
            _def for _def in definitions
            if _def.__class__.__name__ not in [
                "ImportFrom", "Import", "ImportAll", "ExpressionStmt", "AssignmentStmt", "ReturnStmt"
            ]
        ]

        for child_node in child_nodes:
            self.__walk(child_node, visited_nodes)
        self.__leave(node, is_module)

    def __enter(self, node, is_module: bool) -> None:
        method = self.__get_callbacks(node, is_module)[0]
        if method is not None:
            method(node)

    def __leave(self, node, is_module: bool) -> None:
        method = self.__get_callbacks(node, is_module)[1]
        if method is not None:
            method(node)

    def __get_callbacks(self, node: nodes.MypyFile, is_module: bool) -> _EnterAndLeaveFunctions:
        class_ = node.__class__
        methods = self._cache.get(class_)

        if methods is None:
            handler = self._handler
            class_name = class_.__name__.lower()
            name = "moduledef" if class_name == "mypyfile" else class_name
            enter_method = getattr(handler, f"enter_{name}", getattr(handler, "enter_default", None))
            leave_method = getattr(handler, f"leave_{name}", getattr(handler, "leave_default", None))
            self._cache[class_] = (enter_method, leave_method)
        else:
            enter_method, leave_method = methods

        return enter_method, leave_method
