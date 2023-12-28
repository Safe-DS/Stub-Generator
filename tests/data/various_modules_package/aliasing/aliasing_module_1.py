from aliasing_module_2 import AliasingModule2ClassA as AliasModule2
from aliasing_module_3 import ImportMeAliasingModuleClass as ImportMeAlias


# Todo Erstelle ein Todo für Klassen die privat sind jedoch intern als Typen benutzt werden. Das Todo kommt über die
#  Stellen an denen diese Klasse als Typen genutzt wird.
#  // TODO An internal class must not be used as a type in a public class.
class _AliasingModuleClassA:
    ...


class AliasingModuleClassB:
    ...


_some_alias_a = _AliasingModuleClassA
some_alias_b = AliasingModuleClassB


# Todo Create an issue:
#  Wir erben von einer privaten internen Klasse, welche normalerweise nicht generiert werden würde, aber in diesem Fall
#  müssten wir Stubs generieren. Um das zu bewerkstelligen müssten wir die Informationen in den API Daten in so fern
#  erweitern, dass Superklassen Informationen auch in die andere Richtung zeigen, d.h. wir müssen die Unterklassen für
#  alle Klassen erhausfinden.
class AliasingModuleClassC(_some_alias_a):
    typed_alias_attr: some_alias_b
    infer_alias_attr = _some_alias_a()

    typed_alias_attr2: AliasModule2
    infer_alias_attr2 = AliasModule2

    alias_list: list[_some_alias_a | some_alias_b, AliasModule2, ImportMeAlias]
