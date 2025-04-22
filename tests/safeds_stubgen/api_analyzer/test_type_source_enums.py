import pytest

from safeds_stubgen.api_analyzer import TypeSourcePreference, TypeSourceWarning


def test_type_source_preference_from_string() -> None:
    assert TypeSourcePreference.from_string("code") == TypeSourcePreference.CODE
    assert TypeSourcePreference.from_string("docstring") == TypeSourcePreference.DOCSTRING

    with pytest.raises(ValueError, match="Unknown preference type: unknown_docstyle"):
        TypeSourcePreference.from_string("unknown_docstyle")


def test_type_source_warning_from_string() -> None:
    assert TypeSourceWarning.from_string("ignore") == TypeSourceWarning.IGNORE
    assert TypeSourceWarning.from_string("warn") == TypeSourceWarning.WARN

    with pytest.raises(ValueError, match="Unknown warning type: unknown_docstyle"):
        TypeSourceWarning.from_string("unknown_docstyle")
