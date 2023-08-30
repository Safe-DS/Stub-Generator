from collections.abc import Callable
from typing import Any

from mypy.nodes import FuncDef, ClassDef, Decorator, MypyFile, AssignmentStmt

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

        # Todo Is this check still necessary?
        if node in visited_nodes:
            raise AssertionError("Node visited twice")
        visited_nodes.add(node)

        self.__enter(node)

        definitions = []
        if isinstance(node, MypyFile):
            definitions = node.defs
        elif isinstance(node, ClassDef):
            definitions = node.defs.body
        elif isinstance(node, FuncDef):
            definitions = node.body.body

        child_nodes = [
            _def for _def in definitions
            # TODO
            if _def.__class__.__name__ not in [
                "ExpressionStmt", "ImportFrom", "Import", "ImportAll"
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

        # Enums are a special case
        if class_ == "ClassDef":
            for superclass in node.base_type_exprs:
                if superclass.fullname == "enum.Enum":
                    class_ = "EnumDef"

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
