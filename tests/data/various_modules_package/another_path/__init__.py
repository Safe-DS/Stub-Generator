from typing import TYPE_CHECKING

# Testing if the "not_reexported" module is beeing wrongly reexported b/c of the existence
#  of file_creation/package_1/not_reexported.py
from not_reexported import *
import not_reexported

if TYPE_CHECKING:
    from another_module import _YetAnotherPrivateClass

__all__ = [
    "_YetAnotherPrivateClass",
]
