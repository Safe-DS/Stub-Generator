from __future__ import annotations

from typing import TYPE_CHECKING

import mypy.types as mp_types
from mypy.types import Instance

import safeds_stubgen.api_analyzer._types as sds_types

if TYPE_CHECKING:
    from mypy.nodes import ClassDef, FuncDef, MypyFile
    from mypy.types import ProperType
    from safeds_stubgen.api_analyzer._types import AbstractType


def get_classdef_definitions(node: ClassDef):
    return node.defs.body


def get_funcdef_definitions(node: FuncDef):
    return node.body.body


def get_mypyfile_definitions(node: MypyFile):
    return node.defs


def mypy_type_to_abstract_type(mypy_type: Instance | ProperType) -> AbstractType:
    types = []

    # Iterable mypy types
    if isinstance(mypy_type, mp_types.TupleType):
        for item in mypy_type.items:
            types.append(
                mypy_type_to_abstract_type(item),
            )
        return sds_types.TupleType(types=types)
    elif isinstance(mypy_type, mp_types.UnionType):
        for item in mypy_type.items:
            types.append(
                mypy_type_to_abstract_type(item),
            )
        return sds_types.UnionType(types=types)

    # Special Cases
    elif isinstance(mypy_type, mp_types.AnyType):
        return sds_types.NamedType(name="Any")
    elif isinstance(mypy_type, mp_types.NoneType):
        return sds_types.NamedType(name="None")
    elif isinstance(mypy_type, mp_types.UnboundType):
        # Todo Import aliasing auflösen
        return sds_types.NamedType(name=mypy_type.name)

    # Builtins
    elif isinstance(mypy_type, Instance):
        type_name = mypy_type.type.name
        if type_name in {"int", "str", "bool", "float"}:
            return sds_types.NamedType(name=type_name)
        elif type_name == "tuple":
            return sds_types.TupleType(types=[])
        elif type_name == "list":
            for arg in mypy_type.args:
                types.append(
                    mypy_type_to_abstract_type(arg),
                )
            return sds_types.ListType(types=types)
        elif type_name == "set":
            for arg in mypy_type.args:
                types.append(
                    mypy_type_to_abstract_type(arg),
                )
            return sds_types.SetType(types=types)
        elif type_name == "dict":
            key_type = None
            value_type = None
            value_types = []
            for i, arg in enumerate(mypy_type.args):
                if i == 1:
                    key_type = mypy_type_to_abstract_type(arg)
                else:
                    value_types.append(
                        mypy_type_to_abstract_type(arg),
                    )

            if len(value_types) == 1:
                value_type = value_types[0]
            elif len(value_types) >= 2:
                value_type = sds_types.UnionType(types=value_types)

            return sds_types.DictType(key_type=key_type, value_type=value_type)
        else:
            return sds_types.NamedType(name=type_name)
    raise ValueError("Unexpected type.")
