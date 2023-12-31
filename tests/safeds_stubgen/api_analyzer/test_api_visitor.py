from __future__ import annotations

import pytest

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._api import API

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._ast_visitor import MyPyAstVisitor
from safeds_stubgen.docstring_parsing import PlaintextDocstringParser


@pytest.mark.parametrize(
    ("qname", "expected_id", "package_name"),
    [
        (
            "some.path.package_name.src.data",
            "package_name/src/data",
            "package_name",
        ),
        (
            "some.path.package_name",
            "package_name",
            "package_name",
        ),
        (
            "some.path.no_package",
            "",
            "package_name",
        ),
        (
            "",
            "",
            "package_name",
        ),
        (
            "some.package_name.package_name.src.data",
            "package_name/package_name/src/data",
            "package_name",
        ),
        (
            "some.path.package_name.src.package_name",
            "package_name/src/package_name",
            "package_name",
        ),
        (
            "some.package_name.package_name.src.package_name",
            "package_name/package_name/src/package_name",
            "package_name",
        ),
    ],
    ids=[
        "With unneeded data",
        "Without unneeded data",
        "No package name in qname",
        "No qname",
        "Package name twice in qname 1",
        "Package name twice in qname 2",
        "Package name twice in qname 3",
    ],
)
def test__create_module_id(qname: str, expected_id: str, package_name: str) -> None:
    api = API(
        distribution="dist_name",
        package=package_name,
        version="1.3",
    )

    visitor = MyPyAstVisitor(PlaintextDocstringParser(), api)
    if not expected_id:
        with pytest.raises(ValueError, match="Package name could not be found in the qualified name of the module."):
            visitor._create_module_id(qname)
    else:
        module_id = visitor._create_module_id(qname)
        assert module_id == expected_id
