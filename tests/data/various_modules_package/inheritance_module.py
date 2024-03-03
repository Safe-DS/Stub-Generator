class PublicSuperClass:
    def public_superclass_method(self) -> str: ...


class PublicSubClass(PublicSuperClass):
    ...


class _PrivateInternalClass:
    class _PrivateInternalNestedClass:
        def public_internal_nested_class_method(self, a: None) -> bool: ...

    def public_internal_class_method(self, a: int) -> str: ...

    def _private_internal_class_method(self, b: list) -> None: ...


class PublicSubClass2(_PrivateInternalClass):
    def public_subclass_method(self) -> str: ...


class PublicSubClassFromNested(_PrivateInternalClass._PrivateInternalNestedClass):
    ...


class _TransitiveInternalClassA:
    def transitive_class_fun(self, c: list) -> list: ...


class _TransitiveInternalClassB(_TransitiveInternalClassA):
    pass


class InheritTransitively(_TransitiveInternalClassB):
    pass
