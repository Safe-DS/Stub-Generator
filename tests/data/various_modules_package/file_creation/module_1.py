from typing import Self


class C:
    ...


class Lv1:
    def level1_function(self) -> Self:
        ...


class Lv2:
    lv2_attr: Self
