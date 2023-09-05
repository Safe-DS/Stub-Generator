from pathlib import Path

import pytest

from safeds_stubgen.api_analyzer import get_api

_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "some_package"
_main_test_module_name = "test_module"

api_data = get_api(
    package_name=_test_package_name,
    root=Path(_test_dir / "data" / _test_package_name),
).to_dict()


def _get_specific_module_for_tests(module_name: str) -> dict:
    test_module = {}
    for module in api_data["modules"]:
        if module['name'].endswith(module_name):
            test_module = module
    assert test_module != {}
    return test_module


def _sort_list_of_dicts(list_of_dicts: list[dict], keys: list[str]) -> list[dict]:
    # Sometimes the first key is repeated, so we have to sort by several keys
    for key in keys:
        list_of_dicts = sorted(list_of_dicts, key=lambda x: (x[key] is None, x[key]))
    return list_of_dicts


# ############################## Imports ############################## #
test_module_qualified_imports = [
    {
        "qualified_name": "math",
        "alias": "mathematics"
    },
    {
        "qualified_name": "enum.Enum",
        "alias": None
    },
    {
        "qualified_name": "mypy",
        "alias": None
    },
    {
        "qualified_name": "another_path.another_module.AnotherClass",
        "alias": "k"
    },
    {
        "qualified_name": "another_path.another_module.AnotherClass",
        "alias": None
    }
]

test_module_wildcard_imports = [
    {
        "module_name": "docstring_parser"
    },
    {
        "module_name": "typing"
    }
]


@pytest.mark.parametrize(
    ("module_name", "expected_import_data", "import_type"),
    [
        (
            _main_test_module_name,
            test_module_qualified_imports,
            "qualified_imports"
        ),
        (
            _main_test_module_name,
            test_module_wildcard_imports,
            "wildcard_imports"
        ),
    ]
)
def test_imports(
    module_name: str,
    expected_import_data: list[dict],
    import_type: str
) -> None:
    # Get module import data
    module_data = _get_specific_module_for_tests(module_name)
    module_import_data: list[dict] = module_data.get(import_type, [])

    # Assert
    assert len(module_import_data) == len(expected_import_data)

    keys = list(expected_import_data[0].keys())
    module_import_data = _sort_list_of_dicts(module_import_data, keys)
    expected_import_data = _sort_list_of_dicts(expected_import_data, keys)
    assert module_import_data == expected_import_data


# ############################## Classes ############################## # Todo
test_module_SomeClass_data = {
    "id": "some_package/tests.data.some_package.test_module/SomeClass",
    "name": "SomeClass",
    "superclasses": [
        "math",
        "tests.data.some_package.test_module.s"
    ],
    "is_public": True,
    "reexported_by": [],
    "description": "",
    "constructor": {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/SomeClass/__init__-self"
        ],
        "results": []
    },
    "attributes": [
        "some_package/tests.data.some_package.test_module/SomeClass/no_type_hint_public",
        "some_package/tests.data.some_package.test_module/SomeClass/_no_type_hint_private",
        "some_package/tests.data.some_package.test_module/SomeClass/type_hint_public",
        "some_package/tests.data.some_package.test_module/SomeClass/_type_hint_private",
        "some_package/tests.data.some_package.test_module/SomeClass/object_attr",
        "some_package/tests.data.some_package.test_module/SomeClass/object_attr_2",
        "some_package/tests.data.some_package.test_module/SomeClass/tuple_attr_1",
        "some_package/tests.data.some_package.test_module/SomeClass/tuple_attr_2",
        "some_package/tests.data.some_package.test_module/SomeClass/tuple_attr_3",
        "some_package/tests.data.some_package.test_module/SomeClass/list_attr_1",
        "some_package/tests.data.some_package.test_module/SomeClass/list_attr_2",
        "some_package/tests.data.some_package.test_module/SomeClass/list_attr_3",
        "some_package/tests.data.some_package.test_module/SomeClass/list_attr_4",
        "some_package/tests.data.some_package.test_module/SomeClass/dict_attr_1",
        "some_package/tests.data.some_package.test_module/SomeClass/dict_attr_2",
        "some_package/tests.data.some_package.test_module/SomeClass/dict_attr_3",
        "some_package/tests.data.some_package.test_module/SomeClass/bool_attr",
        "some_package/tests.data.some_package.test_module/SomeClass/none_attr",
        "some_package/tests.data.some_package.test_module/SomeClass/flaot_attr",
        "some_package/tests.data.some_package.test_module/SomeClass/int_or_bool_attr",
        "some_package/tests.data.some_package.test_module/SomeClass/str_attr_with_none_value",
        "some_package/tests.data.some_package.test_module/SomeClass/mulit_attr_1",
        "some_package/tests.data.some_package.test_module/SomeClass/_mulit_attr_2_private",
        "some_package/tests.data.some_package.test_module/SomeClass/mulit_attr_3",
        "some_package/tests.data.some_package.test_module/SomeClass/override_in_init"
    ],
    "methods": [
        "some_package/tests.data.some_package.test_module/SomeClass/_some_function",
        "some_package/tests.data.some_package.test_module/SomeClass/static_function",
        "some_package/tests.data.some_package.test_module/SomeClass/test_position",
        "some_package/tests.data.some_package.test_module/SomeClass/multiple_results"
    ],
    "classes": [
        "some_package/tests.data.some_package.test_module/SomeClass/NestedClass"
    ]
}

test_module__PrivateClass_data = {
    "id": "some_package/tests.data.some_package.test_module/_PrivateClass",
    "name": "_PrivateClass",
    "superclasses": [],
    "is_public": False,
    "reexported_by": [],
    "description": "",
    "constructor": {
        "id": "some_package/tests.data.some_package.test_module/_PrivateClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/_PrivateClass/__init__-self"
        ],
        "results": []
    },
    "attributes": [
        "some_package/tests.data.some_package.test_module/_PrivateClass/public_attr_in_private_class"
    ],
    "methods": [
        "some_package/tests.data.some_package.test_module/_PrivateClass/public_func_in_private_class"
    ],
    "classes": []
}

test_module_NestedClass_data = {
    "id": "some_package/tests.data.some_package.test_module/SomeClass/NestedClass",
    "name": "NestedClass",
    "superclasses": [
        "tests.data.some_package.another_path.another_module.AnotherClass",
        "mypy"
    ],
    "is_public": True,
    "reexported_by": [],
    "description": "",
    "constructor": None,
    "attributes": [],
    "methods": [
        "some_package/tests.data.some_package.test_module/SomeClass/NestedClass/nested_class_function"
    ],
    "classes": []
}

test_module_NestedPrivateClass_data = {
    "id": "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass",
    "name": "NestedPrivateClass",
    "superclasses": [],
    "is_public": False,
    "reexported_by": [],
    "description": "",
    "constructor": None,
    "attributes": [
        "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass/nested_class_attr"
    ],
    "methods": [
        "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass/"
        "nested_private_class_function"
    ],
    "classes": []
}

# ############################## Enums ############################## # Todo
# ############################## Class Attributes ############################## #
test_module_SomeClass_attributes = [
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/no_type_hint_public",
        "name": "no_type_hint_public",
        "is_public": True,
        "is_static": True,
        "types": [],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/_no_type_hint_private",
        "name": "_no_type_hint_private",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/type_hint_public",
        "name": "type_hint_public",
        "is_public": True,
        "is_static": True,
        "types": [{
            "kind": "builtins",
            "name": "int"
        }],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/_type_hint_private",
        "name": "_type_hint_private",
        "is_public": False,
        "is_static": True,
        "types": [{
            "kind": "builtins",
            "name": "int"
        }],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/object_attr",
        "name": "object_attr",
        "is_public": True,
        "is_static": True,
        "types": [{
            "kind": "UnboundType",
            "name": "AnotherClass"
        }],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/object_attr_2",
        "name": "object_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "AnotherClass"
            },
            {
                "kind": "UnboundType",
                "name": "math"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/tuple_attr_1",
        "name": "tuple_attr_1",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "tuple"
            },
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/tuple_attr_2",
        "name": "tuple_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "tuple[str | int]"  # Todo Wie soll das dargestellt werden?
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/tuple_attr_3",
        "name": "tuple_attr_3",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "tuple[str, int]"  # Todo Wie soll das dargestellt werden?
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/list_attr_1",
        "name": "list_attr_1",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list"
            },
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/list_attr_2",
        "name": "list_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list[str | AnotherClass]"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/list_attr_3",
        "name": "list_attr_3",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list[str, AnotherClass]"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/list_attr_4",
        "name": "list_attr_4",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list[str, AnotherClass | int]"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/dict_attr_1",
        "name": "dict_attr_1",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "dict"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/dict_attr_2",
        "name": "dict_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "dict[str | int, None | AnotherClass]"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/dict_attr_3",
        "name": "dict_attr_3",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "dict[str, int]"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/bool_attr",
        "name": "bool_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "bool"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/none_attr",
        "name": "none_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "None"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/flaot_attr",
        "name": "flaot_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "float"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/int_or_bool_attr",
        "name": "int_or_bool_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "int"
            },
            {
                "kind": "builtins",
                "name": "bool"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/str_attr_with_none_value",
        "name": "str_attr_with_none_value",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "str"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/mulit_attr_1",
        "name": "x",
        "is_public": True,
        "is_static": True,
        "types": [],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/_mulit_attr_2_private",
        "name": "_mulit_attr_2_private",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/mulit_attr_3",
        "name": "x",
        "is_public": True,
        "is_static": True,
        "types": [],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/_mulit_attr_4_private",
        "name": "_mulit_attr_4_private",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/override_in_init",
        "name": "override_in_init",
        "is_public": True,
        "is_static": False,
        "types": [
            {
                "kind": "builtins",
                "name": "str"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/init_attr",
        "name": "init_attr",
        "is_public": True,
        "is_static": False,
        "types": [
            {
                "kind": "builtins",
                "name": "bool"
            }
        ],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/_init_attr_private",
        "name": "_init_attr_private",
        "is_public": False,
        "is_static": False,
        "types": [
            {
                "kind": "builtins",
                "name": "float"
            }
        ],
        "description": ""
    }
]

test_module__PrivateClass_attributes = [
    {
        "id": "some_package/tests.data.some_package.test_module/_PrivateClass/public_attr_in_private_class",
        "name": "public_attr_in_private_class",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": ""
    },
    {
        "id": "some_package/tests.data.some_package.test_module/_PrivateClass/public_init_attr_in_private_class",
        "name": "public_init_attr_in_private_class",
        "is_public": False,
        "is_static": False,
        "types": {
            "kind": "builtins",
            "name": "int"
        },
        "description": ""
    }
]

test_module_NestedPrivateClass_attributes = [
    {
        "id": "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass/nested_class_attr",
        "name": "nested_class_attr",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": ""
    }
]


@pytest.mark.parametrize(
    ("module_name", "expected_attribute_data", "class_name"),
    [
        (
            _main_test_module_name,
            test_module_SomeClass_attributes,
            "SomeClass"
        ),
        (
            _main_test_module_name,
            test_module__PrivateClass_attributes,
            "_PrivateClass"
        )
    ]
)
def test_class_attributes(
    module_name: str,
    expected_attribute_data: list[dict],
    class_name: str,
) -> None:
    # Get module data
    module_data: dict = _get_specific_module_for_tests(module_name)

    # Get all class attr ids
    class_attr_ids: list[str] = []
    for class_ in module_data["classes"]:
        if class_["name"] == class_name:
            class_attr_ids = class_["attributes"]
        else:
            assert False

    # Get attribute data
    all_module_attributes: list[dict] = module_data["attributes"]

    # Sort out the class attributes
    all_module_class_attributes = [
        attr
        for attr in all_module_attributes
        if attr["id"] in class_attr_ids
    ]

    assert len(expected_attribute_data) == len(all_module_class_attributes)

    # Check attribute data
    assert len(expected_attribute_data) == len(all_module_class_attributes)

    all_module_class_attributes = _sort_list_of_dicts(all_module_class_attributes, ["id"])
    expected_attribute_data = _sort_list_of_dicts(expected_attribute_data, ["id"])

    for attr_data, expected_data in zip(all_module_class_attributes, expected_attribute_data):
        if len(attr_data["types"]) > 1:
            attr_data["types"] = _sort_list_of_dicts(attr_data["types"], ["name"])
            expected_data["types"] = _sort_list_of_dicts(expected_data["types"], ["name"])
        assert attr_data == expected_data

    assert all_module_class_attributes == expected_attribute_data

# ############################## Enum Attributes ############################## # Todo
# ############################## Function Parameters ############################## # Todo
# ############################## Function Results ############################## # Todo
# ############################## Global Functions ############################## # Todo
# ############################## Class Functions ############################## # Todo
# ############################## Module ############################## # Todo
