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
        self.__declaration_stack: list[Module | Class | Function | Enum] = []

    def __get_id(self, name: str) -> str:
        segments = [self.api.package]
        segments += [it.name for it in self.__declaration_stack]
        segments += [name]

        return "/".join(segments)

    def enter_moduledef(self, module_node: MypyFile) -> None:
        id_ = self.__get_id(module_node.name)
        qualified_imports: list[QualifiedImport] = []
        wildcard_imports: list[WildcardImport] = []
        attributes: list[Attribute] = []
        docstring = ""

        # We don't need to check functions and classes, since the ast walker will check them anyway
        child_definitions = [
            _definition for _definition in module_node.defs
            if _definition.__class__.__name__ not in
            ["FuncDef", "Decorator", "ClassDef"]
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

            # Attributes
            elif isinstance(definition, AssignmentStmt):
                if hasattr(definition.lvalues[0], "name"):
                    attr_name = definition.lvalues[0].name

                    attributes.append(Attribute(
                        id=f"{id_}/{attr_name}",
                        name=attr_name,
                        type=definition.type
                    ))

                elif hasattr(definition.lvalues[0], "items"):
                    attr_names = [item.name for item in definition.lvalues[0].items]
                    for attr_name in attr_names:
                        attributes.append(Attribute(
                            id=f"{id_}/{attr_name}",
                            name=attr_name,
                            type=None
                        ))

        # Remember module, so we can later add classes and global functions
        module = Module(
            id_=id_,
            name=module_node.fullname,
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

    def enter_classdef(self, class_node: ClassDef) -> None:
        id_ = self.__get_id(class_node.name)
        name = class_node.name
        docstring: ClassDocstring | None = None

        for definition in class_node.defs.body:
            # Docstring
            if isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                # Todo
                docstring = ClassDocstring(definition.expr.value, definition.expr.value)

        # superclasses
        # Todo Aliase werden noch nicht aufgelöst
        superclasses = [
            superclass.fullname
            for superclass in class_node.base_type_exprs
        ]

        # Remember class, so we can later add methods
        class_ = Class(
            id=id_,
            name=name,
            superclasses=superclasses,
            is_public=self.is_public(class_node.name, name),
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

    def enter_funcdef(self, function_node: FuncDef) -> None:
        function_id = self.__get_id(function_node.name)
        docstring: FunctionDocstring | None = None
        qname = function_node.fullname
        is_public = self.is_public(function_node.name, qname)
        is_static = function_node.is_static
        function_result = None

        for definition in function_node.body.body:
            # Docstring
            if isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = FunctionDocstring(definition.expr.value, definition.expr.value)  # Todo

            # Function Result
            elif isinstance(definition, ReturnStmt):
                function_result = Result(
                    id=f"{function_id}/result",
                    type_=function_node.type.ret_type,  # Todo
                    docstring=""  # todo
                )

        # Function args
        arguments: list[Parameter] = []
        if function_node.type is not None:
            argument_info: list[tuple] = []
            if function_node.arguments is not None:
                argument_info = list(
                    zip(
                        function_node.type.arg_names,
                        function_node.type.arg_types
                    )
                )

            for arg_counter, arg in enumerate(function_node.arguments):
                arg_name = argument_info[arg_counter][0]
                arg_type = argument_info[arg_counter][1]
                # Todo "has_default_value" Feld, oder wie differenzieren wir?

                default_value = None
                if arg.initializer is not None:
                    default_value = getattr(arg.initializer, 'value', None)

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
            name=function_node.name,
            reexported_by=self.reexported.get(qname, []),  # todo
            docstring=docstring if docstring is not None else FunctionDocstring(),
            is_public=is_public,
            is_static=is_static,
            parameters=arguments,
            result=function_result
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

    def enter_enumdef(self, enum_node: ClassDef) -> None:
        id_ = self.__get_id(enum_node.name)
        docstring: ClassDocstring | None = None
        enum_instances: list[EnumInstance] = []

        for definition in enum_node.defs.body:
            # Instances
            if isinstance(definition, AssignmentStmt):
                instance_name = definition.lvalues[0].name

                enum_instances.append(EnumInstance(
                    id=f"{id_}/{instance_name}",
                    name=instance_name,
                    value=definition.rvalue.value,
                ))

            # Docstring
            elif isinstance(definition, ExpressionStmt) and \
                    isinstance(definition.expr, StrExpr):
                docstring = ClassDocstring(definition.expr.value, definition.expr.value)  # Todo

        enum = Enum(
            id=id_,
            name=enum_node.name,
            docstring=docstring if docstring is not None else FunctionDocstring(),
            instances=enum_instances
        )
        self.__declaration_stack.append(enum)

    def leave_enumdef(self):
        enum = self.__declaration_stack.pop()
        if not isinstance(enum, Enum):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested functions for now
            if isinstance(parent, Module):
                self.api.add_enum(enum)
                parent.add_enum(enum)

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
