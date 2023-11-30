import json
import sys
from pathlib import Path

import pytest
from safeds_stubgen.main import main
from syrupy import SnapshotAssertion

_lib_dir = Path(__file__).parent.parent.parent
_test_package_name = "main_package"
_main_dir = Path(_lib_dir / "src" / "main.py")
_test_package_dir = Path(_lib_dir / "tests" / "data" / _test_package_name)
_out_dir = Path(_lib_dir / "tests" / "data" / "out")
_out_file_dir = Path(_out_dir / f"{_test_package_name}__api.json")


def test_main(snapshot: SnapshotAssertion) -> None:
    # Overwrite system arguments
    sys.argv = [
        str(_main_dir),
        "-v",
        "-p",
        str(_test_package_name),
        "-s",
        str(_test_package_dir),
        "-o",
        str(_out_dir),
        "-tr",
        "--docstyle",
        "plaintext",
        "-ci",
    ]

    main()

    with Path.open(_out_file_dir) as f:
        json_data = json.load(f)

    assert json_data == snapshot


def test_main_empty() -> None:
    # Overwrite system arguments
    sys.argv = [
        str(_main_dir),
        "-v",
        "-p",
        str(_test_package_name),
        "-s",
        str(_test_package_dir),
        "-o",
        str(_out_dir),
        "--docstyle",
        "plaintext",
    ]

    with pytest.raises(ValueError, match="No files found to analyse."):
        main()
