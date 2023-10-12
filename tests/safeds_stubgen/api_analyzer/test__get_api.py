from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from safeds_stubgen.api_analyzer import get_api
from safeds_stubgen.docstring_parsing import DocstringStyle

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion

# Setup: API data
_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "test_package"
_main_test_module_name = "test_module"

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


def _get_specific_class_data(class_name: str, docstring_style: str = "plaintext", is_enum: bool = False) -> dict:
    data_type = "enums" if is_enum else "classes"
    api_data = get_api_data(docstring_style)
    for class_ in api_data[data_type]:
        if class_["id"].endswith(f"/{class_name}"):
            return class_
    raise AssertionError


def get_api_data(docstring_style: str) -> dict:
    return {
        "plaintext": api_data_paintext,
        "epydoc": api_data_epydoc,
        "numpydoc": api_data_numpy,
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


# ############################## Module ############################## #
def test_modules_test_module(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data(_main_test_module_name)
    assert module_data == snapshot


def test_modules_another_module(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("another_module")
    assert module_data == snapshot


def test_modules_test_enums(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("test_enums")
    assert module_data == snapshot


def test_modules___init__(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("__init__")
    assert module_data == snapshot


def test_modules_test_docstrings(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("test_docstrings")
    assert module_data == snapshot


# ############################## Imports ############################## #
def get_import_data(module_name: str, import_type: str) -> list[dict]:
    module_data = _get_specific_module_data(module_name)
    return module_data.get(import_type, [])


def test_imports_test_module_qualified_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data(_main_test_module_name, "qualified_imports")
    assert import_data == snapshot


def test_imports_test_module_wildcard_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data(_main_test_module_name, "wildcard_imports")
    assert import_data == snapshot


def test_imports_test_emums_qualified_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("test_enums", "qualified_imports")
    assert import_data == snapshot


def test_imports_test_enums_wildcard_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("test_enums", "wildcard_imports")
    assert import_data == snapshot


def test_imports___init___qualified_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("__init__", "qualified_imports")
    assert import_data == snapshot


def test_imports___init___wildcard_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("__init__", "wildcard_imports")
    assert import_data == snapshot


# ############################## Classes ############################## #
def test_classes_SomeClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("SomeClass", "plaintext")
    assert class_data == snapshot


def test_classes_NestedClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("NestedClass", "plaintext")
    assert class_data == snapshot


def test_classes__PrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("_PrivateClass", "plaintext")
    assert class_data == snapshot


def test_classes_NestedPrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("NestedPrivateClass", "plaintext")
    assert class_data == snapshot


def test_classes_NestedNestedPrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("NestedNestedPrivateClass", "plaintext")
    assert class_data == snapshot


def test_classes_EpydocDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("EpydocDocstringClass", "epydoc")
    assert class_data == snapshot


def test_classes_RestDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("RestDocstringClass", "rest")
    assert class_data == snapshot


def test_classes_NumpyDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("NumpyDocstringClass", "numpydoc")
    assert class_data == snapshot


def test_classes_GoogleDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("GoogleDocstringClass", "google")
    assert class_data == snapshot


def test_classes_ReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("ReexportClass", "plaintext")
    assert class_data == snapshot


def test_classes_AnotherReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("AnotherReexportClass", "plaintext")
    assert class_data == snapshot


def test_classes__ThirdReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("_ThirdReexportClass", "plaintext")
    assert class_data == snapshot


def test_classes_FourthReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("FourthReexportClass", "plaintext")
    assert class_data == snapshot


# ############################## Class Attributes ############################## #
def get_class_attribute_data(class_name: str, docstring_style: str) -> list:
    class_data: dict = _get_specific_class_data(class_name)
    class_attr_ids: list[str] = class_data["attributes"]

    # Sort out the class attribute data we need and return
    api_data = get_api_data(docstring_style)
    return [attr for attr in api_data["attributes"] if attr["id"] in class_attr_ids]


def test_class_attributes_SomeClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("SomeClass", "plaintext")
    assert class_data == snapshot


def test_class_attributes_NestedClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("NestedClass", "plaintext")
    assert class_data == snapshot


def test_class_attributes__PrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("_PrivateClass", "plaintext")
    assert class_data == snapshot


def test_class_attributes_NestedPrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("NestedPrivateClass", "plaintext")
    assert class_data == snapshot


def test_class_attributes_NestedNestedPrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("NestedNestedPrivateClass", "plaintext")
    assert class_data == snapshot


# Todo Epydoc Tests are deactivated right now, since attribute handling is not implemented yet in the
#  docstring_parser library
def xtest_class_attributes_EpydocDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("EpydocDocstringClass", "epydoc")
    assert class_data == snapshot


def test_class_attributes_RestDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("RestDocstringClass", "rest")
    assert class_data == snapshot


def test_class_attributes_NumpyDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("NumpyDocstringClass", "numpydoc")
    assert class_data == snapshot


def test_class_attributes_GoogleDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("GoogleDocstringClass", "google")
    assert class_data == snapshot


# ############################## Enums ############################## #
def test_enums_EnumTest(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_data = _get_specific_class_data("EnumTest", is_enum=True)
    assert enum_data == snapshot


def test_enums__ReexportedEmptyEnum(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_data = _get_specific_class_data("_ReexportedEmptyEnum", is_enum=True)
    assert enum_data == snapshot


def test_enums_AnotherTestEnum(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_data = _get_specific_class_data("AnotherTestEnum", is_enum=True)
    assert enum_data == snapshot


# ############################## Enum Instances ############################## #
def get_enum_instance_data(enum_name: str) -> list:
    # Get enum data
    enum_data = _get_specific_class_data(enum_name, is_enum=True)
    enum_instance_ids = enum_data["instances"]

    all_enum_instances = api_data_paintext["enum_instances"]

    # Sort out the enum instances we need and return
    return [enum_instance for enum_instance in all_enum_instances if enum_instance["id"] in enum_instance_ids]


def test_enum_instances_EnumTest(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_instance_data = get_enum_instance_data("EnumTest")
    assert enum_instance_data == snapshot


def test_enum_instances__ReexportedEmptyEnum(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_instance_data = get_enum_instance_data("_ReexportedEmptyEnum")
    assert enum_instance_data == snapshot


def test_enum_instances_AnotherTestEnum(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_instance_data = get_enum_instance_data("AnotherTestEnum")
    assert enum_instance_data == snapshot


# ############################## Global Functions ############################## #
def get_global_function_data(module_name: str) -> list:
    # Get function data
    module_data = _get_specific_module_data(module_name)
    global_function_ids = module_data["functions"]

    all_functions: list[dict] = api_data_paintext["functions"]

    # Sort out the functions we need and return
    return [function for function in all_functions if function["id"] in global_function_ids]


def test_global_functions_test_module(snapshot: SnapshotAssertion) -> None:
    global_function_data = get_global_function_data(_main_test_module_name)
    assert global_function_data == snapshot


def test_global_functions__reexport_module_1(snapshot: SnapshotAssertion) -> None:
    global_function_data = get_global_function_data("_reexport_module_1")
    assert global_function_data == snapshot


def test_global_functions__reexport_module_2(snapshot: SnapshotAssertion) -> None:
    global_function_data = get_global_function_data("_reexport_module_2")
    assert global_function_data == snapshot


def test_global_functions__reexport_module_3(snapshot: SnapshotAssertion) -> None:
    global_function_data = get_global_function_data("_reexport_module_3")
    assert global_function_data == snapshot


def test_global_functions__reexport_module_4(snapshot: SnapshotAssertion) -> None:
    global_function_data = get_global_function_data("_reexport_module_4")
    assert global_function_data == snapshot


# ############################## Class Methods ############################## #
def get_class_methods_data(class_name: str, docstring_style: str) -> list:
    class_data: dict = _get_specific_class_data(class_name)
    class_method_ids: list[str] = class_data["methods"]

    api_data = get_api_data(docstring_style)
    all_functions: list[dict] = api_data["functions"]

    # Sort out the functions we need and return
    return [method for method in all_functions if method["id"] in class_method_ids]


def test_class_methods_SomeClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("SomeClass", "plaintext")
    assert class_methods_data == snapshot


def test_class_methods_NestedClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("NestedClass", "plaintext")
    assert class_methods_data == snapshot


def test_class_methods__PrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("_PrivateClass", "plaintext")
    assert class_methods_data == snapshot


def test_class_methods_NestedPrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("NestedPrivateClass", "plaintext")
    assert class_methods_data == snapshot


def test_class_methods_NestedNestedPrivateClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("NestedNestedPrivateClass", "plaintext")
    assert class_methods_data == snapshot


def test_class_methods_ReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("ReexportClass", "plaintext")
    assert class_methods_data == snapshot


def test_class_methods_EpydocDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("EpydocDocstringClass", "epydoc")
    assert class_methods_data == snapshot


def test_class_methods_RestDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("RestDocstringClass", "rest")
    assert class_methods_data == snapshot


def test_class_methods_NumpyDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("NumpyDocstringClass", "numpydoc")
    assert class_methods_data == snapshot


def test_class_methods_GoogleDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("GoogleDocstringClass", "google")
    assert class_methods_data == snapshot


# ############################## Function Parameters ############################## #
def get_function_parameter_data(function_name: str, parent_class_name: str, docstring_style: str) -> list:
    function_data: dict = _get_specific_function_data(function_name, parent_class_name)
    function_parameter_ids: list[str] = function_data["parameters"]

    api_data = get_api_data(docstring_style)
    all_parameters: list[dict] = api_data["parameters"]

    # Sort out the parameters we need and return
    return [parameter for parameter in all_parameters if parameter["id"] in function_parameter_ids]


def test_function_parameters_global_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("global_func", "", "plaintext")
    assert function_parameter_data == snapshot


def test_function_parameters_SomeClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data("__init__", "SomeClass", "plaintext")
    assert function_parameter_data == snapshot


def test_function_parameters_static_function(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("static_function", "SomeClass", "plaintext")
    assert function_parameter_data == snapshot


def test_function_parameters_test_position(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("test_position", "SomeClass", "plaintext")
    assert function_parameter_data == snapshot


def test_function_parameters_test_params(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("test_params", "SomeClass", "plaintext")
    assert function_parameter_data == snapshot


def test_function_parameters_nested_class_function(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("nested_class_function", "NestedClass", "plaintext")
    assert function_parameter_data == snapshot


def test_function_parameters_epydoc_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("epydoc_docstring_func", "EpydocDocstringClass", "epydoc")
    assert function_parameter_data == snapshot


def test_function_parameters_EpydocDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data("__init__", "EpydocDocstringClass", "epydoc")
    assert function_parameter_data == snapshot


def test_function_parameters_rest_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("rest_docstring_func", "RestDocstringClass", "rest")
    assert function_parameter_data == snapshot


def test_function_parameters_RestDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data("__init__", "RestDocstringClass", "rest")
    assert function_parameter_data == snapshot


def test_function_parameters_numpy_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("numpy_docstring_func", "NumpyDocstringClass", "numpydoc")
    assert function_parameter_data == snapshot


def test_function_parameters_NumpyDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data("__init__", "NumpyDocstringClass", "numpydoc")
    assert function_parameter_data == snapshot


def test_function_parameters_google_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data("google_docstring_func", "GoogleDocstringClass", "google")
    assert function_parameter_data == snapshot


def test_function_parameters_GoogleDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data("__init__", "GoogleDocstringClass", "google")
    assert function_parameter_data == snapshot


# ############################## Function Results ############################## #
def get_function_result_data(function_name: str, parent_class_name: str, docstring_style: str) -> list:
    function_data: dict = _get_specific_function_data(function_name, parent_class_name)
    function_result_ids: list[str] = function_data["results"]

    api_data = get_api_data(docstring_style)
    all_results: list[dict] = api_data["results"]

    # Sort out the results we need and return
    return [result for result in all_results if result["id"] in function_result_ids]


def test_function_results_global_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("global_func", "", "plaintext")
    assert function_result_data == snapshot


def test_function_results_multiple_results(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("multiple_results", "SomeClass", "plaintext")
    assert function_result_data == snapshot


def test_function_results_static_function(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("static_function", "SomeClass", "plaintext")
    assert function_result_data == snapshot


def test_function_results_test_position(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("test_position", "SomeClass", "plaintext")
    assert function_result_data == snapshot


def test_function_results_nested_class_function(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("nested_class_function", "NestedClass", "plaintext")
    assert function_result_data == snapshot


def test_function_results_epydoc_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("epydoc_docstring_func", "EpydocDocstringClass", "epydoc")
    assert function_result_data == snapshot


def test_function_results_rest_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("rest_docstring_func", "RestDocstringClass", "rest")
    assert function_result_data == snapshot


def test_function_results_numpy_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("numpy_docstring_func", "NumpyDocstringClass", "numpydoc")
    assert function_result_data == snapshot


def test_function_results_google_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data("google_docstring_func", "GoogleDocstringClass", "google")
    assert function_result_data == snapshot
