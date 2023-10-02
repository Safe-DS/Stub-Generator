from __future__ import annotations

from pathlib import Path

import pytest
from docstring_parser import DocstringStyle
from safeds_stubgen.api_analyzer import get_api

_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "test_package"
_main_test_module_name = "test_module"

# API data setup
api_data_paintext = get_api(
    package_name=_test_package_name,
    root=Path(_test_dir / "data" / _test_package_name),
    is_test_run=True,
).to_dict()

api_data_epydoc = get_api(
    package_name=_test_package_name,
    root=Path(_test_dir / "data" / _test_package_name),
    docstring_style=DocstringStyle.EPYDOC,
    is_test_run=True,
).to_dict()

api_data_numpy = get_api(
    package_name=_test_package_name,
    root=Path(_test_dir / "data" / _test_package_name),
    docstring_style=DocstringStyle.NUMPYDOC,
    is_test_run=True,
).to_dict()

api_data_rest = get_api(
    package_name=_test_package_name,
    root=Path(_test_dir / "data" / _test_package_name),
    docstring_style=DocstringStyle.REST,
    is_test_run=True,
).to_dict()

api_data_google = get_api(
    package_name=_test_package_name,
    root=Path(_test_dir / "data" / _test_package_name),
    docstring_style=DocstringStyle.GOOGLE,
    is_test_run=True,
).to_dict()


# Utilites
def _get_specific_module_data(module_name: str, docstring_style: str = "plaintext") -> dict:
    api_data = get_api_data(docstring_style)

    for module in api_data["modules"]:
        if module["name"] == module_name:
            return module
    raise AssertionError


def _get_specific_class_data(class_name: str, docstring_style: str = "plaintext", is_enum=False) -> dict:
    data_type = "enums" if is_enum else "classes"
    api_data = get_api_data(docstring_style)
    for class_ in api_data[data_type]:
        if class_["id"].endswith(f"/{class_name}"):
            return class_
    raise AssertionError


def get_api_data(docstring_style: str):
    return {
        "plaintext": api_data_paintext,
        "epydoc": api_data_epydoc,
        "numpy": api_data_numpy,
        "rest": api_data_rest,
        "google": api_data_google,
    }[docstring_style]


def _get_specific_function_data(
    function_name: str,
    parent_class_name: str = "",
    test_module_name: str = _main_test_module_name,
    docstring_style: str = "plaintext",
) -> dict:
    api_data = get_api_data(docstring_style)

    if parent_class_name == "":
        parent_class_name = test_module_name

    for function in api_data["functions"]:
        if function["id"].endswith(f"{parent_class_name}/{function_name}"):
            return function
    raise AssertionError


def _sort_list_of_dicts(list_of_dicts: list[dict], keys: list[str]) -> list[dict]:
    # Sometimes we have a list[dict[str, list | ...] format and have to sort the innermost list before being able to
    #  assert equality

    # Sometimes the first key is repeated, so we have to sort by several keys
    for key in keys:
        list_of_dicts = sorted(list_of_dicts, key=lambda x: (x[key] is None, x[key]))
    return list_of_dicts


def _assert_list_of_dicts(list_1: list[dict], list_2: list[dict]) -> None:
    assert len(list_1) == len(list_2)
    if len(list_1) == 0:
        return

    keys_1 = list(list_1[0].keys())
    keys_2 = list(list_2[0].keys())

    assert sorted(keys_1) == sorted(keys_2)

    for key in keys_1:
        list_1 = sorted(list_1, key=lambda x: (x[key] is None, x[key]))

    for key in keys_1:
        list_2 = sorted(list_2, key=lambda x: (x[key] is None, x[key]))

    assert list_1 == list_2


# ############################## Module ############################## #
module_test_module = [{
    "id": "test_package/test_module",
    "name": "test_module",
    "docstring": "Docstring of the some_class.py module",
    "qualified_imports": [
        {
            "qualified_name": "math",
            "alias": "mathematics",
        },
        {
            "qualified_name": "mypy",
            "alias": None,
        },
        {
            "qualified_name": "another_path.another_module.AnotherClass",
            "alias": None,
        },
        {
            "qualified_name": "another_path.another_module.AnotherClass",
            "alias": "_AcImportAlias",
        },
    ],
    "wildcard_imports": [
        {
            "module_name": "typing",
        },
        {
            "module_name": "docstring_parser",
        },
    ],
    "classes": [
        "test_package/test_module/SomeClass",
        "test_package/test_module/_PrivateClass",
    ],
    "functions": [
        "test_package/test_module/global_func",
        "test_package/test_module/_private_global_func",
    ],
    "enums": [],
}]

module_another_module = [{
    "id": "test_package/another_module",
    "name": "another_module",
    "docstring": "Another Module Docstring.\n\nFull Docstring Description\n",
    "qualified_imports": [],
    "wildcard_imports": [],
    "classes": [
        "test_package/another_module/AnotherClass",
    ],
    "functions": [],
    "enums": [],
}]

module_test_enums = [{
    "id": "test_package/test_enums",
    "name": "test_enums",
    "docstring": "",
    "qualified_imports": [
        {
            "qualified_name": "enum.Enum",
            "alias": None,
        },
        {
            "qualified_name": "enum.Enum",
            "alias": "_Enum",
        },
        {
            "qualified_name": "another_path.another_module.AnotherClass",
            "alias": "_AcImportAlias",
        },
    ],
    "wildcard_imports": [],
    "classes": [],
    "functions": [],
    "enums": [
        "test_package/test_enums/TestEnum",
        "test_package/test_enums/_ReexportedEmptyEnum",
        "test_package/test_enums/AnotherTestEnum",
    ],
}]

module___init__ = [{
    "id": "test_package/__init__",
    "name": "__init__",
    "docstring": "",
    "qualified_imports": [
        {
            "qualified_name": "_reexport_module_1.ReexportClass",
            "alias": None,
        },
        {
            "qualified_name": "_reexport_module_1",
            "alias": "reex_1",
        },
        {
            "qualified_name": "_reexport_module_2.reexported_function_2",
            "alias": None,
        },
        {
            "qualified_name": "test_enums._ReexportedEmptyEnum",
            "alias": None,
        },
    ],
    "wildcard_imports": [
        {
            "module_name": "_reexport_module_3",
        },
    ],
    "classes": [],
    "functions": [],
    "enums": [],
}]

module_test_docstrings = [{
    "id": "test_package/test_docstrings",
    "name": "test_docstrings",
    "docstring": "Test module for docstring tests.\n\nA module for testing the various docstring types.\n",
    "qualified_imports": [],
    "wildcard_imports": [],
    "classes": [
        "test_package/test_docstrings/EpydocDocstringClass",
        "test_package/test_docstrings/RestDocstringClass",
        "test_package/test_docstrings/NumpyDocstringClass",
        "test_package/test_docstrings/GoogleDocstringClass",
    ],
    "functions": [],
    "enums": [],
}]


@pytest.mark.parametrize(
    ("module_name", "expected_module_data"),
    [
        (
            _main_test_module_name,
            module_test_module,
        ),
        (
            "another_module",
            module_another_module,
        ),
        (
            "test_enums",
            module_test_enums,
        ),
        (
            "__init__",
            module___init__,
        ),
        (
            "test_docstrings",
            module_test_docstrings,
        ),
    ],
    ids=[
        f"Modules: {_main_test_module_name}",
        "Modules: another_module",
        "Modules: test_enums",
        "Modules: __init__",
        "Modules: test_docstrings",
    ],
)
def test_modules(
    module_name: str,
    expected_module_data: dict,
) -> None:
    # Get class data
    module_data: dict = _get_specific_module_data(module_name)

    # Sort data before comparing
    for data_pack in [expected_module_data, module_data]:
        for entry_to_sort in ["enums", "functions", "classes", "wildcard_imports", "qualified_imports"]:
            data_pack[entry_to_sort] = sorted(data_pack[entry_to_sort])

    # Assert
    assert module_data == expected_module_data


# ############################## Imports ############################## #
imports_test_module_qualified_imports = [
    {
        "qualified_name": "math",
        "alias": "mathematics",
    },
    {
        "qualified_name": "mypy",
        "alias": None,
    },
    {
        "qualified_name": "another_path.another_module.AnotherClass",
        "alias": "_AcImportAlias",
    },
    {
        "qualified_name": "another_path.another_module.AnotherClass",
        "alias": None,
    },
]

imports_test_module_wildcard_imports = [
    {
        "module_name": "docstring_parser",
    },
    {
        "module_name": "typing",
    },
]

imports_test_enums_qualified_imports = [
    {
        "qualified_name": "enum.Enum",
        "alias": None,
    },
    {
        "qualified_name": "enum.Enum",
        "alias": "_Enum",
    },
    {
        "qualified_name": "another_path.another_module.AnotherClass",
        "alias": "_AcImportAlias",
    },
]

imports_test_enums_wildcard_imports = []

imports___init___qualified_imports = [
    {
        "qualified_name": "_reexport_module_1.ReexportClass",
        "alias": None,
    },
    {
        "qualified_name": "_reexport_module_1",
        "alias": "reex_1",
    },
    {
        "qualified_name": "_reexport_module_2.reexported_function_2",
        "alias": None,
    },
    {
        "qualified_name": "_reexport_module_4.FourthReexportClass",
        "alias": None,
    },
    {
        "qualified_name": "test_enums._ReexportedEmptyEnum",
        "alias": None,
    },
]

imports___init___wildcard_imports = [{
    "module_name": "_reexport_module_3",
}]


@pytest.mark.parametrize(
    ("module_name", "expected_import_data", "import_type"),
    [
        (
            _main_test_module_name,
            imports_test_module_qualified_imports,
            "qualified_imports",
        ),
        (
            _main_test_module_name,
            imports_test_module_wildcard_imports,
            "wildcard_imports",
        ),
        (
            "test_enums",
            imports_test_enums_qualified_imports,
            "qualified_imports",
        ),
        (
            "test_enums",
            imports_test_enums_wildcard_imports,
            "wildcard_imports",
        ),
        (
            "__init__",
            imports___init___qualified_imports,
            "qualified_imports",
        ),
        (
            "__init__",
            imports___init___wildcard_imports,
            "wildcard_imports",
        ),
    ],
    ids=[
        f"{_main_test_module_name} - qualified_imports",
        f"{_main_test_module_name} - wildcard_imports",
        "test_enums - qualified_imports",
        "test_enums - wildcard_imports",
        "__init__ - qualified_imports",
        "__init__ - wildcard_imports",
    ],
)
def test_imports(
    module_name: str,
    expected_import_data: list[dict],
    import_type: str,
) -> None:
    # Get module import data
    module_data = _get_specific_module_data(module_name)
    module_import_data: list[dict] = module_data.get(import_type, [])

    # Assert
    _assert_list_of_dicts(module_import_data, expected_import_data)


# ############################## Classes ############################## #
# Todo Description for docstring __init__ methods -> Docstrings nötig? -> Ja
class_test_module_someclass = {
    "id": "test_package/test_module/SomeClass",
    "name": "SomeClass",
    "superclasses": [
        "math",
        "tests.data.test_package.test_module.s",
    ],
    "is_public": True,
    "reexported_by": [],
    "description": "Summary of the description.\n\nFull description",
    "constructor": {
        "id": "test_package/test_module/SomeClass/__init__",
        "name": "__init__",
        "description": "Summary of the init description.\n\nFull init description",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/__init__-self",
        ],
        "results": [],
    },
    "attributes": [
        "test_package/test_module/SomeClass/no_type_hint_public",
        "test_package/test_module/SomeClass/_no_type_hint_private",
        "test_package/test_module/SomeClass/type_hint_public",
        "test_package/test_module/SomeClass/_type_hint_private",
        "test_package/test_module/SomeClass/object_attr",
        "test_package/test_module/SomeClass/object_attr_2",
        "test_package/test_module/SomeClass/tuple_attr_1",
        "test_package/test_module/SomeClass/tuple_attr_2",
        "test_package/test_module/SomeClass/tuple_attr_3",
        "test_package/test_module/SomeClass/list_attr_1",
        "test_package/test_module/SomeClass/list_attr_2",
        "test_package/test_module/SomeClass/list_attr_3",
        "test_package/test_module/SomeClass/list_attr_4",
        "test_package/test_module/SomeClass/dict_attr_1",
        "test_package/test_module/SomeClass/dict_attr_2",
        "test_package/test_module/SomeClass/dict_attr_3",
        "test_package/test_module/SomeClass/bool_attr",
        "test_package/test_module/SomeClass/none_attr",
        "test_package/test_module/SomeClass/flaot_attr",
        "test_package/test_module/SomeClass/int_or_bool_attr",
        "test_package/test_module/SomeClass/str_attr_with_none_value",
        "test_package/test_module/SomeClass/mulit_attr_1",
        "test_package/test_module/SomeClass/_mulit_attr_2_private",
        "test_package/test_module/SomeClass/mulit_attr_3",
        "test_package/test_module/SomeClass/override_in_init",
    ],
    "methods": [
        "test_package/test_module/SomeClass/_some_function",
        "test_package/test_module/SomeClass/static_function",
        "test_package/test_module/SomeClass/test_position",
        "test_package/test_module/SomeClass/test_params",
        "test_package/test_module/SomeClass/multiple_results",
        "test_package/test_module/SomeClass/no_return_1",
        "test_package/test_module/SomeClass/no_return_2",
    ],
    "classes": [
        "test_package/test_module/SomeClass/NestedClass",
    ],
}

class_test_module_nestedclass = {
    "id": "test_package/test_module/SomeClass/NestedClass",
    "name": "NestedClass",
    "superclasses": [
        "tests.data.test_package.another_path.another_module.AnotherClass",
        "mypy",
    ],
    "is_public": True,
    "reexported_by": [],
    "description": "",
    "constructor": None,
    "attributes": [],
    "methods": [
        "test_package/test_module/SomeClass/NestedClass/nested_class_function",
    ],
    "classes": [],
}

class_test_module__privateclass = {
    "id": "test_package/test_module/_PrivateClass",
    "name": "_PrivateClass",
    "superclasses": [],
    "is_public": False,
    "reexported_by": [],
    "description": "",
    "constructor": {
        "id": "test_package/test_module/_PrivateClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/_PrivateClass/__init__-self",
        ],
        "results": [],
    },
    "attributes": [
        "test_package/test_module/_PrivateClass/public_attr_in_private_class",
    ],
    "methods": [
        "test_package/test_module/_PrivateClass/public_func_in_private_class",
    ],
    "classes": [
        "test_package/test_module/_PrivateClass/NestedPrivateClass",
    ],
}

class_test_module_nestedprivateclass = {
    "id": "test_package/test_module/_PrivateClass/NestedPrivateClass",
    "name": "NestedPrivateClass",
    "superclasses": [],
    "is_public": False,
    "reexported_by": [],
    "description": "",
    "constructor": None,
    "attributes": [
        "test_package/test_module/_PrivateClass/NestedPrivateClass/nested_class_attr",
    ],
    "methods": [
        "test_package/test_module/_PrivateClass/NestedPrivateClass/"
        "nested_private_class_function",
    ],
    "classes": [
        "test_package/test_module/_PrivateClass/NestedPrivateClass/NestedNestedPrivateClass",
    ],
}

class_test_module_nestednestedprivateclass = {
    "id": "test_package/test_module/_PrivateClass/NestedPrivateClass/NestedNestedPrivateClass",
    "name": "NestedNestedPrivateClass",
    "superclasses": [],
    "is_public": False,
    "reexported_by": [],
    "description": "",
    "constructor": None,
    "attributes": [],
    "methods": [],
    "classes": [],
}

class_test_docstrings_epydocdocstringclass = {
    "id": "test_package/test_docstrings/EpydocDocstringClass",
    "name": "EpydocDocstringClass",
    "superclasses": [],
    "is_public": True,
    "description": "A class with a variety of different methods for calculations."
                   " (Epydoc)",
    "constructor": {
        "id": "test_package/test_docstrings/EpydocDocstringClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": True,
        "is_static": False,
        "results": [],
        "reexported_by": [],
        "parameters": [
            "test_package/test_docstrings/EpydocDocstringClass/__init__/self",
            "test_package/test_docstrings/EpydocDocstringClass/__init__/param_1",
        ],
    },
    "reexported_by": [],
    "attributes": [
        "test_package/test_docstrings/EpydocDocstringClass/attr_1",
    ],
    "methods": [
        "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func",
    ],
    "classes": [],
}

class_test_docstrings_restdocstringclass = {
    "id": "test_package/test_docstrings/RestDocstringClass",
    "name": "RestDocstringClass",
    "superclasses": [],
    "is_public": True,
    "description": "A class with a variety of different methods for calculations. (ReST)",
    "constructor": {
        "id": "test_package/test_docstrings/RestDocstringClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": True,
        "is_static": False,
        "results": [],
        "reexported_by": [],
        "parameters": [
            "test_package/test_docstrings/RestDocstringClass/__init__/self",
            "test_package/test_docstrings/RestDocstringClass/__init__/param_1",
        ],
    },
    "reexported_by": [],
    "attributes": [
        "test_package/test_docstrings/RestDocstringClass/attr_1",
    ],
    "methods": [
        "test_package/test_docstrings/RestDocstringClass/rest_docstring_func",
    ],
    "classes": [],
}

class_test_docstrings_numpydocstringclass = {
    "id": "test_package/test_docstrings/NumpyDocstringClass",
    "name": "NumpyDocstringClass",
    "superclasses": [],
    "is_public": True,
    "description": "A class with a variety of different methods for calculations. (Numpy)",
    "constructor": {
        "id": "test_package/test_docstrings/NumpyDocstringClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": True,
        "is_static": False,
        "results": [],
        "reexported_by": [],
        "parameters": [
            "test_package/test_docstrings/NumpyDocstringClass/__init__/self",
            "test_package/test_docstrings/NumpyDocstringClass/__init__/param_1",
        ],
    },
    "reexported_by": [],
    "attributes": [
        "test_package/test_docstrings/NumpyDocstringClass/attr_1",
    ],
    "methods": [
        "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func",
    ],
    "classes": [],
}

class_test_docstrings_googledocstringclass = {
    "id": "test_package/test_docstrings/GoogleDocstringClass",
    "name": "GoogleDocstringClass",
    "superclasses": [],
    "is_public": True,
    "description": "A class with a variety of different methods for calculations. (Google Style)",
    "constructor": {
        "id": "test_package/test_docstrings/GoogleDocstringClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": True,
        "is_static": False,
        "results": [],
        "reexported_by": [],
        "parameters": [
            "test_package/test_docstrings/GoogleDocstringClass/__init__/self",
            "test_package/test_docstrings/GoogleDocstringClass/__init__/param_1",
        ],
    },
    "reexported_by": [],
    "attributes": [
        "test_package/test_docstrings/GoogleDocstringClass/attr_1",
    ],
    "methods": [
        "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func",
    ],
    "classes": [],
}

class__reexport_module_1_reexportclass = {
    "id": "test_package/_reexport_module_1/ReexportClass",
    "name": "ReexportClass",
    "superclasses": [],
    "is_public": True,
    "description": "",
    "constructor": None,
    "reexported_by": [
        "test_package/__init__",
    ],
    "attributes": [],
    "methods": [
        "test_package/_reexport_module_1/ReexportClass/_private_class_method_of_reexported_class",
    ],
    "classes": [],
}

class__reexport_module_2_anotherreexportclass = {
    "id": "test_package/_reexport_module_2/AnotherReexportClass",
    "name": "AnotherReexportClass",
    "superclasses": [],
    "is_public": True,
    "description": "",
    "constructor": None,
    "reexported_by": [],
    "attributes": [],
    "methods": [],
    "classes": [],
}

class__reexport_module_3_thirdreexportclass = {
    "id": "test_package/_reexport_module_3/_ThirdReexportClass",
    "name": "_ThirdReexportClass",
    "superclasses": [],
    "is_public": False,
    "description": "",
    "constructor": None,
    "reexported_by": [
        "test_package/__init__",
    ],
    "attributes": [],
    "methods": [],
    "classes": [],
}

class__reexport_module_4_fourthreexportclass = {
    "id": "test_package/_reexport_module_4/FourthReexportClass",
    "name": "FourthReexportClass",
    "superclasses": [],
    "is_public": True,
    "description": "",
    "constructor": None,
    "reexported_by": [
        "test_package/__init__",
    ],
    "attributes": [],
    "methods": [],
    "classes": [],
}


@pytest.mark.parametrize(
    ("class_name", "expected_class_data", "docstring_style"),
    [
        (
            "SomeClass",
            class_test_module_someclass,
            "plaintext",
        ),
        (
            "NestedClass",
            class_test_module_nestedclass,
            "plaintext",
        ),
        (
            "_PrivateClass",
            class_test_module__privateclass,
            "plaintext",
        ),
        (
            "NestedPrivateClass",
            class_test_module_nestedprivateclass,
            "plaintext",
        ),
        (
            "NestedNestedPrivateClass",
            class_test_module_nestednestedprivateclass,
            "plaintext",
        ),
        (
            "EpydocDocstringClass",
            class_test_docstrings_epydocdocstringclass,
            "epydoc",
        ),
        (
            "RestDocstringClass",
            class_test_docstrings_restdocstringclass,
            "rest",
        ),
        (
            "NumpyDocstringClass",
            class_test_docstrings_numpydocstringclass,
            "numpy",
        ),
        (
            "GoogleDocstringClass",
            class_test_docstrings_googledocstringclass,
            "google",
        ),
        (
            "ReexportClass",
            class__reexport_module_1_reexportclass,
            "plaintext",
        ),
        (
            "AnotherReexportClass",
            class__reexport_module_2_anotherreexportclass,
            "plaintext",
        ),
        (
            "ThirdReexportClass",
            class__reexport_module_3_thirdreexportclass,
            "plaintext",
        ),
        (
            "FourthReexportClass",
            class__reexport_module_4_fourthreexportclass,
            "plaintext",
        ),
    ],
    ids=[
        "Classes: SomeClass",
        "Classes: NestedClass",
        "Classes: _PrivateClass",
        "Classes: NestedPrivateClass",
        "Classes: NestedNestedPrivateClass",
        "Classes: EpydocDocstringClass",
        "Classes: RestDocstringClass",
        "Classes: NumpyDocstringClass",
        "Classes: GoogleDocstringClass",
        "Classes: ReexportClass",
        "Classes: AnotherReexportClass",
        "Classes: ThirdReexportClass",
        "Classes: FourthReexportClass",
    ],
)
def test_classes(
    class_name: str,
    expected_class_data: dict,
    docstring_style: str,
) -> None:
    # Get class data
    class_data: dict = _get_specific_class_data(class_name, docstring_style)

    # Sort data before comparing
    for data_pack in [expected_class_data, class_data]:
        for entry_to_sort in ["superclasses", "attributes", "methods", "classes"]:
            data_pack[entry_to_sort] = sorted(data_pack[entry_to_sort])

    # Assert
    assert class_data == expected_class_data


# ############################## Class Attributes ############################## #
class_attributes_test_module_someclass = [
    {
        "id": "test_package/test_module/SomeClass/no_type_hint_public",
        "name": "no_type_hint_public",
        "is_public": True,
        "is_static": True,
        "types": [],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/_no_type_hint_private",
        "name": "_no_type_hint_private",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/type_hint_public",
        "name": "type_hint_public",
        "is_public": True,
        "is_static": True,
        "types": [{
            "kind": "builtins",
            "name": "int",
        }],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/_type_hint_private",
        "name": "_type_hint_private",
        "is_public": False,
        "is_static": True,
        "types": [{
            "kind": "builtins",
            "name": "int",
        }],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/object_attr",
        "name": "object_attr",
        "is_public": True,
        "is_static": True,
        "types": [{
            "kind": "UnboundType",
            "name": "AnotherClass",
        }],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/"
              "object_attr_2",
        "name": "object_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "AnotherClass",
            },
            {
                "kind": "UnboundType",
                "name": "math",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/tuple_attr_1",
        "name": "tuple_attr_1",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "tuple",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/tuple_attr_2",
        "name": "tuple_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "tuple[str | int]",  # Todo Wie soll das dargestellt werden?
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/tuple_attr_3",
        "name": "tuple_attr_3",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "tuple[str, int]",  # Todo Wie soll das dargestellt werden?
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/list_attr_1",
        "name": "list_attr_1",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/list_attr_2",
        "name": "list_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list[str | AnotherClass]",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/list_attr_3",
        "name": "list_attr_3",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list[str, AnotherClass]",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/list_attr_4",
        "name": "list_attr_4",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "list[str, AnotherClass | int]",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/dict_attr_1",
        "name": "dict_attr_1",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "dict",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/dict_attr_2",
        "name": "dict_attr_2",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "dict[str | int, None | AnotherClass]",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/dict_attr_3",
        "name": "dict_attr_3",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "UnboundType",
                "name": "dict[str, int]",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/bool_attr",
        "name": "bool_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "bool",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/none_attr",
        "name": "none_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "None",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/flaot_attr",
        "name": "flaot_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "float",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/int_or_bool_attr",
        "name": "int_or_bool_attr",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "int",
            },
            {
                "kind": "builtins",
                "name": "bool",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/str_attr_with_none_value",
        "name": "str_attr_with_none_value",
        "is_public": True,
        "is_static": True,
        "types": [
            {
                "kind": "builtins",
                "name": "str",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/mulit_attr_1",
        "name": "x",
        "is_public": True,
        "is_static": True,
        "types": [],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/_mulit_attr_2_private",
        "name": "_mulit_attr_2_private",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/mulit_attr_3",
        "name": "x",
        "is_public": True,
        "is_static": True,
        "types": [],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/_mulit_attr_4_private",
        "name": "_mulit_attr_4_private",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/override_in_init",
        "name": "override_in_init",
        "is_public": True,
        "is_static": False,
        "types": [
            {
                "kind": "builtins",
                "name": "str",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/init_attr",
        "name": "init_attr",
        "is_public": True,
        "is_static": False,
        "types": [
            {
                "kind": "builtins",
                "name": "bool",
            },
        ],
        "description": "",
    },
    {
        "id": "test_package/test_module/SomeClass/_init_attr_private",
        "name": "_init_attr_private",
        "is_public": False,
        "is_static": False,
        "types": [
            {
                "kind": "builtins",
                "name": "float",
            },
        ],
        "description": "",
    },
]

class_attributes_test_module_nestedclass = []

class_attributes_test_module__privateclass = [
    {
        "id": "test_package/test_module/_PrivateClass/public_attr_in_private_class",
        "name": "public_attr_in_private_class",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": "",
    },
    {
        "id": "test_package/test_module/_PrivateClass/"
              "public_init_attr_in_private_class",
        "name": "public_init_attr_in_private_class",
        "is_public": False,
        "is_static": False,
        "types": {
            "kind": "builtins",
            "name": "int",
        },
        "description": "",
    },
]

class_attributes_test_module_nestedprivateclass = [
    {
        "id": "test_package/test_module/_PrivateClass/NestedPrivateClass/nested_class_attr",
        "name": "nested_class_attr",
        "is_public": False,
        "is_static": True,
        "types": [],
        "description": "",
    },
]

class_attributes_test_module_nestednestedprivateclass = []

class_attributes_test_docstrings_epydocdocstringclass = [{
    "id": "test_package/test_docstrings/EpydocDocstringClass/attr_1",
    "name": "attr_1",
    "is_public": True,
    "is_static": True,
    "type": {
        "kind": "NamedType",
        "name": "str",
    },
    "description": "Attribute of the calculator. (Epydoc)",
}]

class_attributes_test_docstrings_restdocstringclass = [{
    "id": "test_package/test_docstrings/RestDocstringClass/attr_1",
    "name": "attr_1",
    "is_public": True,
    "is_static": True,
    "type": {
        "kind": "NamedType",
        "name": "str",
    },
    "description": "Attribute of the calculator. (ReST)",
}]

class_attributes_test_docstrings_numpydocstringclass = [{
    "id": "test_package/test_docstrings/NumpyDocstringClass/attr_1",
    "name": "attr_1",
    "is_public": True,
    "is_static": True,
    "type": {
        "kind": "NamedType",
        "name": "str",
    },
    "description": "Attribute of the calculator. (Numpy)",
}]

class_attributes_test_docstrings_googledocstringclass = [{
    "id": "test_package/test_docstrings/GoogleDocstringClass/attr_1",
    "name": "attr_1",
    "is_public": True,
    "is_static": True,
    "type": {
        "kind": "NamedType",
        "name": "str",
    },
    "description": "Attribute of the calculator. (Google Style)",
}]


@pytest.mark.parametrize(
    ("class_name", "expected_attribute_data", "docstring_style"),
    [
        (
            "SomeClass",
            class_attributes_test_module_someclass,
            "plaintext",
        ),
        (
            "NestedClass",
            class_attributes_test_module_nestedclass,
            "plaintext",
        ),
        (
            "_PrivateClass",
            class_attributes_test_module__privateclass,
            "plaintext",
        ),
        (
            "NestedPrivateClass",
            class_attributes_test_module_nestedprivateclass,
            "plaintext",
        ),
        (
            "NestedNestedPrivateClass",
            class_attributes_test_module_nestednestedprivateclass,
            "plaintext",
        ),
        (
            "EpydocDocstringClass",
            class_attributes_test_docstrings_epydocdocstringclass,
            "epydoc",
        ),
        (
            "RestDocstringClass",
            class_attributes_test_docstrings_restdocstringclass,
            "rest",
        ),
        (
            "NumpyDocstringClass",
            class_attributes_test_docstrings_numpydocstringclass,
            "numpy",
        ),
        (
            "GoogleDocstringClass",
            class_attributes_test_docstrings_googledocstringclass,
            "google",
        ),
    ],
    ids=[
        "Class Attributes: SomeClass",
        "Class Attributes: NestedClass",
        "Class Attributes: _PrivateClass",
        "Class Attributes: NestedPrivateClass",
        "Class Attributes: NestedNestedPrivateClass",
        "Class Attributes: EpydocDocstringClass",
        "Class Attributes: RestDocstringClass",
        "Class Attributes: NumpyDocstringClass",
        "Class Attributes: GoogleDocstringClass",
    ],
)
def test_class_attributes(
    class_name: str,
    expected_attribute_data: list[dict],
    docstring_style: str,
) -> None:
    # Get class data
    class_data: dict = _get_specific_class_data(class_name)

    # Get all class attr ids
    class_attr_ids: list[str] = class_data["attributes"]
    assert len(class_attr_ids) == len(expected_attribute_data)

    # Sort out the class attribute data we need
    api_data = get_api_data(docstring_style)
    full_attribute_data = [
        attr
        for attr in api_data["attributes"]
        if attr["id"] in class_attr_ids
    ]

    # Sort data before comparing
    for data_set in [full_attribute_data, expected_attribute_data]:
        for attr_data in data_set:
            attr_data["types"] = _sort_list_of_dicts(attr_data["types"], ["name"])

    _assert_list_of_dicts(full_attribute_data, expected_attribute_data)


# ############################## Enums ############################## #
enums_test_enums_testenum = {
    "id": "test_package/test_enums/TestEnum",
    "name": "TestEnum",
    "description": "Enum Docstring.\n    Full Docstring Description\n     ",
    "instances": [
        "test_package/test_module/TestEnum/ONE",
        "test_package/test_module/TestEnum/TWO",
        "test_package/test_module/TestEnum/THREE",
        "test_package/test_module/TestEnum/FOUR",
        "test_package/test_module/TestEnum/FIVE",
        "test_package/test_module/TestEnum/SIX",
        "test_package/test_module/TestEnum/SEVEN",
        "test_package/test_module/TestEnum/EIGHT",
        "test_package/test_module/TestEnum/NINE",
        "test_package/test_module/TestEnum/TEN",
    ],
}

enums_test_enums_emptyenum = {
    "id": "test_package/test_enums/EmptyEnum",
    "name": "EmptyEnum",
    "description": "Nothing's here.",
    "instances": [],
}

enums_test_enums_anothertestenum = {
    "id": "test_package/test_enums/AnotherTestEnum",
    "name": "AnotherTestEnum",
    "description": "",
    "instances": [
        "test_package/test_module/AnotherTestEnum/ELEVEN",
    ],
}


@pytest.mark.parametrize(
    ("enum_name", "expected_enum_data"),
    [
        (
            "TestEnum",
            enums_test_enums_testenum,
        ),
        (
            "EmptyEnum",
            enums_test_enums_emptyenum,
        ),
        (
            "AnotherTestEnum",
            enums_test_enums_anothertestenum,
        ),
    ],
    ids=[
        "Enums: TestEnum",
        "Enums: EmptyEnum",
        "Enums: AnotherTestEnum",
    ],
)
def test_enums(
    enum_name: str,
    expected_enum_data: dict,
) -> None:
    # Get enum data
    enum_data = _get_specific_class_data(enum_name, is_enum=True)

    # Sort data before comparing
    enum_data["instances"] = sorted(enum_data["instances"])
    expected_enum_data["instances"] = sorted(expected_enum_data["instances"])

    # Assert
    assert enum_data == expected_enum_data


# ############################## Enum Instances ############################## #
enum_instances_test_enums_testenum = [
    {
        "id": "test_package/test_module/TestEnum/ONE",
        "name": "ONE",
    },
    {
        "id": "test_package/test_module/TestEnum/TWO",
        "name": "TWO",
    },
    {
        "id": "test_package/test_module/TestEnum/THREE",
        "name": "THREE",
    },
    {
        "id": "test_package/test_module/TestEnum/FOUR",
        "name": "FOUR",
    },
    {
        "id": "test_package/test_module/TestEnum/FIVE",
        "name": "FIVE",
    },
    {
        "id": "test_package/test_module/TestEnum/SIX",
        "name": "SIX",
    },
    {
        "id": "test_package/test_module/TestEnum/SEVEN",
        "name": "SEVEN",
    },
    {
        "id": "test_package/test_module/TestEnum/EIGHT",
        "name": "EIGHT",
    },
    {
        "id": "test_package/test_module/TestEnum/NINE",
        "name": "NINE",
    },
    {
        "id": "test_package/test_module/TestEnum/TEN",
        "name": "TEN",
    },
]

enum_instances_test_enums_emptyenum = []

enum_instances_test_enums_anothertestenum = [
    {
        "id": "test_package/test_module/AnotherTestEnum/ELEVEN",
        "name": "ELEVEN",
    },
]


@pytest.mark.parametrize(
    ("enum_name", "expected_enum_instance_data"),
    [
        (
            "TestEnum",
            enum_instances_test_enums_testenum,
        ),
        (
            "EmptyEnum",
            enum_instances_test_enums_emptyenum,
        ),
        (
            "AnotherTestEnum",
            enum_instances_test_enums_anothertestenum,
        ),
    ],
    ids=[
        "Enum Instances: TestEnum",
        "Enum Instances: EmptyEnum",
        "Enum Instances: AnotherTestEnum",
    ],
)
def test_enum_instances(
    enum_name: str,
    expected_enum_instance_data: list[dict],
) -> None:
    # Get enum data
    enum_data = _get_specific_class_data(enum_name, is_enum=True)
    enum_instance_ids = enum_data["instances"]

    all_enum_instances = api_data_paintext["enum_instances"]

    # Sort out the enum instances we need
    enum_instances = [
        enum_instance
        for enum_instance in all_enum_instances
        if enum_instance["id"] in enum_instance_ids
    ]

    # Assert
    _assert_list_of_dicts(enum_instances, expected_enum_instance_data)


# ############################## Global Functions ############################## #
global_functions_test_module = [
    {
        "id": "test_package/test_module/global_func",
        "name": "global_func",
        "description": "Docstring 1.\n\nDocstring 2.",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/global_func/param_1",
            "test_package/test_module/global_func/param_2",
        ],
        "results": [
            "test_package/test_module/global_func/result_1",
        ],
    },
    {
        "id": "test_package/test_module/_private_global_func",
        "name": "_private_global_func",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [],
        "results": [
            "test_package/test_module/_private_global_func/result_1",
        ],
    },
]

global_functions__reexport_module_1 = [{
    "id": "test_package/_reexport_module_1/reexported_function",
    "name": "reexported_function",
    "description": "",
    "is_public": True,
    "is_static": False,
    "results": [],
    "reexported_by": [
        "test_package/__init__",
    ],
    "parameters": [],
}]

global_functions__reexport_module_2 = [{
    "id": "test_package/_reexport_module_2/reexported_function_2",
    "name": "reexported_function_2",
    "description": "",
    "is_public": True,
    "is_static": False,
    "results": [],
    "reexported_by": [
        "test_package/__init__",
    ],
    "parameters": [],
}]

global_functions__reexport_module_3 = [{
    "id": "test_package/_reexport_module_3/reexported_function_3",
    "name": "reexported_function_3",
    "description": "",
    "is_public": True,
    "is_static": False,
    "results": [],
    "reexported_by": [
        "test_package/__init__",
    ],
    "parameters": [],
}]

global_functions__reexport_module_4 = [{
    "id": "test_package/_reexport_module_4/_unreexported_function",
    "name": "_unreexported_function",
    "description": "",
    "is_public": False,
    "is_static": False,
    "results": [],
    "reexported_by": [],
    "parameters": [],
}]


@pytest.mark.parametrize(
    ("module_name", "expected_function_data"),
    [
        (
            _main_test_module_name,
            global_functions_test_module,
        ),
        (
            "_reexport_module_1",
            global_functions__reexport_module_1,
        ),
        (
            "_reexport_module_2",
            global_functions__reexport_module_2,
        ),
        (
            "_reexport_module_3",
            global_functions__reexport_module_3,
        ),
        (
            "_reexport_module_4",
            global_functions__reexport_module_4,
        ),
    ],
    ids=[
        "Global Functions: TestEnum",
        "Global Functions: _reexport_module_1",
        "Global Functions: _reexport_module_2",
        "Global Functions: _reexport_module_3",
        "Global Functions: _reexport_module_4",
    ],
)
def test_global_functions(
    module_name: str,
    expected_function_data: list[dict],
) -> None:
    # Get function data
    module_data = _get_specific_module_data(module_name)
    global_function_ids = module_data["functions"]

    all_functions: list[dict] = api_data_paintext["functions"]

    # Sort out the functions we need
    function_data: list[dict] = [
        function
        for function in all_functions
        if function["id"] in global_function_ids
    ]

    # Sort data before comparing
    for data_set in [function_data, expected_function_data]:
        for function in data_set:
            for data_type in ["parameters", "results"]:
                function[data_type] = sorted(function[data_type])

    _assert_list_of_dicts(function_data, expected_function_data)


# ############################## Class Methods ############################## #
class_methods_test_module_someclass = [
    {
        "id": "test_package/test_module/SomeClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/__init__/self",
            "test_package/test_module/SomeClass/__init__/init_param_1",
        ],
        "results": [],
    },
    {
        "id": "test_package/test_module/SomeClass/_some_function",
        "name": "_some_function",
        "description": "Function Docstring.\n\nparam_1: bool.",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/_some_function/self",
            "test_package/test_module/SomeClass/_some_function/param_1",
            "test_package/test_module/SomeClass/_some_function/param_2",
        ],
        "results": [
            "test_package/test_module/SomeClass/_some_function/result_1",
        ],
    },
    {
        "id": "test_package/test_module/SomeClass/multiple_results",
        "name": "multiple_results",
        "description": "",
        "is_public": True,
        "is_static": True,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/multiple_results/param_1",
        ],
        "results": [
            "test_package/test_module/SomeClass/multiple_results/result_1",
        ],
    },
    {
        "id": "test_package/test_module/SomeClass/static_function",
        "name": "static_function",
        "description": "",
        "is_public": True,
        "is_static": True,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/static_function/param_1",
            "test_package/test_module/SomeClass/static_function/param_2",
        ],
        "results": [
            "test_package/test_module/SomeClass/static_function/result_1",
            "test_package/test_module/SomeClass/static_function/result_2",
        ],
    },
    {
        "id": "test_package/test_module/SomeClass/test_position",
        "name": "test_position",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/test_position/self",
            "test_package/test_module/SomeClass/test_position/param1",
            "test_package/test_module/SomeClass/test_position/param2",
            "test_package/test_module/SomeClass/test_position/param3",
            "test_package/test_module/SomeClass/test_position/param4",
            "test_package/test_module/SomeClass/test_position/param5",
        ],
        "results": [
            "test_package/test_module/SomeClass/test_position/result_1",
        ],
    },
    {
        "id": "test_package/test_module/SomeClass/test_params",
        "name": "test_params",
        "description": "",
        "is_public": True,
        "is_static": True,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/test_params/args",
            "test_package/test_module/SomeClass/test_params/kwargs",
        ],
        "results": [],
    },
    {
        "id": "test_package/test_module/SomeClass/no_return_1",
        "name": "no_return_1",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/no_return_1/self",
        ],
        "results": [],
    },
    {
        "id": "test_package/test_module/SomeClass/no_return_2",
        "name": "no_return_2",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/no_return_2/self",
        ],
        "results": [],
    },
]

class_methods_test_module_nestedclass = [
    {
        "id": "test_package/test_module/SomeClass/NestedClass/nested_class_function",
        "name": "nested_class_function",
        "description": "",
        "is_public": True,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/SomeClass/NestedClass/nested_class_function/self",
            "test_package/test_module/SomeClass/NestedClass/nested_class_function/param_1",
        ],
        "results": [
            "test_package/test_module/SomeClass/_some_function/result_1",
        ],
    },
]

class_methods_test_module__privateclass = [
    {
        "id": "test_package/test_module/_PrivateClass/__init__",
        "name": "__init__",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/_PrivateClass/__init__/self",
        ],
        "results": [],
    },
    {
        "id": "test_package/test_module/_PrivateClass/public_func_in_private_class",
        "name": "public_func_in_private_class",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [
            "test_package/test_module/_PrivateClass/public_func_in_private_class/self",
        ],
        "results": [],
    },

]

class_methods_test_module_nestedprivateclass = [
    {
        "id": "test_package/test_module/_PrivateClass/NestedPrivateClass/"
              "static_nested_private_class_function",
        "name": "static_nested_private_class_function",
        "description": "",
        "is_public": False,
        "is_static": False,
        "reexported_by": [],
        "parameters": [],
        "results": [],
    },

]

class_methods_test_module_nestednestedprivateclass = []

class_methods__reexport_module_1_reexportclass = [{
    "id": "test_package/_reexport_module_1/ReexportClass/_private_class_method_of_reexported_class",
    "name": "_private_class_method_of_reexported_class",
    "description": "",
    "is_public": False,
    "is_static": True,
    "results": [],
    "reexported_by": [
        "test_package/__init__",
    ],
    "parameters": [],
}]

class_methods_test_docstrings_epydocdocstringclass = [{
    "id": "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func",
    "name": "epydoc_docstring_func",
    "description": "This function checks if the sum of x and y is less than the value 10 and "
                   "returns True if it is. (Epydoc)",
    "is_public": True,
    "is_static": False,
    "results": [
        "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/result_1",
    ],
    "reexported_by": [],
    "parameters": [
        "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/self",
        "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/x",
        "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/y",
    ],
}]

class_methods_test_docstrings_restdocstringclass = [{
    "id": "test_package/test_docstrings/RestDocstringClass/rest_docstring_func",
    "name": "rest_docstring_func",
    "description": "This function checks if the sum of x and y is less than the value 10 "
                   "and returns True if it is. (ReST)",
    "is_public": True,
    "is_static": False,
    "results": [
        "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/result_1",
    ],
    "reexported_by": [],
    "parameters": [
        "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/self",
        "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/x",
        "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/y",
    ],
}]

class_methods_test_docstrings_numpydocstringclass = [{
    "id": "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func",
    "name": "numpy_docstring_func",
    "description": "This function checks if the sum of `x` and `y` is less than the value "
                   "10 and returns True if it is. (Numpy)",
    "is_public": True,
    "is_static": False,
    "results": [
        "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/result_1",
    ],
    "reexported_by": [],
    "parameters": [
        "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/self",
        "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/x",
        "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/y",
    ],
}]

class_methods_test_docstrings_googledocstringclass = [{
    "id": "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func",
    "name": "google_docstring_func",
    "description": "This function checks if the sum of x and y is less than the value 10 "
                   "and returns True if it is. (Google Style)",
    "is_public": True,
    "is_static": False,
    "results": [
        "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/result_1",
    ],
    "reexported_by": [],
    "parameters": [
        "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/self",
        "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/x",
        "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/y",
    ],
}]


@pytest.mark.parametrize(
    ("class_name", "expected_method_data", "docstring_style"),
    [
        (
            "SomeClass",
            class_methods_test_module_someclass,
            "plaintext",
        ),
        (
            "NestedClass",
            class_methods_test_module_nestedclass,
            "plaintext",
        ),
        (
            "_PrivateClass",
            class_methods_test_module__privateclass,
            "plaintext",
        ),
        (
            "NestedPrivateClass",
            class_methods_test_module_nestedprivateclass,
            "plaintext",
        ),
        (
            "NestedNestedPrivateClass",
            class_methods_test_module_nestednestedprivateclass,
            "plaintext",
        ),
        (
            "ReexportClass",
            class_methods__reexport_module_1_reexportclass,
            "plaintext",
        ),
        (
            "EpydocDocstringClass",
            class_methods_test_docstrings_epydocdocstringclass,
            "epydoc",
        ),
        (
            "RestDocstringClass",
            class_methods_test_docstrings_restdocstringclass,
            "rest",
        ),
        (
            "NumpyDocstringClass",
            class_methods_test_docstrings_numpydocstringclass,
            "numpy",
        ),
        (
            "GoogleDocstringClass",
            class_methods_test_docstrings_googledocstringclass,
            "google",
        ),
    ],
    ids=[
        "Class Methods: SomeClass",
        "Class Methods: NestedClass",
        "Class Methods: _PrivateClass",
        "Class Methods: NestedPrivateClass",
        "Class Methods: NestedNestedPrivateClass",
        "Class Methods: ReexportClass",
        "Class Methods: EpydocDocstringClass",
        "Class Methods: RestDocstringClass",
        "Class Methods: NumpyDocstringClass",
        "Class Methods: GoogleDocstringClass",
    ],
)
def test_class_methods(
    class_name: str,
    expected_method_data: list[dict],
    docstring_style: str,
) -> None:
    # Get function data
    class_data: dict = _get_specific_class_data(class_name)
    class_method_ids: list[str] = class_data["methods"]

    api_data = get_api_data(docstring_style)
    all_functions: list[dict] = api_data["functions"]

    # Sort out the functions we need
    method_data: list[dict] = [
        method
        for method in all_functions
        if method["id"] in class_method_ids
    ]

    # Sort data before comparing
    for data_set in [method_data, expected_method_data]:
        for method in data_set:
            for data_type in ["parameters", "results"]:
                method[data_type] = sorted(method[data_type])

    # Assert
    _assert_list_of_dicts(method_data, expected_method_data)


# ############################## Function Parameters ############################## # Todo Docstrings
func_params_test_module_global_func = [
    {
        "id": "test_package/test_module/global_func/param_1",
        "name": "param_1",
        "is_optional": True,
        "default_value": "first param",
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "str",
        },
    },
    {
        "id": "test_package/test_module/global_func/param_2",
        "name": "param_2",
        "is_optional": True,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "UnionType",
            "types": [
                {
                    "kind": "NamedType",
                    "name": "AnotherClass",
                },
                {
                    "kind": "NamedType",
                    "name": "None",
                },
            ],
        },
    },
]

func_params_test_module_someclass___init__ = [
    {
        "id": "test_package/test_module/SomeClass/__init__/init_param_1",
        "name": "init_param_1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "Any",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/__init__/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "SomeClass",
        },
    },
]

func_params_test_module_someclass_static_function = [
    {
        "id": "test_package/test_module/SomeClass/static_function/param_1",
        "name": "param_1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "bool",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/static_function/param_2",
        "name": "param_2",
        "is_optional": True,
        "default_value": 123456,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "UnionType",
            "types": [
                {
                    "kind": "NamedType",
                    "name": "int",
                },
                {
                    "kind": "NamedType",
                    "name": "bool",
                },
            ],
        },
    },
]

func_params_test_module_someclass_test_position = [
    {
        "id": "test_package/test_module/SomeClass/test_position/param1",
        "name": "param1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_ONLY",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "Any",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/test_position/param2",
        "name": "param2",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "bool",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/test_position/param3",
        "name": "param3",
        "is_optional": True,
        "default_value": 1,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "Any",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/test_position/param4",
        "name": "param4",
        "is_optional": True,
        "default_value": None,
        "assigned_by": "NAME_ONLY",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "Any",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/test_position/param5",
        "name": "param5",
        "is_optional": True,
        "default_value": 1,
        "assigned_by": "NAME_ONLY",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/test_position/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "SomeClass",
        },
    },
]

# Todo Check if types are correct
func_params_test_module_someclass_test_params = [
    {
        "id": "test_package/test_module/SomeClass/test_params/args",
        "name": "args",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITIONAL_VARARG",
        "docstring": None,
        "type": {
            "kind": "TupleType",
            "types": [],
        },
    },
    {
        "id": "test_package/test_module/SomeClass/test_params/kwargs",
        "name": "kwargs",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "NAMED_VARARG",
        "docstring": None,
        "type": {
            "kind": "DictType",
            "key_type": {
                "kind": "NamedType",
                "name": "Any",
            },
            "value_type": {
                "kind": "NamedType",
                "name": "str",
            },
        },
    },
]

func_params_test_module_someclass_nestedclass_nested_class_function = [
    {
        "id": "test_package/test_module/SomeClass/NestedClass/nested_class_function/param_1",
        "name": "param_1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
    {
        "id": "test_package/test_module/SomeClass/NestedClass/nested_class_function/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": None,
        "type": {
            "kind": "NamedType",
            "name": "NestedClass",
        },
    },
]

func_params_test_docstrings_epydocdocstringclass_epydoc_docstring_func = [
    {
        "id": "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "EpydocDocstringClass",
        },
    },
    {
        "id": "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/x",
        "name": "x",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
    {
        "id": "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/y",
        "name": "y",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
]

func_params_test_docstrings_epydocdocstringclass___init__ = [
    {
        "id": "test_package/test_docstrings/EpydocDocstringClass/__init__/param_1",
        "name": "param_1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "str",
        },
    },
    {
        "id": "test_package/test_docstrings/EpydocDocstringClass/__init__/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "EpydocDocstringClass",
        },
    },
]

func_params_test_docstrings_restdocstringclass_rest_docstring_func = [
    {
        "id": "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "RestDocstringClass",
        },
    },
    {
        "id": "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/x",
        "name": "x",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
    {
        "id": "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/y",
        "name": "y",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
]

func_params_test_docstrings_restdocstringclass___init__ = [
    {
        "id": "test_package/test_docstrings/RestDocstringClass/__init__/param_1",
        "name": "param_1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "str",
        },
    },
    {
        "id": "test_package/test_docstrings/RestDocstringClass/__init__/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "RestDocstringClass",
        },
    },
]

func_params_test_docstrings_numpydocstringclass_numpy_docstring_func = [
    {
        "id": "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "NumpyDocstringClass",
        },
    },
    {
        "id": "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/x",
        "name": "x",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
    {
        "id": "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/y",
        "name": "y",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
]

func_params_test_docstrings_numpydocstringclass___init__ = [
    {
        "id": "test_package/test_docstrings/NumpyDocstringClass/__init__/param_1",
        "name": "param_1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "str",
        },
    },
    {
        "id": "test_package/test_docstrings/NumpyDocstringClass/__init__/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "NumpyDocstringClass",
        },
    },
]

func_params_test_docstrings_googledocstringclass_google_docstring_func = [
    {
        "id": "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "GoogleDocstringClass",
        },
    },
    {
        "id": "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/x",
        "name": "x",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
    {
        "id": "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/y",
        "name": "y",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
    },
]

func_params_test_docstrings_googledocstringclass___init__ = [
    {
        "id": "test_package/test_docstrings/GoogleDocstringClass/__init__/param_1",
        "name": "param_1",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "POSITION_OR_NAME",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "str",
        },
    },
    {
        "id": "test_package/test_docstrings/GoogleDocstringClass/__init__/self",
        "name": "self",
        "is_optional": False,
        "default_value": None,
        "assigned_by": "IMPLICIT",
        "docstring": {
            "type": "",
            "default_value": "",
            "description": "",
        },
        "type": {
            "kind": "NamedType",
            "name": "GoogleDocstringClass",
        },
    },
]


@pytest.mark.parametrize(
    ("function_name", "parent_class_name", "expected_parameter_data", "docstring_style"),
    [
        (
            "global_func",
            "",
            func_params_test_module_global_func,
            "plaintext",
        ),
        (
            "__init__",
            "SomeClass",
            func_params_test_module_someclass___init__,
            "plaintext",
        ),
        (
            "static_function",
            "SomeClass",
            func_params_test_module_someclass_static_function,
            "plaintext",
        ),
        (
            "test_position",
            "SomeClass",
            func_params_test_module_someclass_test_position,
            "plaintext",
        ),
        (
            "test_params",
            "SomeClass",
            func_params_test_module_someclass_test_params,
            "plaintext",
        ),
        (
            "nested_class_function",
            "NestedClass",
            func_params_test_module_someclass_nestedclass_nested_class_function,
            "plaintext",
        ),
        (
            "epydoc_docstring_func",
            "EpydocDocstringClass",
            func_params_test_docstrings_epydocdocstringclass_epydoc_docstring_func,
            "epydoc",
        ),
        (
            "rest_docstring_func",
            "RestDocstringClass",
            func_params_test_docstrings_restdocstringclass_rest_docstring_func,
            "rest",
        ),
        (
            "numpy_docstring_func",
            "NumpyDocstringClass",
            func_params_test_docstrings_numpydocstringclass_numpy_docstring_func,
            "numpy",
        ),
        (
            "google_docstring_func",
            "GoogleDocstringClass",
            func_params_test_docstrings_googledocstringclass_google_docstring_func,
            "google",
        ),
    ],
    ids=[
        "Function Parameters: global_func",
        "Function Parameters: __init__",
        "Function Parameters: static_function",
        "Function Parameters: test_position",
        "Function Parameters: test_params",
        "Function Parameters: nested_class_function",
        "Function Parameters: epydoc_docstring_func",
        "Function Parameters: rest_docstring_func",
        "Function Parameters: numpy_docstring_func",
        "Function Parameters: google_docstring_func",
    ],
)
def test_function_parameters(
    function_name: str,
    parent_class_name: str,
    expected_parameter_data: list[dict],
    docstring_style: str,
) -> None:
    # Get function data
    function_data: dict = _get_specific_function_data(function_name, parent_class_name)
    function_parameter_ids: list[str] = function_data["parameters"]

    api_data = get_api_data(docstring_style)
    all_parameters: list[dict] = api_data["parameters"]

    # Sort out the parameters we need
    parameter_data: list[dict] = [
        parameter
        for parameter in all_parameters
        if parameter["id"] in function_parameter_ids
    ]

    # Sort data before comparing
    for data_set in [parameter_data, expected_parameter_data]:
        for parameter in data_set:
            parameter["types"] = _sort_list_of_dicts(parameter["types"], ["name"])

    # Assert
    _assert_list_of_dicts(parameter_data, expected_parameter_data)


# ############################## Function Results ############################## # Todo Docstring
results_test_module__private_global_func = [
    {
        "id": "test_package/test_module/global_func/result_1",
        "name": "result_1",
        "type": {
            "kind": "NamedType",
            "name": "AnotherClass",
        },
        "docstring": None,
    },
]

results_test_module_someclass_multiple_results = [
    {
        "id": "test_package/test_module/SomeClass/multiple_results/result_1",
        "name": "result_1",
        "type": {
            "kind": "UnionType",
            "types": [
                {
                    "kind": "NamedType",
                    "name": "Any",
                },
                {
                    "kind": "TupleType",
                    "types": [
                        {
                            "kind": "NamedType",
                            "name": "int",
                        },
                        {
                            "kind": "NamedType",
                            "name": "str",
                        },
                    ],
                },
            ],
        },
        "docstring": None,
    },
]

results_test_module_someclass_static_function = [
    {
        "id": "test_package/test_module/SomeClass/static_function/result_1",
        "name": "result_1",
        "type":
            {
                "kind": "NamedType",
                "name": "bool",
            },
        "docstring": None,
    },
    {
        "id": "test_package/test_module/SomeClass/static_function/result_2",
        "name": "result_2",
        "type": {
            "kind": "NamedType",
            "name": "int",
        },
        "docstring": None,
    },
]

results_test_module_someclass_test_position = [
    {
        "id": "test_package/test_module/SomeClass/test_position/result_1",
        "name": "result_1",
        "type": {
            "kind": "NamedType",
            "name": "Any",
        },
        "docstring": None,
    },
]

results_test_module_someclass_nestedclass_nested_class_function = [
    {
        "id": "test_package/test_module/SomeClass/NestedClass/nested_class_function/result_1",
        "name": "result_1",
        "type": {
            "kind": "SetType",
            "types": [
                {
                    "kind": "UnionType",
                    "types": [
                        {
                            "kind": "NamedType",
                            "name": "bool",
                        },
                        {
                            "kind": "NamedType",
                            "name": "None",
                        },
                    ],
                },
            ],
        },
        "docstring": None,
    },
]

results_test_docstring_epydocdocstringclass_epydoc_docstring_func = [
    {
        "id": "test_package/test_docstrings/EpydocDocstringClass/epydoc_docstring_func/result_1",
        "name": "result_1",
        "type": {
            "kind": "NamedType",
            "name": "bool",
        },
        "docstring": {
            "type": "",
            "description": "",
        },
    },
]

results_test_docstring_restdocstringclass_rest_docstring_func = [
    {
        "id": "test_package/test_docstrings/RestDocstringClass/rest_docstring_func/result_1",
        "name": "result_1",
        "type": {
            "kind": "NamedType",
            "name": "bool",
        },
        "docstring": {
            "type": "",
            "description": "",
        },
    },
]

results_test_docstring_numpydocstringclass_numpy_docstring_func = [
    {
        "id": "test_package/test_docstrings/NumpyDocstringClass/numpy_docstring_func/result_1",
        "name": "result_1",
        "type": {
            "kind": "NamedType",
            "name": "bool",
        },
        "docstring": {
            "type": "",
            "description": "",
        },
    },
]

results_test_docstring_googledocstringclass_google_docstring_func = [
    {
        "id": "test_package/test_docstrings/GoogleDocstringClass/google_docstring_func/result_1",
        "name": "result_1",
        "type": {
            "kind": "NamedType",
            "name": "bool",
        },
        "docstring": {
            "type": "",
            "description": "",
        },
    },
]


@pytest.mark.parametrize(
    ("function_name", "parent_class_name", "expected_result_data", "docstring_style"),
    [
        (
            "_private_global_func",
            "",
            results_test_module__private_global_func,
            "plaintext",
        ),
        (
            "multiple_results",
            "SomeClass",
            results_test_module_someclass_multiple_results,
            "plaintext",
        ),
        (
            "static_function",
            "SomeClass",
            results_test_module_someclass_static_function,
            "plaintext",
        ),
        (
            "test_position",
            "SomeClass",
            results_test_module_someclass_test_position,
            "plaintext",
        ),
        (
            "nested_class_function",
            "NestedClass",
            results_test_module_someclass_nestedclass_nested_class_function,
            "plaintext",
        ),
        (
            "epydoc_docstring_func",
            "EpydocDocstringClass",
            results_test_docstring_epydocdocstringclass_epydoc_docstring_func,
            "epydoc",
        ),
        (
            "rest_docstring_func",
            "RestDocstringClass",
            results_test_docstring_restdocstringclass_rest_docstring_func,
            "rest",
        ),
        (
            "numpy_docstring_func",
            "NumpyDocstringClass",
            results_test_docstring_numpydocstringclass_numpy_docstring_func,
            "numpy",
        ),
        (
            "google_docstring_func",
            "GoogleDocstringClass",
            results_test_docstring_googledocstringclass_google_docstring_func,
            "google",
        ),
    ],
    ids=[
        "Function Results: _private_global_func",
        "Function Results: multiple_results",
        "Function Results: static_function",
        "Function Results: test_position",
        "Function Results: nested_class_function",
        "Function Results: epydoc_docstring_func",
        "Function Results: rest_docstring_func",
        "Function Results: numpy_docstring_func",
        "Function Results: google_docstring_func",
    ],
)
def test_function_results(
    function_name: str,
    parent_class_name: str,
    expected_result_data: list[dict],
    docstring_style: str,
) -> None:
    # Get function data
    function_data: dict = _get_specific_function_data(function_name, parent_class_name)
    function_result_ids: list[str] = function_data["results"]

    api_data = get_api_data(docstring_style)
    all_results: list[dict] = api_data["results"]

    # Sort out the results we need
    result_data: list[dict] = [
        result
        for result in all_results
        if result["id"] in function_result_ids
    ]

    # Sort data before comparing
    for data_set in [result_data, expected_result_data]:
        for parameter in data_set:
            parameter["types"] = _sort_list_of_dicts(parameter["types"], ["name"])

    # Assert
    _assert_list_of_dicts(result_data, expected_result_data)
