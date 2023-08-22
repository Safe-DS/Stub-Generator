# TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  Aktuell klappt der mypy analyzer nicht ganz, irgendwie bekommen wir aliase nicht mehr hin (fehlen infos?)
#  -> Teste das nochmal nur mit der some_class datei wie ganz am Anfang -> Was geht hier falsch? Ist es der mypy
#  Aufruf _get_mypy_ast() in _get_api.py? ---> Eine Möglichkeit ist, dass er nicht alles richtig auflösen kann, weil wir
#  jede Datei einzeln mit mypy analysieren, anstatt die ganze directory anzugeben -> Aber wie hatten wir das vorher
#  gemacht und geschafft (also mit some_class)?

# Todo Enum handling (for modules)
from mypy.nodes import (
    Import, ImportFrom, ImportAll, FuncDef, ClassDef, MypyFile, ExpressionStmt, AssignmentStmt, ReturnStmt, StrExpr
)

from ._api import (
    API,
    Attribute,
    Class,
    Function,
    Module,
    QualifiedImport,
    WildcardImport,
)
from ._names import parent_qualified_name

from ._get_parameter_list import get_parameter_list
from safeds_stubgen.docstring_parsing import AbstractDocstringParser


class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.reexported: dict[str, list[str]] = {}
        self.api: API = api
        self.__declaration_stack: list[Module | Class | Function] = []

    def __get_id(self, name: str) -> str:
        segments = [self.api.package]
        segments += [it.name for it in self.__declaration_stack]
        segments += [name]

        return "/".join(segments)

    def enter_moduledef(self, module_node: MypyFile) -> None:
        qualified_imports: list[QualifiedImport] = []
        wildcard_imports: list[WildcardImport] = []
        docstring = ""

        child_definitions = [
            _definition for _definition in module_node.defs
            if _definition.__class__.__name__ not in ["FuncDef", "ClassDef"]
        ]

        for definition in child_definitions:
            # Imports
            if isinstance(definition, Import):
                for import_name, import_alias in definition.ids:
                    qualified_imports.append(
                        QualifiedImport(import_name, import_alias)
                    )

            elif isinstance(definition, ImportFrom):
                for import_name, import_alias in definition.names:
                    qualified_imports.append(
                        QualifiedImport(
                            f"{definition.id}.{import_name}",
                            import_alias
                        )
                    )

            elif isinstance(definition, ImportAll):
                wildcard_imports.append(
                    WildcardImport(definition.id)
                )

            # Docstring
            elif isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = definition.expr.value

        id_ = f"{self.api.package}/{module_node.fullname}"

        # Remember module, so we can later add classes and global functions
        module = Module(
            id_=id_,
            name=module_node.fullname,
            docstring=docstring,
            qualified_imports=qualified_imports,
            wildcard_imports=wildcard_imports,
        )
        self.__declaration_stack.append(module)

    def leave_moduledef(self, _: MypyFile) -> None:
        module = self.__declaration_stack.pop()
        if not isinstance(module, Module):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        self.api.add_module(module)

    def enter_classdef(self, class_node: ClassDef) -> None:
        id_ = self.__get_id(class_node.name)
        name = class_node.name
        docstring = ""

        for definition in class_node.defs.body:
            if isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = definition.expr.value

        # Remember class, so we can later add methods
        class_ = Class(
            id=id_,
            name=name,
            superclasses=class_node.basenames,  # Todo -> class_node.base_type_exprs
            is_public=self.is_public(class_node.name, name),  # Todo
            reexported_by=self.reexported.get(name, []),  # Todo
            docstring=docstring,
            constructor=None  # Todo
        )
        self.__declaration_stack.append(class_)

    def leave_classdef(self, _: ClassDef) -> None:
        class_ = self.__declaration_stack.pop()
        if not isinstance(class_, Class):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested classes for now
            if isinstance(parent, Module):
                self.api.add_class(class_)
                parent.add_class(class_)

    def enter_funcdef(self, function_node: FuncDef) -> None:
        function_id = self.__get_id(function_node.name)
        docstring = ""
        qname = function_node.fullname
        is_public = self.is_public(function_node.name, qname)  # Todo
        is_static = self.is_static(function_node.name, qname)  # Todo

        for definition in function_node.body.body:
            if isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = definition.expr.value
            elif isinstance(definition, ReturnStmt):
                pass  # Todo

        for args in function_node.arguments:
            pass  # Todo

        function = Function(
            id=function_id,
            name=function_node.name,
            reexported_by=self.reexported.get(qname, []),  # todo
            docstring=docstring,
            is_public=is_public,
            is_static=is_static,
            parameters=[],  # Todo
            # parameters=get_parameter_list(
            #     self.docstring_parser,
            #     function_node,
            #     function_id,
            #     qname,
            #     is_public,
            # ),
            results=[]  # Todo
        )
        self.__declaration_stack.append(function)

    def leave_funcdef(self, _: FuncDef) -> None:
        function = self.__declaration_stack.pop()
        if not isinstance(function, Function):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested functions for now
            if isinstance(parent, Module):
                self.api.add_function(function)
                parent.add_function(function)
            elif isinstance(parent, Class):
                self.api.add_function(function)
                parent.add_method(function)

    # Todo
    def enter_attr(self): ...
    def leave_attr(self): ...

    # Todo
    def is_static(self, name: str, qualified_name: str) -> bool:
        return True

    def is_public(self, name: str, qualified_name: str) -> bool:
        if name.startswith("_") and not name.endswith("__"):
            return False

        if qualified_name in self.reexported:
            return True

        # Containing class is re-exported (always false if the current API element is not a method)
        if isinstance(self.__declaration_stack[-1], Class) and parent_qualified_name(qualified_name) in self.reexported:
            return True

        # The slicing is necessary so __init__ functions are not excluded (already handled in the first condition).
        return all(not it.startswith("_") for it in qualified_name.split(".")[:-1])
