from collections.abc import Callable
from typing import Any

from mypy.nodes import FuncDef, ClassDef, Decorator, MypyFile, AssignmentStmt, ReturnStmt
from mypy.traverser import all_return_statements

_EnterAndLeaveFunctions = tuple[
    Callable[[MypyFile | ClassDef | FuncDef], None] | None,
    Callable[[MypyFile | ClassDef | FuncDef], None] | None,
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

    def walk(self, tree: MypyFile) -> None:
        self.__walk(tree, set())

    def __walk(self, node, visited_nodes: set) -> None:
        # It's possible to get decorator data but for now we'll ignore them and just get the func
        if isinstance(node, Decorator):
            node = node.func

        if node in visited_nodes:
            raise AssertionError("Node visited twice")
        visited_nodes.add(node)

        self.__enter(node)

        definitions: list | set = []
        if isinstance(node, MypyFile):
            definitions = node.defs
        elif isinstance(node, ClassDef):
            definitions = node.defs.body
        elif isinstance(node, FuncDef):
            definitions = set()
            definitions.update(node.body.body)
            # Some return statements can be hidden behind if statements, so we have to get them seperately
            definitions.update(all_return_statements(node))

        # Skip other types, since we either get them through the ast_visitor, some other way or
        # don't need to parse them
        child_nodes = [
            _def for _def in definitions
            if _def.__class__.__name__ in [
                "AssignmentStmt", "FuncDef", "ClassDef", "ReturnStmt", "Decorator"
            ]
        ]

        for child_node in child_nodes:
            # Ignore function attributes
            if isinstance(node, FuncDef) and isinstance(child_node, AssignmentStmt):
                continue

            self.__walk(child_node, visited_nodes)
        self.__leave(node)

    def __enter(self, node) -> None:
        method = self.__get_callbacks(node)[0]
        if method is not None:
            method(node)

    def __leave(self, node) -> None:
        method = self.__get_callbacks(node)[1]
        if method is not None:
            method(node)

    def __get_callbacks(self, node: MypyFile | ClassDef | FuncDef) -> _EnterAndLeaveFunctions:
        class_ = node.__class__
        class_name = class_.__name__.lower()

        # Handle special cases
        if class_name == "classdef":
            for superclass in node.base_type_exprs:
                if superclass.fullname == "enum.Enum":
                    class_name = "enumdef"
        elif class_name == "mypyfile":
            class_name = "moduledef"

        # Get class methods
        methods = self._cache.get(class_name)
        if methods is None:
            handler = self._handler
            enter_method = getattr(handler, f"enter_{class_name}", getattr(handler, "enter_default", None))
            leave_method = getattr(handler, f"leave_{class_name}", getattr(handler, "leave_default", None))
            self._cache[class_name] = (enter_method, leave_method)
        else:
            enter_method, leave_method = methods

        return enter_method, leave_method
