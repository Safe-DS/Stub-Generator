from types import NoneType

from mypy.nodes import (
    ArgKind,
    Argument,
    AssignmentStmt,
    CallExpr,
    ClassDef,
    ExpressionStmt,
    FuncDef,
    Import,
    ImportAll,
    ImportFrom,
    MemberExpr,
    MypyFile,
    NameExpr,
    StrExpr,
)
from mypy.types import get_proper_type, Instance

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
    ParameterDocstring,
    ResultDocstring
)


# Todo Docstring / description & Reexport field handling
class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.reexported: dict[str, list[str]] = {}
        self.api: API = api
        self.__declaration_stack: list[
            Module | Class | Function | Enum | list[Attribute | EnumInstance] | Result
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
                docstring = ClassDocstring("", definition.expr.value)

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
            reexported_by=self.reexported.get(name, []),
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
        name = node.name
        qname = node.fullname
        function_id = self.__get_id(name)

        docstring: FunctionDocstring | None = None

        is_public = self.is_public(name, qname)
        is_static = node.is_static

        for definition in node.body.body:
            # Docstring
            if isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = FunctionDocstring("", definition.expr.value)

        # Function args
        arguments: list[Parameter] = []
        if getattr(node, "arguments", None) is not None:
            arguments = self.parse_parameter_data(node, function_id)

        # Create results
        ret_type = "Any"
        if hasattr(node, "type"):
            ret_type = str(node.type.ret_type)

        result = Result(
            id=f"{function_id}/result",
            type=ret_type,
            name="result",
            docstring=ResultDocstring("")
        )

        # Create and add Function to stack
        function = Function(
            id=function_id,
            name=name,
            docstring=docstring if docstring is not None else FunctionDocstring(),
            is_public=is_public,
            is_static=is_static,
            result=result,
            reexported_by=self.reexported.get(qname, []),
            parameters=arguments,
        )
        self.__declaration_stack.append(function)

    def leave_funcdef(self, _: FuncDef) -> None:
        function = self.__declaration_stack.pop()
        if not isinstance(function, Function):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Add the data of the function and its result to the API class
            self.api.add_function(function)
            self.api.add_result(function.result)

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
                docstring = ClassDocstring(definition.expr.value, definition.expr.value)

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
        """Assignments are attributes or enum instances"""
        parent = self.__declaration_stack[-1]
        assignments: list[Attribute | EnumInstance] = []
        lvalue = node.lvalues[0]

        if isinstance(parent, Class):
            assignments = self.parse_attributes(lvalue, is_static=True)
        elif isinstance(parent, Function) and parent.name == "__init__":
            try:
                grand_parent = self.__declaration_stack[-2]
            except IndexError:
                # If the function has no parent (and is therefore not a class method) ignore the attributes
                grand_parent = None

            if grand_parent is not None and isinstance(grand_parent, Class):
                # Ignore non instance attributes in __init__ classes
                if not isinstance(lvalue, NameExpr):
                    assignments = self.parse_attributes(lvalue, is_static=False)

        elif isinstance(parent, Enum):
            name = lvalue.name
            id_ = self.__get_id(name)

            assignments.append(EnumInstance(
                id=f"{id_}/{name}",
                name=name
            ))

        self.__declaration_stack.append(assignments)

    def leave_assignmentstmt(self, _: AssignmentStmt) -> None:
        """Assignments are attributes or enum instances"""
        assignments: list[Attribute | EnumInstance] = self.__declaration_stack.pop()

        if not isinstance(assignments, list):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]
            assert isinstance(parent, (Function, Class, Enum))

            for assignment in assignments:
                if isinstance(assignment, Attribute):
                    if isinstance(parent, Function):
                        self.api.add_attribute(assignment)
                        # Add the attributes to the (grand)parent class
                        grandparent = self.__declaration_stack[-2]
                        grandparent.add_attribute(assignment)
                    elif isinstance(parent, Class):
                        self.api.add_attribute(assignment)
                        parent.add_attribute(assignment)

                elif isinstance(assignment, EnumInstance):
                    if isinstance(parent, Enum):
                        self.api.add_enum_instance(assignment)
                        parent.add_enum_instance(assignment)

                else:
                    raise ValueError("Unexpected value type for assignments")

    # ############################## Utilities ############################## #

    def parse_attributes(self, lvalue: NameExpr | MemberExpr, is_static=True) -> list[Attribute]:
        attributes: list[Attribute] = []

        if hasattr(lvalue, "name"):
            attributes.append(
                self.create_attribute(lvalue, is_static)
            )

        elif hasattr(lvalue, "items"):
            lvalues = [item for item in lvalue.items]
            for lvalue in lvalues:
                attributes.append(
                    self.create_attribute(lvalue, is_static)
                )

        return attributes

    def create_attribute(self, attribute, is_static: bool) -> Attribute:
        # Get name and qname
        name = attribute.name
        qname = getattr(attribute, "fullname", "")
        if (qname == name or qname == "") and attribute.node is not None:
            qname = attribute.node.fullname

        # Todo Type parsing of get_proper_type result
        # Check if there is a type hint and get its value
        attribute_type: Instance | None = None
        if isinstance(attribute, MemberExpr):
            if not attribute.node.is_inferred:
                attribute_type: Instance = get_proper_type(attribute.node.type)
        elif isinstance(attribute, NameExpr):
            if not attribute.node.explicit_self_type:
                attribute_type: Instance = get_proper_type(attribute.node.type)
        else:
            raise ValueError("Attribute has an unexpected type.")

        return Attribute(
            id=self.__get_id(name),
            name=name,
            type=str(attribute_type),
            is_public=self.is_public(name, qname),
            is_static=is_static,
            description=""
        )

    def parse_parameter_data(self, node: FuncDef, function_id: str) -> list[Parameter]:
        arguments: list[Parameter] = []

        for argument in node.arguments:
            arg_name = argument.variable.name
            arg_type = argument.variable.type
            arg_kind = self.get_argument_kind(argument)

            default_value = None
            is_optional = False
            initializer = argument.initializer
            if initializer is not None:
                if not hasattr(initializer, "value"):
                    if isinstance(initializer, CallExpr):
                        # Special case when the default is a call expression
                        value = None
                    elif initializer.name == "None":
                        value = None
                    else:
                        raise ValueError("No value found for parameter")
                else:
                    value = initializer.value

                if type(value) in [str, bool, int, float, NoneType]:
                    default_value = value
                    is_optional = True

            arguments.append(Parameter(
                id=f"{function_id}/{arg_name}",
                name=arg_name,
                is_optional=is_optional,
                default_value=default_value,
                assigned_by=arg_kind,
                docstring=ParameterDocstring(),
                type=str(arg_type)
            ))

        return arguments

    @staticmethod
    def get_argument_kind(arg: Argument) -> ParameterAssignment:
        if arg.variable.is_self or arg.variable.is_cls:
            return ParameterAssignment.IMPLICIT
        elif arg.kind == ArgKind.ARG_POS and arg.pos_only:
            return ParameterAssignment.POSITION_ONLY
        elif arg.kind in (ArgKind.ARG_OPT, ArgKind.ARG_POS) and not arg.pos_only:
            return ParameterAssignment.POSITION_OR_NAME
        elif arg.kind == ArgKind.ARG_STAR:
            return ParameterAssignment.POSITIONAL_VARARG
        elif arg.kind in (ArgKind.ARG_NAMED, ArgKind.ARG_NAMED_OPT):
            return ParameterAssignment.NAME_ONLY
        elif arg.kind == ArgKind.ARG_STAR2:
            return ParameterAssignment.NAMED_VARARG
        else:
            raise ValueError("Could not find an appropriate parameter assignment.")

    # Todo Test function after implementing reexported functionalities
    def is_public(self, name: str, qualified_name: str) -> bool:
        if name.startswith("_") and not name.endswith("__"):
            return False

        if qualified_name in self.reexported:
            return True

        parent = self.__declaration_stack[-1]
        if isinstance(parent, Class):
            # Containing class is re-exported (always false if the current API element is not a method)
            if parent_qualified_name(qualified_name) in self.reexported:
                return True

            if name == "__init__":
                return parent.is_public

        # The slicing is necessary so __init__ functions are not excluded (already handled in the first condition).
        return all(not it.startswith("_") for it in qualified_name.split(".")[:-1])

    def __get_id(self, name: str) -> str:
        segments = [self.api.package]
        segments += [it.name for it in self.__declaration_stack]
        segments += [name]

        return "/".join(segments)
