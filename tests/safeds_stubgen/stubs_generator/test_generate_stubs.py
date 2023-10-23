from __future__ import annotations

from pathlib import Path

from safeds_stubgen.api_analyzer import get_api
from safeds_stubgen.stubs_generator import StubsGenerator

# Setup - Run API to create stub files
_lib_dir = Path(__file__).parent.parent.parent
_test_package_name = "test_package"
_test_package_dir = Path(_lib_dir / "tests" / "data" / _test_package_name)
_out_dir = Path(_lib_dir / "tests" / "data" / "out")
_out_dir_stubs = Path(_out_dir / _test_package_name)

api = get_api(_test_package_name, _test_package_dir, is_test_run=True)
stubs_generator = StubsGenerator(api, _out_dir)
stubs_generator.generate_stubs()
