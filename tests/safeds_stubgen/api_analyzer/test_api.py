import pytest

from safeds_stubgen.api_analyzer import (
    NamedType,
    Parameter,
    ParameterAssignment,
)
from safeds_stubgen.docstring_parsing import ParameterDocstring


@pytest.mark.parametrize(
    argnames=("default_value", "is_required", "assigned_by", "is_variadic"),
    argvalues=[
        ("test_str", False, ParameterAssignment.POSITIONAL_VARARG, True),
        (None, True, ParameterAssignment.NAMED_VARARG, True),
        (None, True, ParameterAssignment.IMPLICIT, False),
        (None, True, ParameterAssignment.POSITION_ONLY, False),
        (None, True, ParameterAssignment.POSITION_OR_NAME, False),
        (None, True, ParameterAssignment.NAME_ONLY, False),
    ],
)
def test_parameter(
    default_value: str | None,
    is_required: bool,
    assigned_by: ParameterAssignment,
    is_variadic: bool,
) -> None:
    parameter = Parameter(
        id="test/test.Test/test/test_parameter",
        name="test_parameter",
        is_optional=True,
        default_value=default_value,
        assigned_by=assigned_by,
        docstring=ParameterDocstring(None, "r", "r"),
        type=NamedType(name="str", qname=""),
    )

    assert parameter.is_required == is_required
    assert parameter.is_variadic == is_variadic
