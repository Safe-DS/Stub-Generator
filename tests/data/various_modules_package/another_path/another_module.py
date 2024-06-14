"""Another Module Docstring.

Full Docstring Description
"""
from abc import ABC, abstractmethod


class AnotherClass:
    pass


class _AnotherPrivateClass(ABC):
    class AnotherNestedClass:
        ...

    def another_method(self) -> None: ...


class _YetAnotherPrivateClass(ABC):
    class YetAnotherNestedClass(ABC):
        ...

    @abstractmethod
    def yet_another_method(self) -> None: ...
