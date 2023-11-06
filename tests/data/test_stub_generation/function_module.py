class A:
    ...


class B:
    def __init__(self, init_param): ...

    def class_method(self, a: A) -> A: ...

    @staticmethod
    def static_class_method() -> None: ...


def _private(a): ...


def public_no_params_no_result(): ...


def params(
    i: int,
    union: int | bool,
    lst: list[int],
    obj: A,
): ...


def illegal_params(
    none: None,
    none_union: None | None,
    tpl: tuple[int, str, bool, int],
    lst: list[int, str],
    _: int = "String"
): ...


def special_params(
    none_union: None | bool,
): ...


def param_position(self, a, /, b: bool, c=1, *, d=A(), e: int = 1): ...


def opt_pos_only(required, optional=1, /): ...


def req_name_only(*, required, optional=1): ...


def arg(*args, **kwargs): ...


def args_type(*args: int, **kwargs: int): ...


def one_result() -> int: ...


def muliple_results() -> tuple[str, int, bool, A]: ...
