from typing import Optional, Final, Literal


class AttributesClassA:
    ...


class AttributesClassB:
    type_hint_public: int
    _type_hint_private: int

    no_type_hint_public = 1
    _no_type_hint_private = 1

    object_attr: AttributesClassA
    callexpr_attr: AttributesClassA()

    tuple_attr_1: tuple
    tuple_attr_2: tuple[str | int]
    tuple_attr_3: tuple[str, int]

    list_attr_1: list
    list_attr_2: list[str | AttributesClassA]
    list_attr_3: list[str, AttributesClassA]
    list_attr_4: list[str, AttributesClassA | int]

    dict_attr_1: dict
    dict_attr_2: dict[str, int]
    dict_attr_3: dict[str | int, None | AttributesClassA]

    bool_attr: bool
    none_attr: None
    flaot_attr: float
    int_or_bool_attr: int | bool
    str_attr_with_none_value: str = None
    set_: set

    optional: Optional[int]
    final: Final[str] = "Value"
    literal: Literal["Some String"]

    multi_attr_1, _multi_attr_2_private = (123456, "I am a String")
    multi_attr_3 = _multi_attr_4_private = ["I am some", "kind of list"]
    multi_attr_5, multi_attr_6 = ("A", "B")
    multi_attr_7 = multi_attr_8 = "A"

    def __init__(self):
        self.init_attr: bool = False
