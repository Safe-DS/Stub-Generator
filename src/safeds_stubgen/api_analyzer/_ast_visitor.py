from __future__ import annotations

from collections import defaultdict
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
        self.reexported: dict[str, set[Module]] = defaultdict(set)
        self.api: API = api
        self.__declaration_stack: list[Module | Class | Function | Enum | list[Attribute | EnumInstance]] = []
        self.aliases = aliases
        self.mypy_file: mp_nodes.MypyFile | None = None

    def enter_moduledef(self, node: mp_nodes.MypyFile) -> None:
        self.mypy_file = node
        is_package = node.path.endswith("__init__.py")

        # Todo Frage: Alte Importfunktionalität behalten? Wird nicht benutzt
        qualified_imports: list[QualifiedImport] = []
        wildcard_imports: list[WildcardImport] = []
        docstring = ""

        # We don't need to check functions, classes and assignments, since the ast walker will already check them
        child_definitions = [
            _definition
            for _definition in get_mypyfile_definitions(node)
            if _definition.__class__.__name__ not in ["FuncDef", "Decorator", "ClassDef", "AssignmentStmt"]
        ]

        for definition in child_definitions:
            # Imports
            if isinstance(definition, mp_nodes.Import):
                for import_name, import_alias in definition.ids:
                    qualified_imports.append(
                        QualifiedImport(import_name, import_alias),
                    )

            elif isinstance(definition, mp_nodes.ImportFrom):
                for import_name, import_alias in definition.names:
                    qualified_imports.append(
                        QualifiedImport(
                            f"{definition.id}.{import_name}",
                            import_alias,
                        ),
                    )

            elif isinstance(definition, mp_nodes.ImportAll):
                wildcard_imports.append(
                    WildcardImport(definition.id),
                )

            # Docstring
            elif isinstance(definition, mp_nodes.ExpressionStmt) and isinstance(definition.expr, mp_nodes.StrExpr):
                docstring = definition.expr.value

        # Create module id to get the full path
        id_ = self._create_module_id(node.fullname)

        # If we are checking a package node.name will be the package name, but since we get import information from
        # the __init__.py file we set the name to __init__
        if is_package:
            name = "__init__"
            id_ += f"/{name}"
        else:
            name = node.name

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
        for removed_base_type_expr in node.removed_base_type_exprs:
            base = getattr(removed_base_type_expr, "base", None)
            base_name = getattr(base, "name", None)
            if base_name == "Generic":
                generic_exprs.append(removed_base_type_expr)

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
                variance_values: sds_types.AbstractType
                if variance_type == VarianceKind.INVARIANT:
                    variance_values = sds_types.UnionType([
                        self.mypy_type_to_abstract_type(value) for value in generic_type.values
                    ])
                else:
                    variance_values = self.mypy_type_to_abstract_type(generic_type.upper_bound)

                type_parameters.append(
                    TypeParameter(
                        name=generic_type.name,
                        type=variance_values,
                        variance=variance_type,
                    ),
                )

        # superclasses
        superclasses = []
        for superclass in node.base_type_exprs:
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

        # Function args
        arguments: list[Parameter] = []
        if getattr(node, "arguments", None) is not None:
            arguments = self._parse_parameter_data(node, function_id)

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
            # In this case the items of the types set can only be of the class "NamedType" or "TupleType" but we have to
            # make a typecheck anyway for the mypy linter.
            types = set()
            for return_stmt in return_stmts:
                if return_stmt.expr is not None:
                    type_ = mypy_expression_to_sds_type(return_stmt.expr)
                    if isinstance(type_, sds_types.NamedType | sds_types.TupleType):
                        types.add(type_)

            # We have to sort the list for the snapshot tests
            return_stmt_types = list(types)
            return_stmt_types.sort(
                key=lambda x: (x.name if isinstance(x, sds_types.NamedType) else str(len(x.types))),
            )

            if len(return_stmt_types) >= 2:
                return sds_types.TupleType(types=return_stmt_types)
            return return_stmt_types[0]
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
        if hasattr(attribute, "node"):
            if not isinstance(attribute.node, mp_nodes.Var):  # pragma: no cover
                raise TypeError("node has wrong type")

            node: mp_nodes.Var = attribute.node
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
        if isinstance(attribute, mp_nodes.MemberExpr):
            attribute_type = node.type
            if isinstance(attribute_type, mp_types.AnyType) and not has_correct_type_of_any(attribute_type.type_of_any):
                attribute_type = None

        # NameExpr are class attributes
        elif isinstance(attribute, mp_nodes.NameExpr):
            if not node.explicit_self_type:
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

        else:  # pragma: no cover
            raise TypeError("Attribute has an unexpected type.")

        type_ = None
        # Ignore types that are special mypy any types. The Any type "from_unimported_type" could appear for aliase
        if attribute_type is not None and not (
            isinstance(attribute_type, mp_types.AnyType) and not has_correct_type_of_any(attribute_type.type_of_any)
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
            arg_type = None
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
        default_value = None
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
                if isinstance(inferred_default_value, str | bool | int | float | NoneType):
                    default_value = inferred_default_value
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
            if reexport_name in self.reexported:
                for mod in self.reexported[reexport_name]:
                    reexported_by.add(mod)

        return list(reexported_by)

    def _add_reexports(self, module: Module) -> None:
        for qualified_import in module.qualified_imports:
            name = qualified_import.qualified_name
            self.reexported[name].add(module)

        for wildcard_import in module.wildcard_imports:
            name = wildcard_import.module_name
            self.reexported[name].add(module)

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
                name = mypy_type.name
                qname = f"builtins.{mypy_type.name}"
            else:
                name, qname = self._find_alias(mypy_type.name)

            return sds_types.NamedType(name=name, qname=qname)

        # Builtins
        elif isinstance(mypy_type, mp_types.Instance):
            type_name = mypy_type.type.name
            if type_name in {"int", "str", "bool", "float"}:
                return sds_types.NamedType(name=type_name, qname=mypy_type.type.fullname)

            # Iterable builtins
            elif type_name in {"tuple", "list", "set"}:
                types = [self.mypy_type_to_abstract_type(arg) for arg in mypy_type.args]
                match type_name:
                    case "tuple":
                        return sds_types.TupleType(types=types)
                    case "list":
                        return sds_types.ListType(types=types)
                    case "set":
                        return sds_types.SetType(types=types)

            elif type_name == "dict":
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
        if type_name in self.aliases:
            qnames: set = self.aliases[type_name]
            if len(qnames) == 1:
                qname = deepcopy(qnames).pop()
                name = qname.split(".")[-1]

                # We have to check if this is an alias from an import
                import_name, import_qname = self._search_alias_in_qualified_imports(module, type_name)

                name = import_name if import_name else name
                qname = import_qname if import_qname else qname

            else:
                # In this case some type was defined in multiple modules with the same name.
                for alias_qname in qnames:
                    # First we check if the type was defined in the same module
                    type_path = ".".join(alias_qname.split(".")[0:-1])
                    name = alias_qname.split(".")[-1]

                    if self.mypy_file is None:  # pragma: no cover
                        raise TypeError("Expected mypy_file (module information), got None.")

                    if type_path == self.mypy_file.fullname:
                        qname = alias_qname
                        break

                    # Then we check if the type was perhapse imported
                    qimport_name, qimport_qname = self._search_alias_in_qualified_imports(module, name, alias_qname)
                    if qimport_qname:
                        qname = qimport_qname
                        name = qimport_name if qimport_name else name
                        break

                    found_qname = False
                    for wildcard_import in module.wildcard_imports:
                        if wildcard_import.module_name in alias_qname:
                            qname = alias_qname
                            found_qname = True
                            break
                    if found_qname:
                        break

        else:
            name, qname = self._search_alias_in_qualified_imports(module, type_name)

        if not qname:  # pragma: no cover
            raise ValueError(f"It was not possible to find out where the alias {type_name} was defined.")

        return name, qname

    @staticmethod
    def _search_alias_in_qualified_imports(module: Module, alias_name: str, alias_qname: str = "") -> tuple[str, str]:
        for qualified_import in module.qualified_imports:
            if alias_name in {qualified_import.alias, qualified_import.qualified_name.split(".")[-1]}:
                qname = qualified_import.qualified_name
                name = qname.split(".")[-1]
                return name, qname
            elif alias_qname and qualified_import.qualified_name in alias_qname:
                return "", alias_qname
        return "", ""

    def _create_module_id(self, qname: str) -> str:
        """Create an ID for the module object.

        Creates the module ID while discarding possible unnecessary information from the module qname.

        Paramters
        ---------
        qname : str
            The qualified name of the module

        Returns
        -------
        str
            ID of the module
        """
        package_name = self.api.package

        if package_name not in qname:
            raise ValueError("Package name could not be found in the qualified name of the module.")

        # We have to split the qname of the module at the first occurence of the package name and reconnect it while
        # discarding everything in front of it. This is necessary since the qname could contain unwanted information.
        module_id = qname.split(f"{package_name}", 1)[-1]

        if module_id.startswith("."):
            module_id = module_id[1:]

        # Replaces dots with slashes and add the package name at the start of the id, since we removed it
        module_id = f"/{module_id.replace('.', '/')}" if module_id else ""
        return f"{package_name}{module_id}"

    def _is_public(self, name: str, qualified_name: str) -> bool:
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
