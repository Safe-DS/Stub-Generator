from types import NoneType

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
    StrExpr,
    CallExpr,
    Expression,
    NameExpr,
    IntExpr,
    FloatExpr,
    ComplexExpr,
    SetExpr,
    DictExpr,
    ListExpr,
    SetComprehension,
    ListComprehension,
    DictionaryComprehension,
    BytesExpr,
    TupleExpr,
    Var
)
from mypy.types import UnboundType, get_proper_type

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
    Literal,
    Type
)
from ._names import parent_qualified_name

from safeds_stubgen.docstring_parsing import (
    AbstractDocstringParser,
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring
)


# Todo
#  1. How to handle multiple docstrings
#  2. Attribute Types: Mehrere Typen? Gucken wir uns nur den type hint Typ an, oder auch den value Typ?
#  3. Type Klasse: Wenn kein Type Hint, dann sollte da kein Typ sein, also None!
class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.reexported: dict[str, list[str]] = {}
        self.api: API = api
        self.__declaration_stack: list[
            Module | Class | Function | Enum | list[Attribute | EnumInstance] | list[Result]
        ] = []

    def enter_moduledef(self, node: MypyFile) -> None:
        id_ = self.__get_id(node.name)
        qualified_imports: list[QualifiedImport] = []
        wildcard_imports: list[WildcardImport] = []
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
            wildcard_imports=wildcard_imports
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
                docstring = ClassDocstring("", definition.expr.value)  # Todo Future Docstring

        # superclasses
        # Todo Aliase werden noch nicht aufgelöst -> Such nach einer mypy Funktion die die Typen auflöst
        #  irgendwas im zusammenhand mit "type" suchen bzw auflösen von aliasen
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
                docstring = FunctionDocstring("", definition.expr.value)  # Todo

        # Function args
        arguments: list[Parameter] = []
        if getattr(node, "arguments", None) is not None:
            arguments = self.parse_parameter_data(node, function_id)

        function = Function(
            id=function_id,
            name=node.name,
            docstring=docstring if docstring is not None else FunctionDocstring(),
            is_public=is_public,
            is_static=is_static,
            reexported_by=self.reexported.get(qname, []),  # todo
            parameters=arguments,
            results=[]
        )
        self.__declaration_stack.append(function)

    def leave_funcdef(self, _: FuncDef) -> None:
        function = self.__declaration_stack.pop()
        if not isinstance(function, Function):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Add the data to the API class
            self.api.add_function(function)
            for parameter in function.parameters:
                self.api.add_parameter(parameter)

            # Ignore nested functions for now
            if isinstance(parent, Module):
                parent.add_function(function)
            elif isinstance(parent, Class):
                if function.name == "__init__":
                    parent.add_constructor(function)
                else:
                    parent.add_method(function)

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
        assignments: list[Attribute | EnumInstance] = []

        if isinstance(parent, Class):
            if hasattr(node.lvalues[0], "name"):
                lvalue = node.lvalues[0]
                assignments.append(
                    self.create_attribute(lvalue, is_static=True)
                )

            elif hasattr(node.lvalues[0], "items"):
                lvalues = [item for item in node.lvalues[0].items]
                for lvalue in lvalues:
                    assignments.append(
                        self.create_attribute(lvalue, is_static=True)
                    )
        elif isinstance(parent, Function) and parent.name == "__init__":
            pass  # Todo
        elif isinstance(parent, Enum):
            name = node.lvalues[0].name
            id_ = self.__get_id(name)

            assignments.append(EnumInstance(
                id=f"{id_}/{name}",
                name=name,
                value=node.rvalue.value
            ))
        # Todo Attr. von Modulen komplett ignorieren
        elif isinstance(parent, Module):
            pass

        self.__declaration_stack.append(assignments)

    def leave_assignmentstmt(self, _: AssignmentStmt) -> None:
        """Assignments are attributes or enum instances"""
        assignments: list[Attribute | EnumInstance] = self.__declaration_stack.pop()

        if not isinstance(assignments, list):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            for assignment in assignments:
                if isinstance(assignment, Attribute):
                    if isinstance(parent, Module):
                        self.api.add_attribute(assignment)
                    elif isinstance(parent, Class):
                        self.api.add_attribute(assignment)
                        parent.add_attribute(assignment)

                elif isinstance(assignment, EnumInstance):
                    if isinstance(parent, Enum):
                        self.api.add_enum_instance(assignment)
                        parent.add_enum_instance(assignment)

    def enter_returnstmt(self, node: ReturnStmt) -> None:
        return_expr = node.expr
        results: list[Result] = []
        if return_expr is None:
            name = f"result_{node.line}_{node.column}_{node.end_column}"
            results.append(Result(
                id=self.__get_id(name),
                name=name,
                types=[Type(kind=None, name="None")],
                docstring=ResultDocstring("")  # Todo
            ))
        elif isinstance(return_expr, TupleExpr):
            # tuples count as multiple results
            for item in return_expr.items:
                results.append(
                    self.create_result(item)
                )
        else:
            results.append(
                self.create_result(return_expr)
            )

        self.__declaration_stack.append(results)

    def leave_returnstmt(self, _: ReturnStmt) -> None:
        results = self.__declaration_stack.pop()
        if not isinstance(results, list):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested functions for now
            if isinstance(parent, Function):
                self.api.add_result(results)
                parent.add_results(results)

    # ############################## Utilities ############################## #

    def create_attribute(self, lvalue, is_static=False):
        # Todo Attribute description
        name = lvalue.name
        qname = lvalue.fullname
        if qname == name and getattr(lvalue, "node", None) is not None:
            qname = lvalue.node.fullname

        # Todo Attributes können mehrere typen haben -> Handling noch nicht da!
        attribute_type: Type | None = self.create_var_type(lvalue)

        return Attribute(
            id=self.__get_id(name),
            name=name,
            types=[attribute_type],
            is_public=self.is_public(name, qname),
            is_static=is_static
        )

    @staticmethod
    def parse_parameter_data(node: FuncDef, function_id: str) -> list[Parameter]:
        arguments: list[Parameter] = []

        for argument in node.arguments:
            arg_name = argument.variable.name
            arg_type = argument.variable.type
            arg_kind = argument.kind  # Todo

            default_value: Literal | None = None
            initializer = argument.initializer
            if initializer is not None:
                if not hasattr(initializer, "value"):
                    if initializer.name == "None":
                        value = None
                    else:
                        raise ValueError("No value found for parameter")
                else:
                    value = initializer.value
                # Todo Wie behandeln wir andere Fälle, also wenn der Typ nicht in dieser Liste ist? --> Ignorieren
                if type(value) in [str, bool, int, float, NoneType]:
                    default_value = Literal(value)

            # Todo Ein Parameter kann mehrere mögliche Typen haben -> Not handled yet!
            arguments.append(Parameter(
                id_=f"{function_id}/{arg_name}",
                name=arg_name,
                default_value=default_value,
                assigned_by=arg_kind,
                docstring=ParameterDocstring(),  # Todo
                types=[arg_type]
            ))

        return arguments

    # Todo Beide Create Type Funktionen sind noch nicht fertig
    @staticmethod
    def create_var_type(lvalue) -> Type | None:
        var_node: Var = lvalue.node
        if getattr(var_node, "is_inferred", True):
            return None

        proper_type = get_proper_type(var_node.type)
        type_str = str(proper_type)
        kind_name = type_str.split(".")[-1]

        if kind_name == "str":
            type_ = str
        elif kind_name == "float":
            type_ = float
        elif kind_name == "bool":
            type_ = bool
        elif kind_name == "int":
            type_ = int
        elif kind_name == "None":
            type_ = None
        else:
            # special case where the var type is a user defined type and not a buildin type
            type_ = kind_name

        if isinstance(type_, str):
            # handle the special cases
            type_name = type_
        else:
            type_name = type_.__name__ if type_ is not None else "None"

        if type_ not in [str, bool, int, float, None]:
            type_kind = UnboundType(name=type_name)
        else:
            type_kind = type_

        return Type(
            kind=type_kind,
            name=type_name
        )

    @staticmethod
    def create_type_from_expression(expression) -> Type:
        if isinstance(expression, StrExpr):
            type_ = str
        elif isinstance(expression, IntExpr):
            type_ = int
        elif isinstance(expression, FloatExpr):
            type_ = float
        elif isinstance(expression, ComplexExpr):
            type_ = complex
        elif isinstance(expression, SetExpr) or isinstance(expression, SetComprehension):
            type_ = set
        elif isinstance(expression, DictExpr) or isinstance(expression, DictionaryComprehension):
            type_ = dict
        elif isinstance(expression, ListExpr) or isinstance(expression, ListComprehension):
            type_ = list
        elif isinstance(expression, BytesExpr):
            type_ = bytes
        elif isinstance(expression, TupleExpr):
            type_ = tuple
        elif isinstance(expression, NameExpr):
            if expression.fullname in ["builtins.False", "builtins.True"]:
                type_ = bool
            elif expression.fullname == "builtins.None":
                type_ = None
            else:
                # special case where the return_expr is a user defined type and not a buildin type
                type_ = expression.node.name
        elif isinstance(expression, CallExpr):
            # special case where the return_expr is a user defined type and not a buildin type
            type_ = expression.callee.node.name
        else:
            # Todo: Frage Fallback
            type_ = expression.__class__

        if isinstance(type_, str):
            # handle the special cases
            type_name = type_
        else:
            type_name = type_.__name__ if type_ is not None else "None"

        if type_ not in [str, bool, int, float, None]:
            type_kind = UnboundType(name=type_name)
        else:
            type_kind = type_

        return Type(
            kind=type_kind,
            name=type_name,
        )

    def create_result(self, return_expr: Expression) -> Result:
        # Todo Result name fortlaufend hochzählen
        name = f"result_{return_expr.line}_{return_expr.column}_{return_expr.end_column}"
        id_ = self.__get_id(name)

        return_type = self.create_type_from_expression(return_expr)

        # Todo Result can have multiple types -> To handle!
        return Result(
            id=id_,
            types=[return_type],
            name=name,
            docstring=ResultDocstring("")  # todo
        )

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
