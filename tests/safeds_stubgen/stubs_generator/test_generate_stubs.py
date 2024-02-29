from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from safeds_stubgen.api_analyzer import get_api
from safeds_stubgen.stubs_generator import generate_stubs

# noinspection PyProtectedMember
from safeds_stubgen.stubs_generator._generate_stubs import _convert_snake_to_camel_case

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion

# Setup - Run API to create stub files
_lib_dir = Path(__file__).parent.parent.parent
_test_package_name = "various_modules_package"
_test_package_dir = Path(_lib_dir / "data" / _test_package_name)
_out_dir = Path(_lib_dir / "data" / "out")
_out_dir_stubs = Path(_out_dir / _test_package_name)

api = get_api(_test_package_name, _test_package_dir, is_test_run=True)
generate_stubs(api, _out_dir, convert_identifiers=True)


# Utilites
def _assert_file_creation_recursive(python_path: Path, stub_path: Path) -> None:
    assert python_path.is_dir()
    assert stub_path.is_dir()

    python_files: list[Path] = list(python_path.iterdir())
    stub_files: list[Path] = list(stub_path.iterdir())

    # Remove __init__ files and private files without public reexported content.
    # We reexport public content from _module_3 and _module_6, not from empty_module, _module_2 and _module_4.
    actual_python_files = []
    for item in python_files:
        if not (item.is_file() and item.stem in {"__init__", "_module_2", "_module_4"}):
            actual_python_files.append(item)

    assert len(actual_python_files) == len(stub_files)

    actual_python_files.sort(key=lambda x: x.stem)
    stub_files.sort(key=lambda x: x.stem)

    for py_item, stub_item in zip(actual_python_files, stub_files, strict=True):
        if py_item.is_file():
            assert stub_item.is_dir()
            stub_files = list(stub_item.iterdir())
            assert len(stub_files) == 1
            assert stub_files[0].stem == py_item.stem
        else:
            _assert_file_creation_recursive(py_item, stub_item)


def assert_stubs_snapshot(filename: str, snapshot_sds_stub: SnapshotAssertion) -> None:
    stubs_file = Path(_out_dir_stubs / filename / f"{filename}.sdsstub")
    with stubs_file.open("r") as f:
        assert f.read() == snapshot_sds_stub


# ############################## Tests ############################## #
def test_file_creation() -> None:
    _assert_file_creation_recursive(
        python_path=Path(_test_package_dir / "file_creation"),
        stub_path=Path(_out_dir_stubs / "file_creation"),
    )


def test_file_creation_limited_stubs_outside_package(snapshot_sds_stub: SnapshotAssertion) -> None:
    path = Path(_out_dir / "tests/data/main_package/another_path/another_module/another_module.sdsstub")
    assert path.is_file()

    with path.open("r") as f:
        assert f.read() == snapshot_sds_stub


def test_class_creation(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("class_module", snapshot_sds_stub)


def test_class_attribute_creation(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("attribute_module", snapshot_sds_stub)


def test_function_creation(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("function_module", snapshot_sds_stub)


def test_enum_creation(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("enum_module", snapshot_sds_stub)


def test_import_creation(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("import_module", snapshot_sds_stub)


def test_type_inference(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("infer_types_module", snapshot_sds_stub)


def test_variance_creation(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("variance_module", snapshot_sds_stub)


def test_abstract_creation(snapshot_sds_stub: SnapshotAssertion) -> None:
    assert_stubs_snapshot("abstract_module", snapshot_sds_stub)


@pytest.mark.parametrize("file_name", ["aliasing_module_1", "aliasing_module_2", "aliasing_module_3"])
def test_alias_creation(file_name: str, snapshot_sds_stub: SnapshotAssertion) -> None:
    file_data = ""
    stubs_file = Path(_out_dir_stubs / "aliasing" / f"{file_name}" / f"{file_name}.sdsstub")
    with stubs_file.open("r") as f:
        file_data += f.read()

    assert file_data == snapshot_sds_stub


@pytest.mark.parametrize(
    ("name", "expected_result", "is_class_name"),
    [
        ("", "", False),
        ("_", "_", False),
        ("__get_function_name__", "getFunctionName", False),
        ("__get_function_name", "getFunctionName", False),
        ("get_function_name__", "getFunctionName", False),
        ("__getFunction_name__", "getFunctionName", False),
        ("__get__function___name__", "getFunctionName", False),
        ("__get_funCtion_NamE__", "getFunCtionNamE", False),
        ("getFunctionName", "getFunctionName", False),
        ("a_a_A_aAAaA_1_1_2_aAa", "aAAAAAaA112AAa", False),
        ("some_class_name", "SomeClassName", True),
    ],
)
def test_convert_snake_to_camel_case(name: str, expected_result: str, is_class_name: bool) -> None:
    assert _convert_snake_to_camel_case(name, is_class_name=is_class_name) == expected_result
