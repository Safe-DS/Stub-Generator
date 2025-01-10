from typing import Callable


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
    
    def only_in_child_self(self) -> int:
        result = self.same_name()
        return result
    
    def super_same_name(self) -> int:
        result = super().same_name()
        return result

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
    
    def only_in_child_self(self) -> int:
        result = self.same_name()
        return result
    
    def super_same_name(self) -> int:
        result = super().same_name()
        return result
    

class SuperWithNestedClassAsMember:
    def __init__(self) -> None:
        self.super_member_pure: ClassPure = ClassPure()
        self.super_member_impure: ClassImpure = ClassImpure()

    def only_in_super_nested_call_pure(self) -> ClassPure:
        return ClassPure()

    def only_in_super_nested_call_impure(self) -> ClassImpure:
        return ClassImpure()

class ClassWithNestedClassAsMember(SuperWithNestedClassAsMember):
    def __init__(self):
        self.memberWithPureMethods: ClassPure = ClassPure()
        self.memberWithImpureMethods: ClassImpure = ClassImpure()
        self.memberWithPureMethodsWithoutTypeHint = ClassPure()
        self.memberWithImpureMethodsWithoutTypeHint = ClassImpure()
        self.listMemberWithPureMethods: list[ClassPure] = [ClassPure()]
        self.listMemberWithImpureMethods: list[ClassImpure] = [ClassImpure()]
        self.dictMemberWithPureMethods: dict[str, ClassPure] = {"key": ClassPure()}
        self.dictMemberWithImpureMethods: dict[str, ClassImpure] = {"key": ClassImpure()}
        self.recursive: ClassWithNestedClassAsMember = ClassWithNestedClassAsMember()

    def return_class_impure(self) -> ClassImpure:
        return ClassImpure()
    
    def return_class_pure(self) -> ClassPure:
        return ClassPure()
    
    def recursive_function(self) -> ClassWithNestedClassAsMember: # type: ignore
        return ClassWithNestedClassAsMember()
    
    def double_function_pure(self) -> Callable[[], int]:
        return lambda: 10
    
    def double_function_impure(self) -> Callable[[], int]:
        return lambda: global_var
    
    def super_impure(self) -> int:
        result = super().super_member_impure.same_name()
        return result
    
    def super_pure(self) -> int:
        result = super().super_member_pure.same_name()
        return result


class AnotherPureClass:
    def __init__(self):
        pass

    def same_name(self):
        return 21

class PureInitClass:
    def __init__(self):
        result = 10

class ImpureInitClass:
    def __init__(self):
        self.test = global_var

class PureSuperInit(PureInitClass):
    def __init__(self):
        super().__init__()

class ImpureSuperInit(ImpureInitClass):
    def __init__(self):
        super().__init__()

class PureSuperInitFromKeyError(KeyError):
    def __init__(self):
        super().__init__()