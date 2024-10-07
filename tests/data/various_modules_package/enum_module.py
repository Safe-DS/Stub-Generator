from enum import Enum, IntEnum
from enum import Enum as _Enum

from .another_path.another_module import AnotherClass as _AcImportAlias


class _ReexportedEmptyEnum(_Enum):
    """Nothing's here."""


class EnumTest(Enum):
    """Enum Docstring.

    Full Docstring Description
    """
    ONE = "first"
    TWO = (2, 2)
    THREE = 3
    FOUR = FIVE = "forth and fifth"
    SIX, SEVEN = ("sixth", 7)
    EIGHT, NINE = "89"


class EnumTest2(_Enum):
    TEN = _AcImportAlias()


class EnumTest3(IntEnum):
    ele_ven = 11


class EmptyEnum(IntEnum):
    ...
