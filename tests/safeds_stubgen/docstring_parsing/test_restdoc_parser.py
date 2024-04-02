from __future__ import annotations

from pathlib import Path

import pytest
from griffe.enumerations import Parser
from mypy import nodes
from safeds_stubgen.api_analyzer import NamedType, get_classdef_definitions

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._get_api import _get_mypy_asts, _get_mypy_build
from safeds_stubgen.docstring_parsing import (
    ClassDocstring,
    DocstringParser,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)

from tests.safeds_stubgen._helpers import get_specific_mypy_node

# Setup
_test_dir = Path(__file__).parent.parent.parent
files = [str(Path(_test_dir / "data" / "docstring_parser_package" / "restdoc.py"))]
mypy_build = _get_mypy_build(files)
mypy_file = _get_mypy_asts(
    build_result=mypy_build,
    files=files,
    package_paths=[],
)[0]


@pytest.fixture()
def restdoc_parser() -> DocstringParser:
    return DocstringParser(Parser.sphinx, _test_dir)


# ############################## Class Documentation ############################## #
@pytest.mark.parametrize(
    ("class_name", "expected_class_documentation"),
    [
        (
            "ClassWithDocumentation",
            ClassDocstring(
                description="ClassWithDocumentation. Code::\n\n    pass\n\nDolor sit amet.",
                full_docstring="ClassWithDocumentation. Code::\n\n    pass\n\nDolor sit amet.",
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
    restdoc_parser: DocstringParser,
    class_name: str,
    expected_class_documentation: ClassDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)

    assert isinstance(node, nodes.ClassDef)
    assert restdoc_parser.get_class_documentation(node) == expected_class_documentation


# ############################## Function Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_function_documentation"),
    [
        (
            "function_with_documentation",
            FunctionDocstring(
                description="function_with_documentation. Code::\n\n    pass\n\nDolor sit amet.",
                full_docstring="function_with_documentation. Code::\n\n    pass\n\nDolor sit amet.",
            ),
        ),
        (
            "function_without_documentation",
            FunctionDocstring(
                description="",
                full_docstring="",
            ),
        ),
    ],
    ids=[
        "function with documentation",
        "function without documentation",
    ],
)
def test_get_function_documentation(
    restdoc_parser: DocstringParser,
    function_name: str,
    expected_function_documentation: FunctionDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)

    assert isinstance(node, nodes.FuncDef)
    assert restdoc_parser.get_function_documentation(node) == expected_function_documentation


# ############################## Parameter Documentation ############################## #
@pytest.mark.parametrize(
    ("name", "is_class", "parameter_name", "expected_parameter_documentation"),
    [
        (
            "ClassWithParameters",
            True,
            "p",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="1",
                description="foo defaults to 1",
            ),
        ),
        (
            "ClassWithParameters",
            True,
            "missing",
            ParameterDocstring(
                type=None,
                default_value="",
                description="",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "no_type_no_default",
            ParameterDocstring(
                type=None,
                default_value="",
                description="no type and no default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "type_no_default",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="",
                description="type but no default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="2",
                description="foo that defaults to 2",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "*args",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="()",
                description="foo: *args",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "**kwargs",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="{}",
                description="foo: **kwargs",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "missing",
            ParameterDocstring(type=None, default_value="", description=""),
        ),
    ],
    ids=[
        "existing class parameter",
        "missing class parameter",
        "function parameter with no type and no default",
        "function parameter with type and no default",
        "function parameter with default",
        "function parameter with positional vararg",
        "function parameter with named vararg",
        "missing function parameter",
    ],
)
def test_get_parameter_documentation(
    restdoc_parser: DocstringParser,
    name: str,
    is_class: bool,
    parameter_name: str,
    expected_parameter_documentation: ParameterDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, name)
    if is_class:
        assert isinstance(node, nodes.ClassDef)
        parent_qname = node.fullname
    else:
        assert isinstance(node, nodes.FuncDef)
        parent_qname = ""

    # Find the constructor
    if isinstance(node, nodes.ClassDef):
        for definition in get_classdef_definitions(node):
            if isinstance(definition, nodes.FuncDef) and definition.name == "__init__":
                node = definition
                break
        assert isinstance(node, nodes.FuncDef)

    parameter_documentation = restdoc_parser.get_parameter_documentation(
        function_qname=node.fullname,
        parameter_name=parameter_name,
        parent_class_qname=parent_qname,
    )

    assert parameter_documentation == expected_parameter_documentation


# ############################## Result Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_result_documentation"),
    [
        (
            "function_with_return_value_and_type",
            ResultDocstring(type=NamedType(name="bool", qname="builtins.bool"), description="return value"),
        ),
        (
            "function_with_return_value_no_type",
            ResultDocstring(type=NamedType(name="None", qname="builtins.None"), description="return value"),
        ),
        ("function_without_return_value", ResultDocstring(type=None, description="")),
    ],
    ids=["existing return value and type", "existing return value no type", "function without return value"],
)
def test_get_result_documentation(
    restdoc_parser: DocstringParser,
    function_name: str,
    expected_result_documentation: ResultDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)
    assert restdoc_parser.get_result_documentation(node.fullname) == expected_result_documentation
