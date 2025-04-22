import pytest

from safeds_stubgen.docstring_parsing import DocstringStyle


def test_from_string() -> None:
    assert DocstringStyle.from_string("plaintext") == DocstringStyle.PLAINTEXT
    assert DocstringStyle.from_string("google") == DocstringStyle.GOOGLE
    assert DocstringStyle.from_string("numpydoc") == DocstringStyle.NUMPYDOC
    assert DocstringStyle.from_string("rest") == DocstringStyle.REST

    with pytest.raises(ValueError, match="Unknown docstring style: unknown_docstyle"):
        DocstringStyle.from_string("unknown_docstyle")
