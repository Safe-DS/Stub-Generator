from aliasing_module_2 import ImportMeAliasingModuleClass as ImportMeAlias


class ImportMeAliasingModuleClass:
    import_alias_attr: ImportMeAlias = ImportMeAlias()

    alias_list: list[ImportMeAlias, str]
