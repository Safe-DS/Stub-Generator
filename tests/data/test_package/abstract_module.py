from abc import ABC, abstractmethod


class AbstractModuleClass(ABC):
    def __init__(self, param):
        ...

    @abstractmethod
    def abstract_method(self): ...

    # Todo Frage: Bei list[str, int], also mehrere elemente, bekommen wir list[Any]
    @abstractmethod
    def abstract_method_params(self, param_1: int, param_2=False) -> list[str]: ...

    @staticmethod
    @abstractmethod
    def abstract_static_method(): ...

    @staticmethod
    @abstractmethod
    def abstract_static_method_params(param: float) -> bool: ...

    @property
    @abstractmethod
    def abstract_property_method(self) -> tuple[float, int]: ...
