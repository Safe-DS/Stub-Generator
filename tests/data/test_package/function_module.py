from typing import Callable


class FunctionModuleClassA:
    ...


class FunctionModuleClassB:
    def __init__(self, init_param): ...

    def instance_method(self, a: FunctionModuleClassA) -> FunctionModuleClassA: ...

    @staticmethod
    def static_method(): ...

    @staticmethod
    def static_method_params(param_1: int) -> None: ...

    @classmethod
    def class_method(cls): ...

    @classmethod
    def class_method_params(cls, param_1: int) -> bool:
        pass

    class FunctionModuleClassC:
        def nested_class_function(self, param1: int) -> bool: ...

        class FunctionModuleClassD:
            ...


def _private(a): ...


def public_no_params_no_result(): ...


def params(
    i: int,
    union: int | bool,
    lst: list[int],
    obj: FunctionModuleClassA,
): ...


def illegal_params(
    lst: list[int, str],
    lst_2: list[int, str, int],
    tpl: tuple[int, str, bool, int],
    _: int = "String",
): ...


def special_params(
    none_union: None | None,
    none_bool_union: None | bool,
    bool_none_union: bool | None,
    none_bool_none_union: None | bool | None,
    none_bool_int_union: None | bool | int,
    none_none_bool_none_union: None | None | bool | None,
    none_list_union_none_none: None | list[None | None] | None,
    none: None,
): ...


def param_position(self, a, /, b: bool, c=1, *, d=FunctionModuleClassA(), e: int = 1): ...


def opt_pos_only(required, optional=1, /): ...


def req_name_only(*, required, optional=1): ...


def arg(*args, **kwargs): ...


def args_type(*args: int, **kwargs: int): ...


def one_result() -> int: ...


def multiple_results() -> tuple[str, int, bool, FunctionModuleClassA]: ...


def callable_type(param: Callable[[str], tuple[int, str]]) -> Callable[[int, int], int]: ...


class FunctionModulePropertiesClass:
    @property
    def property_function(self): ...

    @property
    def property_function_params(self) -> str: ...

    @property
    def property_function_infer(self):
        return "some string"
