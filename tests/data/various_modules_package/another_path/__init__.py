from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from another_module import _YetAnotherPrivateClass

__all__ = [
    "_YetAnotherPrivateClass",
]
