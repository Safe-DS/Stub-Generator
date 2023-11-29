from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import mypy.types as mp_types
from mypy import nodes as mp_nodes
from mypy.nodes import ArgKind
from mypy.types import Instance

import safeds_stubgen.api_analyzer._types as sds_types

from ._api import ParameterAssignment, VarianceType

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
    unanalyzed_type: mp_types.Type | None = None
) -> AbstractType:

    # Final type
    if unanalyzed_type is not None and hasattr(unanalyzed_type, "name") and unanalyzed_type.name == "Final":
        types = [
            mypy_type_to_abstract_type(arg)
            for arg in unanalyzed_type.args
        ]
        if len(types) == 1:
            return sds_types.FinalType(type_=types[0])
        return sds_types.FinalType(type_=sds_types.UnionType(types=types))

    # Iterable mypy types
    elif isinstance(mypy_type, mp_types.TupleType):
        return sds_types.TupleType(types=[
            mypy_type_to_abstract_type(item)
            for item in mypy_type.items
        ])
    elif isinstance(mypy_type, mp_types.UnionType):
        return sds_types.UnionType(types=[
            mypy_type_to_abstract_type(item)
            for item in mypy_type.items
        ])

    # Special Cases
    elif isinstance(mypy_type, mp_types.CallableType):
        return sds_types.CallableType(
            parameter_types=[
                mypy_type_to_abstract_type(arg_type)
                for arg_type in mypy_type.arg_types
            ],
            return_type=mypy_type_to_abstract_type(mypy_type.ret_type)
        )
    elif isinstance(mypy_type, mp_types.AnyType):
        return sds_types.NamedType(name="Any")
    elif isinstance(mypy_type, mp_types.NoneType):
        return sds_types.NamedType(name="None", qname="builtins.None")
    elif isinstance(mypy_type, mp_types.LiteralType):
        return sds_types.LiteralType(literal=mypy_type.value)
    elif isinstance(mypy_type, mp_types.UnboundType):
        if mypy_type.name == "list":
            return sds_types.ListType(types=[
                mypy_type_to_abstract_type(arg)
                for arg in mypy_type.args
            ])
        # Todo Aliasing: Import auflösen, wir können wir keinen fullname (qname) bekommen
        return sds_types.NamedType(name=mypy_type.name)

    # Builtins
    elif isinstance(mypy_type, Instance):
        type_name = mypy_type.type.name
        if type_name in {"int", "str", "bool", "float"}:
            return sds_types.NamedType(name=type_name, qname=mypy_type.type.fullname)

        # Iterable builtins
        elif type_name in {"tuple", "list", "set"}:
            types = [
                mypy_type_to_abstract_type(arg)
                for arg in mypy_type.args
            ]
            return {
                "tuple": sds_types.TupleType,
                "list": sds_types.ListType,
                "set": sds_types.SetType,
            }[type_name](types=types)

        elif type_name == "dict":
            key_type = mypy_type_to_abstract_type(mypy_type.args[0])
            value_types = [mypy_type_to_abstract_type(arg) for arg in mypy_type.args[1:]]

            value_type: AbstractType
            if len(value_types) == 0:
                value_type = sds_types.NamedType(name="Any")
            elif len(value_types) == 1:
                value_type = value_types[0]
            else:
                value_type = sds_types.UnionType(types=value_types)

            return sds_types.DictType(key_type=key_type, value_type=value_type)
        else:
            return sds_types.NamedType(name=type_name, qname=mypy_type.type.fullname)
    raise ValueError("Unexpected type.")


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
    else:
        raise ValueError("Could not find an appropriate parameter assignment.")


def find_return_stmts_recursive(stmts: list[mp_nodes.Statement]) -> list[mp_nodes.ReturnStmt]:
    return_stmts = []
    for stmt in stmts:
        if isinstance(stmt, mp_nodes.IfStmt):
            return_stmts += find_return_stmts_recursive(stmt.body)
            if stmt.else_body:
                return_stmts += find_return_stmts_recursive(stmt.else_body.body)
        elif isinstance(stmt, mp_nodes.Block | mp_nodes.TryStmt):
            return_stmts += find_return_stmts_recursive(stmt.body)
        elif isinstance(stmt, mp_nodes.MatchStmt):
            return_stmts += find_return_stmts_recursive(stmt.bodies)
        elif isinstance(stmt, mp_nodes.WhileStmt | mp_nodes.WithStmt | mp_nodes.ForStmt):
            return_stmts += find_return_stmts_recursive(stmt.body.body)
        elif isinstance(stmt, mp_nodes.ReturnStmt):
            return_stmts.append(stmt)

    return return_stmts


def mypy_variance_parser(mypy_variance_type: Literal[0, 1, 2]) -> VarianceType:
    match mypy_variance_type:
        case 0:
            return VarianceType.INVARIANT
        case 1:
            return VarianceType.COVARIANT
        case 2:
            return VarianceType.CONTRAVARIANT
        case _:  # pragma: no cover
            raise ValueError("Mypy variance parser received an illegal parameter value.")
