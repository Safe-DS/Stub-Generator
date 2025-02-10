from .another_purity_path.another_purity_module import ContextForWithTest, SuperClass, ClassPure, ClassImpure, ChildClassPure, ChildClassImpure, ClassWithNestedClassAsMember, AnotherPureClass, PureInitClass, PureSuperInit, ImpureInitClass, ImpureSuperInit, PureSuperInitFromKeyError
from . import another_purity_path
from . import test_init_py_pure


# purity analysis should categorize functions as pure, when their name suffix is "pure"
# else they should be categorized as impure
# check: tests\data\out\purity_package__api_purity.json after snapshot_update

def global_func_same_name_pure() -> int:
    child_class_instance: ChildClassPure = ChildClassPure()
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

def global_func_in_super_and_child_of_child_from_T_pure() -> int:
    instance = ClassPure()
    result = instance.in_super_and_child_of_child_pure()
    return result

def global_func_in_super_and_child_of_child_from_T_impure() -> int:
    """ 
        should be impure as ClassPure is a subtype of SuperClass and there in_super_and_child_of_child_impure is 
        impure 
    """
    instance = ClassPure()
    result = instance.in_super_and_child_of_child_impure()
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

# purity analysis seems to treat instanceVariable Read and write as impure

def global_func_nested_class_should_be_pure_but_impure() -> int:
    """
        member access is counted as impure in general, dataflow analysis could improve this
        .memberWithPureMethods
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.memberWithPureMethods.only_in_T()
    return result

def global_func_nested_class_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.memberWithImpureMethods.only_in_T()
    return result

def global_func_from_parameter_same_name_pure(instance: ClassPure) -> int:
    result = instance.same_name()
    return result

def global_func_from_parameter_same_name_impure(instance: ClassImpure) -> int:
    result = instance.same_name()
    return result

def global_func_from_parameter_same_name_nested_pure_but_impure(instance: ClassWithNestedClassAsMember) -> int:
    """
        member access is counted as impure in general and instance can be changed from outside the function
        .memberWithPureMethods
    """
    result = instance.memberWithPureMethods.same_name()
    return result

def global_func_from_parameter_same_name_nested_impure(instance: ClassWithNestedClassAsMember) -> int:
    result = instance.memberWithImpureMethods.same_name()
    return result

def global_func_nested_from_second_call_reference_pure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.return_class_pure().only_in_T()
    return result

def global_func_nested_from_second_call_reference_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.return_class_impure().only_in_T()
    return result

def global_func_nested_with_list_should_be_pure_but_impure() -> int:
    """
        member access is counted as impure in general, dataflow analysis could improve this, as here instance is created and not changed
        .listMemberWithPureMethods
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.listMemberWithPureMethods[0].only_in_T()
    return result

def global_func_nested_with_list_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.listMemberWithImpureMethods[0].only_in_T()
    return result

def global_func_nested_with_dict_should_be_pure_but_impure() -> int:
    """
        member access is counted as impure in general, dataflow analysis could improve this, as here instance is created and not changed
        .dictMemberWithPureMethods
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.dictMemberWithPureMethods["key"].only_in_T()
    return result

def global_func_nested_with_dict_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.dictMemberWithImpureMethods["key"].only_in_T()
    return result

def global_func_multiple_nested_member_should_be_pure_but_impure() -> int:
    """
        member access is counted as impure in general, dataflow analysis could improve this, as here instance is created and not changed
        .recursive
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.recursive.recursive.memberWithPureMethods.only_in_T()
    return result

def global_func_multiple_nested_member_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.recursive.recursive.memberWithImpureMethods.only_in_T()
    return result

def global_func_multiple_nested_methods_pure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.recursive_function().recursive_function().return_class_pure().only_in_T()
    return result

def global_func_multiple_nested_methods_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.recursive_function().recursive_function().return_class_impure().only_in_T()
    return result

def global_func_nested_method_from_super_pure() -> int:
    """
        function access is counted as pure, as it is assumed that functions wont be changed during runtime
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.only_in_super_nested_call_pure().only_in_T()
    return result

def global_func_nested_method_from_super_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.only_in_super_nested_call_impure().only_in_T()
    return result

def global_func_nested_member_from_super_impure() -> int:
    """
        member access is counted as impure in general, dataflow analysis could improve this, as here instance is created and not changed
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.super_member_pure.only_in_T()
    return result

def global_func_nested_member_from_super_impure2() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.super_member_impure.only_in_T()
    return result

def global_func_multiple_recursion_impure() -> int:
    """
        member access is counted as impure in general, dataflow analysis could improve this, as here instance is created and not changed
        .recursive. is the problem here
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.recursive_function().recursive.recursive_function().return_class_pure().only_in_T()
    return result

def global_func_multiple_recursion_impure2() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.recursive_function().recursive.recursive_function().return_class_impure().only_in_T()
    return result

def global_func_double_function_impure() -> int:
    """
        purity analysis cant analyze ()() and returns UNKNOWNCALL, references are found correctly
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.double_function_pure()()
    return result

def global_func_double_function_impure2() -> int:
    """
        purity analysis cant analyze ()() and returns UNKNOWNCALL, references are found correctly
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.double_function_impure()()
    return result

def global_func_return_pure_class() -> ClassPure:
    return ClassPure()

def global_func_start_with_function_pure() -> int:
    result = global_func_return_pure_class().only_in_T()
    return result

def global_func_return_impure_class() -> ClassImpure:
    return ClassImpure()

def global_func_start_with_function_impure() -> int:
    result = global_func_return_impure_class().only_in_T()
    return result

def global_func_start_with_list_pure() -> int:
    instances = [ClassPure()]
    result = instances[0].only_in_T()
    return result

def global_func_start_with_list_impure() -> int:
    instances = [ClassImpure()]
    result = instances[0].only_in_T()
    return result

def global_func_start_with_tuple_pure() -> int:
    instances = (ClassPure(),)
    result = instances[0].only_in_T()
    return result

def global_func_start_with_tuple_impure() -> int:
    instances = (ClassImpure(),)
    result = instances[0].only_in_T()
    return result

def global_func_start_with_dict_pure() -> int:
    instances = {"key": ClassPure()}
    result = instances["key"].only_in_T()
    return result

def global_func_start_with_dict_impure() -> int:
    instances = {"key": ClassImpure()}
    result = instances["key"].only_in_T()
    return result

# # TODO pm implement and test remaining cases, also test if there are multiple sources of type but different types, also add test cases, that have to use the boundary and enum type

def global_func_start_with_nested_type_pure() -> int:
    instances = {"key": [{"key2": ClassPure()}]}
    result = instances["key"][0]["key2"].only_in_T()
    return result

def global_func_start_with_nested_type_impure() -> int:
    instances = {"key": [{"key2": ClassImpure()}]}
    result = instances["key"][0]["key2"].only_in_T()
    return result

def global_helper_func_nested_type_pure_with_list_and_dict() -> dict[str, list[dict[str, ClassPure]]]:
    return {"key": [{"key2": ClassPure()}]}

def global_func_start_with_nested_type_and_function_pure() -> int:
    result = global_helper_func_nested_type_pure_with_list_and_dict()["key"][0]["key2"].only_in_T()
    return result

def global_helper_func_nested_type_impure_with_list_and_dict() -> dict[str, list[dict[str, ClassImpure]]]:
    return {"key": [{"key2": ClassImpure()}]}

def global_func_start_with_nested_type_and_function_impure() -> int:
    result = global_helper_func_nested_type_impure_with_list_and_dict()["key"][0]["key2"].only_in_T()
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

def global_func_from_docstring_as_list_same_name_pure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : list[ClassPure]
        Lorem ipsum
    """
    #fix
    result = instances[0].same_name()
    return result

def global_func_from_docstring_as_list_same_name_impure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : list[ClassImpure]
        Lorem ipsum
    """
    result = instances[0].same_name()
    return result

def global_func_from_docstring_as_tuple_same_name_pure(instances: tuple[AnotherPureClass]) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : tuple[ClassPure]
        Lorem ipsum
    """
    result = instances[0].same_name()
    return result

def global_func_from_docstring_as_tuple_same_name_impure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : tuple[ClassImpure]
        Lorem ipsum
    """
    result = instances[0].same_name()
    return result

def global_func_from_parameter_as_multiple_tuple_same_name_pure(instances: tuple[str, ClassPure]) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : tuple[str, ClassPure]
        Lorem ipsum
    """
    result = instances[1].same_name()
    return result

def global_func_from_parameter_as_multiple_tuple_same_name_impure(instances: tuple[str, ClassImpure]) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : tuple[str, ClassImpure]
        Lorem ipsum
    """
    result = instances[1].same_name()
    return result

def global_func_from_docstring_as_multiple_tuple_same_name_pure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : tuple[str, ClassPure]
        Lorem ipsum
    """
    result = instances[1].same_name()
    return result

def global_func_from_docstring_as_multiple_tuple_same_name_impure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : tuple[str, ClassImpure]
        Lorem ipsum
    """
    result = instances[1].same_name()
    return result

def global_func_from_docstring_as_dict_same_name_pure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : dict[str, ClassPure]
        Lorem ipsum
    """
    result = instances["key"].same_name()
    return result

def global_func_from_docstring_as_dict_same_name_impure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : dict[str, ClassImpure]
        Lorem ipsum
    """
    result = instances["key"].same_name()
    return result

def global_func_from_docstring_as_dict_with_union_same_name_pure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : dict[str, ClassPure | AnotherPureClass]
        Lorem ipsum
    """
    result = instances["key"].same_name()
    return result

def global_func_from_docstring_as_dict_with_union_same_name_impure(instances) -> int:
    """this function should be pure as same_name of ClassPure is pure

    Parameters
    --------
    instances : dict[str, ClassPure | ClassImpure]
        Lorem ipsum
    """
    result = instances["key"].same_name()
    return result

def global_func_union_type_pure(instance: ClassPure | AnotherPureClass) -> int:
    result = instance.same_name()
    return result

def global_func_union_type_impure(instance: ClassImpure | ClassPure) -> int:
    result = instance.only_in_T()
    return result

def global_func_union_type_from_docstring_pure(instance) -> int:
    """this function should be pure as only_in_T() from ClassPure and ChildClassPure are pure

    Parameters
    --------
    instance : ClassPure | AnotherPureClass
        Lorem ipsum
    """
    result = instance.only_in_T()
    return result

def global_func_union_type_from_docstring_impure(instance) -> int:
    """this function should be impure as only_in_T() from ClassImpure is impure

    Parameters
    --------
    instance : ClassPure | ClassImpure
        Lorem ipsum
    """
    result = instance.only_in_T()
    return result

def global_func_call_reference_in_index_pure() -> int:
    instance = ClassPure()
    dictionary = {}
    dictionary[instance.only_in_T()] = 10
    return dictionary[instance.only_in_T()]

def global_func_call_reference_in_index_impure() -> int:
    instance = ClassImpure()
    dictionary = {}
    dictionary[instance.only_in_T()] = 10
    return dictionary[instance.only_in_T()]

def global_func_self_pure() -> int:
    instance = ChildClassPure()
    result = instance.only_in_child_self()
    return result

def global_func_self_impure() -> int:
    instance = ChildClassImpure()
    result = instance.only_in_child_self()
    return result

def global_func_super_init_pure():
    instance = PureSuperInit().__init__()
    return instance

def global_func_super_init_impure():
    instance = ImpureSuperInit().__init__()
    return instance

def global_func_super_method_pure() -> int:
    instance = ChildClassPure()
    result = instance.super_same_name()
    return result

def global_func_super_method_impure() -> int:
    instance = ChildClassImpure()
    result = instance.super_same_name()
    return result

def global_func_super_nested_method_should_be_pure_but_impure() -> int:
    """
        is impure as .super_pure() has a member variable read 
    """
    instance = ClassWithNestedClassAsMember()
    result = instance.super_pure()
    return result

def global_func_super_nested_method_impure() -> int:
    instance = ClassWithNestedClassAsMember()
    result = instance.super_impure()
    return result

def global_func_super_from_builtin_keyError_pure() -> int:
    instance = PureSuperInitFromKeyError()
    return 10

def global_func_list_comprehension_generator_pure() -> list[int]:
    instance = ClassPure()
    result = [instance.same_name() for _ in range(10)]  
    return result

def global_func_list_comprehension_generator_impure() -> list[int]:
    instance = ClassImpure()
    result = [instance.same_name() for _ in range(10)]
    return result

def global_func_list_comprehension_with_if_generator_pure() -> list[int]:
    instance = ClassPure()
    result = [10 for _ in range(10) if instance.same_name() < 10]
    return result

def global_func_list_comprehension_with_if_generator_impure() -> list[int]:
    instance = ClassImpure()
    result = [10 for _ in range(10) if instance.same_name() < 10]
    return result

def global_func_list_comprehension_iterable_is_call_ref_pure() -> list[int]:
    instance = ClassPure()
    result = [10 for _ in range(instance.same_name())]
    return result

def global_func_list_comprehension_iterable_is_call_ref_impure() -> list[int]:
    instance = ClassImpure()
    result = [10 for _ in range(instance.same_name())]
    return result

def global_func_dict_comprehension_generator_pure() -> dict[int, int]:
    instance = ClassPure()
    result = {instance.same_name(): 10 for _ in range(10)}
    return result

def global_func_dict_comprehension_generator_impure() -> dict[int, int]:
    instance = ClassImpure()
    result = {instance.same_name(): 10 for _ in range(10)}
    return result

def global_func_dict_comprehension_with_if_generator_pure() -> dict[int, int]:
    instance = ClassPure()
    result = {10: i for i in range(10) if instance.same_name() < 10}
    return result

def global_func_dict_comprehension_with_if_generator_impure() -> dict[int, int]:
    instance = ClassImpure()
    result = {10: i for i in range(10) if instance.same_name() < 10}
    return result

def global_func_dict_comprehension_iterable_is_call_ref_pure() -> dict[int, int]:
    instance = ClassPure()
    result = {10: i for i in range(instance.same_name())}
    return result

def global_func_dict_comprehension_iterable_is_call_ref_impure() -> dict[int, int]:
    instance = ClassImpure()
    result = {10: i for i in range(instance.same_name())}
    return result

def global_func_set_comprehension_generator_pure() -> set[int]:
    instance = ClassPure()
    result = {instance.same_name() for _ in range(10)}
    return result

def global_func_set_comprehension_generator_impure() -> set[int]:
    instance = ClassImpure()
    result = {instance.same_name() for _ in range(10)}
    return result

def global_func_set_comprehension_with_if_generator_pure() -> set[int]:
    instance = ClassPure()
    result = {i for i in range(10) if instance.same_name() < 10}
    return result

def global_func_set_comprehension_with_if_generator_impure() -> set[int]:
    instance = ClassImpure()
    result = {i for i in range(10) if instance.same_name() < 10}
    return result

def global_func_set_comprehension_iterable_is_call_ref_pure() -> set[int]:
    instance = ClassPure()
    result = {i for i in range(instance.same_name())}
    return result

def global_func_set_comprehension_iterable_is_call_ref_impure() -> set[int]:
    instance = ClassImpure()
    result = {i for i in range(instance.same_name())}
    return result

def global_func_operator_expression_should_be_pure_but_impure():
    """
        in OpExpr mypy doesnt store the type, this seems to be a bug
    """
    instance = ClassPure()
    result = (instance.same_name() + instance.same_name())
    return result

def global_func_isinstance_check_should_be_pure_but_impure(instance: object):
    """
        isinstance checks dont update the ast correctly
    """
    if isinstance(instance, ClassPure):
        result = instance.same_name()
        return result

def global_func_isinstance_check_impure(instance: object):
    """
        isinstance checks dont update the ast correctly
    """
    if isinstance(instance, ClassImpure):
        result = instance.same_name()
        return result
    
def global_func_closure_pure():
    def closure():
        return 0
    closure()

def global_func_closure_should_be_pure_but_impure():
    """
        impure because the receiver of instance.same_name() has any type
        mypy some how cant infer the type here, seems to be a bug?
    """
    def closure():
        instance = ClassPure()
        instance.same_name()  # instance has type any
    closure()

def global_func_closure_impure():
    def closure():
        instance = ClassImpure()
        instance.same_name()
    closure()

def global_func_call_another_global_func_pure():
    global_func_same_name_pure()

def global_func_call_another_global_func_impure():
    global_func_same_name_impure()

# def global_func_builtin():
#     return len([]).to_bytes()

def global_func_call_ref_in_dict_generation_should_be_pure_but_impure():
    """
        mypy bug, as there is no type info in mypy ast for the call ref instance.same_name()
    """
    instance = ClassPure()
    return {"foo": instance.same_name()}

def global_func_call_ref_in_dict_generation_impure():
    instance = ClassImpure()
    return {"foo": instance.same_name()}

def global_func_init_import_pure():
    return another_purity_path.test_init_py_pure()

def global_func_init_import_impure():
    return another_purity_path.test_init_py_impure()

def global_func_import_global_func_impure():
    return test_init_py_pure()

def global_func_module_class_with_static_method_pure():
    return another_purity_path.ClassWithPureStaticMethods.test()

def global_func_module_class_with_static_method_impure():
    return another_purity_path.ClassWithImpureStaticMethods.test()

def global_func_unreachable_code_should_be_pure_but_impure():
    """
        mypy doesnt track the type if code is unreachable
    """
    if False:
        instance = ClassPure()
        return instance.same_name()

def global_func_unreachable_code_impure():
    """
        mypy doesnt track the type if code is unreachable
    """
    if False:
        instance = ClassImpure()
        return instance.same_name()
    
def global_func_inside_of_lambda_with_map_should_be_pure_but_impure():
    """
        mypy doesnt store the type inside of lambda bodies
    """
    instances = [ClassPure()]
    test = map(lambda x: x.same_name(), instances)
    return test

def global_func_inside_of_lambda_with_map_impure():
    instances = [ClassImpure()]
    test = map(lambda x: x.same_name(), instances)
    return test

def global_func_operator_receiver_with_brackets_should_be_pure_but_impure():
    """
        Solution: look into the type of instance1 and retrieve the return type of __add__ which then is the receiver of .same_name()
        but actually  mypy should have the type stored in method_type attribute of OpExpr
    """
    instance1 = ClassPure()
    instance2 = ClassPure()
    return ((instance1 + instance2)
            .same_name())

def global_func_operator_receiver_with_brackets_impure():
    instance1 = ClassImpure()
    instance2 = ClassImpure()
    return ((instance1 + instance2)
            .same_name())

def global_func_with_keyword_should_be_pure_but_impure():
    """
        mypy doesnt track the type if code is in with block...
    """
    with ContextForWithTest() as context:
        instance = ClassPure()
        return instance.same_name()

def global_func_with_keyword_impure():
    with ContextForWithTest() as context:
        instance = ClassImpure()
        return instance.same_name()
        

# TODO pm these functions create this error src\safeds_stubgen\stubs_generator\_generate_stubs.py:128: in _create_outside_package_class
#     module_name = path_parts[-1]
# E   IndexError: list index out of range
# def global_func_tuple_access_pure(instance: tuple[ClassPure, AnotherPureClass, ClassImpure]):
#     result = instance[1].same_name()
#     return result

# def global_func_tuple_access_impure(instance: tuple[ClassPure, AnotherPureClass, ClassImpure]):
#     result = instance[2].same_name()
#     return result

# def global_func_tuple_access_unknown_index_impure(instance: tuple[ClassPure, ClassImpure], index: int):
#     result = instance[0].same_name()
#     return result

# TODO pm add testcases where the index of a tuple is not known or where we have a path where union type is used