from copy import deepcopy

import pytest

from safeds_stubgen.api_analyzer import (
    AbstractType,
    Attribute,
    CallableType,
    DictType,
    FinalType,
    ListType,
    LiteralType,
    NamedSequenceType,
    NamedType,
    Parameter,
    ParameterAssignment,
    SetType,
    TupleType,
    TypeVarType,
    UnionType,
    UnknownType,
)
from safeds_stubgen.docstring_parsing import AttributeDocstring, ParameterDocstring


def test_correct_hash() -> None:
    parameter = Parameter(
        id="test/test.Test/test/test_parameter_for_hashing",
        name="test_parameter_for_hashing",
        is_optional=True,
        default_value="test_str",
        assigned_by=ParameterAssignment.POSITION_OR_NAME,
        docstring=ParameterDocstring(None, "r", "r"),
        type=NamedType(name="str", qname=""),
    )
    assert hash(parameter) == hash(deepcopy(parameter))
    assert NamedType("a", "") == NamedType("a", "")
    assert hash(NamedType("a", "")) == hash(NamedType("a", ""))
    assert NamedType("a", "") != NamedType("b", "")
    assert hash(NamedType("a", "")) != hash(NamedType("b", ""))
    attribute = Attribute(
        id="boundary",
        name="boundary",
        type=NamedType("a", ""),
        is_public=True,
        is_static=True,
        docstring=AttributeDocstring(),
    )
    assert attribute == deepcopy(attribute)
    assert hash(attribute) == hash(deepcopy(attribute))


def test_named_type() -> None:
    name = "str"
    named_type = NamedType(name, "")
    named_type_dict = {"kind": "NamedType", "name": name, "qname": ""}

    assert AbstractType.from_dict(named_type_dict) == named_type

    assert NamedType.from_dict(named_type_dict) == named_type

    assert named_type.to_dict() == named_type_dict


def test_union_type() -> None:
    union_type = UnionType([NamedType("str", ""), NamedType("int", "")])
    union_type_dict = {
        "kind": "UnionType",
        "types": [{"kind": "NamedType", "name": "str", "qname": ""}, {"kind": "NamedType", "name": "int", "qname": ""}],
    }

    assert AbstractType.from_dict(union_type_dict) == union_type
    assert UnionType.from_dict(union_type_dict) == union_type
    assert union_type.to_dict() == union_type_dict

    assert UnionType([NamedType("a", "")]) == UnionType([NamedType("a", "")])
    assert hash(UnionType([NamedType("a", "")])) == hash(UnionType([NamedType("a", "")]))
    assert UnionType([NamedType("a", "")]) != UnionType([NamedType("b", "")])
    assert hash(UnionType([NamedType("a", "")])) != hash(UnionType([NamedType("b", "")]))

    assert UnionType([NamedType("a", ""), LiteralType(["b"])]) == UnionType([LiteralType(["b"]), NamedType("a", "")])
    assert UnionType([NamedType("a", ""), LiteralType(["b"])]) != UnionType([LiteralType(["a"]), NamedType("b", "")])
    assert UnionType([NamedType("a", ""), NamedType("b", "")]) != UnionType([NamedType("a", ""), NamedType("c", "")])


def test_callable_type() -> None:
    callable_type = CallableType(
        parameter_types=[NamedType("str", ""), NamedType("int", "")],
        return_type=TupleType(types=[NamedType("bool", ""), NamedType("None", "")]),
    )
    callable_type_dict = {
        "kind": "CallableType",
        "parameter_types": [
            {"kind": "NamedType", "name": "str", "qname": ""},
            {"kind": "NamedType", "name": "int", "qname": ""},
        ],
        "return_type": {
            "kind": "TupleType",
            "types": [
                {"kind": "NamedType", "name": "bool", "qname": ""},
                {"kind": "NamedType", "name": "None", "qname": ""},
            ],
        },
    }

    assert AbstractType.from_dict(callable_type_dict) == callable_type
    assert CallableType.from_dict(callable_type_dict) == callable_type
    assert callable_type.to_dict() == callable_type_dict

    assert CallableType([NamedType("a", "")], NamedType("a", "")) == CallableType(
        [NamedType("a", "")],
        NamedType("a", ""),
    )
    assert hash(CallableType([NamedType("a", "")], NamedType("a", ""))) == hash(
        CallableType([NamedType("a", "")], NamedType("a", "")),
    )
    assert CallableType([NamedType("a", "")], NamedType("a", "")) != CallableType(
        [NamedType("b", "")],
        NamedType("a", ""),
    )
    assert hash(CallableType([NamedType("a", "")], NamedType("a", ""))) != hash(
        CallableType([NamedType("b", "")], NamedType("a", "")),
    )

    assert CallableType([NamedType("a", ""), LiteralType(["b"])], NamedType("c", "")) == CallableType(
        [LiteralType(["b"]), NamedType("a", "")],
        NamedType("c", ""),
    )
    assert CallableType([NamedType("a", ""), LiteralType(["b"])], NamedType("c", "")) != CallableType(
        [LiteralType(["a"]), NamedType("b", "")],
        NamedType("c", ""),
    )
    assert CallableType([NamedType("a", ""), NamedType("b", "")], NamedType("c", "")) != CallableType(
        [NamedType("a", ""), NamedType("c", "")],
        NamedType("c", ""),
    )


def test_list_type() -> None:
    list_type = ListType([NamedType("str", "builtins.str"), NamedType("int", "builtins.int")])
    list_type_dict = {
        "kind": "ListType",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": "builtins.str"},
            {"kind": "NamedType", "name": "int", "qname": "builtins.int"},
        ],
    }

    assert AbstractType.from_dict(list_type_dict) == list_type
    assert ListType.from_dict(list_type_dict) == list_type
    assert list_type.to_dict() == list_type_dict

    assert ListType([NamedType("a", "")]) == ListType([NamedType("a", "")])
    assert hash(ListType([NamedType("a", "")])) == hash(ListType([NamedType("a", "")]))
    assert ListType([NamedType("a", "")]) != ListType([NamedType("b", "")])
    assert hash(ListType([NamedType("a", "")])) != hash(ListType([NamedType("b", "")]))

    assert ListType([NamedType("a", ""), LiteralType(["b"])]) == ListType([LiteralType(["b"]), NamedType("a", "")])
    assert ListType([NamedType("a", ""), LiteralType(["b"])]) != ListType([LiteralType(["a"]), NamedType("b", "")])
    assert ListType([NamedType("a", ""), NamedType("b", "")]) != ListType([NamedType("a", ""), NamedType("c", "")])


def test_named_sequence_type() -> None:
    list_type = NamedSequenceType("a", "b.a", [NamedType("str", "builtins.str"), NamedType("int", "builtins.int")])
    named_sequence_type_dict = {
        "kind": "NamedSequenceType",
        "name": "a",
        "qname": "b.a",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": "builtins.str"},
            {"kind": "NamedType", "name": "int", "qname": "builtins.int"},
        ],
    }

    assert AbstractType.from_dict(named_sequence_type_dict) == list_type
    assert NamedSequenceType.from_dict(named_sequence_type_dict) == list_type
    assert list_type.to_dict() == named_sequence_type_dict

    assert NamedSequenceType("a", "b.a", [NamedType("a", "")]) == NamedSequenceType("a", "b.a", [NamedType("a", "")])
    assert hash(NamedSequenceType("a", "b.a", [NamedType("a", "")])) == hash(
        NamedSequenceType("a", "b.a", [NamedType("a", "")]),
    )
    assert NamedSequenceType("a", "b.a", [NamedType("a", "")]) != NamedSequenceType("a", "b.a", [NamedType("b", "")])
    assert hash(NamedSequenceType("a", "b.a", [NamedType("a", "")])) != hash(
        NamedSequenceType("a", "b.a", [NamedType("b", "")]),
    )

    assert NamedSequenceType("a", "b.a", [NamedType("a", ""), LiteralType(["b"])]) == NamedSequenceType(
        "a",
        "b.a",
        [LiteralType(["b"]), NamedType("a", "")],
    )
    assert NamedSequenceType("a", "b.a", [NamedType("a", ""), LiteralType(["b"])]) != NamedSequenceType(
        "a",
        "b.a",
        [LiteralType(["a"]), NamedType("b", "")],
    )
    assert NamedSequenceType("a", "b.a", [NamedType("a", ""), NamedType("b", "")]) != NamedSequenceType(
        "a",
        "b.a",
        [NamedType("a", ""), NamedType("c", "")],
    )


def test_dict_type() -> None:
    dict_type = DictType(
        key_type=UnionType([NamedType("str", "builtins.str"), NamedType("int", "builtins.int")]),
        value_type=UnionType([NamedType("str", "builtins.str"), NamedType("int", "builtins.int")]),
    )
    dict_type_dict = {
        "kind": "DictType",
        "key_type": {
            "kind": "UnionType",
            "types": [
                {"kind": "NamedType", "name": "str", "qname": "builtins.str"},
                {"kind": "NamedType", "name": "int", "qname": "builtins.int"},
            ],
        },
        "value_type": {
            "kind": "UnionType",
            "types": [
                {"kind": "NamedType", "name": "str", "qname": "builtins.str"},
                {"kind": "NamedType", "name": "int", "qname": "builtins.int"},
            ],
        },
    }

    assert AbstractType.from_dict(dict_type_dict) == dict_type
    assert DictType.from_dict(dict_type_dict) == dict_type
    assert dict_type.to_dict() == dict_type_dict

    assert DictType(NamedType("a", ""), NamedType("a", "")) == DictType(NamedType("a", ""), NamedType("a", ""))
    assert hash(DictType(NamedType("a", ""), NamedType("a", ""))) == hash(
        DictType(NamedType("a", ""), NamedType("a", "")),
    )
    assert DictType(NamedType("a", ""), NamedType("a", "")) != DictType(NamedType("b", ""), NamedType("a", ""))
    assert hash(DictType(NamedType("a", ""), NamedType("a", ""))) != hash(
        DictType(NamedType("b", ""), NamedType("a", "")),
    )


def test_set_type() -> None:
    set_type = SetType([NamedType("str", "builtins.str"), NamedType("int", "builtins.int")])
    set_type_dict = {
        "kind": "SetType",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": "builtins.str"},
            {"kind": "NamedType", "name": "int", "qname": "builtins.int"},
        ],
    }

    assert AbstractType.from_dict(set_type_dict) == set_type
    assert SetType.from_dict(set_type_dict) == set_type
    assert set_type.to_dict() == set_type_dict

    assert SetType([NamedType("a", "")]) == SetType([NamedType("a", "")])
    assert hash(SetType([NamedType("a", "")])) == hash(SetType([NamedType("a", "")]))
    assert SetType([NamedType("a", "")]) != SetType([NamedType("b", "")])
    assert hash(SetType([NamedType("a", "")])) != hash(SetType([NamedType("b", "")]))

    assert SetType([NamedType("a", ""), LiteralType(["b"])]) == SetType([LiteralType(["b"]), NamedType("a", "")])
    assert SetType([NamedType("a", ""), LiteralType(["b"])]) != SetType([LiteralType(["a"]), NamedType("b", "")])
    assert SetType([NamedType("a", ""), NamedType("b", "")]) != SetType([NamedType("a", ""), NamedType("c", "")])


def test_literal_type() -> None:
    type_ = LiteralType(["Literal_1", 2])
    type_dict = {
        "kind": "LiteralType",
        "literals": ["Literal_1", 2],
    }

    assert AbstractType.from_dict(type_dict) == type_
    assert LiteralType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict

    assert LiteralType(["a"]) == LiteralType(["a"])
    assert hash(LiteralType(["a"])) == hash(LiteralType(["a"]))
    assert LiteralType(["a"]) != LiteralType(["b"])
    assert hash(LiteralType(["a"])) != hash(LiteralType(["b"]))

    assert LiteralType(["a", 1]) == LiteralType([1, "a"])
    assert LiteralType(["a", 1]) != LiteralType(["a", "1"])
    assert LiteralType(["a", "b"]) != LiteralType(["a", "c"])


def test_type_var_type() -> None:
    type_ = TypeVarType("_T")
    type_dict = {"kind": "TypeVarType", "name": "_T", "upper_bound": None}

    assert AbstractType.from_dict(type_dict) == type_
    assert TypeVarType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict

    assert TypeVarType("a", None) == TypeVarType("a", None)
    assert hash(TypeVarType("a", None)) == hash(TypeVarType("a", None))
    assert TypeVarType("a", None) != TypeVarType("b", None)
    assert hash(TypeVarType("a", None)) != hash(TypeVarType("b", None))


def test_final_type() -> None:
    type_ = FinalType(NamedType("some_type", ""))
    type_dict = {
        "kind": "FinalType",
        "type": {"kind": "NamedType", "name": "some_type", "qname": ""},
    }

    assert AbstractType.from_dict(type_dict) == type_
    assert FinalType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict

    assert FinalType(NamedType("a", "")) == FinalType(NamedType("a", ""))
    assert hash(FinalType(NamedType("a", ""))) == hash(FinalType(NamedType("a", "")))
    assert FinalType(NamedType("a", "")) != FinalType(NamedType("b", ""))
    assert hash(FinalType(NamedType("a", ""))) != hash(FinalType(NamedType("b", "")))


def test_unknown_type() -> None:
    type_ = UnknownType()
    type_dict = {"kind": "UnknownType"}

    assert AbstractType.from_dict(type_dict) == type_
    assert UnknownType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict


def test_tuple_type() -> None:
    set_type = TupleType([NamedType("str", "builtins.str"), NamedType("int", "builtins.int")])
    set_type_dict = {
        "kind": "TupleType",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": "builtins.str"},
            {"kind": "NamedType", "name": "int", "qname": "builtins.int"},
        ],
    }

    assert AbstractType.from_dict(set_type_dict) == set_type
    assert TupleType.from_dict(set_type_dict) == set_type
    assert set_type.to_dict() == set_type_dict

    assert TupleType([NamedType("a", "")]) == TupleType([NamedType("a", "")])
    assert hash(TupleType([NamedType("a", "")])) == hash(TupleType([NamedType("a", "")]))
    assert TupleType([NamedType("a", "")]) != TupleType([NamedType("b", "")])
    assert hash(TupleType([NamedType("a", "")])) != hash(TupleType([NamedType("b", "")]))

    assert TupleType([NamedType("a", ""), LiteralType(["b"])]) == TupleType([LiteralType(["b"]), NamedType("a", "")])
    assert TupleType([NamedType("a", ""), LiteralType(["b"])]) != TupleType([LiteralType(["a"]), NamedType("b", "")])
    assert TupleType([NamedType("a", ""), NamedType("b", "")]) != TupleType([NamedType("a", ""), NamedType("c", "")])


def test_abstract_type_from_dict_exception() -> None:
    with pytest.raises(ValueError, match="Cannot parse unknown_type value."):
        AbstractType.from_dict({"kind": "unknown_type"})
