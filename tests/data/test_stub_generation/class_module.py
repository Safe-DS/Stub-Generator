class A:
    ...


class B(A):
    def __init__(self, a: int, b: A | None): ...

    def f(self): ...


class C(A, B):
    attr_1: int
    attr_2: int

    def f1(self): ...
