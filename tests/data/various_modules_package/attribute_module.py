from typing import Optional, Final, Literal
from tests.data.main_package.another_path.another_module import AnotherClass


class AttributesClassA:
    ...


class AttributesClassB:
    type_hint_public: int
    _type_hint_private: int

    no_type_hint_public = 1
    _no_type_hint_private = 1

    object_attr: AttributesClassA
    callexpr_attr_class: AttributesClassA()

    @staticmethod
    def some_func() -> bool:
        return True

    callexpr_attr_function: some_func()

    tuple_attr_1: tuple
    tuple_attr_2: tuple[str | int]
    tuple_attr_3: tuple[str, int]

    defined_three_times: int
    defined_three_times: str
    defined_three_times, _ignore_me = (0, 0)

    list_attr_1: list
    list_attr_2: list[str | AttributesClassA]
    list_attr_3: list[str, AttributesClassA]
    list_attr_4: list[str, AttributesClassA | int]

    set_attr_1: set
    set_attr_2: set[str | AttributesClassA]
    set_attr_3: set[str, AttributesClassA]
    set_attr_4: set[str, AttributesClassA | int]

    dict_attr_1: dict
    dict_attr_2: dict[str, int]
    dict_attr_3: dict[str | int, None | AttributesClassA]

    bool_attr: bool
    none_attr: None
    flaot_attr: float
    int_or_bool_attr: int | bool
    str_attr_with_none_value: str = None

    optional: Optional[int]
    final: Final[str] = "Value"
    finals: Final[str, int] = "Value"
    final_union: Final[str | int] = "Value"
    literal: Literal["Some String"]
    multiple_literals: Literal["Literal_1", "Literal_2", 3, True]
    mixed_literal_union: Literal["L1", 2] | int | Literal[4, False] | str

    multi_attr_1, _multi_attr_2_private = (123456, "I am a String")
    multi_attr_3 = _multi_attr_4_private = ["I am some", "kind of list"]
    multi_attr_5, multi_attr_6 = ("A", "B")
    multi_attr_7 = multi_attr_8 = "A"

    attr_type_from_outside_package: AnotherClass
    attr_default_value_from_outside_package = AnotherClass()

    def __init__(self):
        self.init_attr: bool = False
