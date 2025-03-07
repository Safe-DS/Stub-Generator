from __future__ import annotations

from pathlib import Path

import pytest
from mypy import nodes

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._get_api import _get_mypy_asts, _get_mypy_build
from safeds_stubgen.docstring_parsing import (
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    PlaintextDocstringParser,
)

# noinspection PyProtectedMember
from safeds_stubgen.docstring_parsing._docstring import AttributeDocstring, ResultDocstring
from tests.safeds_stubgen._helpers import get_specific_mypy_node

# Setup
_test_dir = Path(__file__).parent.parent.parent
files = [str(Path(_test_dir / "data" / "docstring_parser_package" / "plaintext.py"))]
mypy_build = _get_mypy_build(files)
mypy_file = _get_mypy_asts(
    build_result=mypy_build,
    files=files,
    package_paths=[],
)[0]


@pytest.fixture
def plaintext_docstring_parser() -> PlaintextDocstringParser:
    return PlaintextDocstringParser()


# ############################## Class Documentation ############################## #
@pytest.mark.parametrize(
    ("class_name", "expected_class_documentation"),
    [
        (
            "ClassWithDocumentation",
            ClassDocstring(
                description="ClassWithDocumentation.\n\nDolor sit amet.",
                full_docstring="ClassWithDocumentation.\n\nDolor sit amet.",
            ),
        ),
        (
            "ClassWithoutDocumentation",
            ClassDocstring(
                description="",
                full_docstring="",
            ),
        ),
    ],
    ids=[
        "class with documentation",
        "class without documentation",
    ],
)
def test_get_class_documentation(
    plaintext_docstring_parser: PlaintextDocstringParser,
    class_name: str,
    expected_class_documentation: ClassDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)

    assert isinstance(node, nodes.ClassDef)
    assert plaintext_docstring_parser.get_class_documentation(node) == expected_class_documentation


# ############################## Function Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_function_documentation"),
    [
        (
            "function_with_documentation",
            FunctionDocstring(
                description="function_with_documentation.\n\nDolor sit amet.",
                full_docstring="function_with_documentation.\n\nDolor sit amet.",
            ),
        ),
        (
            "function_without_documentation",
            FunctionDocstring(description=""),
        ),
    ],
    ids=[
        "function with documentation",
        "function without documentation",
    ],
)
def test_get_function_documentation(
    plaintext_docstring_parser: PlaintextDocstringParser,
    function_name: str,
    expected_function_documentation: FunctionDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)

    assert isinstance(node, nodes.FuncDef)
    assert plaintext_docstring_parser.get_function_documentation(node) == expected_function_documentation


# ############################## Parameter Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "parameter_name", "expected_parameter_documentation"),
    [
        (
            "function_with_documentation",
            "p",
            ParameterDocstring(),
        ),
        (
            "function_without_documentation",
            "p",
            ParameterDocstring(),
        ),
    ],
    ids=[
        "function with documentation",
        "function without documentation",
    ],
)
def test_get_parameter_documentation(
    plaintext_docstring_parser: PlaintextDocstringParser,
    function_name: str,
    parameter_name: str,
    expected_parameter_documentation: ParameterDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)
    assert (
        plaintext_docstring_parser.get_parameter_documentation(
            function_qname=node.fullname,
            parameter_name=parameter_name,
            parent_class_qname=".".join(node.fullname.split(".")[:-1]),
        )
        == expected_parameter_documentation
    )


# ############################## Attribute Documentation ############################## #
@pytest.mark.parametrize(
    ("class_name", "attribute_name", "expected_attribute_documentation"),
    [
        (
            "ClassWithDocumentation",
            "p",
            AttributeDocstring(),
        ),
        (
            "ClassWithoutDocumentation",
            "p",
            AttributeDocstring(),
        ),
    ],
    ids=[
        "function with documentation",
        "function without documentation",
    ],
)
def test_get_attribute_documentation(
    plaintext_docstring_parser: PlaintextDocstringParser,
    class_name: str,
    attribute_name: str,
    expected_attribute_documentation: ParameterDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)
    assert isinstance(node, nodes.ClassDef)
    attribute_documentation = plaintext_docstring_parser.get_attribute_documentation(
        parent_class_qname=node.fullname,
        attribute_name=attribute_name,
    )

    assert attribute_documentation == expected_attribute_documentation


# ############################## Result Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_result_documentation"),
    [
        (
            "function_with_documentation",
            [],
        ),
        (
            "function_without_documentation",
            [],
        ),
    ],
    ids=[
        "class with documentation",
        "class without documentation",
    ],
)
def test_get_result_documentation(
    plaintext_docstring_parser: PlaintextDocstringParser,
    function_name: str,
    expected_result_documentation: list[ResultDocstring],
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)
    assert plaintext_docstring_parser.get_result_documentation(node.fullname) == expected_result_documentation
