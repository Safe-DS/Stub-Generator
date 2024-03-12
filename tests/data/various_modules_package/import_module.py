from another_path.another_module import AnotherClass
from class_module import ClassModuleClassB
from class_module import ClassModuleClassC as ClMCC
from class_module import ClassModuleClassD as ClMCD
if True:
    from class_module import ClassModuleEmptyClassA as ClMECA


class ImportClass(AnotherClass):
    typed_import_attr: ClMCD
    default_import_attr = ClMECA

    def import_function(self, import_param: ClassModuleClassB) -> ClMCC: ...
