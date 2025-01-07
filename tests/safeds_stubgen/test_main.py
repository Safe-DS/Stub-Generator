import json
import sys
from pathlib import Path

import pytest
from safeds_stubgen.main import main
from syrupy.assertion import SnapshotAssertion

_lib_dir = Path(__file__).parent.parent.parent
_test_package_name = "main_package"
_test_package_name_boundaries_valid_values_numpydoc = "boundary_enum_package_numpydoc"
_test_package_name_boundaries_valid_values_googledoc = "boundary_enum_package_googledoc"
_test_package_name_boundaries_valid_values_restdoc = "boundary_enum_package_restdoc"
_test_package_purity = "purity_package"
_main_dir = Path(_lib_dir / "src" / "main.py")
_test_package_dir = Path(_lib_dir / "tests" / "data" / _test_package_name)
_out_dir = Path(_lib_dir / "tests" / "data" / "out")

_astroid_evaluation_dir = Path(_lib_dir / "tests" / "data" / "astroid")
_safeds_v19_evaluation_dir = Path(_lib_dir / "tests" / "data" / "safeds")

@pytest.mark.parametrize(
    ("test_package_name", "out_file_dir", "docstyle"),
    [
        (
            _test_package_name,
            Path(_out_dir / f"{_test_package_name}__api.json"),
            "plaintext"
        ),
        (
            _test_package_name_boundaries_valid_values_numpydoc,
            Path(_out_dir / f"{_test_package_name_boundaries_valid_values_numpydoc}__api.json"),
            "numpydoc"
        ),
        (
            _test_package_name_boundaries_valid_values_googledoc,
            Path(_out_dir / f"{_test_package_name_boundaries_valid_values_googledoc}__api.json"),
            "google"
        ),
        (
            _test_package_name_boundaries_valid_values_restdoc,
            Path(_out_dir / f"{_test_package_name_boundaries_valid_values_restdoc}__api.json"),
            "rest"
        ),
        (
            _test_package_purity,
            Path(_out_dir / f"{_test_package_purity}__api_purity.json"),
            "numpydoc"
        ),
    ],
    ids=[
        "plaintext",
        "numpydoc - boundary - enum",
        "googledoc - boundary - enum",
        "restdoc - boundary - enum",
        "purity"
    ],
)
def test_main(
    test_package_name: str,
    out_file_dir: Path,
    docstyle: str,
    snapshot: SnapshotAssertion
) -> None:
    # Overwrite system arguments

    sys.argv = [
        str(_main_dir),
        "-v",
        "-s",
        str(Path(_lib_dir / "tests" / "data" / test_package_name)),
        "-o",
        str(_out_dir),
        "-tr",
        "--docstyle",
        docstyle,
        "-nc",
    ]

    main()

    with Path.open(out_file_dir, encoding="utf-8") as f:
        json_data = json.load(f)

    assert json_data == snapshot

@pytest.mark.parametrize(
    ("package_path", "out_file_dir", "docstyle"),
    [
        (
            _astroid_evaluation_dir,
            Path(_out_dir / f"{'astroid'}__api_purity.json"),
            "numpydoc"
        ),
        (
            _safeds_v19_evaluation_dir,
            Path(_out_dir / f"{'safedsV19'}__api_purity.json"),
            "numpydoc"
        ),

    ],
    ids=[
        "astroid",
        "safedsV19"
    ],
)
def test_evaluation(
    package_path: Path,
    out_file_dir: Path,
    docstyle: str,
    snapshot: SnapshotAssertion
) -> None:
    # Overwrite system arguments

    sys.argv = [
        str(_main_dir),
        "-v",
        "-s",
        str(package_path),
        "-o",
        str(_out_dir),
        "-tr",
        "--docstyle",
        docstyle,
        "-nc",
        "--evaluate_purity",
        # "--evaluate_api",
        "-old"
    ]

    main()
    assert True

def test_main_empty() -> None:
    # Overwrite system arguments
    sys.argv = [
        str(_main_dir),
        "-v",
        "-s",
        str(_test_package_dir),
        "-o",
        str(_out_dir),
        "--docstyle",
        "plaintext",
    ]

    with pytest.raises(ValueError, match="No files found to analyse."):
        main()
