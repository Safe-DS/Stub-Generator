from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from safeds_stubgen.api_analyzer import TypeSourcePreference, get_api
from safeds_stubgen.docstring_parsing import DocstringStyle
from safeds_stubgen.stubs_generator import NamingConvention, StubsStringGenerator, create_stub_files, generate_stub_data

# noinspection PyProtectedMember
from safeds_stubgen.stubs_generator._generate_stubs import _convert_name_to_convention

if TYPE_CHECKING:
    from collections.abc import Generator

    from syrupy import SnapshotAssertion


# Setup - Run API to create stub files
_lib_dir = Path(__file__).parent.parent.parent
_test_package_name = "various_modules_package"
_test_package_dir = Path(_lib_dir / "data" / _test_package_name)
_out_dir = Path(_lib_dir / "data" / "out")
_out_dir_stubs = Path(_out_dir / "tests/data" / _test_package_name)

_docstring_package_name = "docstring_parser_package"
_docstring_package_dir = Path(_lib_dir / "data" / _docstring_package_name)

api = get_api(_test_package_dir, is_test_run=True)
stubs_generator = StubsStringGenerator(api=api, convert_identifiers=True)
stubs_data = generate_stub_data(stubs_generator=stubs_generator, out_path=_out_dir)


def test_file_creation() -> None:
    data_to_test: list[tuple[str, str]] = [
        ("/".join(stub_data[0].parts), stub_data[1]) for stub_data in stubs_data if "file_creation" in str(stub_data[0])
    ]
    data_to_test.sort(key=lambda x: x[1])

    expected_files: list[tuple[str, str]] = [
        ("tests/data/various_modules_package/file_creation/Lv1", "Lv1"),
        (
            "tests/data/various_modules_package/file_creation/ReexportedInAnotherPackageClass",
            "ReexportedInAnotherPackageClass",
        ),
        (
            "tests/data/various_modules_package/file_creation/ReexportedInAnotherPackageClass2",
            "ReexportedInAnotherPackageClass2",
        ),
        ("tests/data/various_modules_package/file_creation/module_1", "module_1"),
        ("tests/data/various_modules_package/file_creation/package_1/module_5", "module_5"),
        ("tests/data/various_modules_package/file_creation/public_reexported", "public_reexported"),
        ("tests/data/various_modules_package/file_creation", "reexported_from_another_package_3"),
        (
            "tests/data/various_modules_package/file_creation/reexported_in_another_package_function",
            "reexported_in_another_package_function",
        ),
        (
            "tests/data/various_modules_package/file_creation/reexported_in_another_package_function2",
            "reexported_in_another_package_function2",
        ),
    ]
    expected_files.sort(key=lambda x: x[1])

    assert len(data_to_test) == len(expected_files)
    for data_tuple, expected_tuple in zip(data_to_test, expected_files, strict=True):
        assert data_tuple[0].endswith(expected_tuple[0])
        assert data_tuple[1] == expected_tuple[1]


def test_file_creation_limited_stubs_outside_package(snapshot_sds_stub: SnapshotAssertion) -> None:
    create_stub_files(stubs_generator=stubs_generator, stubs_data=stubs_data, out_path=_out_dir)

    path = Path(_out_dir / "tests/data/main_package/another_path/another_module/another_module.sdsstub")
    assert path.is_file()

    with path.open("r", encoding="utf-8") as f:
        assert f.read() == snapshot_sds_stub


def stub_texts() -> Generator[str, None, None]:
    for stub_data in stubs_data:
        yield stub_data[2]


def _stub_ids() -> Generator[str, None, None]:
    for stub_data in stubs_data:
        yield stub_data[1]


@pytest.mark.parametrize("stub_text", stub_texts(), ids=_stub_ids())
class TestStubFileGeneration:
    def test_stub_creation(self, stub_text: str, snapshot_sds_stub: SnapshotAssertion) -> None:
        assert stub_text == snapshot_sds_stub


@pytest.mark.parametrize(
    ("name", "expected_result", "naming_convention", "is_class_name"),
    [
        ("", "", "Safe-DS", False),
        ("_", "_", "Safe-DS", False),
        ("__get_function_name__", "getFunctionName", NamingConvention.SAFE_DS, False),
        ("__get_function_name", "getFunctionName", NamingConvention.SAFE_DS, False),
        ("get_function_name__", "getFunctionName", NamingConvention.SAFE_DS, False),
        ("__getFunction_name__", "getFunctionName", NamingConvention.SAFE_DS, False),
        ("__get__function___name__", "getFunctionName", NamingConvention.SAFE_DS, False),
        ("__get_funCtion_NamE__", "getFunCtionNamE", NamingConvention.SAFE_DS, False),
        ("getFunctionName", "getFunctionName", NamingConvention.SAFE_DS, False),
        ("a_a_A_aAAaA_1_1_2_aAa", "aAAAAAaA112AAa", NamingConvention.SAFE_DS, False),
        ("some_class_name", "SomeClassName", NamingConvention.SAFE_DS, True),
        ("some_class_name", "some_class_name", NamingConvention.PYTHON, True),
        ("__get_function_name__", "__get_function_name__", NamingConvention.PYTHON, False),
    ],
)
def test_convert_name_to_convention(
    name: str,
    expected_result: str,
    naming_convention: NamingConvention,
    is_class_name: bool,
) -> None:
    assert (
        _convert_name_to_convention(name=name, naming_convention=naming_convention, is_class_name=is_class_name)
        == expected_result
    )


@pytest.mark.parametrize(
    ("filename", "docstring_style", "type_source_preference"),
    [
        ("full_docstring", DocstringStyle.PLAINTEXT, TypeSourcePreference.CODE),
        ("googledoc", DocstringStyle.GOOGLE, TypeSourcePreference.CODE),
        ("numpydoc", DocstringStyle.NUMPYDOC, TypeSourcePreference.CODE),
        ("plaintext", DocstringStyle.PLAINTEXT, TypeSourcePreference.CODE),
        ("restdoc", DocstringStyle.REST, TypeSourcePreference.CODE),
        ("docstring_vs_typehints", DocstringStyle.NUMPYDOC, TypeSourcePreference.CODE),
        ("docstring_vs_typehints", DocstringStyle.NUMPYDOC, TypeSourcePreference.DOCSTRING),
    ],
    ids=[
        "full_docstring-PLAINTEXT",
        "googledoc-GOOGLE",
        "numpydoc-NUMPYDOC",
        "plaintext-PLAINTEXT",
        "restdoc-REST",
        "docstring_vs_typehints-CODE",
        "docstring_vs_typehints-DOCSTRING",
    ],
)
def test_stub_docstring_creation(
    filename: str,
    docstring_style: DocstringStyle,
    type_source_preference: TypeSourcePreference,
    snapshot_sds_stub: SnapshotAssertion,
) -> None:
    docstring_api = get_api(
        root=_docstring_package_dir,
        docstring_style=docstring_style,
        is_test_run=True,
        type_source_preference=type_source_preference,
    )
    docstring_stubs_generator = StubsStringGenerator(api=docstring_api, convert_identifiers=True)
    docstring_stubs_data = generate_stub_data(stubs_generator=docstring_stubs_generator, out_path=_out_dir)

    for stub_text in docstring_stubs_data:
        if stub_text[1] == filename:
            assert stub_text[2] == snapshot_sds_stub
            return

    raise pytest.fail(f"Could not find data for '{filename}'.")
