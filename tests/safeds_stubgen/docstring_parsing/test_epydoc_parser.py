from __future__ import annotations

from pathlib import Path

import pytest
from mypy import nodes
from safeds_stubgen.api_analyzer import Class, ParameterAssignment, get_classdef_definitions

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._get_api import _get_mypy_build, _get_mypy_asts
from safeds_stubgen.docstring_parsing import (
    ClassDocstring,
    EpydocParser,
    FunctionDocstring,
    ParameterDocstring,
    ResultDocstring,
)

from tests.safeds_stubgen._helpers import get_specific_mypy_node

# Setup
_test_dir = Path(__file__).parent.parent.parent
files = [str(Path(_test_dir / "data" / "docstring_parser_package" / "epydoc.py"))]
mypy_build = _get_mypy_build(files)
mypy_file = _get_mypy_asts(
    build_result=mypy_build,
    files=files,
    package_paths=[],
    root=Path(_test_dir / "data" / "docstring_parser_package"),
)[0]


@pytest.fixture()
def epydoc_parser() -> EpydocParser:
    return EpydocParser()


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
    epydoc_parser: EpydocParser,
    class_name: str,
    expected_class_documentation: ClassDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)

    assert isinstance(node, nodes.ClassDef)
    assert epydoc_parser.get_class_documentation(node) == expected_class_documentation


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
    epydoc_parser: EpydocParser,
    function_name: str,
    expected_function_documentation: FunctionDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)

    assert isinstance(node, nodes.FuncDef)
    assert epydoc_parser.get_function_documentation(node) == expected_function_documentation


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
        "missing function parameter",
    ],
)
def test_get_parameter_documentation(
    epydoc_parser: EpydocParser,
    name: str,
    is_class: bool,
    parameter_name: str,
    parameter_assigned_by: ParameterAssignment,
    expected_parameter_documentation: ParameterDocstring,
) -> None:
    parent = None
    node = get_specific_mypy_node(mypy_file, name)
    if is_class:
        assert isinstance(node, nodes.ClassDef)
        class_doc = epydoc_parser.get_class_documentation(node)
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

    parameter_documentation = epydoc_parser.get_parameter_documentation(
        function_node=node,
        parameter_name=parameter_name,
        parameter_assigned_by=parameter_assigned_by,
        parent_class=parent,
    )

    assert parameter_documentation == expected_parameter_documentation


# ############################## Attribute Documentation ############################## #
# Todo Epydoc: Attribute handling not yet implemented in dosctring_parser library, thus the tests
#  also don't work yet and are therefore deactivated!
@pytest.mark.parametrize(
    ("class_name", "attribute_name", "expected_parameter_documentation"),
    [
        (
            "ClassWithAttributes",
            "p",
            ParameterDocstring(
                type="int",
                default_value="1",
                description="foo defaults to 1",
            ),
        ),
        (
            "ClassWithAttributesNoType",
            "p",
            ParameterDocstring(
                type="",
                default_value="1",
                description="foo defaults to 1",
            ),
        ),
    ],
    ids=[
        "existing class attributes",
        "existing class attributes no type",
    ],
)
def xtest_get_attribute_documentation(
    epydoc_parser: EpydocParser,
    class_name: str,
    attribute_name: str,
    expected_parameter_documentation: ParameterDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)
    assert isinstance(node, nodes.ClassDef)
    docstring = epydoc_parser.get_class_documentation(node)
    fake_class = Class(id="some_id", name="some_class", superclasses=[], is_public=True, docstring=docstring)

    attribute_documentation = epydoc_parser.get_attribute_documentation(
        parent_class=fake_class,
        attribute_name=attribute_name,
    )

    assert attribute_documentation == expected_parameter_documentation


# ############################## Result Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_result_documentation"),
    [
        (
            "function_with_result_value_and_type",
            ResultDocstring(type="float", description="return value"),
        ),
        (
            "function_with_result_value_no_type",
            ResultDocstring(type="", description="return value"),
        ),
        (
            "function_without_result_value",
            ResultDocstring(type="", description=""),
        ),
    ],
    ids=[
        "existing return value and type",
        "existing return value no type",
        "function without return value",
    ],
)
def test_get_result_documentation(
    epydoc_parser: EpydocParser,
    function_name: str,
    expected_result_documentation: ResultDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)
    assert epydoc_parser.get_result_documentation(node) == expected_result_documentation
