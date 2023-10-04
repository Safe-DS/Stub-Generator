from __future__ import annotations

from types import NoneType
from typing import TYPE_CHECKING

import mypy.types as mp_types
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

import safeds_stubgen.api_analyzer._types as sds_types
from safeds_stubgen.docstring_parsing import AbstractDocstringParser

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
from ._mypy_helpers import get_classdef_definitions, get_mypyfile_definitions, mypy_type_to_abstract_type

if TYPE_CHECKING:
    from mypy.types import Instance


# Todo Docstring / description
class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.reexported: dict[str, list[Module]] = {}
        self.api: API = api
        self.__declaration_stack: list[
            Module | Class | Function | Enum | list[Attribute | EnumInstance | Result]
            ] = []

    def enter_moduledef(self, node: MypyFile) -> None:
        is_package = node.path.endswith("__init__.py")

        qualified_imports: list[QualifiedImport] = []
        wildcard_imports: list[WildcardImport] = []
        docstring = ""

        # We don't need to check functions, classes and assignments, since the ast walker will already check them
        child_definitions = [
            _definition for _definition in get_mypyfile_definitions(node)
            if _definition.__class__.__name__ not in
            ["FuncDef", "Decorator", "ClassDef", "AssignmentStmt"]
        ]

        for definition in child_definitions:
            # Imports
            if isinstance(definition, Import):
                for import_name, import_alias in definition.ids:
                    qualified_imports.append(
                        QualifiedImport(import_name, import_alias),
                    )

            elif isinstance(definition, ImportFrom):
                for import_name, import_alias in definition.names:
                    qualified_imports.append(
                        QualifiedImport(
                            f"{definition.id}.{import_name}",
                            import_alias,
                        ),
                    )

            elif isinstance(definition, ImportAll):
                wildcard_imports.append(
                    WildcardImport(definition.id),
                )

            # Docstring
            elif isinstance(definition, ExpressionStmt) and isinstance(definition.expr, StrExpr):
                docstring = definition.expr.value

        # If we are checking a package node.name will be the package name, but since we get import information from
        # the __init__.py file we set the name to __init__
        if is_package:
            name = "__init__"
        else:
            name = node.name
        id_ = self.__get_id(name)

        # Remember module, so we can later add classes and global functions
        module = Module(
            id_=id_,
            name=name,
            docstring=docstring,
            qualified_imports=qualified_imports,
            wildcard_imports=wildcard_imports,
        )

        if is_package:
            self.add_reexports(module)

        self.__declaration_stack.append(module)

    def leave_moduledef(self, _: MypyFile) -> None:
        module = self.__declaration_stack.pop()
        if not isinstance(module, Module):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        self.api.add_module(module)

    def enter_classdef(self, node: ClassDef) -> None:
        id_ = self.__get_id(node.name)
        name = node.name

        # Get docstring
        docstring = self.docstring_parser.get_class_documentation(node)

        # superclasses
        # Todo Aliase werden noch nicht aufgelöst -> Such nach einer mypy Funktion die die Typen auflöst
        #  irgendwas im zusammenhand mit "type" suchen bzw auflösen von aliasen
        superclasses = [
            superclass.fullname
            for superclass in node.base_type_exprs
        ]

        # Get reexported data
        reexported_by = self.get_reexported_by(name)

        # Get constructor docstring
        definitions = get_classdef_definitions(node)
        constructor_fulldocstring = ""
        for definition in definitions:
            if isinstance(definition, FuncDef) and definition.name == "__init__":
                constructor_docstring = self.docstring_parser.get_function_documentation(definition)
                constructor_fulldocstring = constructor_docstring.full_docstring

        # Remember class, so we can later add methods
        class_ = Class(
            id=id_,
            name=name,
            superclasses=superclasses,
            is_public=self.is_public(node.name, name),
            docstring=docstring,
            reexported_by=reexported_by,
            constructor_fulldocstring=constructor_fulldocstring,
        )
        self.__declaration_stack.append(class_)

    def leave_classdef(self, _: ClassDef) -> None:
        class_ = self.__declaration_stack.pop()
        if not isinstance(class_, Class):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            if isinstance(parent, Module | Class):
                self.api.add_class(class_)
                parent.add_class(class_)

    def enter_funcdef(self, node: FuncDef) -> None:
        name = node.name
        function_id = self.__get_id(name)

        is_public = self.is_public(name, node.fullname)
        is_static = node.is_static

        # Get docstring
        docstring = self.docstring_parser.get_function_documentation(node)

        # Function args
        arguments: list[Parameter] = []
        if getattr(node, "arguments", None) is not None:
            arguments = self.parse_parameter_data(node, function_id)

        # Create results
        results = self.create_result(node, function_id)

        # Get reexported data
        reexported_by = self.get_reexported_by(name)

        # Create and add Function to stack
        function = Function(
            id=function_id,
            name=name,
            docstring=docstring,
            is_public=is_public,
            is_static=is_static,
            results=results,
            reexported_by=reexported_by,
            parameters=arguments,
        )
        self.__declaration_stack.append(function)

    def leave_funcdef(self, _: FuncDef) -> None:
        function = self.__declaration_stack.pop()
        if not isinstance(function, Function):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Add the data of the function and its results to the API class
            self.api.add_function(function)
            self.api.add_results(function.results)

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
        enum = Enum(
            id=id_,
            name=node.name,
            docstring=self.docstring_parser.get_class_documentation(node),
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
        # Assignments are attributes or enum instances
        parent = self.__declaration_stack[-1]
        assignments: list[Attribute | EnumInstance] = []

        for lvalue in node.lvalues:
            if isinstance(parent, Class):
                for assignment in self.parse_attributes(lvalue, node.unanalyzed_type, is_static=True):
                    assignments.append(assignment)
            elif isinstance(parent, Function) and parent.name == "__init__":
                try:
                    grand_parent = self.__declaration_stack[-2]
                except IndexError:
                    # If the function has no parent (and is therefore not a class method) ignore the attributes
                    grand_parent = None

                if grand_parent is not None and isinstance(grand_parent, Class) and not isinstance(lvalue, NameExpr):
                    # Ignore non instance attributes in __init__ classes
                    for assignment in self.parse_attributes(lvalue, node.unanalyzed_type, is_static=False):
                        assignments.append(assignment)

            elif isinstance(parent, Enum):
                names = []
                if hasattr(lvalue, "items"):
                    for item in lvalue.items:
                        names.append(item.name)
                else:
                    names.append(lvalue.name)

                for name in names:
                    assignments.append(EnumInstance(
                        id=f"{parent.id}/{name}",
                        name=name,
                    ))

        self.__declaration_stack.append(assignments)

    def leave_assignmentstmt(self, _: AssignmentStmt) -> None:
        # Assignments are attributes or enum instances
        assignments: list[Attribute | EnumInstance] = self.__declaration_stack.pop()

        if not isinstance(assignments, list):
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]
            assert isinstance(parent, Function | Class | Enum)

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
                    raise TypeError("Unexpected value type for assignments")

    # ############################## Utilities ############################## #

    # #### Result utilities

    def create_result(self, node: FuncDef, function_id: str) -> list[Result]:
        ret_type = None
        if getattr(node, "type", None) and not isinstance(node.type.ret_type, mp_types.NoneType):
            ret_type = mypy_type_to_abstract_type(node.type.ret_type)

        if ret_type is None:
            return []

        results = []
        parent = self.__declaration_stack[-1]
        docstring = self.docstring_parser.get_result_documentation(node, parent)
        if isinstance(ret_type, sds_types.TupleType):
            for i, type_ in enumerate(ret_type.types):
                name = f"result_{i + 1}"
                results.append(Result(
                    id=f"{function_id}/{name}",
                    type=type_,
                    name=name,
                    docstring=docstring,
                ))
        else:
            name = "result_1"
            results.append(Result(
                id=f"{function_id}/{name}",
                type=ret_type,
                name=name,
                docstring=docstring,
            ))

        return results

    # #### Attribute utilities

    def parse_attributes(
        self,
        lvalue: NameExpr | MemberExpr,
        unanalyzed_type: mp_types.UnboundType,
        is_static=True,
    ) -> list[Attribute]:
        attributes: list[Attribute] = []

        if hasattr(lvalue, "name"):
            if self.check_attribute_already_defined(lvalue, lvalue.name):
                return attributes

            attributes.append(
                self.create_attribute(lvalue, unanalyzed_type, is_static),
            )

        elif hasattr(lvalue, "items"):
            lvalues = list(lvalue.items)
            for lvalue_ in lvalues:
                if self.check_attribute_already_defined(lvalue_, lvalue_.name):
                    continue

                attributes.append(
                    self.create_attribute(lvalue_, unanalyzed_type, is_static),
                )

        return attributes

    def check_attribute_already_defined(self, lvalue: NameExpr, value_name: str) -> bool:
        # If node is None, it's possible that the attribute was already defined once
        if lvalue.node is None:
            parent = self.__declaration_stack[-1]
            if isinstance(parent, Function):
                parent = self.__declaration_stack[-2]

            for attribute in parent.attributes:
                if value_name == attribute.name:
                    return True

            raise ValueError(f"The attribute {value_name} has no value.")
        return False

    def create_attribute(
        self,
        attribute: NameExpr | MemberExpr,
        unanalyzed_type: mp_types.UnboundType,
        is_static: bool,
    ) -> Attribute:
        # Get name and qname
        name = attribute.name
        qname = getattr(attribute, "fullname", "")
        if qname in (name, "") and attribute.node is not None:
            qname = attribute.node.fullname

        # Check if there is a type hint and get its value
        attribute_type: Instance | None = None
        if isinstance(attribute, MemberExpr):
            # Sometimes the is_inferred value is True even thoght has_explicit_value is False, thus the second check
            if not attribute.node.is_inferred or (attribute.node.is_inferred and not attribute.node.has_explicit_value):
                attribute_type: Instance = attribute.node.type
        elif isinstance(attribute, NameExpr):
            if not attribute.node.explicit_self_type and not attribute.node.is_inferred:
                attribute_type: Instance = attribute.node.type

                # We need to get the unanalyzed_type for lists, since mypy is not able to check information regarding
                #  list item types
                if hasattr(attribute_type, "type") and attribute_type.type.fullname == "builtins.list":
                    attribute_type.args = unanalyzed_type.args

        else:
            raise TypeError("Attribute has an unexpected type.")

        type_ = None
        if attribute_type is not None:
            type_ = mypy_type_to_abstract_type(attribute_type)

        # Get docstring
        parent = self.__declaration_stack[-1]
        if isinstance(parent, Function) and parent.name == "__init__":
            parent = self.__declaration_stack[-2]
        assert isinstance(parent, Class)
        docstring = self.docstring_parser.get_attribute_documentation(parent, name)

        # Remove __init__ for attribute ids
        id_ = self.__get_id(name).replace("__init__/", "")

        return Attribute(
            id=id_,
            name=name,
            type=type_,
            is_public=self.is_public(name, qname),
            is_static=is_static,
            docstring=docstring,
        )

    # #### Parameter utilities

    def parse_parameter_data(self, node: FuncDef, function_id: str) -> list[Parameter]:
        arguments: list[Parameter] = []

        for argument in node.arguments:
            arg_name = argument.variable.name
            arg_type = mypy_type_to_abstract_type(argument.variable.type)
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

                if type(value) in {str, bool, int, float, NoneType}:
                    default_value = value
                    is_optional = True

            parent = self.__declaration_stack[-1]
            parent = parent if isinstance(parent, Class) else None
            docstring = self.docstring_parser.get_parameter_documentation(
                function_node=node,
                parameter_name=arg_name,
                parameter_assigned_by=arg_kind,
                parent_class=parent
            )

            arguments.append(Parameter(
                id=f"{function_id}/{arg_name}",
                name=arg_name,
                is_optional=is_optional,
                default_value=default_value,
                assigned_by=arg_kind,
                docstring=docstring,
                type=arg_type,
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

    # #### Reexport utilities

    def get_reexported_by(self, name: str) -> list[Module]:
        # Get the uppermost module and the path to the current node
        parents = []
        parent = None
        i = 1
        while not isinstance(parent, Module):
            parent = self.__declaration_stack[-i]
            parents.append(parent.name)
            i += 1
        path = [*list(reversed(parents)), name]

        # Check if there is a reexport entry for each item in the path to the current module
        reexported_by = set()
        for i in range(len(path)):
            reexport_name = ".".join(path[:i + 1])
            if reexport_name in self.reexported:
                for mod in self.reexported[reexport_name]:
                    reexported_by.add(mod)

        return list(reexported_by)

    def add_reexports(self, module: Module) -> None:
        for qualified_import in module.qualified_imports:
            name = qualified_import.qualified_name
            if name in self.reexported:
                if module not in self.reexported[name]:
                    self.reexported[name].append(module)
            else:
                self.reexported[name] = [module]

        for wildcard_import in module.wildcard_imports:
            name = wildcard_import.module_name
            if name in self.reexported:
                if module not in self.reexported[name]:
                    self.reexported[name].append(module)
            else:
                self.reexported[name] = [module]

    # #### Misc. utilities

    def is_public(self, name: str, qualified_name: str) -> bool:
        if name.startswith("_") and not name.endswith("__"):
            return False

        for reexported_item in self.reexported:
            if reexported_item.endswith(f".{name}"):
                return True

        parent = self.__declaration_stack[-1]
        if isinstance(parent, Class):
            # Containing class is re-exported (always false if the current API element is not a method)
            if parent.reexported_by:
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