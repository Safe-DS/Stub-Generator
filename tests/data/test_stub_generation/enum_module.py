from enum import Enum, IntEnum
from enum import Enum as _Enum


class EnumTest(Enum):
    ONE = "first"
    TWO = (2, 2)
    THREE = 3
    FOUR = FIVE = "forth and fifth"
    SIX, SEVEN = ("sixth", 7)
    EIGHT, NINE = "89"


class EnumTest2(_Enum):
    TEN = "TEN"


class EnumTest3(IntEnum):
    ELEVEN = 11
