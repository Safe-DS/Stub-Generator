from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from safeds_stubgen.api_analyzer import get_api
from safeds_stubgen.docstring_parsing import DocstringStyle

if TYPE_CHECKING:
    from collections.abc import Generator

    from syrupy import SnapshotAssertion

# Setup: API data
_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "various_modules_package"
package_root = Path(_test_dir / "data" / _test_package_name)

api_data_paintext = get_api(
    root=package_root,
    is_test_run=True,
).to_dict()

api_data_numpy = get_api(
    root=package_root,
    docstring_style=DocstringStyle.NUMPYDOC,
    is_test_run=True,
).to_dict()

api_data_rest = get_api(
    root=package_root,
    docstring_style=DocstringStyle.REST,
    is_test_run=True,
).to_dict()

api_data_google = get_api(
    root=package_root,
    docstring_style=DocstringStyle.GOOGLE,
    is_test_run=True,
).to_dict()


# Utilites
def _get_specific_module_data(module_name: str, docstring_style: str = "plaintext") -> dict:
    api_data = get_api_data(docstring_style)

    for module in api_data["modules"]:
        if module["name"] == module_name:
            return module
    raise pytest.fail(f"Could not find module data for '{module_name}'.")


def _get_specific_class_data(
    module_name: str,
    class_name: str,
    docstring_style: str = "plaintext",
    is_enum: bool = False,
) -> dict:
    data_type = "enums" if is_enum else "classes"
    api_data = get_api_data(docstring_style)
    for class_ in api_data[data_type]:
        if module_name in class_["id"] and class_["id"].endswith(f"/{class_name}"):
            return class_
    raise pytest.fail(f"Could not find class data for '{class_name}' in module '{module_name}'.")


def get_api_data(docstring_style: str) -> dict:
    return {
        "plaintext": api_data_paintext,
        "numpydoc": api_data_numpy,
        "rest": api_data_rest,
        "google": api_data_google,
    }[docstring_style]


def _get_specific_function_data(
    module_name: str,
    function_name: str,
    parent_class_name: str = "",
    docstring_style: str = "plaintext",
) -> dict:
    api_data = get_api_data(docstring_style)

    if parent_class_name == "":
        parent_class_name = module_name

    for function in api_data["functions"]:
        if function["id"].endswith(f"{parent_class_name}/{function_name}"):
            return function
    raise pytest.fail(f"Could not find function data for '{function_name}' in module '{module_name}'.")


_function_module_name = "function_module"
_enum_module_name = "enum_module"
_docstring_module_name = "docstring_module"
_class_module_name = "class_module"
_import_module_name = "import_module"
_abstract_module_name = "abstract_module"
_infer_types_module_name = "infer_types_module"
_type_var_module_name = "type_var_module"


# ############################## Tests ############################## #
def _python_files() -> Generator:
    return package_root.rglob(pattern="*.py")


def _python_file_ids() -> Generator:
    files = package_root.rglob(pattern="*.py")
    for file in files:
        yield str(file.relative_to(package_root).as_posix()).removesuffix(".py")


@pytest.mark.parametrize("python_file", _python_files(), ids=_python_file_ids())
def test_modules(python_file: Path, snapshot: SnapshotAssertion) -> None:
    file_name = python_file.parts[-1]
    is_package = file_name == "__init__.py"

    module_id = ""
    if is_package:
        for part in python_file.parts[:-1]:
            if part.startswith("_"):
                return
        module_id = "/".join(python_file.parts[:-1])

    api_data = get_api_data("plaintext")

    for module in api_data["modules"]:
        is_init_file = is_package and module_id.endswith(module["id"])
        is_module_file = "/".join(python_file.parts).endswith(f"{module['id']}.py")
        if is_init_file or is_module_file:
            assert module == snapshot
            return
    raise pytest.fail(f"Could not find module data for '{file_name}'.")


@pytest.mark.parametrize(
    argnames=("module_name", "import_type"),
    argvalues=[
        (_import_module_name, "qualified_imports"),
        (_import_module_name, "wildcard_imports"),
        (_enum_module_name, "qualified_imports"),
        (_enum_module_name, "wildcard_imports"),
        ("__init__", "qualified_imports"),
        ("__init__", "wildcard_imports"),
    ],
    ids=[
        "import_module (qualified_imports)",
        "import_module (wildcard_imports)",
        "enum_module (qualified_imports)",
        "enum_module (wildcard_imports)",
        "__init__ (qualified_imports)",
        "__init__ (wildcard_imports)",
    ],
)
def test_imports(module_name: str, import_type: str, snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data(module_name)
    import_data = module_data.get(import_type, [])
    assert import_data == snapshot


@pytest.mark.parametrize(
    argnames=("module_name", "class_name", "docstring_style"),
    argvalues=[
        (_class_module_name, "ClassModuleEmptyClassA", "plaintext"),
        (_class_module_name, "ClassModuleClassB", "plaintext"),
        (_class_module_name, "ClassModuleClassC", "plaintext"),
        (_class_module_name, "ClassModuleClassD", "plaintext"),
        (_class_module_name, "ClassModuleNestedClassE", "plaintext"),
        (_class_module_name, "_ClassModulePrivateDoubleNestedClassF", "plaintext"),
        (_class_module_name, "_ClassModulePrivateClassG", "plaintext"),
        ("variance_module", "VarianceClassOnlyCovarianceNoBound", "plaintext"),
        ("variance_module", "VarianceClassOnlyVarianceNoBound", "plaintext"),
        ("variance_module", "VarianceClassOnlyContravarianceNoBound", "plaintext"),
        ("variance_module", "VarianceClassAll", "plaintext"),
        (_infer_types_module_name, "InferMyTypes", "plaintext"),
        (_docstring_module_name, "RestDocstringClass", "rest"),
        (_docstring_module_name, "NumpyDocstringClass", "numpydoc"),
        (_docstring_module_name, "GoogleDocstringClass", "google"),
        ("_reexport_module_1", "ReexportClass", "plaintext"),
        ("_reexport_module_2", "AnotherReexportClass", "plaintext"),
        ("_reexport_module_3", "_ThirdReexportClass", "plaintext"),
        ("_reexport_module_4", "FourthReexportClass", "plaintext"),
        (_abstract_module_name, "AbstractModuleClass", "plaintext"),
    ],
    ids=[
        "ClassModuleEmptyClassA",
        "ClassModuleClassB",
        "ClassModuleClassC",
        "ClassModuleClassD",
        "ClassModuleNestedClassE",
        "_ClassModulePrivateDoubleNestedClassF",
        "_ClassModulePrivateClassG",
        "VarianceClassOnlyCovarianceNoBound",
        "VarianceClassOnlyVarianceNoBound",
        "VarianceClassOnlyContravarianceNoBound",
        "VarianceClassAll",
        "InferMyTypes",
        "RestDocstringClass",
        "NumpyDocstringClass",
        "GoogleDocstringClass",
        "ReexportClass",
        "AnotherReexportClass",
        "_ThirdReexportClass",
        "FourthReexportClass",
        "AbstractModuleClass",
    ],
)
def test_classes(module_name: str, class_name: str, docstring_style: str, snapshot: SnapshotAssertion) -> None:
    class_data = _get_specific_class_data(module_name, class_name, docstring_style, is_enum=False)
    assert class_data == snapshot


@pytest.mark.parametrize(
    argnames=("module_name", "class_name", "docstring_style"),
    argvalues=[
        ("attribute_module", "AttributesClassB", "plaintext"),
        (_class_module_name, "ClassModuleNestedClassE", "plaintext"),
        (_class_module_name, "_ClassModulePrivateClassG", "plaintext"),
        (_docstring_module_name, "RestDocstringClass", "rest"),
        (_docstring_module_name, "NumpyDocstringClass", "numpydoc"),
        (_docstring_module_name, "GoogleDocstringClass", "google"),
    ],
    ids=[
        "AttributesClassB",
        "ClassModuleNestedClassE",
        "_ClassModulePrivateClassG",
        "RestDocstringClass",
        "NumpyDocstringClass",
        "GoogleDocstringClass",
    ],
)
def test_class_attributes(module_name: str, class_name: str, docstring_style: str, snapshot: SnapshotAssertion) -> None:
    class_data: dict = _get_specific_class_data(module_name, class_name, docstring_style)
    class_attr_ids: list[str] = class_data["attributes"]

    api_data = get_api_data(docstring_style)

    # Sort out the class attribute data we need and return
    class_attribute_data = [attr for attr in api_data["attributes"] if attr["id"] in class_attr_ids]

    assert class_attribute_data == snapshot


@pytest.mark.parametrize(
    argnames=("module_name", "class_name"),
    argvalues=[
        (_enum_module_name, "EnumTest"),
        (_enum_module_name, "_ReexportedEmptyEnum"),
        (_enum_module_name, "EnumTest2"),
        (_enum_module_name, "EnumTest3"),
    ],
    ids=[
        "EnumTest",
        "_ReexportedEmptyEnum",
        "EnumTest2",
        "EnumTest3",
    ],
)
def test_enums(module_name: str, class_name: str, snapshot: SnapshotAssertion) -> None:
    enum_data = _get_specific_class_data(module_name, class_name, is_enum=True)
    assert enum_data == snapshot


@pytest.mark.parametrize(
    argnames=("enum_name", "module_name"),
    argvalues=[
        ("EnumTest", _enum_module_name),
        ("_ReexportedEmptyEnum", _enum_module_name),
        ("EnumTest3", _enum_module_name),
    ],
    ids=[
        "EnumTest",
        "_ReexportedEmptyEnum",
        "EnumTest3",
    ],
)
def test_enum_instances(enum_name: str, module_name: str, snapshot: SnapshotAssertion) -> None:
    # Get enum data
    enum_data = _get_specific_class_data(module_name, enum_name, is_enum=True)
    enum_instance_ids = enum_data["instances"]

    # Sort out the enum instances we need and return
    enum_instance_data = [
        enum_instance
        for enum_instance in api_data_paintext["enum_instances"]
        if enum_instance["id"] in enum_instance_ids
    ]

    assert enum_instance_data == snapshot


@pytest.mark.parametrize(
    argnames="module_name",
    argvalues=[
        _function_module_name,
        "_reexport_module_1",
        "_reexport_module_2",
        "_reexport_module_3",
        "_reexport_module_4",
    ],
    ids=[
        _function_module_name,
        "_reexport_module_1",
        "_reexport_module_2",
        "_reexport_module_3",
        "_reexport_module_4",
    ],
)
def test_global_functions(module_name: str, snapshot: SnapshotAssertion) -> None:
    # Get function data
    module_data = _get_specific_module_data(module_name)
    global_function_ids = module_data["functions"]

    all_functions: list[dict] = api_data_paintext["functions"]

    # Sort out the functions we need and return
    global_function_data = [function for function in all_functions if function["id"] in global_function_ids]

    assert global_function_data == snapshot


@pytest.mark.parametrize(
    argnames=("module_name", "class_name", "docstring_style"),
    argvalues=[
        (_class_module_name, "ClassModuleEmptyClassA", "plaintext"),
        (_class_module_name, "ClassModuleClassB", "plaintext"),
        (_class_module_name, "ClassModuleClassC", "plaintext"),
        (_class_module_name, "ClassModuleNestedClassE", "plaintext"),
        (_class_module_name, "_ClassModulePrivateDoubleNestedClassF", "plaintext"),
        (_function_module_name, "FunctionModuleClassB", "plaintext"),
        (_function_module_name, "FunctionModuleClassC", "plaintext"),
        (_function_module_name, "FunctionModulePropertiesClass", "plaintext"),
        (_infer_types_module_name, "InferMyTypes", "plaintext"),
        (_type_var_module_name, "GenericTypeVar", "plaintext"),
        (_type_var_module_name, "GenericTypeVar2", "plaintext"),
        (_type_var_module_name, "SequenceTypeVar", "plaintext"),
        (_type_var_module_name, "SequenceTypeVar2", "plaintext"),
        (_type_var_module_name, "CollectionTypeVar", "plaintext"),
        (_type_var_module_name, "CollectionTypeVar2", "plaintext"),
        ("_reexport_module_1", "ReexportClass", "plaintext"),
        (_abstract_module_name, "AbstractModuleClass", "plaintext"),
        (_docstring_module_name, "RestDocstringClass", "rest"),
        (_docstring_module_name, "NumpyDocstringClass", "numpydoc"),
        (_docstring_module_name, "GoogleDocstringClass", "google"),
    ],
    ids=[
        "ClassModuleEmptyClassA",
        "ClassModuleClassB",
        "ClassModuleClassC",
        "ClassModuleNestedClassE",
        "_ClassModulePrivateDoubleNestedClassF",
        "FunctionModuleClassB",
        "FunctionModuleClassC",
        "FunctionModulePropertiesClass",
        "InferMyTypes",
        "GenericTypeVar",
        "GenericTypeVar2",
        "SequenceTypeVar",
        "SequenceTypeVar2",
        "CollectionTypeVar",
        "CollectionTypeVar2",
        "ReexportClass",
        "AbstractModuleClass",
        "RestDocstringClass",
        "NumpyDocstringClass",
        "GoogleDocstringClass",
    ],
)
def test_class_methods(module_name: str, class_name: str, docstring_style: str, snapshot: SnapshotAssertion) -> None:
    class_data: dict = _get_specific_class_data(module_name, class_name)
    class_method_ids: list[str] = class_data["methods"]

    api_data = get_api_data(docstring_style)
    all_functions: list[dict] = api_data["functions"]

    # Sort out the functions we need and return
    class_methods_data = [method for method in all_functions if method["id"] in class_method_ids]

    assert class_methods_data == snapshot


@pytest.mark.parametrize(
    argnames=("function_name", "module_name", "parent_class_name", "docstring_style"),
    argvalues=[
        ("__init__", _function_module_name, "FunctionModuleClassB", "plaintext"),
        ("static_method_params", _function_module_name, "FunctionModuleClassB", "plaintext"),
        ("class_method", _function_module_name, "FunctionModuleClassB", "plaintext"),
        ("class_method_params", _function_module_name, "FunctionModuleClassB", "plaintext"),
        ("nested_class_function", _function_module_name, "FunctionModuleClassC", "plaintext"),
        ("_private", _function_module_name, "", "plaintext"),
        ("public_no_params_no_result", _function_module_name, "", "plaintext"),
        ("params", _function_module_name, "", "plaintext"),
        ("illegal_params", _function_module_name, "", "plaintext"),
        ("special_params", _function_module_name, "", "plaintext"),
        ("param_position", _function_module_name, "", "plaintext"),
        ("opt_pos_only", _function_module_name, "", "plaintext"),
        ("req_name_only", _function_module_name, "", "plaintext"),
        ("arg", _function_module_name, "", "plaintext"),
        ("args_type", _function_module_name, "", "plaintext"),
        ("callable_type", _function_module_name, "", "plaintext"),
        ("param_from_outside_the_package", _function_module_name, "", "plaintext"),
        ("type_var_func", _type_var_module_name, "", "plaintext"),
        ("multiple_type_var", _type_var_module_name, "", "plaintext"),
        ("abstract_method_params", _abstract_module_name, "AbstractModuleClass", "plaintext"),
        ("abstract_static_method_params", _abstract_module_name, "AbstractModuleClass", "plaintext"),
        ("abstract_property_method", _abstract_module_name, "AbstractModuleClass", "plaintext"),
        ("rest_docstring_func", _docstring_module_name, "RestDocstringClass", "rest"),
        ("__init__", _docstring_module_name, "RestDocstringClass", "rest"),
        ("numpy_docstring_func", _docstring_module_name, "NumpyDocstringClass", "numpydoc"),
        ("__init__", _docstring_module_name, "NumpyDocstringClass", "numpydoc"),
        ("google_docstring_func", _docstring_module_name, "GoogleDocstringClass", "google"),
        ("__init__", _docstring_module_name, "GoogleDocstringClass", "google"),
    ],
    ids=[
        "FunctionModuleClassB.__init__",
        "static_method_params",
        "class_method",
        "class_method_params",
        "nested_class_function",
        "_private",
        "public_no_params_no_result",
        "params",
        "illegal_params",
        "special_params",
        "param_position",
        "opt_pos_only",
        "req_name_only",
        "arg",
        "args_type",
        "callable_type",
        "param_from_outside_the_package",
        "type_var_func",
        "multiple_type_var",
        "abstract_method_params",
        "abstract_static_method_params",
        "abstract_property_method",
        "rest_docstring_func",
        "rest.__init__",
        "numpy_docstring_func",
        "numpy.__init__",
        "google_docstring_func",
        "google.__init__",
    ],
)
def test_function_parameters(
    function_name: str,
    module_name: str,
    parent_class_name: str,
    docstring_style: str,
    snapshot: SnapshotAssertion,
) -> None:
    function_data: dict = _get_specific_function_data(module_name, function_name, parent_class_name, docstring_style)
    function_parameter_ids: list[str] = function_data["parameters"]

    api_data = get_api_data(docstring_style)

    # Sort out the parameters we need and return
    function_parameter_data = [
        parameter for parameter in api_data["parameters"] if parameter["id"] in function_parameter_ids
    ]

    assert function_parameter_data == snapshot


@pytest.mark.parametrize(
    argnames=("function_name", "module_name", "parent_class_name", "docstring_style"),
    argvalues=[
        ("int_result", _function_module_name, "", "plaintext"),
        ("str_result", _function_module_name, "", "plaintext"),
        ("float_result", _function_module_name, "", "plaintext"),
        ("none_result", _function_module_name, "", "plaintext"),
        ("obj_result", _function_module_name, "", "plaintext"),
        ("callexr_result_class", _function_module_name, "", "plaintext"),
        ("callexr_result_function", _function_module_name, "", "plaintext"),
        ("tuple_results", _function_module_name, "", "plaintext"),
        ("union_results", _function_module_name, "", "plaintext"),
        ("list_results", _function_module_name, "", "plaintext"),
        ("illegal_list_results", _function_module_name, "", "plaintext"),
        ("dictionary_results", _function_module_name, "", "plaintext"),
        ("dictionary_results_no_key_no_value", _function_module_name, "", "plaintext"),
        ("illegal_dictionary_results", _function_module_name, "", "plaintext"),
        ("union_dictionary_results", _function_module_name, "", "plaintext"),
        ("set_results", _function_module_name, "", "plaintext"),
        ("illegal_set_results", _function_module_name, "", "plaintext"),
        ("optional_results", _function_module_name, "", "plaintext"),
        ("literal_results", _function_module_name, "", "plaintext"),
        ("any_results", _function_module_name, "", "plaintext"),
        ("callable_type", _function_module_name, "", "plaintext"),
        ("result_from_outside_the_package", _function_module_name, "", "plaintext"),
        ("type_var_func", _type_var_module_name, "", "plaintext"),
        ("multiple_type_var", _type_var_module_name, "", "plaintext"),
        ("instance_method", _function_module_name, "FunctionModuleClassB", "plaintext"),
        ("static_method_params", _function_module_name, "FunctionModuleClassB", "plaintext"),
        ("class_method_params", _function_module_name, "FunctionModuleClassB", "plaintext"),
        ("nested_class_function", _function_module_name, "FunctionModuleClassC", "plaintext"),
        ("property_function", _function_module_name, "FunctionModulePropertiesClass", "plaintext"),
        ("property_function_params", _function_module_name, "FunctionModulePropertiesClass", "plaintext"),
        ("property_function_infer", _function_module_name, "FunctionModulePropertiesClass", "plaintext"),
        ("infer_function", _infer_types_module_name, "InferMyTypes", "plaintext"),
        ("abstract_method_params", _abstract_module_name, "AbstractModuleClass", "plaintext"),
        ("abstract_static_method_params", _abstract_module_name, "AbstractModuleClass", "plaintext"),
        ("abstract_property_method", _abstract_module_name, "AbstractModuleClass", "plaintext"),
        ("rest_docstring_func", _docstring_module_name, "RestDocstringClass", "rest"),
        ("numpy_docstring_func", _docstring_module_name, "NumpyDocstringClass", "numpydoc"),
        ("google_docstring_func", _docstring_module_name, "GoogleDocstringClass", "google"),
    ],
    ids=[
        "int_result",
        "str_result",
        "float_result",
        "none_result",
        "obj_result",
        "callexr_result_class",
        "callexr_result_function",
        "tuple_results",
        "union_results",
        "list_results",
        "illegal_list_results",
        "dictionary_results",
        "dictionary_results_no_key_no_value",
        "illegal_dictionary_results",
        "union_dictionary_results",
        "set_results",
        "illegal_set_results",
        "optional_results",
        "literal_results",
        "any_results",
        "callable_type",
        "result_from_outside_the_package",
        "type_var_func",
        "multiple_type_var",
        "instance_method",
        "static_method_params",
        "class_method_params",
        "nested_class_function",
        "property_function",
        "property_function_params",
        "property_function_infer",
        "infer_function",
        "abstract_method_params",
        "abstract_static_method_params",
        "abstract_property_method",
        "rest_docstring_func",
        "numpy_docstring_func",
        "google_docstring_func",
    ],
)
def test_function_results(
    function_name: str,
    module_name: str,
    parent_class_name: str,
    docstring_style: str,
    snapshot: SnapshotAssertion,
) -> None:
    function_data: dict = _get_specific_function_data(module_name, function_name, parent_class_name, docstring_style)
    function_result_ids: list[str] = function_data["results"]
    api_data = get_api_data(docstring_style)

    # Sort out the results we need and return
    function_result_data = [result for result in api_data["results"] if result["id"] in function_result_ids]

    assert function_result_data == snapshot
