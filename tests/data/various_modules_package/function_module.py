from typing import Callable, Optional, Literal, Any, Union
from tests.data.main_package.another_path.another_module import AnotherClass
import numpy as np


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
    integer: int,
    boolean: bool,
    float_: float,
    none: None,
    string: str,
    obj: FunctionModuleClassA,
    callexpr: FunctionModuleClassA(),
    union: int | bool,
    union_with_none_1: int | None,
    union_with_none_2: None | int,
    list_: list[int],
    dictionary: dict[str, int | float],
    set_: set[str],
    optional: Optional[int],
    tuple_: tuple[int, str, bool],
    literal: Literal["Some String"],
    any_: Any,
    callable_none: Callable[[int, float], None] | None,
    literal_none: Literal["1", 2] | None,
    literal_none2: None | Literal["1", 2],
    set_none: set[int] | None,
    dict_none: dict[str, int] | None,
    named_class_none: FunctionModuleClassA | None,
    list_class_none: list[float] | None,
    tuple_class_none: tuple[int, str] | None,
): ...


def params_with_default_value(
    integer: int = 3,
    negative_int: int = -1,
    negative_float: float = -2.3,
    boolean: bool = True,
    float_: float = 1.2,
    none: None = None,
    string: str = "Some String",
    obj: FunctionModuleClassA = FunctionModuleClassA(),
    callexpr: FunctionModuleClassA() = FunctionModuleClassA(),
    union: int | bool = 2,
    union_with_none_1: int | None = 2,
    union_with_none_2: None | int = 3,
    list_: list[int] = [1, 2, 3],
    dictionary: dict[str, int | float] = {"key": 1, "key2": 1.2},
    set_: set[str] = {"a", "b"},
    optional: Optional[int] = None,
    tuple_: tuple[int, str, bool] = (1, "2", True),
    literal: Literal["Some String"] = "Some String",
    any_: Any = False,
    single_quote: str = '"'
): ...


def illegal_params(
    lst: list[int, str],
    lst_2: list[int, str, int],
    tpl: tuple[int, str, bool, int],
    dct: dict[str, int, None, bool],
    _: int = "String",
): ...


def special_params(
    none_union: None | None,
    none_bool_union: None | bool,
    bool_none_union: bool | None,
    bool_none_str: None | str,
    none_bool_none_union: None | bool | None,
    none_bool_int_union: None | bool | int,
    none_none_bool_none_union: None | None | bool | None,
    none_list_union_none_none: None | list[None | None] | None,
    none: None,
    not_true=not 1
): ...


def param_position(self, a, /, b: bool, c=FunctionModuleClassA, *, d=FunctionModuleClassA(), e: int = 1): ...


def opt_pos_only(required, optional=1, /): ...


def req_name_only(*, required, optional=1): ...


def arg(*args, **kwargs): ...


def args_type(*args: int, **kwargs: int): ...


def int_result() -> int: ...


def str_result() -> str: ...


def bool_result() -> bool: ...


def float_result() -> float: ...


def obj_result() -> FunctionModuleClassA: ...


def callexr_result_class() -> FunctionModuleClassA(): ...


def callexr_result_function() -> float_result(): ...


def tuple_results() -> tuple[str, FunctionModuleClassA]: ...


def union_results() -> int | str: ...


def list_results() -> list[int]: ...


def illegal_list_results() -> list[int, str]: ...


def dictionary_results() -> dict[str, FunctionModuleClassA]: ...


def dictionary_results_no_key_no_value() -> dict: ...


def illegal_dictionary_results() -> dict[int, str, FunctionModuleClassA]: ...


def union_dictionary_results() -> dict[int | str, bool | float]: ...


def set_results() -> set[str]: ...


def illegal_set_results() -> set[str, bool]: ...


def optional_results() -> Optional[int]: ...


def literal_results() -> Literal["Some String"]: ...


def any_results() -> Any: ...


def callable_type(param: Callable[[str], tuple[int, str]]) -> Callable[[int, int], int]: ...


def param_from_outside_the_package(param_type: AnotherClass, param_value=AnotherClass): ...


def result_from_outside_the_package() -> AnotherClass: ...


class FunctionModulePropertiesClass:
    @property
    def property_function(self): ...

    @property
    def property_function_params(self) -> str: ...

    @property
    def property_function_infer(self):
        return "some string"


def ret_conditional_statement():
    return 1 if True else False


def ignore_assignment(a: int, b: int):
    def _f(x: int, y: int) -> int:
        return x + y

    g, f = _f(a, b)
    Cxy = _f(g, f)**2
    return Cxy, f


def ignore_assignment2(a: int, b: int):
    Cxy = 3**2
    return Cxy


def ignore_assignment3(xys, p):
    return ((p - xys[0]) ** 2).sum(), xys[0], (0, 0)


def ignore_assignment4(a, b, c):
    return ignore_assignment3(a, a), (ignore_assignment2(b, a), ignore_assignment(c, a))


def return_inner_function():
    def return_me():
        return 123

    return return_me


def return_param1(a):
    return a


def return_param2(a: int):
    return a


def return_param3(a: int, b, c: bool):
    return a if b else c


def return_param4(a: int, b, x):
    if x == 0:
        return a, b, a, b

    return True


def return_not_statement():
    return not (0 or "...")


ArrayLike = Union["ExtensionArray", Any]
def type_alias_param(values: ArrayLike) -> ArrayLike:
    ...


def alias_subclass_result_type() -> ArrayLike | np.ndarray:
    ...


def alias_subclass_param_type(x: ArrayLike | np.ndarray):
    ...


def different_result_operants(y):
    if y:
        return False
    elif y - 1:
        return y or y - 1
    elif y - 2:
        return y and y + 1
    elif y - 3:
        return y or y - 1 and y - 2
    elif y - 4:
        return y is not None
    elif y - 5:
        return y is None
    return not y


def none_result_1() -> None:
    ...


def none_result_2():
    return


def none_result_3():
    return None

