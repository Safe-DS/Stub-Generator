from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import mypy.types as mp_types
from mypy import nodes as mp_nodes
from mypy.nodes import ArgKind
from mypy.types import Instance

import safeds_stubgen.api_analyzer._types as sds_types

from ._api import ParameterAssignment, VarianceKind

if TYPE_CHECKING:
    from mypy.nodes import ClassDef, FuncDef, MypyFile
    from mypy.types import ProperType
    from mypy.types import Type as MypyType

    from safeds_stubgen.api_analyzer._types import AbstractType


def get_classdef_definitions(node: ClassDef) -> list:
    return node.defs.body


def get_funcdef_definitions(node: FuncDef) -> list:
    return node.body.body


def get_mypyfile_definitions(node: MypyFile) -> list:
    return node.defs


def mypy_type_to_abstract_type(
    mypy_type: Instance | ProperType | MypyType,
    unanalyzed_type: mp_types.Type | None = None,
) -> AbstractType:

    # Special cases where we need the unanalyzed_type to get the type information we need
    if unanalyzed_type is not None and hasattr(unanalyzed_type, "name"):
        unanalyzed_type_name = unanalyzed_type.name
        if unanalyzed_type_name == "Final":
            # Final type
            types = [mypy_type_to_abstract_type(arg) for arg in getattr(unanalyzed_type, "args", [])]
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
                return mypy_type_to_abstract_type(unanalyzed_type)

    # Iterable mypy types
    if isinstance(mypy_type, mp_types.TupleType):
        return sds_types.TupleType(types=[mypy_type_to_abstract_type(item) for item in mypy_type.items])
    elif isinstance(mypy_type, mp_types.UnionType):
        return sds_types.UnionType(types=[mypy_type_to_abstract_type(item) for item in mypy_type.items])

    # Special Cases
    elif isinstance(mypy_type, mp_types.CallableType):
        return sds_types.CallableType(
            parameter_types=[mypy_type_to_abstract_type(arg_type) for arg_type in mypy_type.arg_types],
            return_type=mypy_type_to_abstract_type(mypy_type.ret_type),
        )
    elif isinstance(mypy_type, mp_types.AnyType):
        return sds_types.NamedType(name="Any")
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
            ](types=[mypy_type_to_abstract_type(arg) for arg in mypy_type.args])
        # Todo Aliasing: Import auflösen, wir können hier keinen fullname (qname) bekommen
        return sds_types.NamedType(name=mypy_type.name)

    # Builtins
    elif isinstance(mypy_type, Instance):
        type_name = mypy_type.type.name
        if type_name in {"int", "str", "bool", "float"}:
            return sds_types.NamedType(name=type_name, qname=mypy_type.type.fullname)

        # Iterable builtins
        elif type_name in {"tuple", "list", "set"}:
            types = [mypy_type_to_abstract_type(arg) for arg in mypy_type.args]
            match type_name:
                case "tuple":
                    return sds_types.TupleType(types=types)
                case "list":
                    return sds_types.ListType(types=types)
                case "set":
                    return sds_types.SetType(types=types)

        elif type_name == "dict":
            return sds_types.DictType(
                key_type=mypy_type_to_abstract_type(mypy_type.args[0]),
                value_type=mypy_type_to_abstract_type(mypy_type.args[1]),
            )
        else:
            return sds_types.NamedType(name=type_name, qname=mypy_type.type.fullname)
    raise ValueError("Unexpected type.")  # pragma: no cover


def get_argument_kind(arg: mp_nodes.Argument) -> ParameterAssignment:
    if arg.variable.is_self or arg.variable.is_cls:
        return ParameterAssignment.IMPLICIT
    elif arg.kind in {ArgKind.ARG_POS, ArgKind.ARG_OPT} and arg.pos_only:
        return ParameterAssignment.POSITION_ONLY
    elif arg.kind in (ArgKind.ARG_OPT, ArgKind.ARG_POS) and not arg.pos_only:
        return ParameterAssignment.POSITION_OR_NAME
    elif arg.kind == ArgKind.ARG_STAR:
        return ParameterAssignment.POSITIONAL_VARARG
    elif arg.kind in (ArgKind.ARG_NAMED, ArgKind.ARG_NAMED_OPT):
        return ParameterAssignment.NAME_ONLY
    elif arg.kind == ArgKind.ARG_STAR2:
        return ParameterAssignment.NAMED_VARARG
    else:  # pragma: no cover
        raise ValueError("Could not find an appropriate parameter assignment.")


def find_return_stmts_recursive(stmts: list[mp_nodes.Statement] | list[mp_nodes.Block]) -> list[mp_nodes.ReturnStmt]:
    return_stmts = []
    for stmt in stmts:
        if isinstance(stmt, mp_nodes.IfStmt):
            return_stmts += find_return_stmts_recursive(stmt.body)
            if stmt.else_body:
                return_stmts += find_return_stmts_recursive(stmt.else_body.body)
        elif isinstance(stmt, mp_nodes.Block):
            return_stmts += find_return_stmts_recursive(stmt.body)
        elif isinstance(stmt, mp_nodes.TryStmt):
            return_stmts += find_return_stmts_recursive([stmt.body])
            return_stmts += find_return_stmts_recursive(stmt.handlers)
        elif isinstance(stmt, mp_nodes.MatchStmt):
            return_stmts += find_return_stmts_recursive(stmt.bodies)
        elif isinstance(stmt, mp_nodes.WhileStmt | mp_nodes.WithStmt | mp_nodes.ForStmt):
            return_stmts += find_return_stmts_recursive(stmt.body.body)
        elif isinstance(stmt, mp_nodes.ReturnStmt):
            return_stmts.append(stmt)

    return return_stmts


def mypy_variance_parser(mypy_variance_type: Literal[0, 1, 2]) -> VarianceKind:
    match mypy_variance_type:
        case 0:
            return VarianceKind.INVARIANT
        case 1:
            return VarianceKind.COVARIANT
        case 2:
            return VarianceKind.CONTRAVARIANT
        case _:  # pragma: no cover
            raise ValueError("Mypy variance parser received an illegal parameter value.")


def has_correct_type_of_any(type_of_any: int) -> bool:
    # In Mypy AnyType can be set as type because of different reasons (see TypeOfAny class-documentation)
    return type_of_any in {
        mp_types.TypeOfAny.explicit,
        mp_types.TypeOfAny.from_omitted_generics,
        mp_types.TypeOfAny.from_another_any,
    }


def mypy_expression_to_sds_type(expr: mp_nodes.Expression) -> sds_types.AbstractType:
    if isinstance(expr, mp_nodes.NameExpr):
        if expr.name in {"False", "True"}:
            return sds_types.NamedType(name="bool", qname="builtins.bool")
        else:
            return sds_types.NamedType(name=expr.name, qname=expr.fullname)
    elif isinstance(expr, mp_nodes.IntExpr):
        return sds_types.NamedType(name="int", qname="builtins.int")
    elif isinstance(expr, mp_nodes.FloatExpr):
        return sds_types.NamedType(name="float", qname="builtins.float")
    elif isinstance(expr, mp_nodes.StrExpr):
        return sds_types.NamedType(name="str", qname="builtins.str")
    elif isinstance(expr, mp_nodes.TupleExpr):
        return sds_types.TupleType(types=[mypy_expression_to_sds_type(item) for item in expr.items])

    raise TypeError("Unexpected expression type.")  # pragma: no cover


def mypy_expression_to_python_value(expr: mp_nodes.Expression) -> str | None | int | float:
    if isinstance(expr, mp_nodes.NameExpr):
        match expr.name:
            case "None":
                return None
            case "True":
                return True
            case "False":
                return False
            case _:
                return expr.name
    elif isinstance(expr, mp_nodes.IntExpr | mp_nodes.FloatExpr | mp_nodes.StrExpr):
        return expr.value

    raise TypeError("Unexpected expression type.")  # pragma: no cover
