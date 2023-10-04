from enum import Enum
from enum import Enum as _Enum

from .another_path.another_module import AnotherClass as _AcImportAlias


class TestEnum(Enum):
    """Enum Docstring.

    Full Docstring Description
    """

    ONE = "first"
    TWO = (2, 2)
    THREE = 3
    FOUR = FIVE = "forth and fifth"
    SIX, SEVEN = ("sixth", 7)
    EIGHT, NINE = "89"
    TEN = _AcImportAlias()


class _ReexportedEmptyEnum(_Enum):
    """Nothing's here."""


class AnotherTestEnum(_Enum, Enum):
    ELEVEN = 11