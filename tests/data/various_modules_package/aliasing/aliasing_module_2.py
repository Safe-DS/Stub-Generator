from aliasing_module_1 import AliasingModuleClassC


class AliasingModule2ClassA:
    ...


class AliasingModuleClassB:
    ...


class ImportMeAliasingModuleClass:
    ...


some_alias_b = AliasingModuleClassB
ImportMeAlias = AliasingModuleClassC


class AliasingModuleClassC:
    typed_alias_attr: some_alias_b
    typed_alias_infer = ImportMeAlias

    alias_list: list[str | some_alias_b, ImportMeAliasingModuleClass]
