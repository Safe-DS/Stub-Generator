global_var = 10
global_var2 = 20
global_var3 = 30

from .another_purity_path.another_purity_module import AnotherClass
from .another_purity_path.another_purity_module import AnotherClass as _AcImportAlias

def global_func_same_name_pure() -> int:
    child_class_instance = ChildClassPure()
    result = child_class_instance.same_name()
    return result

def global_func_same_name_impure() -> int:
    child_class_instance = ChildClassImpure()
    result = child_class_instance.same_name()  # call reference to impure function
    return result

def global_func_only_in_T_pure() -> int:
    instance = ClassPure()
    result = instance.only_in_T()
    return result

def global_func_only_in_T_impure() -> int:
    instance = ClassImpure()
    result = instance.only_in_T()
    return result

def global_func_only_in_super_from_T_pure() -> int:
    instance = ClassPure()
    result = instance.only_in_super_pure()
    return result

def global_func_only_in_super_from_T_impure() -> int:
    instance = ClassPure()
    result = instance.only_in_super_impure()
    return result

def global_func_only_in_super_from_Child_pure() -> int:
    instance = ChildClassPure()
    result = instance.only_in_super_pure()
    return result

def global_func_only_in_super_from_Child_impure() -> int:
    instance = ChildClassPure()
    result = instance.only_in_super_impure()
    return result

class SuperClass:
    def __init__(self) -> None:
        pass

    def same_name(self) -> int:
        x = 20
        return x
    
    def only_in_super_pure(self) -> int:
        return 10
    
    def only_in_super_impure(self) -> int:
        return global_var
    
    def in_super_and_child_pure(self) -> int:
        return 10
    
    def in_super_and_child_impure(self) -> int:
        return global_var
    
class ClassPure(SuperClass):
    """contains pure functions only
    """
    def same_name(self) -> int:
        return 20
    
    def only_in_T(self) -> int:
        return 20
    
    def in_super_and_child_pure(self) -> int:
        return 20
    
    def in_super_and_child_impure(self) -> int:
        return 20
    
    def in_child_and_child_of_child_pure(self) -> int:
        return 20
    
    def in_child_and_child_of_child_impure(self) -> int:
        return 20
    

class ClassImpure(SuperClass):
    """contains impure functions only
    """
    def same_name(self) -> int:
        return global_var2
    
    def only_in_T(self) -> int:
        return global_var2
    
    def in_super_and_child_pure(self) -> int:
        return global_var2
    
    def in_super_and_child_impure(self) -> int:
        return global_var2

    def in_child_and_child_of_child_pure(self) -> int:
        return global_var2
    
    def in_child_and_child_of_child_impure(self) -> int:
        return global_var2

class ChildClassPure(ClassPure):
    """contains pure functions only
    """
    def only_in_child(self) -> int:
        return 30
    
    def in_child_and_child_of_child_pure(self) -> int:
        return 30
    
    def in_child_and_child_of_child_impure(self) -> int:
        return 30

class ChildClassImpure(ClassImpure):
    """contains impure functions only
    """
    def only_in_child(self) -> int:
        return global_var3
    
    def in_child_and_child_of_child_pure(self) -> int:
        return global_var3
    
    def in_child_and_child_of_child_impure(self) -> int:
        return global_var3