from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import mypy.types as mp_types
from mypy import nodes as mp_nodes
from mypy.nodes import ArgKind

import safeds_stubgen.api_analyzer._types as sds_types

from ._api import ParameterAssignment, VarianceKind

if TYPE_CHECKING:
    from mypy.nodes import ClassDef, FuncDef, MypyFile


def get_classdef_definitions(node: ClassDef) -> list:
    return node.defs.body


def get_funcdef_definitions(node: FuncDef) -> list:
    return node.body.body


def get_mypyfile_definitions(node: MypyFile) -> list:
    return node.defs


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
        mp_types.TypeOfAny.from_another_any,
        mp_types.TypeOfAny.from_unimported_type,
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


def mypy_expression_to_python_value(
    expr: mp_nodes.IntExpr | mp_nodes.FloatExpr | mp_nodes.StrExpr | mp_nodes.NameExpr,
) -> str | None | int | float:
    if isinstance(expr, mp_nodes.NameExpr):
        match expr.name:
            case "None":
                return None
            case "True":
                return True
            case "False":
                return False
    elif isinstance(expr, mp_nodes.IntExpr | mp_nodes.FloatExpr | mp_nodes.StrExpr):
        return expr.value

    raise TypeError("Unexpected expression type.")  # pragma: no cover
