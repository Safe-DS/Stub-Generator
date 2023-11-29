from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from safeds_stubgen.api_analyzer import get_api
from safeds_stubgen.docstring_parsing import DocstringStyle

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion

# Setup: API data
_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "test_package"

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


def _get_specific_class_data(
    module_name: str,
    class_name: str,
    docstring_style: str = "plaintext",
    is_enum: bool = False
) -> dict:
    data_type = "enums" if is_enum else "classes"
    api_data = get_api_data(docstring_style)
    for class_ in api_data[data_type]:
        if module_name in class_["id"] and class_["id"].endswith(f"/{class_name}"):
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
    raise AssertionError


# ############################## Module ############################## #
def test_modules_class_module(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("class_module")
    assert module_data == snapshot


def test_modules_another_module(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("another_module")
    assert module_data == snapshot


def test_modules_enum_module(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("enum_module")
    assert module_data == snapshot


def test_modules___init__(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("__init__")
    assert module_data == snapshot


def test_modules_docstring_module(snapshot: SnapshotAssertion) -> None:
    module_data = _get_specific_module_data("docstring_module")
    assert module_data == snapshot


# ############################## Imports ############################## # Todo new tests after issue #38
def get_import_data(module_name: str, import_type: str) -> list[dict]:
    module_data = _get_specific_module_data(module_name)
    return module_data.get(import_type, [])


def test_imports_module_qualified_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("import_module", "qualified_imports")
    assert import_data == snapshot


def test_imports_module_wildcard_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("import_module", "wildcard_imports")
    assert import_data == snapshot


def test_imports_enum_module_qualified_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("enum_module", "qualified_imports")
    assert import_data == snapshot


def test_imports_enum_module_wildcard_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("enum_module", "wildcard_imports")
    assert import_data == snapshot


def test_imports___init___qualified_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("__init__", "qualified_imports")
    assert import_data == snapshot


def test_imports___init___wildcard_imports(snapshot: SnapshotAssertion) -> None:
    import_data = get_import_data("__init__", "wildcard_imports")
    assert import_data == snapshot


# ############################## Classes ############################## #
def test_classes_ClassModuleEmptyClassA(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("class_module", "ClassModuleEmptyClassA")
    assert class_data == snapshot


def test_classes_ClassModuleClassB(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("class_module", "ClassModuleClassB")
    assert class_data == snapshot


def test_classes_ClassModuleClassC(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("class_module", "ClassModuleClassC")
    assert class_data == snapshot


def test_classes_ClassModuleClassD(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("class_module", "ClassModuleClassD")
    assert class_data == snapshot


def test_classes_ClassModuleNestedClassE(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("class_module", "ClassModuleNestedClassE")
    assert class_data == snapshot


def test_classes__ClassModulePrivateDoubleNestedClassF(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("class_module", "_ClassModulePrivateDoubleNestedClassF")
    assert class_data == snapshot


def test_classes__ClassModulePrivateClassG(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("class_module", "_ClassModulePrivateClassG")
    assert class_data == snapshot


def test_classes_VarianceClassAll(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("variance_module", "VarianceClassAll")
    assert class_data == snapshot


def test_classes_VarianceClassOnlyInvariance(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("variance_module", "VarianceClassOnlyInvariance")
    assert class_data == snapshot


def test_classes_InferMyTypes(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("infer_types_module", "InferMyTypes")
    assert class_data == snapshot


def test_classes_EpydocDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("docstring_module", "EpydocDocstringClass", "epydoc")
    assert class_data == snapshot


def test_classes_RestDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("docstring_module", "RestDocstringClass", "rest")
    assert class_data == snapshot


def test_classes_NumpyDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("docstring_module", "NumpyDocstringClass", "numpydoc")
    assert class_data == snapshot


def test_classes_GoogleDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("docstring_module", "GoogleDocstringClass", "google")
    assert class_data == snapshot


def test_classes_ReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("_reexport_module_1", "ReexportClass")
    assert class_data == snapshot


def test_classes_AnotherReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("_reexport_module_2", "AnotherReexportClass")
    assert class_data == snapshot


def test_classes__ThirdReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("_reexport_module_3", "_ThirdReexportClass")
    assert class_data == snapshot


def test_classes_FourthReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("_reexport_module_4", "FourthReexportClass")
    assert class_data == snapshot


def test_classes_AbstractModuleClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = _get_specific_class_data("abstract_module", "AbstractModuleClass")
    assert class_data == snapshot


# ############################## Class Attributes ############################## #
def get_class_attribute_data(module_name: str, class_name: str, docstring_style: str) -> list:
    class_data: dict = _get_specific_class_data(module_name, class_name, docstring_style)
    class_attr_ids: list[str] = class_data["attributes"]

    # Sort out the class attribute data we need and return
    api_data = get_api_data(docstring_style)
    return [attr for attr in api_data["attributes"] if attr["id"] in class_attr_ids]


def test_class_attributes_AttributesClassB(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("attribute_module", "AttributesClassB", "plaintext")
    assert class_data == snapshot


def test_class_attributes_ClassModuleNestedClassE(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("class_module", "ClassModuleNestedClassE", "plaintext")
    assert class_data == snapshot


def test_class_attributes__ClassModulePrivateClassG(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("class_module", "_ClassModulePrivateClassG", "plaintext")
    assert class_data == snapshot


# Todo Epydoc Tests are deactivated right now, since attribute handling is not implemented yet in the
#  docstring_parser library
def xtest_class_attributes_EpydocDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("docstring_module", "EpydocDocstringClass", "epydoc")
    assert class_data == snapshot


def test_class_attributes_RestDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("docstring_module", "RestDocstringClass", "rest")
    assert class_data == snapshot


def test_class_attributes_NumpyDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("docstring_module", "NumpyDocstringClass", "numpydoc")
    assert class_data == snapshot


def test_class_attributes_GoogleDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_data = get_class_attribute_data("docstring_module", "GoogleDocstringClass", "google")
    assert class_data == snapshot


# ############################## Enums ############################## #
def test_enums_EnumTest(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_data = _get_specific_class_data("enum_module", "EnumTest", is_enum=True)
    assert enum_data == snapshot


def test_enums__ReexportedEmptyEnum(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_data = _get_specific_class_data("enum_module", "_ReexportedEmptyEnum", is_enum=True)
    assert enum_data == snapshot


def test_enums_EnumTest2(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_data = _get_specific_class_data("enum_module", "EnumTest2", is_enum=True)
    assert enum_data == snapshot


def test_enums_EnumTest3(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_data = _get_specific_class_data("enum_module", "EnumTest3", is_enum=True)
    assert enum_data == snapshot


# ############################## Enum Instances ############################## #
def get_enum_instance_data(enum_name: str, module_name: str = "enum_module") -> list:
    # Get enum data
    enum_data = _get_specific_class_data(module_name, enum_name, is_enum=True)
    enum_instance_ids = enum_data["instances"]

    # Sort out the enum instances we need and return
    return [
        enum_instance
        for enum_instance in api_data_paintext["enum_instances"]
        if enum_instance["id"] in enum_instance_ids
    ]


def test_enum_instances_EnumTest(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_instance_data = get_enum_instance_data("EnumTest")
    assert enum_instance_data == snapshot


def test_enum_instances__ReexportedEmptyEnum(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_instance_data = get_enum_instance_data("_ReexportedEmptyEnum")
    assert enum_instance_data == snapshot


def test_enum_instances_EnumTest3(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    enum_instance_data = get_enum_instance_data("EnumTest3")
    assert enum_instance_data == snapshot


# ############################## Global Functions ############################## #
def get_global_function_data(module_name: str) -> list:
    # Get function data
    module_data = _get_specific_module_data(module_name)
    global_function_ids = module_data["functions"]

    all_functions: list[dict] = api_data_paintext["functions"]

    # Sort out the functions we need and return
    return [function for function in all_functions if function["id"] in global_function_ids]


def test_global_functions_function_module(snapshot: SnapshotAssertion) -> None:
    global_function_data = get_global_function_data("function_module")
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
def get_class_methods_data(module_name: str, class_name: str, docstring_style: str = "plaintext") -> list:
    class_data: dict = _get_specific_class_data(module_name, class_name)
    class_method_ids: list[str] = class_data["methods"]

    api_data = get_api_data(docstring_style)
    all_functions: list[dict] = api_data["functions"]

    # Sort out the functions we need and return
    return [method for method in all_functions if method["id"] in class_method_ids]


def test_class_methods_ClassModuleEmptyClassA(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("class_module", "ClassModuleEmptyClassA")
    assert class_methods_data == snapshot


def test_class_methods_ClassModuleClassB(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("class_module", "ClassModuleClassB")
    assert class_methods_data == snapshot


def test_class_methods_ClassModuleClassC(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("class_module", "ClassModuleClassC")
    assert class_methods_data == snapshot


def test_class_methods_function_module_FunctionModuleClassB(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("function_module", "FunctionModuleClassB")
    assert class_methods_data == snapshot


def test_class_methods_function_module_FunctionModuleClassC(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("function_module", "FunctionModuleClassC")
    assert class_methods_data == snapshot


def test_class_methods_InferMyTypes(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("infer_types_module", "InferMyTypes")
    assert class_methods_data == snapshot


def test_class_methods_FunctionModulePropertiesClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("function_module", "FunctionModulePropertiesClass")
    assert class_methods_data == snapshot


def test_class_methods_ClassModuleNestedClassE(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("class_module", "ClassModuleNestedClassE")
    assert class_methods_data == snapshot


def test_class_methods__ClassModulePrivateDoubleNestedClassF(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("class_module", "_ClassModulePrivateDoubleNestedClassF")
    assert class_methods_data == snapshot


def test_class_methods_ReexportClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("_reexport_module_1", "ReexportClass")
    assert class_methods_data == snapshot


def test_class_methods_AbstractModuleClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("abstract_module", "AbstractModuleClass")
    assert class_methods_data == snapshot


def test_class_methods_EpydocDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("docstring_module", "EpydocDocstringClass", "epydoc")
    assert class_methods_data == snapshot


def test_class_methods_RestDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("docstring_module", "RestDocstringClass", "rest")
    assert class_methods_data == snapshot


def test_class_methods_NumpyDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("docstring_module", "NumpyDocstringClass", "numpydoc")
    assert class_methods_data == snapshot


def test_class_methods_GoogleDocstringClass(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    class_methods_data = get_class_methods_data("docstring_module", "GoogleDocstringClass", "google")
    assert class_methods_data == snapshot


# ############################## Function Parameters ############################## #
def get_function_parameter_data(
    function_name: str,
    module_name: str = "function_module",
    parent_class_name: str = "",
    docstring_style: str = "plaintext"
) -> list:
    function_data: dict = _get_specific_function_data(module_name, function_name, parent_class_name, docstring_style)
    function_parameter_ids: list[str] = function_data["parameters"]

    api_data = get_api_data(docstring_style)

    # Sort out the parameters we need and return
    return [
        parameter
        for parameter in api_data["parameters"]
        if parameter["id"] in function_parameter_ids
    ]


def test_function_parameters_function_module_FunctionModuleClassB___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        function_name="__init__",
        parent_class_name="FunctionModuleClassB"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_FunctionModuleClassB_static_method_params(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        function_name="static_method_params",
        parent_class_name="FunctionModuleClassB"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_FunctionModuleClassB_class_method(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        function_name="class_method",
        parent_class_name="FunctionModuleClassB"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_FunctionModuleClassB_class_method_params(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        function_name="class_method_params",
        parent_class_name="FunctionModuleClassB"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_FunctionModuleClassC_nested_class_function(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        function_name="nested_class_function",
        parent_class_name="FunctionModuleClassC"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_function_module__private(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="_private")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_public_no_params_no_result(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="public_no_params_no_result")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_params(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="params")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_illegal_params(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="illegal_params")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_special_params(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="special_params")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_param_position(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="param_position")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_opt_pos_only(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="opt_pos_only")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_req_name_only(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="req_name_only")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_arg(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="arg")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_args_type(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="args_type")
    assert function_parameter_data == snapshot


def test_function_parameters_function_module_callable_type(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(function_name="callable_type")
    assert function_parameter_data == snapshot


def test_function_parameters_abstract_module_abstract_method_params(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(
        module_name="abstract_module",
        function_name="abstract_method_params",
        parent_class_name="AbstractModuleClass",
    )
    assert function_parameter_data == snapshot


def test_function_parameters_abstract_module_abstract_static_method_params(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(
        module_name="abstract_module",
        function_name="abstract_static_method_params",
        parent_class_name="AbstractModuleClass",
    )
    assert function_parameter_data == snapshot


def test_function_parameters_abstract_module_abstract_property_method(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(
        module_name="abstract_module",
        function_name="abstract_property_method",
        parent_class_name="AbstractModuleClass",
    )
    assert function_parameter_data == snapshot


def test_function_parameters_epydoc_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="epydoc_docstring_func",
        parent_class_name="EpydocDocstringClass",
        docstring_style="epydoc")
    assert function_parameter_data == snapshot


def test_function_parameters_EpydocDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="__init__",
        parent_class_name="EpydocDocstringClass",
        docstring_style="epydoc"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_rest_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="rest_docstring_func",
        parent_class_name="RestDocstringClass",
        docstring_style="rest"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_RestDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="__init__",
        parent_class_name="RestDocstringClass",
        docstring_style="rest"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_numpy_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="numpy_docstring_func",
        parent_class_name="NumpyDocstringClass",
        docstring_style="numpydoc"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_NumpyDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="__init__",
        parent_class_name="NumpyDocstringClass",
        docstring_style="numpydoc"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_google_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="google_docstring_func",
        parent_class_name="GoogleDocstringClass",
        docstring_style="google"
    )
    assert function_parameter_data == snapshot


def test_function_parameters_GoogleDocstringClass___init__(snapshot: SnapshotAssertion) -> None:  # noqa: N802
    function_parameter_data = get_function_parameter_data(
        module_name="docstring_module",
        function_name="__init__",
        parent_class_name="GoogleDocstringClass",
        docstring_style="google"
    )
    assert function_parameter_data == snapshot


# ############################## Function Results ############################## #
def get_function_result_data(
    function_name: str,
    module_name: str = "function_module",
    parent_class_name: str = "",
    docstring_style: str = "plaintext"
) -> list:
    function_data: dict = _get_specific_function_data(module_name, function_name, parent_class_name, docstring_style)
    function_result_ids: list[str] = function_data["results"]

    api_data = get_api_data(docstring_style)

    # Sort out the results we need and return
    return [
        result
        for result in api_data["results"]
        if result["id"] in function_result_ids
    ]


def test_function_results_instance_method(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        function_name="instance_method",
        parent_class_name="FunctionModuleClassB"
    )
    assert function_result_data == snapshot


def test_function_results_static_method_params(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        function_name="static_method_params",
        parent_class_name="FunctionModuleClassB"
    )
    assert function_result_data == snapshot


def test_function_results_class_method_params(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        function_name="class_method_params",
        parent_class_name="FunctionModuleClassB"
    )
    assert function_result_data == snapshot


def test_function_results_nested_class_function(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        function_name="nested_class_function",
        parent_class_name="FunctionModuleClassC"
    )
    assert function_result_data == snapshot


@pytest.mark.parametrize(
    argnames="func_name",
    argvalues=[
        "int_result",
        "str_result",
        "float_result",
        "none_result",
        "obj_result",
        "callexr_result",
        "tuple_results",
        "union_results",
        "list_results",
        "illegal_list_results",
        "dictionary_results",
        "illegal_dictionary_results",
        "union_dictionary_results",
        "set_results",
        "illegal_set_results",
        "optional_results",
        "literal_results",
        "any_results",
        "callable_type",
    ],
    ids=[
        "int_result",
        "str_result",
        "float_result",
        "none_result",
        "obj_result",
        "callexr_result",
        "tuple_results",
        "union_results",
        "list_results",
        "illegal_list_results",
        "dictionary_results",
        "illegal_dictionary_results",
        "union_dictionary_results",
        "set_results",
        "illegal_set_results",
        "optional_results",
        "literal_results",
        "any_results",
        "callable_type",
    ],
)
def test_function_results_int_result(func_name: str, snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        function_name=func_name,
    )
    assert function_result_data == snapshot


def test_function_results_infer_function(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="infer_types_module",
        function_name="infer_function",
        parent_class_name="InferMyTypes"
    )
    assert function_result_data == snapshot


def test_function_results_abstract_method_params(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="abstract_module",
        function_name="abstract_method_params",
        parent_class_name="AbstractModuleClass"
    )
    assert function_result_data == snapshot


def test_function_results_abstract_static_method_params(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="abstract_module",
        function_name="abstract_static_method_params",
        parent_class_name="AbstractModuleClass"
    )
    assert function_result_data == snapshot


def test_function_results_abstract_property_method(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="abstract_module",
        function_name="abstract_property_method",
        parent_class_name="AbstractModuleClass"
    )
    assert function_result_data == snapshot


def test_function_results_function_module_property_function(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="function_module",
        function_name="property_function",
        parent_class_name="FunctionModulePropertiesClass",
    )
    assert function_result_data == snapshot


def test_function_results_function_module_property_function_params(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="function_module",
        function_name="property_function_params",
        parent_class_name="FunctionModulePropertiesClass",
    )
    assert function_result_data == snapshot


def test_function_results_function_module_property_function_infer(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="function_module",
        function_name="property_function_infer",
        parent_class_name="FunctionModulePropertiesClass",
    )
    assert function_result_data == snapshot


def test_function_results_epydoc_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="docstring_module",
        function_name="epydoc_docstring_func",
        parent_class_name="EpydocDocstringClass",
        docstring_style="epydoc"
    )
    assert function_result_data == snapshot


def test_function_results_rest_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="docstring_module",
        function_name="rest_docstring_func",
        parent_class_name="RestDocstringClass",
        docstring_style="rest"
    )
    assert function_result_data == snapshot


def test_function_results_numpy_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="docstring_module",
        function_name="numpy_docstring_func",
        parent_class_name="NumpyDocstringClass",
        docstring_style="numpydoc"
    )
    assert function_result_data == snapshot


def test_function_results_google_docstring_func(snapshot: SnapshotAssertion) -> None:
    function_result_data = get_function_result_data(
        module_name="docstring_module",
        function_name="google_docstring_func",
        parent_class_name="GoogleDocstringClass",
        docstring_style="google"
    )
    assert function_result_data == snapshot
