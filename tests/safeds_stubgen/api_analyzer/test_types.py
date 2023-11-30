from copy import deepcopy

import pytest
from safeds_stubgen.api_analyzer import (
    AbstractType,
    Attribute,
    BoundaryType,
    CallableType,
    DictType,
    EnumType,
    FinalType,
    ListType,
    LiteralType,
    NamedType,
    Parameter,
    ParameterAssignment,
    SetType,
    TupleType,
    UnionType,
)
from safeds_stubgen.docstring_parsing import AttributeDocstring, ParameterDocstring


def test_correct_hash() -> None:
    parameter = Parameter(
        id="test/test.Test/test/test_parameter_for_hashing",
        name="test_parameter_for_hashing",
        is_optional=True,
        default_value="test_str",
        default_is_none=False,
        assigned_by=ParameterAssignment.POSITION_OR_NAME,
        docstring=ParameterDocstring("'hashvalue'", "r", "r"),
        type=NamedType("str"),
        is_type_inferred=False
    )
    assert hash(parameter) == hash(deepcopy(parameter))
    enum_values = frozenset({"a", "b", "c"})
    enum_type = EnumType(enum_values, "full_match")
    assert enum_type == deepcopy(enum_type)
    assert hash(enum_type) == hash(deepcopy(enum_type))
    assert enum_type == EnumType(deepcopy(enum_values), "full_match")
    assert hash(enum_type) == hash(EnumType(deepcopy(enum_values), "full_match"))
    assert enum_type != EnumType(frozenset({"a", "b"}), "full_match")
    assert hash(enum_type) != hash(EnumType(frozenset({"a", "b"}), "full_match"))
    assert NamedType("a") == NamedType("a")
    assert hash(NamedType("a")) == hash(NamedType("a"))
    assert NamedType("a") != NamedType("b")
    assert hash(NamedType("a")) != hash(NamedType("b"))
    attribute = Attribute(
        id="boundary",
        name="boundary",
        type=BoundaryType(
            base_type="int",
            min=0,
            max=1,
            min_inclusive=True,
            max_inclusive=True,
        ),
        is_type_inferred=False,
        is_public=True,
        is_static=True,
        docstring=AttributeDocstring(),
    )
    assert attribute == deepcopy(attribute)
    assert hash(attribute) == hash(deepcopy(attribute))


def test_named_type() -> None:
    name = "str"
    named_type = NamedType(name)
    named_type_dict = {"kind": "NamedType", "name": name, "qname": ""}

    assert AbstractType.from_dict(named_type_dict) == named_type

    assert NamedType.from_dict(named_type_dict) == named_type
    assert NamedType.from_string(name) == named_type

    assert named_type.to_dict() == named_type_dict


def test_enum_type() -> None:
    value = frozenset({"a", "b"})
    type_ = EnumType(value, "a, b")
    type_dict = {"kind": "EnumType", "values": {"a", "b"}}

    assert AbstractType.from_dict(type_dict) == type_
    assert EnumType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict


def test_boundary_type() -> None:
    type_ = BoundaryType(
        base_type="int",
        min=1,
        max="b",
        min_inclusive=True,
        max_inclusive=True,
    )
    type_dict = {
        "kind": "BoundaryType",
        "base_type": "int",
        "min": 1,
        "max": "b",
        "min_inclusive": True,
        "max_inclusive": True,
    }

    assert AbstractType.from_dict(type_dict) == type_
    assert BoundaryType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict


def test_union_type() -> None:
    union_type = UnionType([NamedType("str"), NamedType("int")])
    union_type_dict = {
        "kind": "UnionType",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": ""},
            {"kind": "NamedType", "name": "int", "qname": ""}
        ],
    }

    assert AbstractType.from_dict(union_type_dict) == union_type
    assert UnionType.from_dict(union_type_dict) == union_type
    assert union_type.to_dict() == union_type_dict

    assert UnionType([NamedType("a")]) == UnionType([NamedType("a")])
    assert hash(UnionType([NamedType("a")])) == hash(UnionType([NamedType("a")]))
    assert UnionType([NamedType("a")]) != UnionType([NamedType("b")])
    assert hash(UnionType([NamedType("a")])) != hash(UnionType([NamedType("b")]))


def test_callable_type() -> None:
    callable_type = CallableType(
        parameter_types=[NamedType("str"), NamedType("int")],
        return_type=TupleType(types=[NamedType("bool"), NamedType("None")])
    )
    callable_type_dict = {
        "kind": "CallableType",
        "parameter_types": [
            {"kind": "NamedType", "name": "str", "qname": ""},
            {"kind": "NamedType", "name": "int", "qname": ""}
        ],
        "return_type": {"kind": "TupleType", "types": [
            {"kind": "NamedType", "name": "bool", "qname": ""},
            {"kind": "NamedType", "name": "None", "qname": ""}
        ]},
    }

    assert AbstractType.from_dict(callable_type_dict) == callable_type
    assert CallableType.from_dict(callable_type_dict) == callable_type
    assert callable_type.to_dict() == callable_type_dict

    assert CallableType([NamedType("a")], NamedType("a")) == CallableType([NamedType("a")], NamedType("a"))
    assert hash(CallableType([NamedType("a")], NamedType("a"))) == hash(CallableType([NamedType("a")], NamedType("a")))
    assert CallableType([NamedType("a")], NamedType("a")) != CallableType([NamedType("b")], NamedType("a"))
    assert hash(CallableType([NamedType("a")], NamedType("a"))) != hash(CallableType([NamedType("b")], NamedType("a")))


def test_list_type() -> None:
    list_type = ListType([NamedType("str"), NamedType("int")])
    list_type_dict = {
        "kind": "ListType",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": ""},
            {"kind": "NamedType", "name": "int", "qname": ""}
        ],
    }

    assert AbstractType.from_dict(list_type_dict) == list_type
    assert ListType.from_dict(list_type_dict) == list_type
    assert list_type.to_dict() == list_type_dict

    assert ListType([NamedType("a")]) == ListType([NamedType("a")])
    assert hash(ListType([NamedType("a")])) == hash(ListType([NamedType("a")]))
    assert ListType([NamedType("a")]) != ListType([NamedType("b")])
    assert hash(ListType([NamedType("a")])) != hash(ListType([NamedType("b")]))


def test_dict_type() -> None:
    dict_type = DictType(
        key_type=UnionType([NamedType("str"), NamedType("int")]),
        value_type=UnionType([NamedType("str"), NamedType("int")]),
    )
    dict_type_dict = {
        "kind": "DictType",
        "key_type": {
            "kind": "UnionType",
            "types": [
                {"kind": "NamedType", "name": "str", "qname": ""},
                {"kind": "NamedType", "name": "int", "qname": ""}
            ],
        },
        "value_type": {
            "kind": "UnionType",
            "types": [
                {"kind": "NamedType", "name": "str", "qname": ""},
                {"kind": "NamedType", "name": "int", "qname": ""}
            ],
        },
    }

    assert AbstractType.from_dict(dict_type_dict) == dict_type
    assert DictType.from_dict(dict_type_dict) == dict_type
    assert dict_type.to_dict() == dict_type_dict

    assert DictType(NamedType("a"), NamedType("a")) == DictType(NamedType("a"), NamedType("a"))
    assert hash(DictType(NamedType("a"), NamedType("a"))) == hash(DictType(NamedType("a"), NamedType("a")))
    assert DictType(NamedType("a"), NamedType("a")) != DictType(NamedType("b"), NamedType("a"))
    assert hash(DictType(NamedType("a"), NamedType("a"))) != hash(DictType(NamedType("b"), NamedType("a")))


def test_set_type() -> None:
    set_type = SetType([NamedType("str"), NamedType("int")])
    set_type_dict = {
        "kind": "SetType",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": ""},
            {"kind": "NamedType", "name": "int", "qname": ""}
        ],
    }

    assert AbstractType.from_dict(set_type_dict) == set_type
    assert SetType.from_dict(set_type_dict) == set_type
    assert set_type.to_dict() == set_type_dict

    assert SetType([NamedType("a")]) == SetType([NamedType("a")])
    assert hash(SetType([NamedType("a")])) == hash(SetType([NamedType("a")]))
    assert SetType([NamedType("a")]) != SetType([NamedType("b")])
    assert hash(SetType([NamedType("a")])) != hash(SetType([NamedType("b")]))


def test_literal_type() -> None:
    type_ = LiteralType("Literal_1")
    type_dict = {
        "kind": "LiteralType",
        "literal": "Literal_1",
    }

    assert AbstractType.from_dict(type_dict) == type_
    assert LiteralType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict

    assert LiteralType("a") == LiteralType("a")
    assert hash(LiteralType("a")) == hash(LiteralType("a"))
    assert LiteralType("a") != LiteralType("b")
    assert hash(LiteralType("a")) != hash(LiteralType("b"))


def test_final_type() -> None:
    type_ = FinalType(NamedType("some_type"))
    type_dict = {
        "kind": "FinalType",
        "type": {"kind": "NamedType", "name": "some_type", "qname": ""},
    }

    assert AbstractType.from_dict(type_dict) == type_
    assert FinalType.from_dict(type_dict) == type_
    assert type_.to_dict() == type_dict

    assert FinalType(NamedType("a")) == FinalType(NamedType("a"))
    assert hash(FinalType(NamedType("a"))) == hash(FinalType(NamedType("a")))
    assert FinalType(NamedType("a")) != FinalType(NamedType("b"))
    assert hash(FinalType(NamedType("a"))) != hash(FinalType(NamedType("b")))


def test_tuple_type() -> None:
    set_type = TupleType([NamedType("str"), NamedType("int")])
    set_type_dict = {
        "kind": "TupleType",
        "types": [
            {"kind": "NamedType", "name": "str", "qname": ""},
            {"kind": "NamedType", "name": "int", "qname": ""}
        ],
    }

    assert AbstractType.from_dict(set_type_dict) == set_type
    assert TupleType.from_dict(set_type_dict) == set_type
    assert set_type.to_dict() == set_type_dict

    assert TupleType([NamedType("a")]) == TupleType([NamedType("a")])
    assert hash(TupleType([NamedType("a")])) == hash(TupleType([NamedType("a")]))
    assert TupleType([NamedType("a")]) != TupleType([NamedType("b")])
    assert hash(TupleType([NamedType("a")])) != hash(TupleType([NamedType("b")]))


def test_abstract_type_from_dict_exception() -> None:
    with pytest.raises(ValueError, match="Cannot parse unknown_type value."):
        AbstractType.from_dict({"kind": "unknown_type"})


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        (
            (
                "float, default=0.0 Tolerance for singular values computed by svd_solver == 'arpack'.\nMust be of range"
                " [0.0, infinity).\n\n.. versionadded:: 0.18.0"
            ),
            BoundaryType(
                base_type="float",
                min=0,
                max="Infinity",
                min_inclusive=True,
                max_inclusive=True,
            ),
        ),
        (
            """If bootstrap is True, the number of samples to draw from X\nto train each base estimator.\n\n
            - If None (default), then draw `X.shape[0]` samples.\n- If int, then draw `max_samples` samples.\n
            - If float, then draw `max_samples * X.shape[0]` samples. Thus,\n  `max_samples` should be in the interval `(0.0, 1.0]`.\n\n..
            versionadded:: 0.22""",
            BoundaryType(
                base_type="float",
                min=0,
                max=1,
                min_inclusive=False,
                max_inclusive=True,
            ),
        ),
        (
            """When building the vocabulary ignore terms that have a document\nfrequency strictly lower than the given threshold. This value is also\n
            called cut-off in the literature.\nIf float in range of [0.0, 1.0], the parameter represents a proportion\nof documents, integer absolute counts.\n
            This parameter is ignored if vocabulary is not None.""",
            BoundaryType(
                base_type="float",
                min=0,
                max=1,
                min_inclusive=True,
                max_inclusive=True,
            ),
        ),
        (
            """float in range [0.0, 1.0] or int, default=1.0 When building the vocabulary ignore terms that have a document\n
            frequency strictly higher than the given threshold (corpus-specific\nstop words).\nIf float, the parameter represents a proportion of documents, integer\n
            absolute counts.\nThis parameter is ignored if vocabulary is not None.""",
            BoundaryType(
                base_type="float",
                min=0,
                max=1,
                min_inclusive=True,
                max_inclusive=True,
            ),
        ),
        (
            (
                "Tolerance for singular values computed by svd_solver == 'arpack'.\nMust be of range [-2, -1].\n\n.."
                " versionadded:: 0.18.0"
            ),
            BoundaryType(
                base_type="float",
                min=-2,
                max=-1,
                min_inclusive=True,
                max_inclusive=True,
            ),
        ),
        (
            "Damping factor in the range (-1, -0.5)",
            BoundaryType(
                base_type="float",
                min=-1,
                max=-0.5,
                min_inclusive=False,
                max_inclusive=False,
            ),
        ),
        (
            "'max_samples' should be in the interval (-1.0, -0.5]",
            BoundaryType(
                base_type="float",
                min=-1.0,
                max=-0.5,
                min_inclusive=False,
                max_inclusive=True,
            ),
        ),
    ],
)
def test_boundaries_from_string(string: str, expected: BoundaryType) -> None:
    ref_type = BoundaryType.from_string(string)
    assert ref_type == expected


@pytest.mark.parametrize(
    ("docstring_type", "expected"),
    [
        ("", ""),
        ('{"frobenius", "spectral"}, default="frobenius"', {"frobenius", "spectral"}),
        (
            "{'strict', 'ignore', 'replace'}, default='strict'",
            {"strict", "ignore", "replace"},
        ),
        (
            "{'linear', 'poly',             'rbf', 'sigmoid', 'cosine', 'precomputed'}, default='linear'",
            {"linear", "poly", "rbf", "sigmoid", "cosine", "precomputed"},
        ),
        # https://github.com/lars-reimann/sem21/pull/30#discussion_r771288528
        (r"{\"frobenius\", \'spectral\'}", set()),
        (r"""{"frobenius'}""", set()),
        (r"""{'spectral"}""", set()),
        (r"""{'text\", \"that'}""", {'text", "that'}),
        (r"""{'text", "that'}""", {'text", "that'}),
        (r"{'text\', \'that'}", {"text', 'that"}),
        (r"{'text', 'that'}", {"text", "that"}),
        (r"""{"text\', \'that"}""", {"text', 'that"}),
        (r"""{"text', 'that"}""", {"text', 'that"}),
        (r"""{"text\", \"that"}""", {'text", "that'}),
        (r'{"text", "that"}', {"text", "that"}),
        (r"""{\"not', 'be', 'matched'}""", {", "}),
        ("""{"gini\\", \\"entropy"}""", {'gini", "entropy'}),
        ("""{'best\\', \\'random'}""", {"best', 'random"}),
    ],
)
def test_enum_from_string(docstring_type: str, expected: set[str] | None) -> None:
    result = EnumType.from_string(docstring_type)
    if result is not None:
        assert result.values == expected


# Todo create_type Tests deactivated since create_type is not in use yet
# @pytest.mark.parametrize(
#     ("docstring_type", "expected"),
#     [
#         (
#             "",
#             {"kind": "NamedType", "name": "None", "qname": ""}
#         ),
#         (
#             "int, or None, 'manual', {'auto', 'sqrt', 'log2'}, default='auto'",
#             {
#                 "kind": "UnionType",
#                 "types": [
#                     {"kind": "EnumType", "values": {"auto", "log2", "sqrt"}},
#                     {"kind": "NamedType", "name": "int", "qname": ""},
#                     {"kind": "NamedType", "name": "None", "qname": ""},
#                     {"kind": "NamedType", "name": "'manual'", "qname": ""},
#                 ],
#             },
#         ),
#         (
#             "tuple of slice, AUTO or array of shape (12,2), default=(slice(70, 195), slice(78, 172))",
#             {
#                 "kind": "UnionType",
#                 "types": [
#                     {"kind": "NamedType", "name": "tuple of slice", "qname": ""},
#                     {"kind": "NamedType", "name": "AUTO", "qname": ""},
#                     {"kind": "NamedType", "name": "array of shape (12,2)", "qname": ""},
#                 ],
#             },
#         ),
#         ("object", {"kind": "NamedType", "name": "object", "qname": ""}),
#         (
#             "ndarray, shape (n_samples,), default=None",
#             {
#                 "kind": "UnionType",
#                 "types": [
#                     {"kind": "NamedType", "name": "ndarray", "qname": ""},
#                     {"kind": "NamedType", "name": "shape (n_samples,)", "qname": ""},
#                 ],
#             },
#         ),
#         (
#             "estor adventus or None",
#             {
#                 "kind": "UnionType",
#                 "types": [
#                     {"kind": "NamedType", "name": "estor adventus", "qname": ""},
#                     {"kind": "NamedType", "name": "None", "qname": ""},
#                 ],
#             },
#         ),
#         (
#             "int or array-like, shape (n_samples, n_classes) or (n_samples, 1)                     when binary.",
#             {
#                 "kind": "UnionType",
#                 "types": [
#                     {"kind": "NamedType", "name": "int", "qname": ""},
#                     {"kind": "NamedType", "name": "array-like", "qname": ""},
#                     {
#                         "kind": "NamedType",
#                         "name": "shape (n_samples, n_classes) or (n_samples, 1) when binary.", "qname": ""
#                     },
#                 ],
#             },
#         ),
#     ],
# )
# def test_union_from_string(docstring_type: str, expected: dict[str, Any]) -> None:
#     result = create_type(docstring_type, docstring_type)
#     if result is None:
#         assert expected == {}
#     else:
#         assert result.to_dict() == expected


# @pytest.mark.parametrize(
#     ("description", "expected"),
#     [
#         (
#             "Scale factor between inner and outer circle in the range `[0, 1)`",
#             {
#                 "base_type": "float",
#                 "kind": "BoundaryType",
#                 "max": 1.0,
#                 "max_inclusive": False,
#                 "min": 0.0,
#                 "min_inclusive": True,
#             },
#         ),
#         (
#             (
#                 "Tolerance for singular values computed by svd_solver == 'arpack'.\nMust be of range [1,"
#                 " infinity].\n\n.. versionadded:: 0.18.0"
#             ),
#             {
#                 "base_type": "float",
#                 "kind": "BoundaryType",
#                 "max": "Infinity",
#                 "max_inclusive": True,
#                 "min": 1.0,
#                 "min_inclusive": True,
#             },
#         ),
#         ("", {}),
#     ],
# )
# def test_boundary_from_string(description: str, expected: dict[str, Any]) -> None:
#     result = create_type(ParameterDocstring("", "", description))
#     if result is None:
#         assert expected == {}
#     else:
#         assert result.to_dict() == expected


# @pytest.mark.parametrize(
#     ("docstring_type", "docstring_description", "expected"),
#     [
#         (
#             "int or 'Auto', or {'today', 'yesterday'}",
#             "int in the range `[0, 10]`",
#             {
#                 "kind": "UnionType",
#                 "types": [
#                     {
#                         "base_type": "int",
#                         "kind": "BoundaryType",
#                         "max": 10.0,
#                         "max_inclusive": True,
#                         "min": 0.0,
#                         "min_inclusive": True,
#                     },
#                     {"kind": "EnumType", "values": ["today", "yesterday"]},
#                     {"kind": "NamedType", "name": "int", "qname": ""},
#                     {"kind": "NamedType", "name": "'Auto'", "qname": ""},
#                 ],
#             },
#         ),
#     ],
# )
# def test_boundary_and_union_from_string(
#     docstring_type: str,
#     docstring_description: str,
#     expected: dict[str, Any],
# ) -> None:
#     result = create_type(
#         ParameterDocstring(type=docstring_type, default_value="", description=docstring_description),
#     )
#
#     if result is None:
#         assert expected == {}
#     else:
#         assert result.to_dict() == expected
