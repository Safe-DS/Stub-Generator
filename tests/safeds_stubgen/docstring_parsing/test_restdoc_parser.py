from __future__ import annotations

from pathlib import Path

import pytest
from mypy import nodes
from safeds_stubgen.api_analyzer import Class, ParameterAssignment, get_classdef_definitions

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._get_api import _get_mypy_ast
from safeds_stubgen.docstring_parsing import (
    ClassDocstring,
    FunctionDocstring,
    ParameterDocstring,
    RestDocParser,
    ResultDocstring,
)

from tests.safeds_stubgen._helpers import _get_specific_mypy_node

# Setup
_test_dir = Path(__file__).parent.parent.parent
mypy_file = _get_mypy_ast(
    files=[
        str(Path(_test_dir / "data" / "test_docstring_parser_package" / "test_restdoc.py")),
    ],
    package_paths=[],
    root=Path(_test_dir / "data" / "test_docstring_parser_package"),
)[0]


@pytest.fixture()
def restdoc_parser() -> RestDocParser:
    return RestDocParser()


# ############################## Class Documentation ############################## #
@pytest.mark.parametrize(
    ("class_name", "expected_class_documentation"),
    [
        (
            "ClassWithDocumentation",
            ClassDocstring(
                description="Lorem ipsum. Code::\n\npass\n\nDolor sit amet.",
                full_docstring="Lorem ipsum. Code::\n\n    pass\n\nDolor sit amet.",
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
    restdoc_parser: RestDocParser,
    class_name: str,
    expected_class_documentation: ClassDocstring,
) -> None:
    node = _get_specific_mypy_node(mypy_file, class_name)

    assert isinstance(node, nodes.ClassDef)
    assert restdoc_parser.get_class_documentation(node) == expected_class_documentation


# ############################## Function Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_function_documentation"),
    [
        (
            "function_with_documentation",
            FunctionDocstring(
                description="Lorem ipsum. Code::\n\npass\n\nDolor sit amet.",
                full_docstring="Lorem ipsum. Code::\n\n    pass\n\nDolor sit amet.",
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
    restdoc_parser: RestDocParser,
    function_name: str,
    expected_function_documentation: FunctionDocstring,
) -> None:
    node = _get_specific_mypy_node(mypy_file, function_name)

    assert isinstance(node, nodes.FuncDef)
    assert restdoc_parser.get_function_documentation(node) == expected_function_documentation


# ############################## Parameter Documentation ############################## #
@pytest.mark.parametrize(
    ("name", "is_class", "parameter_name", "parameter_assigned_by", "expected_parameter_documentation"),
    [
        (
            "ClassWithParameters",
            True,
            "p",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="1",
                description="foo defaults to 1",
            ),
        ),
        (
            "ClassWithParameters",
            True,
            "missing",
            ParameterAssignment.POSITION_OR_NAME,
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
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="",
                default_value="",
                description="no type and no default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "type_no_default",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="",
                description="type but no default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="2",
                description="foo that defaults to 2",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "*args",
            ParameterAssignment.POSITIONAL_VARARG,
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
            ParameterAssignment.NAMED_VARARG,
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
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(type="", default_value="", description=""),
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
    restdoc_parser: RestDocParser,
    name: str,
    is_class: bool,
    parameter_name: str,
    parameter_assigned_by: ParameterAssignment,
    expected_parameter_documentation: ParameterDocstring,
) -> None:
    parent = None
    node = _get_specific_mypy_node(mypy_file, name)
    if is_class:
        assert isinstance(node, nodes.ClassDef)
        class_doc = restdoc_parser.get_class_documentation(node)
        parent = Class(
            id=node.fullname,
            name=node.name,
            superclasses=[],
            is_public=True,
            docstring=class_doc
        )
    else:
        assert isinstance(node, nodes.FuncDef)

    # Find the constructor
    if isinstance(node, nodes.ClassDef):
        for definition in get_classdef_definitions(node):
            if isinstance(definition, nodes.FuncDef) and definition.name == "__init__":
                node = definition
                break
        assert isinstance(node, nodes.FuncDef)

    parameter_documentation = restdoc_parser.get_parameter_documentation(
        function_node=node,
        parameter_name=parameter_name,
        parameter_assigned_by=parameter_assigned_by,
        parent_class=parent
    )

    assert (
        parameter_documentation
        == expected_parameter_documentation
    )


# ############################## Result Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_result_documentation"),
    [
        (
            "function_with_return_value_and_type",
            ResultDocstring(type="bool", description="return value"),
        ),
        (
            "function_with_return_value_no_type",
            ResultDocstring(type="", description="return value"),
        ),
        (
            "function_without_return_value",
            ResultDocstring(type="", description="")
        ),
    ],
    ids=[
        "existing return value and type",
        "existing return value no type",
        "function without return value"
    ],
)
def test_get_result_documentation(
    restdoc_parser: RestDocParser,
    function_name: str,
    expected_result_documentation: ResultDocstring,
) -> None:
    node = _get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)

    fake_parent = Class(id="", name="", superclasses=[], is_public=True, docstring=ClassDocstring())
    assert (
        restdoc_parser.get_result_documentation(node, fake_parent)
        == expected_result_documentation
    )
