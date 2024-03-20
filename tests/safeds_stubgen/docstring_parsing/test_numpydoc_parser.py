from __future__ import annotations

from pathlib import Path

import pytest
from mypy import nodes
from safeds_stubgen.api_analyzer import Class, ParameterAssignment, get_classdef_definitions

# noinspection PyProtectedMember
from safeds_stubgen.api_analyzer._get_api import _get_mypy_asts, _get_mypy_build
from safeds_stubgen.docstring_parsing import (
    ClassDocstring,
    FunctionDocstring,
    NumpyDocParser,
    ParameterDocstring,
    ResultDocstring,
)

# noinspection PyProtectedMember
from safeds_stubgen.docstring_parsing._docstring import AttributeDocstring

from tests.safeds_stubgen._helpers import get_specific_mypy_node

# Setup
_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "docstring_parser_package"
files = [str(Path(_test_dir / "data" / "docstring_parser_package" / "numpydoc.py"))]
mypy_build = _get_mypy_build(files)
mypy_file = _get_mypy_asts(
    build_result=mypy_build,
    files=files,
    package_paths=[],
)[0]


@pytest.fixture()
def numpydoc_parser() -> NumpyDocParser:
    return NumpyDocParser()


# ############################## Class Documentation ############################## #
@pytest.mark.parametrize(
    ("class_name", "expected_class_documentation"),
    [
        (
            "ClassWithDocumentation",
            ClassDocstring(
                description="Lorem ipsum. Code::\n\n    pass\n\nDolor sit amet.",
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
    numpydoc_parser: NumpyDocParser,
    class_name: str,
    expected_class_documentation: ClassDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)

    assert isinstance(node, nodes.ClassDef)
    assert numpydoc_parser.get_class_documentation(node) == expected_class_documentation


# ############################## Function Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_function_documentation"),
    [
        (
            "function_with_documentation",
            FunctionDocstring(
                description="Lorem ipsum. Code::\n\n    pass\n\nDolor sit amet.",
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
    numpydoc_parser: NumpyDocParser,
    function_name: str,
    expected_function_documentation: FunctionDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)

    assert isinstance(node, nodes.FuncDef)
    assert numpydoc_parser.get_function_documentation(node) == expected_function_documentation


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
                description="foo",
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
                description="foo: no_type_no_default. Code::\n\n    pass",
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
                description="foo: type_no_default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "optional_unknown_default",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="",
                description="foo: optional_unknown_default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default_syntax_1",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="1",
                description="foo: with_default_syntax_1",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default_syntax_2",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(type="int", default_value="2", description="foo: with_default_syntax_2"),
        ),
        (
            "function_with_parameters",
            False,
            "with_default_syntax_3",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(type="int", default_value="3", description="foo: with_default_syntax_3"),
        ),
        (
            "function_with_parameters",
            False,
            "grouped_parameter_1",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="4",
                description="foo: grouped_parameter_1 and grouped_parameter_2",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "grouped_parameter_2",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="4",
                description="foo: grouped_parameter_1 and grouped_parameter_2",
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
        (
            "ClassAndConstructorWithParameters",
            True,
            "x",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="str",
                default_value="",
                description="Lorem ipsum 1.",
            ),
        ),
        (
            "ClassAndConstructorWithParameters",
            True,
            "y",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="str",
                default_value="",
                description="Lorem ipsum 2.",
            ),
        ),
        (
            "ClassAndConstructorWithParameters",
            True,
            "z",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="5",
                description="Lorem ipsum 3.",
            ),
        ),
        (
            "ClassWithParametersAndAttributes",
            True,
            "x",
            ParameterAssignment.POSITION_OR_NAME,
            ParameterDocstring(
                type="int",
                default_value="1",
                description="foo",
            ),
        ),
        (
            "ClassWithParametersAndAttributes",
            True,
            "q",
            ParameterAssignment.POSITION_OR_NAME,
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
        "function parameter with optional unknown default",
        "function parameter with default syntax 1 (just space)",
        "function parameter with default syntax 2 (colon)",
        "function parameter with default syntax 3 (equals)",
        "function parameter with grouped parameters 1",
        "function parameter with grouped parameters 2",
        "function parameter with positional vararg",
        "function parameter with named vararg",
        "missing function parameter",
        "class and __init__ with params 1",
        "class and __init__ with params 2",
        "class and __init__ with params 3",
        "class with parameter and attribute existing parameter",
        "class with parameter and attribute missing parameter",
    ],
)
def test_get_parameter_documentation(
    numpydoc_parser: NumpyDocParser,
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
        class_doc = numpydoc_parser.get_class_documentation(node)
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

    parameter_documentation = numpydoc_parser.get_parameter_documentation(
        function_node=node,
        parameter_name=parameter_name,
        parameter_assigned_by=parameter_assigned_by,
        parent_class=parent,
    )

    assert parameter_documentation == expected_parameter_documentation


# ############################## Attribute Documentation ############################## #
@pytest.mark.parametrize(
    ("class_name", "attribute_name", "expected_attribute_documentation"),
    [
        (
            "ClassWithAttributes",
            "no_type_no_default",
            AttributeDocstring(
                type="",
                default_value="",
                description="foo: no_type_no_default. Code::\n\n    pass",
            ),
        ),
        (
            "ClassWithAttributes",
            "type_no_default",
            AttributeDocstring(
                type="int",
                default_value="",
                description="foo: type_no_default",
            ),
        ),
        (
            "ClassWithAttributes",
            "optional_unknown_default",
            AttributeDocstring(
                type="int",
                default_value="",
                description="foo: optional_unknown_default",
            ),
        ),
        (
            "ClassWithAttributes",
            "with_default_syntax_1",
            AttributeDocstring(
                type="int",
                default_value="1",
                description="foo: with_default_syntax_1",
            ),
        ),
        (
            "ClassWithAttributes",
            "with_default_syntax_2",
            AttributeDocstring(type="int", default_value="2", description="foo: with_default_syntax_2"),
        ),
        (
            "ClassWithAttributes",
            "with_default_syntax_3",
            AttributeDocstring(type="int", default_value="3", description="foo: with_default_syntax_3"),
        ),
        (
            "ClassWithAttributes",
            "grouped_attribute_1",
            AttributeDocstring(
                type="int",
                default_value="4",
                description="foo: grouped_attribute_1 and grouped_attribute_2",
            ),
        ),
        (
            "ClassWithAttributes",
            "grouped_attribute_2",
            AttributeDocstring(
                type="int",
                default_value="4",
                description="foo: grouped_attribute_1 and grouped_attribute_2",
            ),
        ),
        (
            "ClassWithAttributes",
            "missing",
            AttributeDocstring(type="", default_value="", description=""),
        ),
        (
            "ClassWithParametersAndAttributes",
            "r",
            AttributeDocstring(
                type="",
                default_value="",
                description="",
            ),
        ),
        (
            "ClassWithParametersAndAttributes",
            "q",
            AttributeDocstring(
                type="int",
                default_value="1",
                description="foo",
            ),
        ),
    ],
    ids=[
        "class attribute with no type and no default",
        "class attribute with type and no default",
        "class attribute with optional unknown default",
        "class attribute with default syntax 1 (just space)",
        "class attribute with default syntax 2 (colon)",
        "class attribute with default syntax 3 (equals)",
        "class attribute with grouped attributes 1",
        "class attribute with grouped attributes 2",
        "missing function parameter",
        "class with parameter and attribute missing attribute",
        "class with parameter and attribute existing attribute",
    ],
)
def test_get_attribute_documentation(
    numpydoc_parser: NumpyDocParser,
    class_name: str,
    attribute_name: str,
    expected_attribute_documentation: AttributeDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)
    assert isinstance(node, nodes.ClassDef)
    docstring = numpydoc_parser.get_class_documentation(node)
    fake_class = Class(id="some_id", name="some_class", superclasses=[], is_public=True, docstring=docstring)

    attribute_documentation = numpydoc_parser.get_attribute_documentation(
        parent_class=fake_class,
        attribute_name=attribute_name,
    )

    assert attribute_documentation == expected_attribute_documentation


# ############################## Result Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_result_documentation"),
    [
        (
            "function_with_result_value_and_type",
            ResultDocstring(type="bool", description="this will be the return value"),
        ),
        ("function_without_result_value", ResultDocstring(type="", description="")),
    ],
    ids=["existing return value and type", "function without return value"],
)
def test_get_result_documentation(
    numpydoc_parser: NumpyDocParser,
    function_name: str,
    expected_result_documentation: ResultDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)
    assert numpydoc_parser.get_result_documentation(node) == expected_result_documentation
