from .another_purity_path.another_purity_module import SuperClass, ClassPure, ClassImpure, ChildClassPure, ChildClassImpure

# purity analysis should categorize functions as pure, when their name suffix is "pure"
# else they should be categorized as impure
# check: tests\data\out\purity_package__api_purity.json after snapshot_update

def global_func_same_name_pure() -> int:
    child_class_instance = ChildClassPure()
    result = child_class_instance.same_name()
    return result

def global_func_same_name_impure() -> int:
    child_class_instance = ChildClassImpure()
    result = child_class_instance.same_name()  # call reference to impure function
    return result

def global_func_only_in_T_pure() -> int:  
    """
        improved purity analysis should reference function only_in_T() of ClassPure 
        and not only_in_T() of ClassImpure as well
    """
    instance = ClassPure()
    result = instance.only_in_T()
    return result

def global_func_only_in_T_impure() -> int:
    instance = ClassImpure()
    result = instance.only_in_T()
    return result

def global_func_only_in_T_from_Child_pure() -> int:  
    instance = ChildClassPure()
    result = instance.only_in_T()
    return result

def global_func_only_in_T_from_Child_impure() -> int:
    instance = ChildClassImpure()
    result = instance.only_in_T()
    return result

def global_func_only_in_Child_pure() -> int:
    instance = ChildClassPure()
    result = instance.only_in_child()
    return result

def global_func_only_in_Child_impure() -> int:
    instance = ChildClassImpure()
    result = instance.only_in_child()
    return result

def global_func_only_in_super_from_T_pure() -> int:
    instance = ClassPure()
    result = instance.only_in_super_pure()
    return result

def global_func_only_in_super_from_T_impure() -> int:
    instance = ClassPure()
    result = instance.only_in_super_impure()
    return result

def global_func_only_in_super_from_child_pure() -> int:
    instance = ChildClassPure()
    result = instance.only_in_super_pure()
    return result

def global_func_only_in_super_from_child_impure() -> int:
    instance = ChildClassPure()
    result = instance.only_in_super_impure()
    return result

def global_func_in_super_and_child_from_super_impure() -> int:
    """
        this call is impure as ClassImpure also has in_super_and_child_pure() which is impure
        ClassImpure is a child of SuperClass
    """
    instance = SuperClass()
    result = instance.in_super_and_child_pure()
    return result

def global_func_in_super_and_child_from_T_pure() -> int:
    instance = ClassPure()
    result = instance.in_super_and_child_pure()
    return result

def global_func_in_super_and_child_from_T_impure() -> int:
    instance = ClassImpure()
    result = instance.in_super_and_child_impure()
    return result

def global_func_in_child_and_child_of_child_from_T_pure() -> int:
    """
        pure function, as instance is of type ClassPure, which has ChildClassPure as child
        there no function is impure and so the purity analysis should only find 
        referenced functions which are pure
    """
    instance = ClassPure()
    result = instance.in_child_and_child_of_child_pure() + instance.in_child_and_child_of_child_impure()
    return result

def global_func_in_child_and_child_of_child_from_T_impure() -> int:
    instance = ClassImpure()
    result = instance.in_child_and_child_of_child_impure() + instance.in_child_and_child_of_child_pure()
    instance.only_in_super_impure()
    return result

def global_func_in_child_and_child_of_child_from_child_of_child_pure() -> int:
    instance = ChildClassPure()
    result = instance.in_child_and_child_of_child_pure() + instance.in_child_and_child_of_child_impure()
    return result

def global_func_in_child_and_child_of_child_from_child_of_child_impure() -> int:
    instance = ChildClassImpure()
    result = instance.in_child_and_child_of_child_impure() + instance.in_child_and_child_of_child_pure()
    return result

def global_func_all_functions_pure() -> int:
    instance = ChildClassPure()
    if True:
        instance.only_in_child()
    if False:
        pass
    else:
        instance.in_child_and_child_of_child_pure()
    for x in range(1):
        instance.only_in_T()
    instance.only_in_super_pure()
    instance.in_super_and_child_pure()
    instance.same_name()
    return 10

def global_func_find_deeply_nested_function_impure() -> int:
    instance = ClassImpure()
    if True:
        while True:
            if False:
                pass
            elif True:
                for x in range(1):
                    try:
                        instance.only_in_super_pure()
                    except NameError:
                        if False:
                            pass
                        else:
                            instance.only_in_T()
            break
    return 10                

def global_func_from_parameter_same_name_pure(instance: ClassPure) -> int:
    result = instance.same_name()
    return result

def global_func_from_parameter_same_name_impure(instance: ClassImpure) -> int:
    result = instance.same_name()
    return result

def global_func_from_docstring_same_name_pure(instance) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instance : ClassPure
        Lorem ipsum
    """
    result = instance.same_name()
    return result

def global_func_from_docstring_same_name_impure(instance) -> int:
    """this function should be pure as same_name of ClassImpure is impure

    Parameters
    --------
    instance : ClassImpure
        Lorem ipsum
    """
    result = instance.same_name()
    return result