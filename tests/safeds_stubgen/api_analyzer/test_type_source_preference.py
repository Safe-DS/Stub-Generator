import pytest
from safeds_stubgen.api_analyzer import TypeSourcePreference


def test_from_string() -> None:
    assert TypeSourcePreference.from_string("code") == TypeSourcePreference.CODE
    assert TypeSourcePreference.from_string("docstring") == TypeSourcePreference.DOCSTRING
    assert TypeSourcePreference.from_string("throw_warning") == TypeSourcePreference.THROW_WARNING

    with pytest.raises(ValueError, match="Unknown preference type: unknown_docstyle"):
        TypeSourcePreference.from_string("unknown_docstyle")
