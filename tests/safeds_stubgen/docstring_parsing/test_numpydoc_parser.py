from __future__ import annotations

from pathlib import Path

import pytest
from griffe.enumerations import Parser
from mypy import nodes
from safeds_stubgen.api_analyzer import (
    DictType,
    ListType,
    NamedType,
    SetType,
    TupleType,
    UnionType,
    get_classdef_definitions,
)

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
_test_package_name = "docstring_parser_package"
files = [str(Path(_test_dir / "data" / "docstring_parser_package" / "numpydoc.py"))]
mypy_build = _get_mypy_build(files)
mypy_file = _get_mypy_asts(
    build_result=mypy_build,
    files=files,
    package_paths=[],
)[0]


@pytest.fixture()
def numpydoc_parser() -> DocstringParser:
    return DocstringParser(Parser.numpy, _test_dir)


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
    numpydoc_parser: DocstringParser,
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
    numpydoc_parser: DocstringParser,
    function_name: str,
    expected_function_documentation: FunctionDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)

    assert isinstance(node, nodes.FuncDef)
    assert numpydoc_parser.get_function_documentation(node) == expected_function_documentation


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
                description="foo",
            ),
        ),
        (
            "ClassWithParameters",
            True,
            "grouped_parameter_1",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="4",
                description="foo: grouped_parameter_1 and grouped_parameter_2",
            ),
        ),
        (
            "ClassWithParameters",
            True,
            "grouped_parameter_2",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="4",
                description="foo: grouped_parameter_1 and grouped_parameter_2",
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
                description="foo: no_type_no_default. Code::\n\n    pass",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "type_no_default",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="",
                description="foo: type_no_default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "optional_unknown_default",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="",
                description="foo: optional_unknown_default",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default_syntax_1",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="1",
                description="foo: with_default_syntax_1",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default_syntax_2",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="2",
                description="foo: with_default_syntax_2",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "with_default_syntax_3",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="3",
                description="foo: with_default_syntax_3",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "grouped_parameter_1",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="4",
                description="foo: grouped_parameter_1 and grouped_parameter_2",
            ),
        ),
        (
            "function_with_parameters",
            False,
            "grouped_parameter_2",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="4",
                description="foo: grouped_parameter_1 and grouped_parameter_2",
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
                type=DictType(
                    key_type=NamedType(name="str", qname="builtins.str"),
                    value_type=NamedType(name="int", qname="builtins.int")
                ),
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
        (
            "ClassAndConstructorWithParameters",
            True,
            "x",
            ParameterDocstring(
                type=NamedType(name="str", qname="builtins.str"),
                default_value="",
                description="Lorem ipsum 1.",
            ),
        ),
        (
            "ClassAndConstructorWithParameters",
            True,
            "y",
            ParameterDocstring(
                type=NamedType(name="str", qname="builtins.str"),
                default_value="",
                description="Lorem ipsum 2.",
            ),
        ),
        (
            "ClassAndConstructorWithParameters",
            True,
            "z",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="5",
                description="Lorem ipsum 3.",
            ),
        ),
        (
            "ClassWithParametersAndAttributes",
            True,
            "x",
            ParameterDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                default_value="1",
                description="foo",
            ),
        ),
        (
            "ClassWithParametersAndAttributes",
            True,
            "q",
            ParameterDocstring(
                type=None,
                default_value="",
                description="",
            ),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "no_type",
            ParameterDocstring(type=None),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "optional_type",
            ParameterDocstring(type=NamedType(name="int", qname="builtins.int")),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "none_type",
            ParameterDocstring(type=NamedType(name="None", qname="builtins.None")),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "int_type",
            ParameterDocstring(type=NamedType(name="int", qname="builtins.int")),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "bool_type",
            ParameterDocstring(type=NamedType(name="bool", qname="builtins.bool")),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "str_type",
            ParameterDocstring(type=NamedType(name="str", qname="builtins.str")),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "float_type",
            ParameterDocstring(type=NamedType(name="float", qname="builtins.float")),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "multiple_types",
            ParameterDocstring(
                type=TupleType(
                    types=[NamedType(name="int", qname="builtins.int"), NamedType(name="bool", qname="builtins.bool")],
                ),
            ),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "list_type_1",
            ParameterDocstring(type=ListType(types=[])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "list_type_2",
            ParameterDocstring(type=ListType(types=[NamedType(name="str", qname="builtins.str")])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "list_type_3",
            ParameterDocstring(
                type=ListType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="bool", qname="builtins.bool"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "list_type_4",
            ParameterDocstring(type=ListType(types=[ListType(types=[NamedType(name="int", qname="builtins.int")])])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "set_type_1",
            ParameterDocstring(type=SetType(types=[])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "set_type_2",
            ParameterDocstring(type=SetType(types=[NamedType(name="str", qname="builtins.str")])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "set_type_3",
            ParameterDocstring(
                type=SetType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="bool", qname="builtins.bool"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "set_type_4",
            ParameterDocstring(type=SetType(types=[ListType(types=[NamedType(name="int", qname="builtins.int")])])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "tuple_type_1",
            ParameterDocstring(type=TupleType(types=[])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "tuple_type_2",
            ParameterDocstring(type=TupleType(types=[NamedType(name="str", qname="builtins.str")])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "tuple_type_3",
            ParameterDocstring(
                type=TupleType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="bool", qname="builtins.bool"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "tuple_type_4",
            ParameterDocstring(type=TupleType(types=[ListType(types=[NamedType(name="int", qname="builtins.int")])])),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "any_type",
            ParameterDocstring(type=NamedType(name="Any", qname="typing.Any")),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "optional_type_2",
            ParameterDocstring(
                type=UnionType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="None", qname="builtins.None"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "class_type",
            ParameterDocstring(
                type=NamedType(
                    name="ClassWithAttributes",
                    qname="tests.data.docstring_parser_package.numpydoc.ClassWithAttributes",
                ),
            ),
        ),
        (
            "ClassWithVariousParameterTypes",
            True,
            "imported_type",
            ParameterDocstring(
                type=NamedType(
                    name="AnotherClass",
                    qname="tests.data.various_modules_package.another_path.another_module.AnotherClass",
                ),
            ),
        ),
    ],
    ids=[
        "existing class parameter",
        "grouped_parameter_1",
        "grouped_parameter_2",
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
        "Various types: no_type",
        "Various types: optional_type : int, optional",
        "Various types: none_type : None",
        "Various types: int_type : int",
        "Various types: bool_type : bool",
        "Various types: str_type : str",
        "Various types: float_type : float",
        "Various types: multiple_types : int, bool",
        "Various types: list_type_1 : list",
        "Various types: list_type_2 : list[str]",
        "Various types: list_type_3 : list[int, bool]",
        "Various types: list_type_4 : list[list[int]]",
        "Various types: set_type_1 : set",
        "Various types: set_type_2 : set[str]",
        "Various types: set_type_3 : set[int, bool]",
        "Various types: set_type_4 : set[list[int]]",
        "Various types: tuple_type_1 : tuple",
        "Various types: tuple_type_2 : tuple[str]",
        "Various types: tuple_type_3 : tuple[int, bool]",
        "Various types: tuple_type_4 : tuple[list[int]]",
        "Various types: any_type : Any",
        "Various types: optional_type_2 : Optional[int]",
        "Various types: class_type : ClassWithAttributes",
        "Various types: imported_type : AnotherClass",
    ],
)
def test_get_parameter_documentation(
    numpydoc_parser: DocstringParser,
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

    parameter_documentation = numpydoc_parser.get_parameter_documentation(
        function_qname=node.fullname,
        parameter_name=parameter_name,
        parent_class_qname=parent_qname,
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
                type=None,
                description="foo: no_type_no_default. Code::\n\n    pass",
            ),
        ),
        (
            "ClassWithAttributes",
            "type_no_default",
            AttributeDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                description="foo: type_no_default",
            ),
        ),
        (
            "ClassWithAttributes",
            "optional_unknown_default",
            AttributeDocstring(
                type=UnionType(
                    types=[NamedType(name="int", qname="builtins.int"), NamedType(name="None", qname="builtins.None")],
                ),
                description="foo: optional_unknown_default",
            ),
        ),
        (
            "ClassWithAttributes",
            "with_default_syntax_1",
            AttributeDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                description="foo: with_default_syntax_1",
            ),
        ),
        (
            "ClassWithAttributes",
            "with_default_syntax_2",
            AttributeDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                description="foo: with_default_syntax_2",
            ),
        ),
        (
            "ClassWithAttributes",
            "with_default_syntax_3",
            AttributeDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                description="foo: with_default_syntax_3",
            ),
        ),
        (
            "ClassWithAttributes",
            "grouped_attribute_1",
            AttributeDocstring(
                type=None,
                description="",
            ),
        ),
        (
            "ClassWithAttributes",
            "grouped_attribute_2",
            AttributeDocstring(
                type=None,
                description="",
            ),
        ),
        (
            "ClassWithAttributes",
            "missing",
            AttributeDocstring(None, description=""),
        ),
        (
            "ClassWithParametersAndAttributes",
            "r",
            AttributeDocstring(
                type=None,
                description="",
            ),
        ),
        (
            "ClassWithParametersAndAttributes",
            "q",
            AttributeDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                description="foo",
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "no_type",
            AttributeDocstring(type=None),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "optional_type",
            AttributeDocstring(
                type=UnionType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="None", qname="builtins.None"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "none_type",
            AttributeDocstring(type=NamedType(name="None", qname="builtins.None")),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "int_type",
            AttributeDocstring(type=NamedType(name="int", qname="builtins.int")),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "bool_type",
            AttributeDocstring(type=NamedType(name="bool", qname="builtins.bool")),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "str_type",
            AttributeDocstring(type=NamedType(name="str", qname="builtins.str")),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "float_type",
            AttributeDocstring(type=NamedType(name="float", qname="builtins.float")),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "multiple_types",
            AttributeDocstring(
                type=TupleType(
                    types=[NamedType(name="int", qname="builtins.int"), NamedType(name="bool", qname="builtins.bool")],
                ),
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "list_type_1",
            AttributeDocstring(type=ListType(types=[])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "list_type_2",
            AttributeDocstring(type=ListType(types=[NamedType(name="str", qname="builtins.str")])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "list_type_3",
            AttributeDocstring(
                type=ListType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="bool", qname="builtins.bool"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "list_type_4",
            AttributeDocstring(type=ListType(types=[ListType(types=[NamedType(name="int", qname="builtins.int")])])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "set_type_1",
            AttributeDocstring(type=SetType(types=[])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "set_type_2",
            AttributeDocstring(type=SetType(types=[NamedType(name="str", qname="builtins.str")])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "set_type_3",
            AttributeDocstring(
                type=SetType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="bool", qname="builtins.bool"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "set_type_4",
            AttributeDocstring(type=SetType(types=[ListType(types=[NamedType(name="int", qname="builtins.int")])])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "tuple_type_1",
            AttributeDocstring(type=TupleType(types=[])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "tuple_type_2",
            AttributeDocstring(type=TupleType(types=[NamedType(name="str", qname="builtins.str")])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "tuple_type_3",
            AttributeDocstring(
                type=TupleType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="bool", qname="builtins.bool"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "tuple_type_4",
            AttributeDocstring(type=TupleType(types=[ListType(types=[NamedType(name="int", qname="builtins.int")])])),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "any_type",
            AttributeDocstring(type=NamedType(name="Any", qname="typing.Any")),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "optional_type_2",
            AttributeDocstring(
                type=UnionType(
                    types=[
                        NamedType(name="int", qname="builtins.int"),
                        NamedType(name="None", qname="builtins.None"),
                    ],
                ),
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "class_type",
            AttributeDocstring(
                type=NamedType(
                    name="ClassWithAttributes",
                    qname="tests.data.docstring_parser_package.numpydoc.ClassWithAttributes",
                ),
            ),
        ),
        (
            "ClassWithVariousAttributeTypes",
            "imported_type",
            AttributeDocstring(
                type=NamedType(
                    name="AnotherClass",
                    qname="tests.data.various_modules_package.another_path.another_module.AnotherClass",
                ),
            ),
        ),
        (
            "ClassAndConstructorWithAttributes",
            "x",
            AttributeDocstring(
                type=NamedType(name="str", qname="builtins.str"),
                description="Lorem ipsum 1.",
            ),
        ),
        (
            "ClassAndConstructorWithAttributes",
            "y",
            AttributeDocstring(
                type=NamedType(name="str", qname="builtins.str"),
                description="Lorem ipsum 2.",
            ),
        ),
        (
            "ClassAndConstructorWithAttributes",
            "z",
            AttributeDocstring(
                type=NamedType(name="int", qname="builtins.int"),
                description="Lorem ipsum 3.",
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
        "missing attribute",
        "class with parameter and attribute missing attribute",
        "class with parameter and attribute existing attribute",
        "Various types: no_type",
        "Various types: optional_type : int, optional",
        "Various types: none_type : None",
        "Various types: int_type : int",
        "Various types: bool_type : bool",
        "Various types: str_type : str",
        "Various types: float_type : float",
        "Various types: multiple_types : int, bool",
        "Various types: list_type_1 : list",
        "Various types: list_type_2 : list[str]",
        "Various types: list_type_3 : list[int, bool]",
        "Various types: list_type_4 : list[list[int]]",
        "Various types: set_type_1 : set",
        "Various types: set_type_2 : set[str]",
        "Various types: set_type_3 : set[int, bool]",
        "Various types: set_type_4 : set[list[int]]",
        "Various types: tuple_type_1 : tuple",
        "Various types: tuple_type_2 : tuple[str]",
        "Various types: tuple_type_3 : tuple[int, bool]",
        "Various types: tuple_type_4 : tuple[list[int]]",
        "Various types: class_type : ClassWithAttributes",
        "Various types: imported_type : AnotherClass",
        "Various types: class_type : ClassWithAttributes",
        "Various types: imported_type : AnotherClass",
        "Class with attributes in constructor - x",
        "Class with attributes in constructor - y",
        "Class with attributes in constructor - z",
    ],
)
def test_get_attribute_documentation(
    numpydoc_parser: DocstringParser,
    class_name: str,
    attribute_name: str,
    expected_attribute_documentation: AttributeDocstring,
) -> None:
    node = get_specific_mypy_node(mypy_file, class_name)
    assert isinstance(node, nodes.ClassDef)
    attribute_documentation = numpydoc_parser.get_attribute_documentation(
        parent_class_qname=node.fullname,
        attribute_name=attribute_name,
    )

    assert attribute_documentation == expected_attribute_documentation


# ############################## Result Documentation ############################## #
@pytest.mark.parametrize(
    ("function_name", "expected_result_documentation"),
    [
        (
            "function_with_result_value_and_type",
            [
                ResultDocstring(
                    type=NamedType(name="bool", qname="builtins.bool"),
                    description="this will be the return value",
                ),
            ],
        ),
        (
            "function_without_result_value",
            [],
        ),
        (
            "function_with_multiple_results",
            [
                ResultDocstring(
                    type=NamedType(name="int", qname="builtins.int"),
                    description="first result",
                    name="first_result",
                ),
                ResultDocstring(
                    type=NamedType(name="bool", qname="builtins.bool"),
                    description="second result",
                    name="second_result",
                ),
            ],
        ),
    ],
    ids=[
        "existing return value and type",
        "function without return value",
        "function with multiple results",
    ],
)
def test_get_result_documentation(
    numpydoc_parser: DocstringParser,
    function_name: str,
    expected_result_documentation: list[ResultDocstring],
) -> None:
    node = get_specific_mypy_node(mypy_file, function_name)
    assert isinstance(node, nodes.FuncDef)
    assert numpydoc_parser.get_result_documentation(node.fullname) == expected_result_documentation
