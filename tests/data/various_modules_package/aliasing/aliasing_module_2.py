class AliasingModule2ClassA:
    ...


class AliasingModuleClassB:
    ...


class ImportMeAliasingModuleClass:
    ...


some_alias_b = AliasingModuleClassB


class AliasingModuleClassC:
    typed_alias_attr: some_alias_b

    alias_list: list[str | some_alias_b, ImportMeAliasingModuleClass]