from pathlib import Path

import pytest

from safeds_stubgen.api_analyzer import get_api

_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "some_package"
_main_test_module_name = "test_module"

# Setup
api_data = get_api(
    package_name=_test_package_name,
    root=Path(_test_dir / "data" / _test_package_name),
).to_dict()


# Utilites
def _get_specific_module_for_tests(module_name: str) -> dict:
    for module in api_data["modules"]:
        if module['name'].endswith(module_name):
            return module
    assert False


def _get_specific_class_for_tests(class_id: str, is_enum=False) -> dict:
    data_type = "enums" if is_enum else "classes"
    for class_ in api_data[data_type]:
        if class_["id"].endswith(class_id):
            return class_
    assert False


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
    ],
    ids=[
        "qualified_imports",
        "wildcard_imports"
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


# ############################## Classes ############################## # Todo reexported
test_module_SomeClass_data = {
    "id": "some_package/tests.data.some_package.test_module/SomeClass",
    "name": "SomeClass",
    "superclasses": [
        "math",
        "tests.data.some_package.test_module.s"
    ],
    "is_public": True,
    "reexported_by": [],
    "description": "Summary of the description\nFull description",
    "constructor": {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/__init__",
        "name": "__init__",
        "description": "Summary of the init description\nFull init description",
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
    "classes": [
        "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass"
    ]
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
    "classes": [
        "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass/NestedNestedPrivateClass"
    ]
}

test_module_NestedNestedPrivateClass_data = {
    "id": "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass/NestedNestedPrivateClass",
    "name": "NestedNestedPrivateClass",
    "superclasses": [],
    "is_public": False,
    "reexported_by": [],
    "description": "",
    "constructor": None,
    "attributes": [],
    "methods": [],
    "classes": []
}


@pytest.mark.parametrize(
    ("class_name", "expected_class_data"),
    [
        (
            "SomeClass",
            test_module_SomeClass_data
        ),
        (
            "NestedClass",
            test_module_NestedClass_data
        ),
        (
            "_PrivateClass",
            test_module__PrivateClass_data
        ),
        (
            "NestedPrivateClass",
            test_module_NestedPrivateClass_data
        ),
        (
            "NestedNestedPrivateClass",
            test_module_NestedNestedPrivateClass_data
        )
    ],
    ids=[
        "SomeClass",
        "NestedClass",
        "_PrivateClass",
        "NestedPrivateClass",
        "NestedNestedPrivateClass"
    ]
)
def test_classes(
    class_name: str,
    expected_class_data: dict
) -> None:
    # Get class data
    class_data: dict = _get_specific_class_for_tests(class_name)

    # Sort data before comparing
    for data_pack in [expected_class_data, class_data]:
        for entry_to_sort in ["superclasses", "attributes", "methods", "classes"]:
            data_pack[entry_to_sort] = sorted(data_pack[entry_to_sort])

    # Assert
    assert class_data == expected_class_data


# ############################## Class Attributes ############################## # Todo Attr Desc.
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

test_module_NestedClass_attributes = []

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

test_module_NestedNestedPrivateClass_attributes = []


@pytest.mark.parametrize(
    ("class_name", "expected_attribute_data"),
    [
        (
            "SomeClass",
            test_module_SomeClass_attributes
        ),
        (
            "NestedClass",
            test_module_NestedClass_attributes
        ),
        (
            "_PrivateClass",
            test_module__PrivateClass_attributes
        ),
        (
            "NestedPrivateClass",
            test_module_NestedPrivateClass_attributes
        ),
        (
            "NestedNestedPrivateClass",
            test_module_NestedNestedPrivateClass_attributes
        )
    ],
    ids=[
        "SomeClass",
        "NestedClass",
        "_PrivateClass",
        "NestedPrivateClass",
        "NestedNestedPrivateClass"
    ]
)
def test_class_attributes(
    class_name: str,
    expected_attribute_data: list[dict]
) -> None:
    # Get class data
    class_data: dict = _get_specific_class_for_tests(class_name)

    # Get all class attr ids
    class_attr_ids: list[str] = class_data["attributes"]
    assert len(class_attr_ids) == len(expected_attribute_data)

    # Sort out the class attribute data we need
    full_attribute_data = [
        attr
        for attr in api_data["attributes"]
        if attr["id"] in class_attr_ids
    ]

    assert len(full_attribute_data) == len(expected_attribute_data)

    # Sort data before comparing
    for data_set in [full_attribute_data, expected_attribute_data]:
        for attr_data in data_set:
            attr_data["types"] = _sort_list_of_dicts(attr_data["types"], ["name"])

    full_attribute_data = _sort_list_of_dicts(full_attribute_data, ["id"])
    expected_attribute_data = _sort_list_of_dicts(expected_attribute_data, ["id"])

    # Assert
    assert full_attribute_data == expected_attribute_data


# ############################## Enums ############################## #
test_module_TestEnum = {
    "id": "some_package/tests.data.some_package.test_module/TestEnum",
    "name": "TestEnum",
    "description": "Enum Docstring\nFull Docstring Description",
    "instances": [
        "some_package/tests.data.some_package.test_module/TestEnum/ONE",
        "some_package/tests.data.some_package.test_module/TestEnum/TWO",
        "some_package/tests.data.some_package.test_module/TestEnum/THREE",
        "some_package/tests.data.some_package.test_module/TestEnum/FOUR",
        "some_package/tests.data.some_package.test_module/TestEnum/FIVE",
        "some_package/tests.data.some_package.test_module/TestEnum/SIX",
        "some_package/tests.data.some_package.test_module/TestEnum/SEVEN",
        "some_package/tests.data.some_package.test_module/TestEnum/EIGHT",
        "some_package/tests.data.some_package.test_module/TestEnum/NINE",
        "some_package/tests.data.some_package.test_module/TestEnum/TEN"
    ],
}

test_module_EmptyEnum = {
    "id": "some_package/tests.data.some_package.test_module/EmptyEnum",
    "name": "EmptyEnum",
    "description": "Nothing's here",
    "instances": [],
}

test_module_AnotherTestEnum = {
    "id": "some_package/tests.data.some_package.test_module/AnotherTestEnum",
    "name": "AnotherTestEnum",
    "description": "Nothing's here",
    "instances": [
        "some_package/tests.data.some_package.test_module/AnotherTestEnum/ELEVEN",
    ],
}


@pytest.mark.parametrize(
    ("enum_name", "expected_enum_data"),
    [
        (
            "TestEnum",
            test_module_TestEnum
        ),
        (
            "EmptyEnum",
            test_module_EmptyEnum
        ),
        (
            "AnotherTestEnum",
            test_module_AnotherTestEnum
        )
    ],
    ids=[
        "TestEnum",
        "EmptyEnum",
        "AnotherTestEnum"
    ]
)
def test_enums(
    enum_name: str,
    expected_enum_data: dict
) -> None:
    # Get enum data
    enum_data = _get_specific_class_for_tests(enum_name, is_enum=True)

    # Sort data before comparing
    enum_data["instances"] = sorted(enum_data["instances"])
    expected_enum_data["instances"] = sorted(expected_enum_data["instances"])

    # Assert
    assert enum_data == expected_enum_data


# ############################## Enum Instances ############################## # Todo values
test_module_TestEnum_instances = [
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/ONE",
        "name": "ONE",
        "value": {
            "value": "first"
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/TWO",
        "name": "TWO",
        "value": {
            "value": (2, 2)
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/THREE",
        "name": "THREE",
        "value": {
            "value": 3
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/FOUR",
        "name": "FOUR",
        "value": {
            "value": "forth and fifth"
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/FIVE",
        "name": "FIVE",
        "value": {
            "value": "forth and fifth"
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/SIX",
        "name": "SIX",
        "value": {
            "value": "sixth"
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/SEVEN",
        "name": "SEVEN",
        "value": {
            "value": 7
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/EIGHT",
        "name": "EIGHT",
        "value": {
            "value": "8"
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/NINE",
        "name": "NINE",
        "value": {
            "value": "9"
        }
    },
    {
        "id": "some_package/tests.data.some_package.test_module/TestEnum/TEN",
        "name": "TEN",
        "value": {
            "value": "k()"
        }
    },
]

test_module_EmptyEnum_instances = []

test_module_AnotherTestEnum_instances = [
    {
        "id": "some_package/tests.data.some_package.test_module/AnotherTestEnum/ELEVEN",
        "name": "ELEVEN",
        "value": {
            "value": 11
        }
    }
]


@pytest.mark.parametrize(
    ("enum_name", "expected_enum_instance_data"),
    [
        (
            "TestEnum",
            test_module_TestEnum_instances
        ),
        (
            "EmptyEnum",
            test_module_EmptyEnum_instances
        ),
        (
            "AnotherTestEnum",
            test_module_AnotherTestEnum_instances
        )
    ],
    ids=[
        "TestEnum",
        "EmptyEnum",
        "AnotherTestEnum"
    ]
)
def test_enum_instances(
    enum_name: str,
    expected_enum_instance_data: list[dict]
) -> None:
    # Get enum data
    enum_data = _get_specific_class_for_tests(enum_name, is_enum=True)
    enum_instance_ids = enum_data["instances"]

    all_enum_instances = api_data["enum_instances"]

    # Sort out the enum instances we need
    enum_instances = [
        enum_instance
        for enum_instance in all_enum_instances
        if enum_instance["id"] in enum_instance_ids
    ]
    assert len(enum_instances) == len(expected_enum_instance_data)

    # Sort data before comparing
    enum_instances = _sort_list_of_dicts(enum_instances, ["id"])
    expected_enum_instance_data = _sort_list_of_dicts(expected_enum_instance_data, ["id"])

    # Assert
    assert enum_instances == expected_enum_instance_data


# ############################## Global Functions ############################## # Todo reexported
test_module_global_functions = [
    {
        "id": "some_package/tests.data.some_package.test_module/global_func",
        "name": "global_func",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/global_func/param_1",
            "some_package/tests.data.some_package.test_module/global_func/param_2"
        ],
        "results": [
            "some_package/tests.data.some_package.test_module/global_func/result_23_11_14"
        ]
    },
    {
        "id": "some_package/tests.data.some_package.test_module/_private_global_func",
        "name": "_private_global_func",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [],
        "results": [
            "some_package/tests.data.some_package.test_module/_private_global_func/result_27_11_25"
        ]
    }
]


@pytest.mark.parametrize(
    ("module_name", "expected_function_data"),
    [
        (
            _main_test_module_name,
            test_module_global_functions
        )
    ]
)
def test_global_functions(
    module_name: str,
    expected_function_data: list[dict]
) -> None:
    # Get function data
    module_data = _get_specific_module_for_tests(module_name)
    global_function_ids = module_data["functions"]

    all_functions: list[dict] = api_data["functions"]

    # Sort out the functions we need
    function_data: list[dict] = [
        function
        for function in all_functions
        if function["id"] in global_function_ids
    ]
    assert len(function_data) == len(expected_function_data)

    # Sort data before comparing
    for data_set in [function_data, expected_function_data]:
        for function in data_set:
            for data_type in ["parameters", "results"]:
                function[data_type] = sorted(function[data_type])

    function_data = _sort_list_of_dicts(function_data, ["id"])
    expected_function_data = _sort_list_of_dicts(expected_function_data, ["id"])

    # Assert
    assert function_data == expected_function_data


# ############################## Class Methods ############################## # Todo reexported
test_module_SomeClass_methods = [
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/SomeClass/__init__/self"
        ],
        "results": []
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/_some_function",
        "name": "_some_function",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/SomeClass/_some_function/self",
            "some_package/tests.data.some_package.test_module/SomeClass/_some_function/param_1",
            "some_package/tests.data.some_package.test_module/SomeClass/_some_function/param_2"
        ],
        "results": [
            "some_package/tests.data.some_package.test_module/SomeClass/_some_function/result_82_15_25"
        ]
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/multiple_results",
        "name": "multiple_results",
        "description": "",
        "is_public": True,
        "is_static": True,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/param_1"
        ],
        "results": [
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_121_8_14",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_106_19_32",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_118_19_33",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_98_19_21",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_112_19_31",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_108_19_35",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_104_19_24",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_100_19_24",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_114_19_41",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_116_19_28",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_120_19_23",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_120_25_41",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_120_43_45",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_102_19_23",
            "some_package/tests.data.some_package.test_module/SomeClass/multiple_results/result_110_19_34"
        ]
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/static_function",
        "name": "static_function",
        "description": "",
        "is_public": True,
        "is_static": True,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/SomeClass/static_function/param_1",
            "some_package/tests.data.some_package.test_module/SomeClass/static_function/param_2"
        ],
        "results": [
            "some_package/tests.data.some_package.test_module/SomeClass/static_function/result_87_15_22",
            "some_package/tests.data.some_package.test_module/SomeClass/static_function/result_87_24_31"
        ]
    },
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/test_position",
        "name": "test_position",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/SomeClass/test_position/self",
            "some_package/tests.data.some_package.test_module/SomeClass/test_position/param1",
            "some_package/tests.data.some_package.test_module/SomeClass/test_position/param2",
            "some_package/tests.data.some_package.test_module/SomeClass/test_position/param3",
            "some_package/tests.data.some_package.test_module/SomeClass/test_position/param4",
            "some_package/tests.data.some_package.test_module/SomeClass/test_position/param5"
        ],
        "results": [
            "some_package/tests.data.some_package.test_module/SomeClass/test_position/result_92_15_56"
        ]
    }
]

test_module_NestedClass_methods = [
    {
        "id": "some_package/tests.data.some_package.test_module/SomeClass/NestedClass/nested_class_function",
        "name": "nested_class_function",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/SomeClass/NestedClass/nested_class_function/self"
        ],
        "results": []
    }
]

test_module__PrivateClass_methods = [
    {
        "id": "some_package/tests.data.some_package.test_module/_PrivateClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/_PrivateClass/__init__/self"
        ],
        "results": []
    },
    {
        "id": "some_package/tests.data.some_package.test_module/_PrivateClass/public_func_in_private_class",
        "name": "public_func_in_private_class",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "some_package/tests.data.some_package.test_module/_PrivateClass/public_func_in_private_class/self"
        ],
        "results": []
    },

]

test_module_NestedPrivateClass_methods = [
    {
        "id": "some_package/tests.data.some_package.test_module/_PrivateClass/NestedPrivateClass/"
              "static_nested_private_class_function",
        "name": "static_nested_private_class_function",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [],
        "results": []
    },

]

test_module_NestedNestedPrivateClass_methods = []


@pytest.mark.parametrize(
    ("class_name", "expected_method_data"),
    [
        (
            "SomeClass",
            test_module_SomeClass_methods
        ),
        (
            "NestedClass",
            test_module_NestedClass_methods
        ),
        (
            "_PrivateClass",
            test_module__PrivateClass_methods
        ),
        (
            "NestedPrivateClass",
            test_module_NestedPrivateClass_methods
        ),
        (
            "NestedNestedPrivateClass",
            test_module_NestedNestedPrivateClass_methods
        )
    ],
    ids=[
        "Class Methods: SomeClass",
        "Class Methods: NestedClass",
        "Class Methods: _PrivateClass",
        "Class Methods: NestedPrivateClass",
        "Class Methods: NestedNestedPrivateClass"
    ]
)
def test_class_methods(
    class_name: str,
    expected_method_data: list[dict]
) -> None:
    # Get function data
    class_data: dict = _get_specific_class_for_tests(class_name)
    class_method_ids: list[str] = class_data["methods"]

    all_functions: list[dict] = api_data["functions"]

    # Sort out the functions we need
    method_data: list[dict] = [
        method
        for method in all_functions
        if method["id"] in class_method_ids
    ]
    assert len(method_data) == len(expected_method_data)

    # Sort data before comparing
    for data_set in [method_data, expected_method_data]:
        for method in data_set:
            for data_type in ["parameters", "results"]:
                method[data_type] = sorted(method[data_type])

    method_data = _sort_list_of_dicts(method_data, ["id"])
    expected_method_data = _sort_list_of_dicts(expected_method_data, ["id"])

    # Assert
    assert method_data == expected_method_data


# ############################## Function Parameters ############################## # Todo
# ############################## Function Results ############################## # Todo
# ############################## Module ############################## # Todo
