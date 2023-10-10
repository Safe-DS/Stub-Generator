import json
import sys
from pathlib import Path

from safeds_stubgen.main import main

_lib_dir = Path(__file__).parent.parent.parent
_test_package_name = "test_package"
_main_dir = Path(_lib_dir / "src" / "main.py")
_test_package_dir = Path(_lib_dir / "tests" / "data" / _test_package_name)
_out_dir = Path(_lib_dir / "tests" / "data" / "out")
_out_file_dir = Path(_out_dir / f"{_test_package_name}__api.json")


def test_main(snapshot):
    sys_args = [
        _main_dir, "-p", str(_test_package_name), "-s", str(_test_package_dir), "-o", str(_out_dir), "-tr", "True"
    ]
    sys.argv = sys_args

    main()

    with Path.open(_out_file_dir) as f:
        json_data = json.load(f)

    assert json_data == snapshot
