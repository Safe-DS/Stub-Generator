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
_test_package_name = "test_stub_generation"
_test_package_dir = Path(_lib_dir / "data" / _test_package_name)
_out_dir = Path(_lib_dir / "data" / "out")
_out_dir_stubs = Path(_out_dir / _test_package_name)

api = get_api(_test_package_name, _test_package_dir, is_test_run=True)
generate_stubs(api, _out_dir)


# Utilites
def _assert_file_creation_recursive(python_path: Path, stub_path: Path) -> None:
    assert python_path.is_dir()
    assert stub_path.is_dir()

    python_files: list[Path] = list(python_path.iterdir())
    stub_files: list[Path] = list(stub_path.iterdir())

    # Remove __init__ files and private files without public reexported content.
    # We reexport public content from _module_3 and _module_6, not from _module_2 and _module_4.
    for i, item in enumerate(python_files):
        if item.is_file() and item.stem in {"__init__", "_module_2", "_module_4"}:
            python_files.pop(i)

    assert len(python_files) == len(stub_files)

    for py_item, stub_item in zip(python_files, stub_files, strict=True):
        if py_item.is_file():
            assert stub_item.is_dir()
            stub_files = list(stub_item.iterdir())
            assert len(stub_files) == 1
            assert stub_files[0].stem == py_item.stem
        else:
            _assert_file_creation_recursive(py_item, stub_item)


def assert_stubs_snapshot(filename: str, snapshot: SnapshotAssertion) -> None:
    stubs_file = Path(_out_dir_stubs / filename / f"{filename}.sdsstub")
    with stubs_file.open("r") as f:
        assert f.read() == snapshot


# ############################## Tests ############################## #
def test_file_creation() -> None:
    _assert_file_creation_recursive(
        python_path=Path(_test_package_dir / "test_file_creation"),
        stub_path=Path(_out_dir_stubs / "test_file_creation")
    )


# Todo Check snapshot
def test_class_creation(snapshot: SnapshotAssertion) -> None:
    assert_stubs_snapshot("class_module", snapshot)


# Todo Check snapshot
def test_class_attribute_creation(snapshot: SnapshotAssertion) -> None:
    assert_stubs_snapshot("attribute_module", snapshot)


# Todo Check snapshot
def test_function_creation(snapshot: SnapshotAssertion) -> None:
    assert_stubs_snapshot("function_module", snapshot)


# Todo Check snapshot
def test_enum_creation(snapshot: SnapshotAssertion) -> None:
    assert_stubs_snapshot("enum_module", snapshot)


# Todo Check snapshot
def test_import_creation(snapshot: SnapshotAssertion) -> None:
    assert_stubs_snapshot("import_module", snapshot)


# Todo Check snapshot
def test_type_inference(snapshot: SnapshotAssertion) -> None:
    assert_stubs_snapshot("infer_types_module", snapshot)


# Todo Check snapshot
def test_variance_creation(snapshot: SnapshotAssertion) -> None:
    assert_stubs_snapshot("variance_module", snapshot)


# Todo
def test_docstring_creation() -> None: ...


@pytest.mark.parametrize(
    ("name", "expected_result"),
    [
        (
            "",
            "",
        ),
        (
            "_",
            "_",
        ),
        (
            "__get_function_name__",
            "getFunctionName",
        ),
        (
            "__get_function_name",
            "getFunctionName",
        ),
        (
            "get_function_name__",
            "getFunctionName",
        ),
        (
            "__getFunction_name__",
            "getFunctionName",
        ),
        (
            "__get__function___name__",
            "getFunctionName",
        ),
        (
            "__get_funCtion_NamE__",
            "getFunCtionNamE",
        ),
        (
            "getFunctionName",
            "getFunctionName",
        ),
        (
            "a_a_A_aAAaA_1_1_2_aAa",
            "aAAAAAaA112AAa",
        ),
    ],
)
def test_convert_snake_to_camel_case(name: str, expected_result: str) -> None:
    assert _convert_snake_to_camel_case(name) == expected_result
