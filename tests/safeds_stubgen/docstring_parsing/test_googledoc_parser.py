from __future__ import annotations

from pathlib import Path

import pytest
from griffe.enumerations import Parser
from mypy import nodes
from safeds_stubgen.api_analyzer import Class, get_classdef_definitions

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._get_api import _get_mypy_asts, _get_mypy_build
from safeds_stubgen.docstring_parsing import (
    ClassDocstring,
    DocstringParser,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)

# noinspection PyProtectedMember
from safeds_stubgen.docstring_parsing._docstring import AttributeDocstring

from tests.safeds_stubgen._helpers import get_specific_mypy_node

# Setup
_test_dir = Path(__file__).parent.parent.parent
files = [str(Path(_test_dir / "data" / "docstring_parser_package" / "googledoc.py"))]
mypy_build = _get_mypy_build(files)
mypy_file = _get_mypy_asts(
    build_result=mypy_build,
    files=files,
    package_paths=[],
)[0]


@pytest.fixture()
def googlestyledoc_parser() -> DocstringParser:
    return DocstringParser(Parser.google, _test_dir)


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
    googlestyledoc_parser: DocstringParser,
    class_name: str,
    expected_class_documentation: ClassDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)

    assert isinstance(node, nodes.ClassDef)
    assert googlestyledoc_parser.get_class_documentation(node) == expected_class_documentation


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
    googlestyledoc_parser: DocstringParser,
    function_name: str,
    expected_function_documentation: FunctionDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)

    assert isinstance(node, nodes.FuncDef)
    assert googlestyledoc_parser.get_function_documentation(node) == expected_function_documentation


# ############################## Parameter Documentation ############################## #
@pytest.mark.parametrize(
    ("name", "is_class", "parameter_name", "expected_parameter_documentation"),
    [
        (
            "ClassWithParameters",
            True,
            "p",
            ParameterDocstring(
                type="int",
                default_value="1",
                description="foo. Defaults to 1.",
            ),
        ),
        (
            "ClassWithParameters",
            True,
            "missing",
            ParameterDocstring(
                type="",
                default_value="",
                description="",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "no_type_no_default",
            ParameterDocstring(
                type="",
                default_value="",
                description="no type and no default.",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "type_no_default",
            ParameterDocstring(
                type="int",
                default_value="",
                description="type but no default.",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default",
            ParameterDocstring(
                type="int",
                default_value="2",
                description="foo. Defaults to 2.",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "*args",
            ParameterDocstring(
                type="int",
                default_value="",
                description="foo: *args",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "**kwargs",
            ParameterDocstring(
                type="int",
                default_value="",
                description="foo: **kwargs",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "missing",
            ParameterDocstring(type="", default_value="", description=""),
        ),
        (
            "function_with_attributes_and_parameters",
            False,
            "q",
            ParameterDocstring(
                type="int",
                default_value="2",
                description="foo. Defaults to 2.",
            ),
        ),
        (
            "function_with_attributes_and_parameters",
            False,
            "p",
            ParameterDocstring(
                type="",
                default_value="",
                description="",
            ),
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
        "function with attributes and parameters existing parameter",
        "function with attributes and parameters missing parameter",
    ],
)
def test_get_parameter_documentation(
    googlestyledoc_parser: DocstringParser,
    name: str,
    is_class: bool,
    parameter_name: str,
    expected_parameter_documentation: ParameterDocstring,
) -> None:
    parent = None
    node = get_specific_mypy_node(mypy_file, name)
    if is_class:
        assert isinstance(node, nodes.ClassDef)
        class_doc = googlestyledoc_parser.get_class_documentation(node)
        parent = Class(id=node.fullname, name=node.name, superclasses=[], is_public=True, docstring=class_doc)
    else:
        assert isinstance(node, nodes.FuncDef)

    # Find the constructor
    if isinstance(node, nodes.ClassDef):
        for definition in get_classdef_definitions(node):
            if isinstance(definition, nodes.FuncDef) and definition.name == "__init__":
                node = definition
                break
        assert isinstance(node, nodes.FuncDef)

    parameter_documentation = googlestyledoc_parser.get_parameter_documentation(
        function_node=node,
        parameter_name=parameter_name,
        parent_class=parent,
    )

    assert parameter_documentation == expected_parameter_documentation


# ############################## Attribute Documentation ############################## #
@pytest.mark.parametrize(
    ("class_name", "attribute_name", "expected_attribute_documentation"),
    [
        (
            "ClassWithAttributes",
            "p",
            AttributeDocstring(
                type="int",
                description="foo. Defaults to 1.",
            ),
        ),
        (
            "ClassWithAttributes",
            "missing",
            AttributeDocstring(
                type="",
                description="",
            ),
        ),
    ],
    ids=[
        "existing class attribute",
        "missing class attribute",
    ],
)
def test_get_attribute_documentation(
    googlestyledoc_parser: DocstringParser,
    class_name: str,
    attribute_name: str,
    expected_attribute_documentation: AttributeDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)
    assert isinstance(node, nodes.ClassDef)
    attribute_documentation = googlestyledoc_parser.get_attribute_documentation(
        parent_class_qname=node.fullname,
        attribute_name=attribute_name,
    )

    assert attribute_documentation == expected_attribute_documentation


# ############################## Result Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_result_documentation"),
    [
        (
            "function_with_return_value_and_type",
            ResultDocstring(type="bool", description="this will be the return value."),
        ),
        (
            "function_with_return_value_no_type",
            ResultDocstring(type="", description="None"),
        ),
        ("function_without_return_value", ResultDocstring(type="", description="")),
    ],
    ids=["existing return value and type", "existing return value no description", "function without return value"],
)
def test_get_result_documentation(
    googlestyledoc_parser: DocstringParser,
    function_name: str,
    expected_result_documentation: ResultDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)
    assert googlestyledoc_parser.get_result_documentation(node.fullname) == expected_result_documentation
