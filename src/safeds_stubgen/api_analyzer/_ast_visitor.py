from __future__ import annotations

from types import NoneType
from typing import TYPE_CHECKING

import mypy.types as mp_types
from mypy import nodes as mp_nodes

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
    Variance,
    VarianceType,
    WildcardImport,
)
from ._mypy_helpers import (
    find_return_stmts_recursive,
    get_argument_kind,
    get_classdef_definitions,
    get_funcdef_definitions,
    get_mypyfile_definitions,
    has_correct_type_of_any,
    mypy_expression_to_sds_type,
    mypy_type_to_abstract_type,
    mypy_variance_parser,
)

if TYPE_CHECKING:
    from safeds_stubgen.docstring_parsing import AbstractDocstringParser, ResultDocstring


class MyPyAstVisitor:
    def __init__(self, docstring_parser: AbstractDocstringParser, api: API) -> None:
        self.docstring_parser: AbstractDocstringParser = docstring_parser
        self.reexported: dict[str, list[Module]] = {}
        self.api: API = api
        self.__declaration_stack: list[Module | Class | Function | Enum | list[Attribute | EnumInstance]] = []

    def enter_moduledef(self, node: mp_nodes.MypyFile) -> None:
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
        generic_exprs = [
            removed_base_type_expr
            for removed_base_type_expr in node.removed_base_type_exprs
            if removed_base_type_expr.base.name == "Generic"
        ]
        variances = []
        if generic_exprs:
            # Can only be one, since a class can inherit "Generic" only one time
            generic_expr = generic_exprs[0].index

            if isinstance(generic_expr, mp_nodes.TupleExpr):
                generic_types = [item.node for item in generic_expr.items]
            elif isinstance(generic_expr, mp_nodes.NameExpr):
                generic_types = [generic_expr.node]
            else:  # pragma: no cover
                raise TypeError("Unexpected type while parsing generic type.")

            for generic_type in generic_types:
                variance_type = mypy_variance_parser(generic_type.variance)
                if variance_type == VarianceType.INVARIANT:
                    variance_values = sds_types.UnionType([
                        mypy_type_to_abstract_type(value)
                        for value in generic_type.values
                    ])
                else:
                    variance_values = mypy_type_to_abstract_type(generic_type.upper_bound)

                variances.append(Variance(
                    name=generic_type.name,
                    type=variance_values,
                    variance_type=variance_type,
                ))

        # superclasses
        # Todo Aliasing: Werden noch nicht aufgelöst
        superclasses = [superclass.fullname for superclass in node.base_type_exprs if hasattr(superclass, "fullname")]
        is_abstract_class = "abc.ABC" in superclasses

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
            is_abstract=is_abstract_class,
            docstring=docstring,
            reexported_by=reexported_by,
            constructor_fulldocstring=constructor_fulldocstring,
            variances=variances,
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
        ret_type = None
        is_type_inferred = False
        if hasattr(node, "type"):
            node_type = node.type
            if node_type is not None and hasattr(node_type, "ret_type"):
                node_ret_type = node_type.ret_type

                if not isinstance(node_ret_type, mp_types.NoneType):
                    if (isinstance(node_ret_type, mp_types.AnyType) and
                            not has_correct_type_of_any(node_ret_type.type_of_any)):
                        # In this case, the "Any" type was given because it was not explicitly annotated.
                        # Therefor we have to try to infer the type.
                        ret_type = self._infer_type_from_return_stmts(node)
                        is_type_inferred = ret_type is not None
                    else:
                        # Otherwise, we can parse the type normally
                        ret_type = mypy_type_to_abstract_type(node_ret_type, node.unanalyzed_type.ret_type)
            else:
                # Infer type
                ret_type = self._infer_type_from_return_stmts(node)
                is_type_inferred = ret_type is not None

        if ret_type is None:
            return []

        result_docstring = self.docstring_parser.get_result_documentation(node)

        if is_type_inferred and isinstance(ret_type, sds_types.TupleType):
            return self._create_infered_results(ret_type, result_docstring, function_id)

        # If we got a TupleType, we can iterate it for the results, but if we got a NamedType, we have just one result
        return_results = ret_type.types if isinstance(ret_type, sds_types.TupleType) else [ret_type]
        return [
            Result(
                id=f"{function_id}/result_{i + 1}",
                type=type_,
                is_type_inferred=is_type_inferred,
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
            types = {
                mypy_expression_to_sds_type(return_stmt.expr)
                for return_stmt in return_stmts
            }

            # We have to sort the list for the snapshot tests
            return_stmt_types = list(types)
            return_stmt_types.sort(
                key=lambda x: (
                    x.name
                    if isinstance(x, sds_types.NamedType)
                    else str(len(x.types))
                ),
            )

            if len(return_stmt_types) >= 2:
                return sds_types.TupleType(types=return_stmt_types)
            return return_stmt_types[0]
        return None

    @staticmethod
    def _create_infered_results(
        results: sds_types.TupleType, result_docstring: ResultDocstring, function_id: str,
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
        type_: sds_types.NamedType | sds_types.TupleType
        for type_ in results.types:
            if isinstance(type_, sds_types.NamedType):
                if result_array:
                    result_array[0].append(type_)
                else:
                    result_array.append([type_])
            else:
                for i, type__ in enumerate(type_.types):
                    if len(result_array) > i:
                        result_array[i].append(type__)
                    else:
                        result_array.append([type__])

        inferred_results = []
        for i, result_list in enumerate(result_array):
            result_count = len(result_list)
            if result_count == 0:
                break
            elif result_count == 1:
                result_type = result_list[0]
            else:
                result_type = sds_types.UnionType(result_list)

            name = f"result_{i + 1}"
            inferred_results.append(
                Result(
                    id=f"{function_id}/{name}",
                    type=result_type,
                    is_type_inferred=True,
                    name=name,
                    docstring=result_docstring,
                ),
            )

        return inferred_results

    # #### Attribute utilities

    def _parse_attributes(
        self,
        lvalue: mp_nodes.NameExpr | mp_nodes.MemberExpr | mp_nodes.TupleExpr,
        unanalyzed_type: mp_types.Type | None,
        is_static: bool = True,
    ) -> list[Attribute]:
        assert isinstance(lvalue, mp_nodes.NameExpr | mp_nodes.MemberExpr | mp_nodes.TupleExpr)
        attributes: list[Attribute] = []

        if hasattr(lvalue, "name"):
            if self._is_attribute_already_defined(lvalue, lvalue.name):
                return attributes

            attributes.append(
                self._create_attribute(lvalue, unanalyzed_type, is_static),
            )

        elif hasattr(lvalue, "items"):
            lvalues = list(lvalue.items)
            for lvalue_ in lvalues:
                if not hasattr(lvalue_, "name"):  # pragma: no cover
                    raise AttributeError("Expected value to have attribute 'name'.")

                if self._is_attribute_already_defined(lvalue_, lvalue_.name):
                    continue

                attributes.append(
                    self._create_attribute(lvalue_, unanalyzed_type, is_static),
                )

        return attributes

    def _is_attribute_already_defined(self, lvalue: mp_nodes.Expression, value_name: str) -> bool:
        assert isinstance(lvalue, mp_nodes.NameExpr | mp_nodes.MemberExpr | mp_nodes.TupleExpr)
        if hasattr(lvalue, "node"):
            node = lvalue.node
        else:  # pragma: no cover
            raise AttributeError("Expected value to have attribute 'node'.")

        # If node is None, it's possible that the attribute was already defined once
        if node is None:
            parent = self.__declaration_stack[-1]
            if isinstance(parent, Function):
                parent = self.__declaration_stack[-2]

            if not isinstance(parent, Class):  # pragma: no cover
                raise TypeError("Parent has the wrong class, cannot get attribute values.")

            for attribute in parent.attributes:
                if value_name == attribute.name:
                    return True

            raise ValueError(f"The attribute {value_name} has no value.")  # pragma: no cover
        return False

    def _create_attribute(
        self,
        attribute: mp_nodes.Expression,
        unanalyzed_type: mp_types.Type | None,
        is_static: bool,
    ) -> Attribute:
        # Get name and qname
        if hasattr(attribute, "name"):
            name = attribute.name
        else:  # pragma: no cover
            raise AttributeError("Expected attribute to have attribute 'name'.")
        qname = getattr(attribute, "fullname", "")

        # Get node information
        if hasattr(attribute, "node"):
            if not isinstance(attribute.node, mp_nodes.Var):  # pragma: no cover
                raise TypeError("node has wrong type")

            node: mp_nodes.Var = attribute.node
        else:  # pragma: no cover
            raise AttributeError("Expected attribute to have attribute 'node'.")

        # Sometimes the qname is not in the attribute.fullname field, in that case we have to get it from the node
        if qname in (name, "") and node is not None:
            qname = node.fullname

        attribute_type = None
        is_type_inferred = False

        # MemberExpr are constructor (__init__) attributes
        if isinstance(attribute, mp_nodes.MemberExpr):
            attribute_type = node.type
            if isinstance(attribute_type, mp_types.AnyType) and not has_correct_type_of_any(attribute_type.type_of_any):
                attribute_type = None

            # Sometimes the is_inferred value is True even thoght has_explicit_value is False, thus we HAVE to check
            # has_explicit_value, too.
            is_type_inferred = node.is_inferred and node.has_explicit_value

        # NameExpr are class attributes
        elif isinstance(attribute, mp_nodes.NameExpr):
            if not node.explicit_self_type:
                attribute_type = node.type
                is_type_inferred = node.is_inferred

                # We need to get the unanalyzed_type for lists, since mypy is not able to check type hint information
                # regarding list item types
                if (
                    attribute_type is not None
                    and hasattr(attribute_type, "type")
                    and hasattr(attribute_type, "args")
                    and attribute_type.type.fullname == "builtins.list"
                    and not is_type_inferred
                ):
                    if unanalyzed_type is not None and hasattr(unanalyzed_type, "args"):
                        attribute_type.args = unanalyzed_type.args
                    else:  # pragma: no cover
                        raise AttributeError("Could not get argument information for attribute.")

        else:  # pragma: no cover
            raise TypeError("Attribute has an unexpected type.")

        type_ = None
        # Ignore types that are special mypy any types
        if (attribute_type is not None and not (isinstance(attribute_type, mp_types.AnyType) and
                                                not has_correct_type_of_any(attribute_type.type_of_any))):
            # noinspection PyTypeChecker
            type_ = mypy_type_to_abstract_type(attribute_type, unanalyzed_type)

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
            is_type_inferred=is_type_inferred,
            is_public=self._is_public(name, qname),
            is_static=is_static,
            docstring=docstring,
        )

    # #### Parameter utilities

    def _get_default_parameter_value_and_type(
        self, initializer: mp_nodes.Expression, infer_arg_type: bool = False,
    ) -> tuple[None | str | float | int | bool | NoneType, None | sds_types.NamedType]:
        # Get default value information
        default_value = None
        arg_type = None

        if hasattr(initializer, "value"):
            value = initializer.value
        elif isinstance(initializer, mp_nodes.NameExpr):
            if initializer.name == "None":
                value = None
            elif initializer.name == "True":
                value = True
            elif initializer.name == "False":
                value = False
            else:
                # Check if callee path is in our package and create type information
                if self._check_if_qname_in_package(initializer.fullname):
                    default_value = initializer.name
                    if infer_arg_type:
                        arg_type = sds_types.NamedType(name=initializer.name, qname=initializer.fullname)

                return default_value, arg_type

        elif isinstance(initializer, mp_nodes.CallExpr):
            # We do not support call expressions as types
            return default_value, arg_type

        else:  # pragma: no cover
            raise ValueError("No value found for parameter")

        if type(value) in {str, bool, int, float, NoneType}:
            default_value = NoneType if value is None else value

            # Infer the type, if no type hint was found
            if infer_arg_type:
                value_type_name = {
                    str: "str",
                    bool: "bool",
                    int: "int",
                    float: "float",
                    NoneType: "None",
                }[type(value)]
                arg_type = sds_types.NamedType(name=value_type_name, qname=f"builtins.{value_type_name}")

        return default_value, arg_type

    def _parse_parameter_data(self, node: mp_nodes.FuncDef, function_id: str) -> list[Parameter]:
        arguments: list[Parameter] = []

        for argument in node.arguments:
            arg_name = argument.variable.name
            mypy_type = argument.variable.type
            is_type_inferred = False
            arg_kind = get_argument_kind(argument)
            type_annotation = argument.type_annotation
            arg_type = None

            if mypy_type is None:  # pragma: no cover
                raise ValueError("Argument has no type.")
            elif isinstance(mypy_type, mp_types.AnyType) and not has_correct_type_of_any(mypy_type.type_of_any):
                # We try to infer the type through the default value later, if possible
                pass
            elif (isinstance(type_annotation, mp_types.UnboundType) and
                  type_annotation.name in {"list", "set"} and
                  len(type_annotation.args) >= 2):
                # A special case where the argument is a list with multiple types. We have to handle this case like this
                # b/c something like list[int, str] is not allowed according to PEP and therefore not handled the normal
                # way in Mypy.
                arg_type = mypy_type_to_abstract_type(type_annotation)
            elif type_annotation is not None:
                arg_type = mypy_type_to_abstract_type(mypy_type)

            # Get default value and infer type information
            initializer = argument.initializer
            default_value = None
            default_is_none = False
            if initializer is not None:
                infer_arg_type = arg_type is None
                default_value, inferred_arg_type = self._get_default_parameter_value_and_type(
                    initializer=initializer,
                    infer_arg_type=infer_arg_type,
                )

                if default_value == NoneType:
                    default_is_none = True
                    default_value = None

                if infer_arg_type:
                    arg_type = inferred_arg_type
                    is_type_inferred = True

            # Create parameter docstring
            parent = self.__declaration_stack[-1]
            docstring = self.docstring_parser.get_parameter_documentation(
                function_node=node,
                parameter_name=arg_name,
                parameter_assigned_by=arg_kind,
                parent_class=parent if isinstance(parent, Class) else None,
            )

            # Create parameter object
            arguments.append(
                Parameter(
                    id=f"{function_id}/{arg_name}",
                    name=arg_name,
                    is_optional=default_value is not None or default_is_none,
                    default_value=default_value,
                    default_is_none=default_is_none,
                    assigned_by=arg_kind,
                    docstring=docstring,
                    type=arg_type,
                    is_type_inferred=is_type_inferred,
                ),
            )

        return arguments

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

    # Todo This check is currently too weak, we should try to get the path to the package from the api object, not
    #  just the package name. We will resolve this with or after issue #24 and #38, since more information are needed
    #  from the package.
    def _check_if_qname_in_package(self, qname: str) -> bool:
        return self.api.package in qname

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
