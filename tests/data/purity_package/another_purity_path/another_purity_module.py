global_var = 10
global_var2 = 20
global_var3 = 30
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
    
    def in_super_and_child_of_child_pure(self) -> int:
        return 10
    
    def in_super_and_child_of_child_impure(self) -> int:
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
    
    def in_super_and_child_of_child_pure(self) -> int:
        return 30
    
    def in_super_and_child_of_child_impure(self) -> int:
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
    
    def in_super_and_child_of_child_pure(self) -> int:
        return global_var3
    
    def in_super_and_child_of_child_impure(self) -> int:
        return global_var3