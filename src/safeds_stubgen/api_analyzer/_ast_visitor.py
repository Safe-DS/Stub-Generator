from __future__ import annotations

from copy import deepcopy
from types import NoneType
from typing import TYPE_CHECKING

import mypy.nodes as mp_nodes
import mypy.types as mp_types

import safeds_stubgen.api_analyzer._types as sds_types

from ._api import (
    API,
    Attribute,
    Class,
    Enum,
    EnumInstance,
    Function,
    Module,
    Parameter,
    QualifiedImport,
    Result,
    TypeParameter,
    VarianceKind,
    WildcardImport,
)
from ._mypy_helpers import (
    find_return_stmts_recursive,
    get_argument_kind,
    get_classdef_definitions,
    get_funcdef_definitions,
    get_mypyfile_definitions,
    has_correct_type_of_any,
    mypy_expression_to_python_value,
    mypy_expression_to_sds_type,
    mypy_variance_parser,
)

if TYPE_CHECKING:
    from safeds_stubgen.api_analyzer._types import AbstractType
    from safeds_stubgen.docstring_parsing import AbstractDocstringParser, ResultDocstring


class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API, aliases: dict[str, set[str]]) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.api: API = api
        self.__declaration_stack: list[Module | Class | Function | Enum | list[Attribute | EnumInstance]] = []
        self.aliases = aliases
        self.mypy_file: mp_nodes.MypyFile | None = None
        # We gather type var types used as a parameter type in a function
        self.type_var_types: set[sds_types.TypeVarType] = set()

    def enter_moduledef(self, node: mp_nodes.MypyFile) -> None:
        self.mypy_file = node
        is_package = node.path.endswith("__init__.py")

        qualified_imports: list[QualifiedImport] = []
        wildcard_imports: list[WildcardImport] = []
        docstring = ""

        # We don't need to check functions, classes and assignments, since the ast walker will already check them
        child_definitions = [
            _definition
            for _definition in get_mypyfile_definitions(node)
            if _definition.__class__.__name__ not in ["FuncDef", "Decorator", "ClassDef", "AssignmentStmt"]
        ]

        # Imports
        for import_ in node.imports:
            if isinstance(import_, mp_nodes.Import):
                for import_name, import_alias in import_.ids:
                    qualified_imports.append(
                        QualifiedImport(import_name, import_alias),
                    )

            elif isinstance(import_, mp_nodes.ImportFrom):
                import_id = f"{import_.id}." if import_.id else ""
                for import_name, import_alias in import_.names:
                    qualified_imports.append(
                        QualifiedImport(
                            f"{import_id}{import_name}",
                            import_alias,
                        ),
                    )

            elif isinstance(import_, mp_nodes.ImportAll):
                wildcard_imports.append(
                    WildcardImport(import_.id),
                )

        # Search for a Docstring
        for definition in child_definitions:
            if isinstance(definition, mp_nodes.ExpressionStmt) and isinstance(definition.expr, mp_nodes.StrExpr):
                docstring = definition.expr.value
                break

        # Create module id to get the full path
        id_ = node.fullname.replace(".", "/")

        # If we are checking a package node.name will be the package name, but since we get import information from
        # the __init__.py file we set the name to __init__
        name = "__init__" if is_package else node.name

        # Remember module, so we can later add classes and global functions
        module = Module(
            id_=id_,
            name=name,
            docstring=docstring,
            qualified_imports=qualified_imports,
            wildcard_imports=wildcard_imports,
        )

        if is_package:
            self._add_reexports(module)

        self.__declaration_stack.append(module)

    def leave_moduledef(self, _: mp_nodes.MypyFile) -> None:
        module = self.__declaration_stack.pop()
        if not isinstance(module, Module):  # pragma: no cover
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        self.api.add_module(module)

    def enter_classdef(self, node: mp_nodes.ClassDef) -> None:
        name = node.name
        id_ = self._create_id_from_stack(name)

        # Get docstring
        docstring = self.docstring_parser.get_class_documentation(node)

        # Variance
        # Special base classes like Generic[...] get moved to "removed_base_type_expr" during semantic analysis of mypy
        generic_exprs = []
        for base_type_expr in node.removed_base_type_exprs + node.base_type_exprs:
            base = getattr(base_type_expr, "base", None)
            base_name = getattr(base, "name", None)
            if base_name in {"Collection", "Generic", "Sequence"}:
                generic_exprs.append(base_type_expr)

        type_parameters = []
        if generic_exprs:
            # Can only be one, since a class can inherit "Generic" only one time
            generic_expr = getattr(generic_exprs[0], "index", None)

            if isinstance(generic_expr, mp_nodes.TupleExpr):
                generic_types = [item.node for item in generic_expr.items if hasattr(item, "node")]
            elif isinstance(generic_expr, mp_nodes.NameExpr):
                generic_types = [generic_expr.node]
            else:  # pragma: no cover
                raise TypeError("Unexpected type while parsing generic type.")

            for generic_type in generic_types:
                variance_type = mypy_variance_parser(generic_type.variance)
                variance_values: sds_types.AbstractType | None = None
                if variance_type == VarianceKind.INVARIANT:
                    values = [self.mypy_type_to_abstract_type(value) for value in generic_type.values]
                    if values:
                        variance_values = sds_types.UnionType(
                            [self.mypy_type_to_abstract_type(value) for value in generic_type.values],
                        )
                else:
                    upper_bound = generic_type.upper_bound
                    if upper_bound.__str__() != "builtins.object":
                        variance_values = self.mypy_type_to_abstract_type(upper_bound)

                type_parameters.append(
                    TypeParameter(
                        name=generic_type.name,
                        type=variance_values,
                        variance=variance_type,
                    ),
                )

        # superclasses
        superclasses = []
        inherits_from_exception = False
        for superclass in node.base_type_exprs:
            # Check for superclasses that inherit directly or transitively from Exception and remove them
            if (
                hasattr(superclass, "node")
                and isinstance(superclass.node, mp_nodes.TypeInfo)
                and self._inherits_from_exception(superclass.node)
            ):
                inherits_from_exception = True

            if hasattr(superclass, "fullname"):
                superclass_qname = superclass.fullname
                superclass_name = superclass_qname.split(".")[-1]

                # Check if the superclass name is an alias and find the real name
                if superclass_name in self.aliases:
                    _, superclass_alias_qname = self._find_alias(superclass_name)
                    superclass_qname = superclass_alias_qname if superclass_alias_qname else superclass_qname

                superclasses.append(superclass_qname)

        # Get reexported data
        reexported_by = self._get_reexported_by(name)

        # Get constructor docstring
        definitions = get_classdef_definitions(node)
        constructor_fulldocstring = ""
        for definition in definitions:
            if isinstance(definition, mp_nodes.FuncDef) and definition.name == "__init__":
                constructor_docstring = self.docstring_parser.get_function_documentation(definition)
                constructor_fulldocstring = constructor_docstring.full_docstring

        # Remember class, so we can later add methods
        class_ = Class(
            id=id_,
            name=name,
            superclasses=superclasses,
            is_public=self._is_public(node.name, name),
            docstring=docstring,
            reexported_by=reexported_by,
            constructor_fulldocstring=constructor_fulldocstring,
            inherits_from_exception=inherits_from_exception,
            type_parameters=type_parameters,
        )
        self.__declaration_stack.append(class_)

    def leave_classdef(self, _: mp_nodes.ClassDef) -> None:
        class_ = self.__declaration_stack.pop()
        if not isinstance(class_, Class):  # pragma: no cover
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            if isinstance(parent, Module | Class):
                self.api.add_class(class_)
                parent.add_class(class_)

    def enter_funcdef(self, node: mp_nodes.FuncDef) -> None:
        name = node.name
        function_id = self._create_id_from_stack(name)

        is_public = self._is_public(name, node.fullname)
        is_static = node.is_static

        # Get docstring
        docstring = self.docstring_parser.get_function_documentation(node)

        # Function args & TypeVar
        arguments: list[Parameter] = []
        type_var_types: list[sds_types.TypeVarType] = []
        # Reset the type_var_types list
        self.type_var_types = set()
        if getattr(node, "arguments", None) is not None:
            arguments = self._parse_parameter_data(node, function_id)

            if self.type_var_types:
                type_var_types = list(self.type_var_types)
                # Sort for the snapshot tests
                type_var_types.sort(key=lambda x: x.name)

        # Create results
        results = self._parse_results(node, function_id)

        # Get reexported data
        reexported_by = self._get_reexported_by(name)

        # Create and add Function to stack
        function = Function(
            id=function_id,
            name=name,
            docstring=docstring,
            is_public=is_public,
            is_static=is_static,
            is_class_method=node.is_class,
            is_property=node.is_property,
            results=results,
            reexported_by=reexported_by,
            parameters=arguments,
            type_var_types=type_var_types,
        )
        self.__declaration_stack.append(function)

    def leave_funcdef(self, _: mp_nodes.FuncDef) -> None:
        function = self.__declaration_stack.pop()
        if not isinstance(function, Function):  # pragma: no cover
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

    def enter_enumdef(self, node: mp_nodes.ClassDef) -> None:
        id_ = self._create_id_from_stack(node.name)
        self.__declaration_stack.append(
            Enum(
                id=id_,
                name=node.name,
                docstring=self.docstring_parser.get_class_documentation(node),
            ),
        )

    def leave_enumdef(self, _: mp_nodes.ClassDef) -> None:
        enum = self.__declaration_stack.pop()
        if not isinstance(enum, Enum):  # pragma: no cover
            raise AssertionError("Imbalanced push/pop on stack")  # noqa: TRY004

        if len(self.__declaration_stack) > 0:
            parent = self.__declaration_stack[-1]

            # Ignore nested functions for now
            if isinstance(parent, Module):
                self.api.add_enum(enum)
                parent.add_enum(enum)

    def enter_assignmentstmt(self, node: mp_nodes.AssignmentStmt) -> None:
        # Assignments are attributes or enum instances
        parent = self.__declaration_stack[-1]
        assignments: list[Attribute | EnumInstance] = []

        for lvalue in node.lvalues:
            if isinstance(parent, Class):
                for assignment in self._parse_attributes(lvalue, node.unanalyzed_type, is_static=True):
                    assignments.append(assignment)
            elif isinstance(parent, Function) and parent.name == "__init__":
                grand_parent = self.__declaration_stack[-2]
                # If the grandparent is not a class we ignore the attributes
                if isinstance(grand_parent, Class) and not isinstance(lvalue, mp_nodes.NameExpr):
                    # Ignore non instance attributes in __init__ classes
                    for assignment in self._parse_attributes(lvalue, node.unanalyzed_type, is_static=False):
                        assignments.append(assignment)

            elif isinstance(parent, Enum):
                names = []
                if hasattr(lvalue, "items"):
                    for item in lvalue.items:
                        names.append(item.name)
                else:
                    if not hasattr(lvalue, "name"):  # pragma: no cover
                        raise AttributeError("Expected lvalue to have attribtue 'name'.")
                    names.append(lvalue.name)

                for name in names:
                    assignments.append(
                        EnumInstance(
                            id=f"{parent.id}/{name}",
                            name=name,
                        ),
                    )

        self.__declaration_stack.append(assignments)

    def leave_assignmentstmt(self, _: mp_nodes.AssignmentStmt) -> None:
        # Assignments are attributes or enum instances
        assignments = self.__declaration_stack.pop()

        if not isinstance(assignments, list):  # pragma: no cover
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

                        if not isinstance(grandparent, Class):  # pragma: no cover
                            raise TypeError(f"Expected 'Class'. Got {grandparent.__class__}.")

                        grandparent.add_attribute(assignment)
                    elif isinstance(parent, Class):
                        self.api.add_attribute(assignment)
                        parent.add_attribute(assignment)

                elif isinstance(assignment, EnumInstance):
                    if isinstance(parent, Enum):
                        self.api.add_enum_instance(assignment)
                        parent.add_enum_instance(assignment)

                else:  # pragma: no cover
                    raise TypeError("Unexpected value type for assignments")

    # ############################## Utilities ############################## #

    # #### Result utilities

    def _parse_results(self, node: mp_nodes.FuncDef, function_id: str) -> list[Result]:
        # __init__ functions aren't supposed to have returns, so we can ignore them
        if node.name == "__init__":
            return []

        # Get type
        ret_type: sds_types.AbstractType | None = None
        type_is_inferred = False
        if hasattr(node, "type"):
            node_type = node.type
            if node_type is not None and hasattr(node_type, "ret_type"):
                node_ret_type = node_type.ret_type

                if not isinstance(node_ret_type, mp_types.NoneType):
                    if isinstance(node_ret_type, mp_types.AnyType) and not has_correct_type_of_any(
                        node_ret_type.type_of_any,
                    ):
                        # In this case, the "Any" type was given because it was not explicitly annotated.
                        # Therefor we have to try to infer the type.
                        ret_type = self._infer_type_from_return_stmts(node)
                        type_is_inferred = ret_type is not None
                    else:
                        # Otherwise, we can parse the type normally
                        unanalyzed_ret_type = getattr(node.unanalyzed_type, "ret_type", None)
                        ret_type = self.mypy_type_to_abstract_type(node_ret_type, unanalyzed_ret_type)
            else:
                # Infer type
                ret_type = self._infer_type_from_return_stmts(node)
                type_is_inferred = ret_type is not None

        if ret_type is None:
            return []

        result_docstring = self.docstring_parser.get_result_documentation(node)

        if type_is_inferred and isinstance(ret_type, sds_types.TupleType):
            return self._create_inferred_results(ret_type, result_docstring, function_id)

        # If we got a TupleType, we can iterate it for the results, but if we got a NamedType, we have just one result
        return_results = ret_type.types if isinstance(ret_type, sds_types.TupleType) else [ret_type]
        return [
            Result(
                id=f"{function_id}/result_{i + 1}",
                type=type_,
                name=f"result_{i + 1}",
                docstring=result_docstring,
            )
            for i, type_ in enumerate(return_results)
        ]

    @staticmethod
    def _infer_type_from_return_stmts(func_node: mp_nodes.FuncDef) -> sds_types.NamedType | sds_types.TupleType | None:
        # To infer the type, we iterate through all return statements we find in the function
        func_defn = get_funcdef_definitions(func_node)
        return_stmts = find_return_stmts_recursive(func_defn)
        if return_stmts:
            types = set()
            for return_stmt in return_stmts:
                if return_stmt.expr is None:  # pragma: no cover
                    continue

                if not isinstance(return_stmt.expr, mp_nodes.CallExpr | mp_nodes.MemberExpr):
                    # If the return statement is a conditional expression we parse the "if" and "else" branches
                    if isinstance(return_stmt.expr, mp_nodes.ConditionalExpr):
                        for conditional_branch in [return_stmt.expr.if_expr, return_stmt.expr.else_expr]:
                            if conditional_branch is None:  # pragma: no cover
                                continue

                            if not isinstance(conditional_branch, mp_nodes.CallExpr | mp_nodes.MemberExpr):
                                type_ = mypy_expression_to_sds_type(conditional_branch)
                                if isinstance(type_, sds_types.NamedType | sds_types.TupleType):
                                    types.add(type_)
                    else:
                        type_ = mypy_expression_to_sds_type(return_stmt.expr)
                        if isinstance(type_, sds_types.NamedType | sds_types.TupleType):
                            types.add(type_)

            # We have to sort the list for the snapshot tests
            return_stmt_types = list(types)
            return_stmt_types.sort(
                key=lambda x: (x.name if isinstance(x, sds_types.NamedType) else str(len(x.types))),
            )

            if len(return_stmt_types) == 1:
                return return_stmt_types[0]
            elif len(return_stmt_types) >= 2:
                return sds_types.TupleType(types=return_stmt_types)
        return None

    @staticmethod
    def _create_inferred_results(
        results: sds_types.TupleType,
        result_docstring: ResultDocstring,
        function_id: str,
    ) -> list[Result]:
        """Create Result objects with inferred results.

        If we inferred the result types, we have to create a two-dimensional array for the results since tuples are
        considered as multiple results, but other return types have to be grouped as one union. For example, if a
        function has the following returns "return 42" and "return True, 1.2" we would have to group the integer and
        boolean as "result_1: Union[int, bool]" and the float number as "result_2: Union[float, None]".

        Paramters
        ---------
        ret_type : sds_types.TupleType
            An object representing a tuple with all inferred types.
        result_docstring : ResultDocstring
            The docstring of the function to which the results belong to.
        function_id : str
            The function ID.

        Returns
        -------
        list[Result]
            A list of Results objects representing the possible results of a funtion.
        """
        result_array: list[list] = []
        for type_ in results.types:
            if isinstance(type_, sds_types.NamedType):
                if result_array:
                    result_array[0].append(type_)
                else:
                    result_array.append([type_])
            elif isinstance(type_, sds_types.TupleType):
                for i, type__ in enumerate(type_.types):
                    if len(result_array) > i:
                        result_array[i].append(type__)
                    else:
                        result_array.append([type__])
            else:  # pragma: no cover
                raise TypeError(f"Expected NamedType or TupleType, received {type(type_)}")

        inferred_results = []
        for i, result_list in enumerate(result_array):
            result_count = len(result_list)
            if result_count == 1:
                result_type = result_list[0]
            else:
                result_type = sds_types.UnionType(result_list)

            name = f"result_{i + 1}"
            inferred_results.append(
                Result(
                    id=f"{function_id}/{name}",
                    type=result_type,
                    name=name,
                    docstring=result_docstring,
                ),
            )

        return inferred_results

    # #### Attribute utilities

    def _parse_attributes(
        self,
        lvalue: mp_nodes.Expression,
        unanalyzed_type: mp_types.Type | None,
        is_static: bool = True,
    ) -> list[Attribute]:
        assert isinstance(lvalue, mp_nodes.NameExpr | mp_nodes.MemberExpr | mp_nodes.TupleExpr)
        attributes: list[Attribute] = []

        if hasattr(lvalue, "name"):
            if self._is_attribute_already_defined(lvalue.name):
                return attributes

            attributes.append(
                self._create_attribute(lvalue, unanalyzed_type, is_static),
            )

        elif hasattr(lvalue, "items"):
            lvalues = list(lvalue.items)
            for lvalue_ in lvalues:
                if not hasattr(lvalue_, "name"):  # pragma: no cover
                    raise AttributeError("Expected value to have attribute 'name'.")

                if self._is_attribute_already_defined(lvalue_.name):
                    continue

                attributes.append(
                    self._create_attribute(lvalue_, unanalyzed_type, is_static),
                )

        return attributes

    def _is_attribute_already_defined(self, value_name: str) -> bool:
        # If node is None, it's possible that the attribute was already defined once
        parent = self.__declaration_stack[-1]
        if isinstance(parent, Function):
            parent = self.__declaration_stack[-2]

        if not isinstance(parent, Class):  # pragma: no cover
            raise TypeError("Parent has the wrong class, cannot get attribute values.")

        return any(value_name == attribute.name for attribute in parent.attributes)

    def _create_attribute(
        self,
        attribute: mp_nodes.Expression,
        unanalyzed_type: mp_types.Type | None,
        is_static: bool,
    ) -> Attribute:
        # Get node information
        type_: sds_types.AbstractType | None = None
        node = None
        if hasattr(attribute, "node"):
            if not isinstance(attribute.node, mp_nodes.Var):
                # In this case we have a TypeVar attribute
                attr_name = getattr(attribute, "name", "")

                if not attr_name:  # pragma: no cover
                    raise AttributeError("Expected TypeVar to have attribute 'name'.")

                type_ = sds_types.TypeVarType(attr_name)
            else:
                node = attribute.node
        else:  # pragma: no cover
            raise AttributeError("Expected attribute to have attribute 'node'.")

        # Get name and qname
        name = getattr(attribute, "name", "")
        qname = getattr(attribute, "fullname", "")

        # Sometimes the qname is not in the attribute.fullname field, in that case we have to get it from the node
        if qname in (name, "") and node is not None:
            qname = node.fullname

        attribute_type = None

        # MemberExpr are constructor (__init__) attributes
        if node is not None and isinstance(attribute, mp_nodes.MemberExpr):
            attribute_type = node.type
            if isinstance(attribute_type, mp_types.AnyType) and not has_correct_type_of_any(attribute_type.type_of_any):
                attribute_type = None

        # NameExpr are class attributes
        elif node is not None and isinstance(attribute, mp_nodes.NameExpr) and not node.explicit_self_type:
            attribute_type = node.type

            # We need to get the unanalyzed_type for lists, since mypy is not able to check type hint information
            # regarding list item types
            if (
                attribute_type is not None
                and hasattr(attribute_type, "type")
                and hasattr(attribute_type, "args")
                and attribute_type.type.fullname == "builtins.list"
                and not node.is_inferred
            ):
                if unanalyzed_type is not None and hasattr(unanalyzed_type, "args"):
                    attribute_type.args = unanalyzed_type.args
                else:  # pragma: no cover
                    raise AttributeError("Could not get argument information for attribute.")

        # Ignore types that are special mypy any types. The Any type "from_unimported_type" could appear for aliase
        if (
            attribute_type is not None
            and not (
                isinstance(attribute_type, mp_types.AnyType) and not has_correct_type_of_any(attribute_type.type_of_any)
            )
            and not isinstance(attribute_type, mp_types.CallableType)
        ):
            # noinspection PyTypeChecker
            type_ = self.mypy_type_to_abstract_type(attribute_type, unanalyzed_type)

        # Get docstring
        parent = self.__declaration_stack[-1]
        if isinstance(parent, Function) and parent.name == "__init__":
            parent = self.__declaration_stack[-2]
        assert isinstance(parent, Class)
        docstring = self.docstring_parser.get_attribute_documentation(parent, name)

        # Remove __init__ for attribute ids
        id_ = self._create_id_from_stack(name).replace("__init__/", "")

        return Attribute(
            id=id_,
            name=name,
            type=type_,
            is_public=self._is_public(name, qname),
            is_static=is_static,
            docstring=docstring,
        )

    # #### Parameter utilities

    def _parse_parameter_data(self, node: mp_nodes.FuncDef, function_id: str) -> list[Parameter]:
        arguments: list[Parameter] = []

        for argument in node.arguments:
            mypy_type = argument.variable.type
            type_annotation = argument.type_annotation
            arg_type: AbstractType | None = None
            default_value = None
            default_is_none = False

            # Get type information for parameter
            if mypy_type is None:  # pragma: no cover
                raise ValueError("Argument has no type.")
            elif isinstance(mypy_type, mp_types.AnyType) and not has_correct_type_of_any(mypy_type.type_of_any):
                # We try to infer the type through the default value later, if possible
                pass
            elif (
                isinstance(type_annotation, mp_types.UnboundType)
                and type_annotation.name in {"list", "set"}
                and len(type_annotation.args) >= 2
            ):
                # A special case where the argument is a list with multiple types. We have to handle this case like this
                # b/c something like list[int, str] is not allowed according to PEP and therefore not handled the normal
                # way in Mypy.
                arg_type = self.mypy_type_to_abstract_type(type_annotation)
            elif type_annotation is not None:
                arg_type = self.mypy_type_to_abstract_type(mypy_type)

            # Get default value and infer type information
            initializer = argument.initializer
            if initializer is not None:
                default_value, default_is_none = self._get_parameter_type_and_default_value(initializer)
                if arg_type is None and (default_is_none or default_value is not None):
                    arg_type = mypy_expression_to_sds_type(initializer)

            arg_name = argument.variable.name
            arg_kind = get_argument_kind(argument)

            # Create parameter docstring
            parent = self.__declaration_stack[-1]
            docstring = self.docstring_parser.get_parameter_documentation(
                function_node=node,
                parameter_name=arg_name,
                parameter_assigned_by=arg_kind,
                parent_class=parent if isinstance(parent, Class) else None,
            )

            if isinstance(default_value, type):  # pragma: no cover
                raise TypeError("default_value has the unexpected type 'type'.")

            # Create parameter object
            arguments.append(
                Parameter(
                    id=f"{function_id}/{arg_name}",
                    name=arg_name,
                    is_optional=default_value is not None or default_is_none,
                    default_value=default_value,
                    assigned_by=arg_kind,
                    docstring=docstring,
                    type=arg_type,
                ),
            )

        return arguments

    @staticmethod
    def _get_parameter_type_and_default_value(
        initializer: mp_nodes.Expression,
    ) -> tuple[str | None | int | float, bool]:
        default_value: str | None | int | float = None
        default_is_none = False
        if initializer is not None:
            if isinstance(initializer, mp_nodes.NameExpr) and initializer.name not in {"None", "True", "False"}:
                # Ignore this case, b/c Safe-DS does not support types that aren't core classes or classes definied
                # in the package we analyze with Safe-DS.
                return default_value, default_is_none
            elif isinstance(initializer, mp_nodes.CallExpr):
                # Safe-DS does not support call expressions as types
                return default_value, default_is_none
            elif isinstance(
                initializer,
                mp_nodes.IntExpr | mp_nodes.FloatExpr | mp_nodes.StrExpr | mp_nodes.NameExpr,
            ):
                # See https://github.com/Safe-DS/Stub-Generator/issues/34#issuecomment-1819643719
                inferred_default_value = mypy_expression_to_python_value(initializer)
                if isinstance(inferred_default_value, bool | int | float | NoneType):
                    default_value = inferred_default_value
                elif isinstance(inferred_default_value, str):
                    default_value = f'"{inferred_default_value}"'
                else:  # pragma: no cover
                    raise TypeError("Default value got an unsupported value.")

                default_is_none = default_value is None
        return default_value, default_is_none

    # #### Reexport utilities

    def _get_reexported_by(self, name: str) -> list[Module]:
        # Get the uppermost module and the path to the current node
        parents = []
        parent = None
        i = 1
        while not isinstance(parent, Module):
            parent = self.__declaration_stack[-i]
            if isinstance(parent, list):  # pragma: no cover
                continue
            parents.append(parent.name)
            i += 1
        path = [*list(reversed(parents)), name]

        # Check if there is a reexport entry for each item in the path to the current module
        reexported_by = set()
        for i in range(len(path)):
            reexport_name = ".".join(path[: i + 1])
            if reexport_name in self.api.reexport_map:
                for mod in self.api.reexport_map[reexport_name]:
                    reexported_by.add(mod)

        return list(reexported_by)

    def _add_reexports(self, module: Module) -> None:
        for qualified_import in module.qualified_imports:
            name = qualified_import.qualified_name
            self.api.reexport_map[name].add(module)

        for wildcard_import in module.wildcard_imports:
            name = wildcard_import.module_name
            self.api.reexport_map[name].add(module)

    # #### Misc. utilities
    def mypy_type_to_abstract_type(
        self,
        mypy_type: mp_types.Instance | mp_types.ProperType | mp_types.Type,
        unanalyzed_type: mp_types.Type | None = None,
    ) -> AbstractType:

        # Special cases where we need the unanalyzed_type to get the type information we need
        if unanalyzed_type is not None and hasattr(unanalyzed_type, "name"):
            unanalyzed_type_name = unanalyzed_type.name
            if unanalyzed_type_name == "Final":
                # Final type
                types = [self.mypy_type_to_abstract_type(arg) for arg in getattr(unanalyzed_type, "args", [])]
                if len(types) == 1:
                    return sds_types.FinalType(type_=types[0])
                elif len(types) == 0:  # pragma: no cover
                    raise ValueError("Final type has no type arguments.")
                return sds_types.FinalType(type_=sds_types.UnionType(types=types))
            elif unanalyzed_type_name in {"list", "set"}:
                type_args = getattr(mypy_type, "args", [])
                if (
                    len(type_args) == 1
                    and isinstance(type_args[0], mp_types.AnyType)
                    and not has_correct_type_of_any(type_args[0].type_of_any)
                ):
                    # This case happens if we have a list or set with multiple arguments like "list[str, int]" which is
                    # not allowed. In this case mypy interprets the type as "list[Any]", but we want the real types
                    # of the list arguments, which we cant get through the "unanalyzed_type" attribute
                    return self.mypy_type_to_abstract_type(unanalyzed_type)

        # Iterable mypy types
        if isinstance(mypy_type, mp_types.TupleType):
            return sds_types.TupleType(types=[self.mypy_type_to_abstract_type(item) for item in mypy_type.items])
        elif isinstance(mypy_type, mp_types.UnionType):
            return sds_types.UnionType(types=[self.mypy_type_to_abstract_type(item) for item in mypy_type.items])

        # Special Cases
        elif isinstance(mypy_type, mp_types.TypeVarType):
            upper_bound = mypy_type.upper_bound
            type_ = None
            if upper_bound.__str__() != "builtins.object":
                type_ = self.mypy_type_to_abstract_type(upper_bound)

            type_var = sds_types.TypeVarType(name=mypy_type.name, upper_bound=type_)
            self.type_var_types.add(type_var)
            return type_var
        elif isinstance(mypy_type, mp_types.CallableType):
            return sds_types.CallableType(
                parameter_types=[self.mypy_type_to_abstract_type(arg_type) for arg_type in mypy_type.arg_types],
                return_type=self.mypy_type_to_abstract_type(mypy_type.ret_type),
            )
        elif isinstance(mypy_type, mp_types.AnyType):
            if mypy_type.type_of_any == mp_types.TypeOfAny.from_unimported_type:
                # If the Any type is generated b/c of from_unimported_type, then we can parse the type
                # from the import information
                missing_import_name = mypy_type.missing_import_name.split(".")[-1]  # type: ignore[union-attr]
                name, qname = self._find_alias(missing_import_name)
                return sds_types.NamedType(name=name, qname=qname)
            else:
                return sds_types.NamedType(name="Any", qname="builtins.Any")
        elif isinstance(mypy_type, mp_types.NoneType):
            return sds_types.NamedType(name="None", qname="builtins.None")
        elif isinstance(mypy_type, mp_types.LiteralType):
            return sds_types.LiteralType(literals=[mypy_type.value])
        elif isinstance(mypy_type, mp_types.UnboundType):
            if mypy_type.name in {"list", "set"}:
                return {
                    "list": sds_types.ListType,
                    "set": sds_types.SetType,
                }[
                    mypy_type.name
                ](types=[self.mypy_type_to_abstract_type(arg) for arg in mypy_type.args])

            # Get qname
            if mypy_type.name in {"Any", "str", "int", "bool", "float", "None"}:
                return sds_types.NamedType(name=mypy_type.name, qname=f"builtins.{mypy_type.name}")
            else:
                # first we check if it's a class from the same module
                module = self.__declaration_stack[0]

                if not isinstance(module, Module):  # pragma: no cover
                    raise TypeError(f"Expected module, got {type(module)}.")

                for module_class in module.classes:
                    if module_class.name == mypy_type.name:
                        qname = module_class.id.replace("/", ".")
                        return sds_types.NamedType(name=module_class.name, qname=qname)

                # if not, we check if it's an alias
                name, qname = self._find_alias(mypy_type.name)
                return sds_types.NamedType(name=name, qname=qname)

        # Builtins
        elif isinstance(mypy_type, mp_types.Instance):
            type_name = mypy_type.type.name
            if type_name in {"int", "str", "bool", "float"}:
                return sds_types.NamedType(name=type_name, qname=mypy_type.type.fullname)

            # Iterable builtins
            elif type_name in {"tuple", "list", "set", "Sequence", "Collection"}:
                types = [self.mypy_type_to_abstract_type(arg) for arg in mypy_type.args]
                match type_name:
                    case "tuple":
                        return sds_types.TupleType(types=types)
                    case "list":
                        return sds_types.ListType(types=types)
                    case "set":
                        return sds_types.SetType(types=types)
                    case "Sequence":
                        return sds_types.ListType(types=types)
                    case "Collection":
                        return sds_types.ListType(types=types)

            elif type_name in {"dict", "Mapping"}:
                return sds_types.DictType(
                    key_type=self.mypy_type_to_abstract_type(mypy_type.args[0]),
                    value_type=self.mypy_type_to_abstract_type(mypy_type.args[1]),
                )
            else:
                return sds_types.NamedType(name=type_name, qname=mypy_type.type.fullname)
        raise ValueError("Unexpected type.")  # pragma: no cover

    def _find_alias(self, type_name: str) -> tuple[str, str]:
        module = self.__declaration_stack[0]

        # At this point, the first item of the stack can only ever be a module
        if not isinstance(module, Module):  # pragma: no cover
            raise TypeError(f"Expected module, got {type(module)}.")

        name = ""
        qname = ""
        qualified_imports = module.qualified_imports
        import_aliases = [qimport.alias for qimport in qualified_imports]

        if type_name in self.aliases:
            qnames: set = self.aliases[type_name]
            if len(qnames) == 1:
                # We have to check if this is an alias from an import
                import_name, import_qname = self._search_alias_in_qualified_imports(qualified_imports, type_name)

                # We need a deepcopy since qnames is a pointer to the set in the alias dict
                qname = import_qname if import_qname else deepcopy(qnames).pop()
                name = import_name if import_name else qname.split(".")[-1]
            elif type_name in import_aliases:
                # We check if the type was imported
                qimport_name, qimport_qname = self._search_alias_in_qualified_imports(qualified_imports, type_name)

                if qimport_qname:
                    qname = qimport_qname
                    name = qimport_name
            else:
                # In this case some types where defined in multiple modules with the same names.
                for alias_qname in qnames:
                    # We check if the type was defined in the same module
                    type_path = ".".join(alias_qname.split(".")[0:-1])
                    name = alias_qname.split(".")[-1]

                    if self.mypy_file is None:  # pragma: no cover
                        raise TypeError("Expected mypy_file (module information), got None.")

                    if type_path == self.mypy_file.fullname:
                        qname = alias_qname
                        break
        else:
            name, qname = self._search_alias_in_qualified_imports(qualified_imports, type_name)

        if not qname:  # pragma: no cover
            raise ValueError(f"It was not possible to find out where the alias {type_name} was defined.")

        return name, qname

    @staticmethod
    def _search_alias_in_qualified_imports(
        qualified_imports: list[QualifiedImport],
        alias_name: str,
    ) -> tuple[str, str]:
        for qualified_import in qualified_imports:
            if alias_name in {qualified_import.alias, qualified_import.qualified_name.split(".")[-1]}:
                qname = qualified_import.qualified_name
                name = qname.split(".")[-1]
                return name, qname
        return "", ""

    def _is_public(self, name: str, qname: str) -> bool:
        if self.mypy_file is None:  # pragma: no cover
            raise ValueError("A Mypy file (module) should be defined.")

        parent = self.__declaration_stack[-1]

        if not isinstance(parent, Module | Class) and not (isinstance(parent, Function) and parent.name == "__init__"):
            raise TypeError(
                f"Expected parent for {name} in module {self.mypy_file.fullname} to be a class or a module.",
            )  # pragma: no cover

        if not isinstance(parent, Function):
            _check_publicity_with_reexports: bool | None = self._check_publicity_in_reexports(name, qname, parent)

            if _check_publicity_with_reexports is not None:
                return _check_publicity_with_reexports

        if is_internal(name) and not name.endswith("__"):
            return False

        if isinstance(parent, Class) and (name == "__init__" or not is_internal(name)):
            return parent.is_public

        # The slicing is necessary so __init__ functions are not excluded (already handled in the first condition).
        return all(not is_internal(it) for it in qname.split(".")[:-1])

    def _create_id_from_stack(self, name: str) -> str:
        """Create an ID for a new object using previous objects of the stack.

        Creates an ID by connecting the previous objects of the __declaration_stack stack and the new objects name,
        which is on the highest level.

        Paramters
        ---------
        name : str
            The name of the new object which lies on the highest level.

        Returns
        -------
        str
            ID of the object
        """
        segments = [
            it.id if isinstance(it, Module) else it.name  # Special case, to get the module path info the id
            for it in self.__declaration_stack
            if not isinstance(it, list)  # Check for the linter, on runtime can never be list type
        ]
        segments += [name]

        return "/".join(segments)

    def _inherits_from_exception(self, node: mp_nodes.TypeInfo) -> bool:
        if node.fullname == "builtins.Exception":
            return True

        return any(self._inherits_from_exception(base.type) for base in node.bases)

    def _check_publicity_in_reexports(self, name: str, qname: str, parent: Module | Class) -> bool | None:
        not_internal = not is_internal(name)
        module_qname = getattr(self.mypy_file, "fullname", "")
        module_name = getattr(self.mypy_file, "name", "")
        package_id = "/".join(module_qname.split(".")[:-1])

        for reexported_key in self.api.reexport_map:
            module_is_reexported = reexported_key in {module_name, module_qname}

            # Check if the function/class/module is reexported
            if reexported_key.endswith(name) or module_is_reexported:

                # Iterate through all sources (__init__.py files) where it was reexported
                for reexport_source in self.api.reexport_map[reexported_key]:

                    # We have to check if it's the correct reexport with the ID
                    is_from_same_package = reexport_source.id == package_id
                    is_from_another_package = reexported_key in {qname, module_qname}
                    if not is_from_same_package and not is_from_another_package:
                        continue

                    # If the whole module was reexported we have to check if the name or alias is intern
                    if module_is_reexported:

                        # Check the wildcard imports of the source
                        for wildcard_import in reexport_source.wildcard_imports:
                            if (
                                (
                                    (is_from_same_package and wildcard_import.module_name == module_name)
                                    or (is_from_another_package and wildcard_import.module_name == module_qname)
                                )
                                and not_internal
                                and (isinstance(parent, Module) or parent.is_public)
                            ):
                                return True

                        # Check the qualified imports of the source
                        for qualified_import in reexport_source.qualified_imports:

                            # If the whole module was exported, we have to check if the func / class / attr we are
                            #  checking here is internal, and if not, if any parents are internal.
                            if (
                                qualified_import.qualified_name in {module_name, module_qname}
                                and (
                                    (qualified_import.alias is None and not_internal)
                                    or (qualified_import.alias is not None and not is_internal(qualified_import.alias))
                                )
                                and not_internal
                                and (isinstance(parent, Module) or parent.is_public)
                            ):
                                # If the module name or alias is not internal, check if the parent is public
                                return True

                    # A specific function or class was reexported.
                    if reexported_key.endswith(name):

                        # For wildcard imports we check in the _is_public method if the func / class is internal
                        for qualified_import in reexport_source.qualified_imports:

                            if qname.endswith(qualified_import.qualified_name) and (
                                qualified_import.alias is not None
                                and not is_internal(qualified_import.alias)
                                or (qualified_import.alias is None and not_internal)
                            ):
                                # First we check if we've found the right import then do the following:
                                # If a specific func / class was reexported check
                                #   1. If it has an alias and if it's alias is internal
                                #   2. Else if it has no alias and is not internal
                                return True
        return None


def is_internal(name: str) -> bool:
    return name.startswith("_")
