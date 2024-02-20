from aliasing_module_2 import AliasingModule2ClassA as AliasModule2
from aliasing_module_3 import ImportMeAliasingModuleClass as ImportMeAlias


# Todo Erstelle ein Todo für Klassen die privat sind jedoch intern als Typen benutzt werden. Das Todo kommt über die
#  Stellen an denen diese Klasse als Typen genutzt wird.
#  "// TODO An internal class must not be used as a type in a public class."
class _AliasingModuleClassA:
    ...


class AliasingModuleClassB:
    ...


_some_alias_a = _AliasingModuleClassA
some_alias_b = AliasingModuleClassB


class AliasingModuleClassC(_some_alias_a):
    typed_alias_attr: some_alias_b
    infer_alias_attr = _some_alias_a()

    typed_alias_attr2: AliasModule2
    infer_alias_attr2 = AliasModule2

    alias_list: list[_some_alias_a | some_alias_b, AliasModule2, ImportMeAlias]
