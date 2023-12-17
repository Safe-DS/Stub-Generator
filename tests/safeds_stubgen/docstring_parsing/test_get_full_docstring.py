from __future__ import annotations

from pathlib import Path

import pytest
from mypy import nodes

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._get_api import _get_mypy_asts, _get_mypy_build

# noinspection PyProtectedMember
from safeds_stubgen.docstring_parsing._helpers import get_full_docstring

from tests.safeds_stubgen._helpers import get_specific_mypy_node

# Setup
_test_dir = Path(__file__).parent.parent.parent
files = [str(Path(_test_dir / "data" / "docstring_parser_package" / "full_docstring.py"))]
mypy_build = _get_mypy_build(files)
mypy_file = _get_mypy_asts(
    build_result=mypy_build,
    files=files,
    package_paths=[],
    root=Path(_test_dir / "data" / "docstring_parser_package"),
)[0]


@pytest.mark.parametrize(
    ("name", "expected_docstring"),
    [
        (
            "ClassWithMultiLineDocumentation",
            "Lorem ipsum.\n\nDolor sit amet.",
        ),
        (
            "ClassWithSingleLineDocumentation",
            "Lorem ipsum.",
        ),
        (
            "ClassWithoutDocumentation",
            "",
        ),
        (
            "function_with_multi_line_documentation",
            "Lorem ipsum.\n\nDolor sit amet.",
        ),
        (
            "function_with_single_line_documentation",
            "Lorem ipsum.",
        ),
        (
            "function_without_documentation",
            "",
        ),
    ],
    ids=[
        "class with multi line documentation",
        "class with single line documentation",
        "class without documentation",
        "function with multi line documentation",
        "function with single line documentation",
        "function without documentation",
    ],
)
def test_get_full_docstring(name: str, expected_docstring: str) -> None:
    node = get_specific_mypy_node(mypy_file, name)

    assert isinstance(node, nodes.ClassDef | nodes.FuncDef)
    assert get_full_docstring(node) == expected_docstring
