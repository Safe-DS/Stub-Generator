from mypy.nodes import (
    AssignmentStmt,
    ClassDef,
    ExpressionStmt,
    FuncDef,
    Import,
    ImportAll,
    ImportFrom,
    MypyFile,
    ReturnStmt,
    StrExpr
)

from ._api import (
    API,
    Attribute,
    Class,
    Enum,
    EnumInstance,
    Function,
    Module,
    Parameter,
    ParameterAssignment,
    QualifiedImport,
    Result,
    WildcardImport,
)
from ._names import parent_qualified_name

from safeds_stubgen.docstring_parsing import (
    AbstractDocstringParser,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring
)


class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.reexported: dict[str, list[str]] = {}
        self.api: API = api
        self.__declaration_stack: list[
            Module | Class | Function | Enum | Attribute | EnumInstance | Result
        ] = []

    def enter_moduledef(self, node: MypyFile) -> None:
        id_ = self.__get_id(node.name)
        qualified_imports: list[QualifiedImport] = []
        wildcard_imports: list[WildcardImport] = []
        attributes: list[Attribute] = []
        docstring = ""

        # We don't need to check functions and classes, since the ast walker will check them anyway
        child_definitions = [
            _definition for _definition in node.defs
            if _definition.__class__.__name__ not in
            ["FuncDef", "Decorator", "ClassDef", "AssignmentStmt"]
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
            elif isinstance(definition, ExpressionStmt) and \
                    isinstance(definition.expr, StrExpr):
                docstring = definition.expr.value

        # Remember module, so we can later add classes and global functions
        module = Module(
            id_=id_,
            name=node.fullname,
            docstring=docstring,
            qualified_imports=qualified_imports,
            wildcard_imports=wildcard_imports,
            global_attributes=attributes
        )
        self.__declaration_stack.append(module)

    def leave_moduledef(self, _: MypyFile) -> None:
        module = self.__declaration_stack.pop()
        if not isinstance(module, Module):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        self.api.add_module(module)

    def enter_classdef(self, node: ClassDef) -> None:
        id_ = self.__get_id(node.name)
        name = node.name
        docstring: ClassDocstring | None = None

        for definition in node.defs.body:
            # Docstring
            if isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = ClassDocstring(definition.expr.value, definition.expr.value)  # Todo

        # superclasses
        # Todo Aliase werden noch nicht aufgelöst
        superclasses = [
            superclass.fullname
            for superclass in node.base_type_exprs
        ]

        # Remember class, so we can later add methods
        class_ = Class(
            id=id_,
            name=name,
            superclasses=superclasses,
            is_public=self.is_public(node.name, name),
            reexported_by=self.reexported.get(name, []),  # Todo
            docstring=docstring or ClassDocstring(),
            constructor=None
        )
        self.__declaration_stack.append(class_)

    def leave_classdef(self, _: ClassDef) -> None:
        class_ = self.__declaration_stack.pop()
        if not isinstance(class_, Class):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            if isinstance(parent, Module):
                self.api.add_class(class_)
                parent.add_class(class_)
            elif isinstance(parent, Class):
                self.api.add_class(class_)
                parent.add_class(class_)

    def enter_funcdef(self, node: FuncDef) -> None:
        function_id = self.__get_id(node.name)
        docstring: FunctionDocstring | None = None
        qname = node.fullname
        is_public = self.is_public(node.name, qname)
        is_static = node.is_static

        for definition in node.body.body:
            # Docstring
            if isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = FunctionDocstring(definition.expr.value, definition.expr.value)  # Todo

        # Function args Todo add to API class
        arguments: list[Parameter] = []
        if node.type is not None:
            argument_info: list[tuple] = []
            if node.arguments is not None:
                argument_info = list(
                    zip(
                        node.type.arg_names,
                        node.type.arg_types
                    )
                )

            for arg_counter, arg in enumerate(node.arguments):
                arg_name = argument_info[arg_counter][0]
                arg_type = argument_info[arg_counter][1]
                # Todo "has_default_value" Feld, oder wie differenzieren wir?

                default_value = None
                if arg.initializer is not None:
                    default_value = getattr(arg.initializer, "value", None)

                arguments.append(Parameter(
                    id_=f"{function_id}/{arg_name}",
                    name=arg_name,
                    default_value=default_value,
                    assigned_by=ParameterAssignment.IMPLICIT,  # Todo
                    docstring=ParameterDocstring(),  # Todo
                    type_=arg_type,
                ))

        function = Function(
            id=function_id,
            name=node.name,
            reexported_by=self.reexported.get(qname, []),  # todo
            docstring=docstring if docstring is not None else FunctionDocstring(),
            is_public=is_public,
            is_static=is_static,
            parameters=arguments
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

                if function.name == "__init__":
                    parent.add_constructor(function)

    def enter_enumdef(self, node: ClassDef) -> None:
        id_ = self.__get_id(node.name)
        docstring: ClassDocstring | None = None

        for definition in node.defs.body:
            # Docstring
            if isinstance(definition, ExpressionStmt) and \
                    isinstance(definition.expr, StrExpr):
                docstring = ClassDocstring(definition.expr.value, definition.expr.value)  # Todo

        enum = Enum(
            id=id_,
            name=node.name,
            docstring=docstring if docstring is not None else FunctionDocstring()
        )
        self.__declaration_stack.append(enum)

    def leave_enumdef(self, _: ClassDef) -> None:
        enum = self.__declaration_stack.pop()
        if not isinstance(enum, Enum):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested functions for now
            if isinstance(parent, Module):
                self.api.add_enum(enum)
                parent.add_enum(enum)

    def enter_assignmentstmt(self, node: AssignmentStmt) -> None:
        """Assignments are attributes"""
        parent = self.__declaration_stack[-1]
        assignment: Attribute | EnumInstance | None = None

        if isinstance(parent, Class) or isinstance(parent, Module):
            # Todo desc
            if hasattr(node.lvalues[0], "name"):
                name = node.lvalues[0].name
                id_ = self.__get_id(name)

                assignment = Attribute(
                    id=id_,
                    name=name,
                    type=node.type,
                    is_public=not name.startswith("_"),  # Todo
                    is_static=False  # Todo
                )

            elif hasattr(node.lvalues[0], "items"):  # Todo better handling for multiple attr names
                attr_names = [item.name for item in node.lvalues[0].items]
                # Todo Wir bekommen mehrere Attribute mit verschiedenen Namen, wie sollen wir das handeln,
                #  weil jeder einzelne auch der API Classe und dem parent hinzugefügt werden muss
                for attr_name in attr_names:
                    assignment = Attribute(
                        id=self.__get_id(attr_name),
                        name=attr_name,
                        type=None,
                        is_public=not attr_name.startswith("_"),  # Todo
                        is_static=False  # Todo
                    )

        elif isinstance(parent, Enum):
            name = node.lvalues[0].name
            id_ = self.__get_id(name)

            EnumInstance(
                id=f"{id_}/{name}",
                name=name,
                value=node.rvalue.value
            )

        if assignment is None:
            raise AssertionError("Wrong kind of assignment/attribute entered")
        self.__declaration_stack.append(assignment)

    def leave_assignmentstmt(self, _: AssignmentStmt) -> None:
        """Assignments are attributes or enum instances"""
        assignment = self.__declaration_stack.pop()

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            if isinstance(assignment, Attribute):
                if isinstance(parent, Module):
                    self.api.add_attribute(assignment)
                    parent.add_attribute(assignment)
                elif isinstance(parent, Class):
                    self.api.add_attribute(assignment)
                    parent.add_attribute(assignment)

            elif isinstance(assignment, EnumInstance):
                if isinstance(parent, Enum):
                    self.api.add_enum_instance(assignment)
                    parent.add_enum_instance(assignment)

            else:
                raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

    def enter_returnstmt(self, node: ReturnStmt) -> None:
        id_ = self.__get_id("result")

        result = Result(
            id=id_,
            type_=node.type.ret_type,  # Todo
            docstring=""  # todo
        )
        self.__declaration_stack.append(result)

    def leave_returnstmt(self, _: ReturnStmt) -> None:
        result = self.__declaration_stack.pop()
        if not isinstance(result, Result):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested functions for now
            if isinstance(parent, Function):
                self.api.add_result(result)
                parent.set_result(result)

    # ############################## Utilities ############################## #

    def is_public(self, name: str, qualified_name: str) -> bool:
        if name.startswith("_") and not name.endswith("__"):
            return False

        if qualified_name in self.reexported:
            return True

        parent = self.__declaration_stack[-1]
        if isinstance(parent, Class):
            # Containing class is re-exported (always false if the current API element is not a method) Todo
            if parent_qualified_name(qualified_name) in self.reexported:
                return True

            if name == "__init__":
                return parent.is_public

        # The slicing is necessary so __init__ functions are not excluded (already handled in the first condition). Todo
        return all(not it.startswith("_") for it in qualified_name.split(".")[:-1])

    def __get_id(self, name: str) -> str:
        segments = [self.api.package]
        segments += [it.name for it in self.__declaration_stack]
        segments += [name]

        return "/".join(segments)
