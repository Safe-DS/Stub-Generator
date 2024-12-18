from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, get_args, get_origin, Union

import mypy.build as mypy_build
import mypy.main as mypy_main
from mypy import nodes as mypy_nodes
from mypy import types as mypy_types

from safeds_stubgen.api_analyzer._type_source_enums import TypeSourcePreference, TypeSourceWarning
from safeds_stubgen.api_analyzer._types import AbstractType, CallableType, DictType, FinalType, ListType, NamedSequenceType, NamedType, SetType, TupleType, UnionType
from safeds_stubgen._evaluation import ApiEvaluation
from safeds_stubgen.docstring_parsing import DocstringStyle, create_docstring_parser

from ._api import API, Attribute, CallReference, Function, Class
from ._ast_visitor import MyPyAstVisitor
from ._ast_walker import ASTWalker
from ._package_metadata import distribution, distribution_version

if TYPE_CHECKING:
    from pathlib import Path


def get_api(
    root: Path,
    docstring_style: DocstringStyle = DocstringStyle.PLAINTEXT,
    is_test_run: bool = False,
    type_source_preference: TypeSourcePreference = TypeSourcePreference.CODE,
    type_source_warning: TypeSourceWarning = TypeSourceWarning.WARN,
    evaluation: ApiEvaluation | None = None
) -> API:
    """Parse a given code package with Mypy, walk the Mypy AST and create an API object."""
    init_roots = _get_nearest_init_dirs(root)
    if len(init_roots) == 1:
        root = init_roots[0]

    logging.info("Started gathering the raw package data with Mypy.")

    walkable_files = []
    package_paths = []
    for file_path in root.glob(pattern="./**/*.py"):
        # Check if the current path is a test directory
        if not is_test_run and ("test" in file_path.parts or "tests" in file_path.parts or "docs" in file_path.parts):
            log_msg = f"Skipping test file in {file_path}"
            logging.info(log_msg)
            continue

        # Check if the current file is an init file
        if file_path.parts[-1] == "__init__.py":
            # if a directory contains an __init__.py file it's a package
            package_paths.append(
                str(file_path.parent),
            )
            continue

        walkable_files.append(str(file_path))

    if not walkable_files:
        raise ValueError("No files found to analyse.")

    # Package name
    package_name = root.stem

    # Get distribution data
    dist = distribution(package_name=package_name) or ""
    dist_version = distribution_version(dist=dist) or ""

    # Get mypy ast and aliases
    build_result = _get_mypy_build(files=walkable_files)
    mypy_asts = _get_mypy_asts(build_result=build_result, files=walkable_files, package_paths=package_paths)
    aliases = _get_aliases(result_types=build_result.types, package_name=package_name)

    # Setup api walker
    path_to_package = ""
    if is_test_run and evaluation is not None:
        path_to_package = f"tests/data/{dist}"
    api = API(distribution=dist, package=package_name, version=dist_version, path_to_package=path_to_package)
    docstring_parser = create_docstring_parser(style=docstring_style, package_path=root)
    callable_visitor = MyPyAstVisitor(
        docstring_parser=docstring_parser,
        api=api,
        aliases=aliases,
        type_source_preference=type_source_preference,
        type_source_warning=type_source_warning,
        evaluation=evaluation
    )
    walker = ASTWalker(handler=callable_visitor)

    for tree in mypy_asts:
        walker.walk(tree=tree)

    api = callable_visitor.api
    _update_class_subclass_relation(api)
    _find_correct_type_by_path_to_call_reference(api)
    _find_all_referenced_functions_for_all_call_references(api)

    return api

def _update_class_subclass_relation(api: API) -> None:
    """
        For each class, updates each superclass by appending the id of the class to subclasses list of the superclass

        Parameters
        ----------
        api : API
            Stores api data of analyzed package
    """
    for class_def in api.classes.values():
        super_classes: list[Class] = []
        for super_class_id in class_def.superclasses:
            class_to_append = api.classes.get("/".join(super_class_id.split(".")), None)
            if class_to_append is None:  # super class imported from outside of the analyzed package
                continue
            super_classes.append(class_to_append)
        for super_class in super_classes:
            super_class.subclasses.append(class_def.id)

def _get_named_types_from_nested_type(nested_type: AbstractType) -> list[NamedType] | None:
    """
        Iterates through a nested type recursively, to find a NamedType

        Parameters
        ----------
        nested_type : AbstractType
            Abstract class for types
        
        Returns
        ----------
        type : list[NamedType] | None
    """
    if isinstance(nested_type, NamedType):
        return [nested_type]
    elif isinstance(nested_type, ListType):
        return _get_named_types_from_nested_type(nested_type.types[0])  # a list can only have one type
    elif isinstance(nested_type, NamedSequenceType):
        return _get_named_types_from_nested_type(nested_type.types[0])  # can only have one type
    elif isinstance(nested_type, DictType):
        return _get_named_types_from_nested_type(nested_type.value_type)
    elif isinstance(nested_type, SetType):
        return _get_named_types_from_nested_type(nested_type.types[0])  # a set can only have one type 
    elif isinstance(nested_type, FinalType):
        return _get_named_types_from_nested_type(nested_type.type_)
    elif isinstance(nested_type, CallableType):
        return _get_named_types_from_nested_type(nested_type.return_type)
    elif isinstance(nested_type, UnionType):
        result = []
        for type in nested_type.types:
            extracted_types = _get_named_types_from_nested_type(type)
            if extracted_types is None:
                continue
            result.extend(extracted_types)
        return result
    elif isinstance(nested_type, TupleType):
        result = []
        for type in nested_type.types:
            extracted_types = _get_named_types_from_nested_type(type)
            if extracted_types is None:
                continue
            result.extend(extracted_types)
        return result

    for member_name in dir(nested_type):
        if not member_name.startswith("__"):
            member = getattr(nested_type, member_name)
            if isinstance(member, AbstractType):
                return _get_named_types_from_nested_type(member)
            elif isinstance(member, list) and len(member) > 0 and isinstance(member[0], AbstractType):
                types: list[NamedType] = []
                for type in member:
                    named_type = _get_named_types_from_nested_type(type)
                    if named_type is not None:
                        types.extend(named_type)
                return list(filter(lambda type: not type.qname.startswith("builtins"), list(set(types))))


def _find_attribute_in_class_and_super_classes(api: API, attribute_name: str, current_class: Class) -> Attribute | None:
    attribute = list(filter(lambda attribute: attribute.name == attribute_name, current_class.attributes))
    if len(attribute) != 1:
        # look in superclass
        for super_class_name in current_class.superclasses:
            super_class = api.classes.get("/".join(super_class_name.split(".")))
            if super_class is None:
                continue
            attribute = _find_attribute_in_class_and_super_classes(api, attribute_name, super_class)
            if attribute is not None:
                return attribute
        return None
    attribute = attribute[0]
    return attribute

def _find_method_in_class_and_super_classes(api: API, method_name: str, current_class: Class) -> Function | None:
    method = list(filter(lambda method: method.name == method_name, current_class.methods))
    if len(method) != 1:
        # look in superclass
        for super_class_name in current_class.superclasses:
            super_class = api.classes.get("/".join(super_class_name.split(".")))
            if super_class is None:
                continue
            method = _find_method_in_class_and_super_classes(api, method_name, super_class)
            if method is not None:
                return method
        return None
    method = method[0]
    return method

def _find_correct_type_by_path_to_call_reference(api: API):
    """
        Call references can be nested, for example: "instance.attribute.method()" or "instance.method().method2()" etc.
        Therefore the call_reference type stores a path of the names to the call. The path is of type: list[str]
        
        For each call reference of each function, the correct class is attempted to be found,
        by iterating through the path which is stored in the call_reference class.
        For each string of the path, it is first assumed, that the string is the name of an attribute of the 
        current class. If there is no attribute with the string of the path as name, then it is assumed
        that the string is the name of a method. For either attribute or method, we try to find the next 
        class along the path, until the the end of the path to the call reference is reached.

        Parameters:
        ----------
        api : API
            Stores api data of analyzed package
    """
    for function in api.functions.values():
        for call_reference in function.body.call_references.values():
            type = call_reference.receiver.type
            classes: list[Class | Any] | None = []
            if isinstance(type, list):
                if isinstance(type[0], NamedType):
                    for t in type:
                        class_of_receiver = api.classes.get("/".join(t.qname.split(".")))
                        if class_of_receiver is None:
                            continue
                        classes.append(class_of_receiver)
                elif api.classes.get("/".join(type[0].type.fullname.split("."))) is not None:
                    for t in type:
                        class_of_receiver = api.classes.get("/".join(t.type.fullname.split(".")))
                        if class_of_receiver is None:
                            continue
                        classes.append(class_of_receiver)
                else:
                    classes.append(type)

            elif isinstance(type, NamedType):
                class_of_receiver = api.classes.get("/".join(type.qname.split(".")))
                if class_of_receiver is None:
                    continue
                classes.append(class_of_receiver)
            elif hasattr(type, "type") and api.classes.get("/".join(type.type.fullname.split("."))) is not None:
                class_of_receiver = api.classes.get("/".join(type.type.fullname.split(".")))
                if class_of_receiver is None:
                    continue
                classes.append(class_of_receiver)
            elif isinstance(type, str):
                class_of_receiver = api.classes.get("/".join(type.split(".")))
                if class_of_receiver is None:
                    continue
                call_reference.receiver.found_classes.append(class_of_receiver)
                # if call_reference.isSuperCallRef:
                #     super_classes = class_of_receiver.superclasses
                # classes.append(class_of_receiver)
            else:  # type is tuple or dict
                classes.append(type)
            
            if not call_reference.isSuperCallRef:
                for classs in classes:
                    _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, classs, call_reference.receiver.path_to_call_reference, 0)

def _find_correct_types_by_path_to_call_reference_recursively(api: API, call_reference: CallReference, type_of_receiver: Class | Any, path: list[str], depth: int):
    path_copy = path.copy()
    part = path_copy.pop()

    if type_of_receiver is None:
        return
    if depth == 0:  
        # first part of path is a variable name etc so we can skip 
        _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type_of_receiver, path_copy, depth + 1)
        return 
    if part == "()":  
        # return type is found below in except KeyError block
        _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type_of_receiver, path_copy, depth + 1)
        return 
    if part.startswith("[") and part.endswith("]"):
        if isinstance(type_of_receiver, tuple):
            key = part.removeprefix("[").removesuffix("]")
            if key == "":
                for type in type_of_receiver:
                    _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type, path, depth)
                return
            else:
                type_of_receiver = type_of_receiver[int(key)]
        elif hasattr(type_of_receiver, "args") and len(type_of_receiver.args) == 1:  # type: ignore | list
            type_of_receiver = type_of_receiver.args[0]  # type: ignore
        elif hasattr(type_of_receiver, "args") and len(type_of_receiver.args) == 2:  # type: ignore | dictionary
            type_of_receiver = type_of_receiver.args[1]  # type: ignore
        elif isinstance(type_of_receiver, list):
            type_of_receiver = type_of_receiver[0]
        elif isinstance(type_of_receiver, dict):
            type_of_receiver = type_of_receiver[1]

        if not isinstance(type_of_receiver, Class):
            # here we get the correct class from namedType etc if possible
            if isinstance(type_of_receiver, NamedType):
                class_of_receiver = api.classes.get("/".join(type_of_receiver.qname.split(".")))
                if class_of_receiver is not None:
                    type_of_receiver = class_of_receiver
            elif hasattr(type_of_receiver, "type") and api.classes.get("/".join(type_of_receiver.type.fullname.split("."))) is not None:
                class_of_receiver = api.classes.get("/".join(type_of_receiver.type.fullname.split(".")))
                if class_of_receiver is not None:
                    type_of_receiver = class_of_receiver
            else:  # type_of_receiver is not a class 
                pass
        _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type_of_receiver, path_copy, depth + 1)
        return


    if not isinstance(type_of_receiver, Class):  # as from here on, type_of_receiver needs to be of type Class
        if (isinstance(type_of_receiver, list)):
            for type in type_of_receiver:
                _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type, path, depth)
            return
        elif isinstance(type_of_receiver, NamedType):
            class_of_receiver = api.classes.get("/".join(type_of_receiver.qname.split(".")))
            if class_of_receiver is not None:
                type_of_receiver = class_of_receiver
        elif hasattr(type_of_receiver, "type") and api.classes.get("/".join(type_of_receiver.type.fullname.split("."))) is not None:
            class_of_receiver = api.classes.get("/".join(type_of_receiver.type.fullname.split(".")))
            if class_of_receiver is not None:
                type_of_receiver = class_of_receiver
        elif hasattr(type_of_receiver, "__origin__") and type_of_receiver.__origin__ is Union:
            for type in get_args(type_of_receiver):
                _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type, path, depth)
            return
        elif isinstance(type_of_receiver, AbstractType):
            type_of_receiver = _get_named_types_from_nested_type(type_of_receiver)
            for type in get_args(type_of_receiver):
                _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type, path, depth)
            return
        else:
            return

    try:  # assume the part of the path is a name of a member 
        attribute_name = part
        attribute = _find_attribute_in_class_and_super_classes(api, attribute_name, type_of_receiver)  
        if attribute is None:
            raise KeyError()
        type_of_attribute = attribute.type
        if type_of_attribute is None:
            print("missing type info!")
            return

        # attribute can be object (class), list, tuple or dict so we need to extract the namedType from nested types
        types = _get_named_types_from_nested_type(type_of_attribute)
        if types is None:
            print("NamedType not found")
            return

        for type in types:
            found_class = api.classes.get("/".join(type.qname.split(".")))
            if found_class is None:
                print(f"Class {type.name} not found")
                call_reference.receiver.found_classes = []
                return
            type_of_receiver = found_class
            _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type, path_copy, depth + 1)
        return  # next class found, check next part of path

    except KeyError:  # current part of path was not a member so we assume its a method
        is_last_method = all(item == "()" for item in path_copy)  # maybe we need to check for [] as well
        if is_last_method:  # here we have "method()" or "method()()"
            if type_of_receiver is not None and isinstance(type_of_receiver, Class):
                call_reference.receiver.found_classes.append(type_of_receiver)
            return
        else:  # here we have something like this "method1().method2()" or "method1().member.method2()" or "method()[0].member.method2()" or "method()()"
            method_name = part
            method = _find_method_in_class_and_super_classes(api, method_name, type_of_receiver)
            if method is None:
                print(f"Method {method_name} and Attribute {attribute_name} not found in class {type_of_receiver.name} and superclasses!")
                return

            result = method.results[0]  # in this case there can only be one result
            if result.type is None:
                print(f"Result {result.name} has type None")
                return

            # get NamedType from result
            types = _get_named_types_from_nested_type(result.type)  # will find the type of expressions like "method()[0]"
            if types is None:
                print("NamedType not found")
                return

            for type in types:
                found_class = api.classes.get("/".join(type.qname.split(".")))
                if found_class is None:
                    print(f"Class {type.name} not found")
                    call_reference.receiver.found_classes = []
                    return 
                type_of_receiver = found_class
                _find_correct_types_by_path_to_call_reference_recursively(api, call_reference, type, path_copy, depth + 1)

            return  # next class found, check next part of path

def _find_all_referenced_functions_for_all_call_references(api: API) -> None:
    """
        Once the correct receiver type was found in _find_correct_type_by_path_to_call_reference,
        all possibly referenced functions for each call references need to be found by this function. 

        For that, found class of each call reference is accessed, if its None, the possibly referenced
        functions for this call reference will be empty. If they are empty, the purity analysis will 
        fall back to using a list of all functions with the same name as possibly referenced functions.

        The possibly referenced functions can also be functions of the subclasses or superclasses.
        Therefore we also need to check the superclasses, if the type of the receiver doesnt have the 
        function. If the type has subtypes, we need to search for the function in each subtype.

        Parameters:
        ----------
        api : API
            Stores api data of analyzed package
    """
    for function in api.functions.values():
        for call_reference in function.body.call_references.values():
            # use found class of _find_correct_type_by_path_to_call_reference if not None
            if call_reference.receiver.found_classes is None or len(call_reference.receiver.found_classes) == 0:
                continue
            else:
                current_classes = call_reference.receiver.found_classes

            for current_class in current_classes:
                # check if specified class has method with name of callreference
                if not call_reference.isSuperCallRef:
                    specified_class_has_method = False
                    methods = current_class.methods
                    for method in methods:
                        if method.name == call_reference.function_name:
                            specified_class_has_method = True
                            break  # as there can only be one method of that name in a python class
                    
                    referenced_functions: list[Function] = []
                    _get_referenced_functions_from_class_and_subclasses(
                        api, 
                        call_reference,
                        current_class.id,
                        [],
                        referenced_functions
                    )

                if not specified_class_has_method or call_reference.isSuperCallRef:  # then python will look for method in super but so we have to do that as well
                # find function in superclasses but only first appearance as python will also only call the first appearance
                    try:
                        super_classes: list[Class] = []
                        # for super_class_id in current_class.superclasses:
                        #     api.classes
                        #     super_class = filter(lambda class_id: class_id.endswith(api.package + "/".join(super_class_id.split("."))), api.classes.keys())
                        for super_class_id in current_class.superclasses:
                            correct_id = "/".join(super_class_id.split("."))
                            if correct_id.startswith(api.path_to_package):
                                super_class = api.classes.get(correct_id, None)
                                if super_class is not None:
                                    super_classes.append(super_class)
                            else:
                                correct_id = api.path_to_package + "/" + correct_id
                                super_class = api.classes.get(correct_id, None)
                                if super_class is not None:
                                    super_classes.append(super_class)
                        # super_classes = [api.classes["/".join(x.split("."))] for x in current_class.superclasses]
                    except KeyError as error:
                        print(error)
                    _get_referenced_function_from_super_classes(
                        api,
                        call_reference,
                        super_classes,
                        referenced_functions
                    )

                call_reference.possibly_referenced_functions.extend(referenced_functions)

def _get_referenced_function_from_super_classes(
    api: API, 
    call_reference: CallReference, 
    super_classes: list[Class], 
    referenced_functions: list[Function]
) -> None:
    """
        finds the first referenced function in super classes recursively

        Parameters
        ----------
        api : API
            Stores api data of analyzed package
        call_reference : CallReference
            The call reference
        super_classes : list[Class]
            The super classes of the type of the receiver of the super class or of those super classes
        referenced_functions : list[Function]
            Passed along recursion to store all possibly referenced functions
    """
    for super_class in super_classes:
        found_method = False
        for method in super_class.methods:
            if method.name == call_reference.function_name:
                referenced_functions.append(method)
                found_method = True
                break
        if found_method:
            break
        else: 
            try:
                next_super_classes: list[Class] = []
                # for super_class_id in current_class.superclasses:
                #     api.classes
                #     super_class = filter(lambda class_id: class_id.endswith(api.package + "/".join(super_class_id.split("."))), api.classes.keys())
                for next_super_class_id in super_class.superclasses:
                    correct_id = "/".join(next_super_class_id.split("."))
                    if correct_id.startswith(api.path_to_package):
                        next_super_class = api.classes.get(correct_id, None)
                        if next_super_class is not None:
                            next_super_classes.append(next_super_class)
                    else:
                        correct_id = api.path_to_package + "/" + correct_id
                        next_super_class = api.classes.get(correct_id, None)
                        if next_super_class is not None:
                            next_super_classes.append(next_super_class)
                # super_classes = [api.classes["/".join(x.split("."))] for x in current_class.superclasses]
            except KeyError as error:
                print(error)
            # next_super_classes = [api.classes["/".join(x.split("."))] for x in super_class.superclasses]
            _get_referenced_function_from_super_classes(
                api,
                call_reference,
                next_super_classes,
                referenced_functions
            )

def _get_referenced_functions_from_class_and_subclasses(
    api: API, 
    call_reference: CallReference, 
    current_class_id: str, 
    visited_classes: list[str], 
    referenced_functions: list[Function]
) -> None:
    """
        Finds all additional function defs with same name in sub classes recursively, as they could also be called

        Parameters
        ----------
        api : API
            Stores api data of analyzed package
        call_reference : CallReference
            The call reference
        current_class_id : str
            The id of the current class, which has the sub classes
        visited_classes : list[str]
            Stores visited class ids, so that we dont visit classes twice, during recursion
        referenced_functions : list[Function]
            Passed along recursion to store all possibly referenced functions
    """
    # find all additional function defs with same name in sub classes as they could also be called
    if current_class_id in visited_classes:
        return
    current_class = api.classes[current_class_id]
    visited_classes.append(current_class_id)
    methods = current_class.methods
    for method in methods:
        if method.name == call_reference.function_name:
            referenced_functions.append(method)
            break  # as there can only be one method of that name in a python class

    if len(current_class.subclasses) != 0:
        for subclass in current_class.subclasses:
            _get_referenced_functions_from_class_and_subclasses(
                api, 
                call_reference,
                subclass,
                visited_classes,
                referenced_functions
            )

def _get_nearest_init_dirs(root: Path) -> list[Path]:
    """Check for the nearest directory with an __init__.py file.

    For the Mypy parser we need to start at a directory with an __init__.py file. Directories without __init__.py files
    will be skipped py Mypy.
    """
    all_inits = list(root.glob("./**/__init__.py"))
    shortest_init_paths = []
    shortest_len = -1
    for init in all_inits:
        path_len = len(init.parts)
        if shortest_len == -1:
            shortest_len = path_len
            shortest_init_paths.append(init.parent)
        elif path_len <= shortest_len:  # pragma: no cover
            if path_len == shortest_len:
                shortest_init_paths.append(init.parent)
            else:
                shortest_len = path_len
                shortest_init_paths = [init.parent]

    return shortest_init_paths


def _get_mypy_build(files: list[str]) -> mypy_build.BuildResult:
    """Build a mypy checker and return the build result."""
    mypyfiles, opt = mypy_main.process_options(files)

    # Disable the memory optimization of freeing ASTs when possible
    opt.preserve_asts = True
    # Only check parts of the code that have changed since the last check
    opt.fine_grained_incremental = True
    # Export inferred types for all expressions
    opt.export_types = True

    return mypy_build.build(mypyfiles, options=opt)


def _get_mypy_asts(
    build_result: mypy_build.BuildResult,
    files: list[str],
    package_paths: list[str],
) -> list[mypy_nodes.MypyFile]:
    """Get all module ASTs from Mypy.

    We have to return the package ASTs first though, b/c we need to parse all reexports first.
    """
    package_ast = []
    module_ast = []
    for graph_key in build_result.graph:
        ast = build_result.graph[graph_key].tree

        if ast is None:  # pragma: no cover
            raise ValueError

        if ast.path.endswith("__init__.py"):
            ast_package_path = ast.path.split("__init__.py")[0][:-1]
            if ast_package_path in package_paths:
                package_ast.append(ast)
        elif ast.path in files:
            module_ast.append(ast)

    # The packages need to be checked first, since we have to get the reexported data first
    return package_ast + module_ast


def _get_aliases(result_types: dict, package_name: str) -> dict[str, set[str]]:
    """Get the needed aliases from Mypy.

    Mypy has a long list of all aliases it has found. We have to parse the list and get only the aliases we need for our
    package we analyze.
    """
    aliases: dict[str, set[str]] = defaultdict(set)
    for key in result_types:
        if isinstance(key, mypy_nodes.NameExpr | mypy_nodes.MemberExpr | mypy_nodes.TypeVarExpr):
            in_package = False
            name = ""

            if isinstance(key, mypy_nodes.NameExpr):
                type_value = result_types[key]

                if hasattr(type_value, "type") and getattr(type_value, "type", None) is not None:
                    name = type_value.type.name
                    in_package = package_name in type_value.type.fullname
                elif hasattr(key, "name"):
                    name = key.name
                    fullname = ""

                    if (
                        hasattr(key, "node")
                        and isinstance(key.node, mypy_nodes.TypeAlias)
                        and isinstance(key.node.target, mypy_types.Instance)
                    ):
                        fullname = key.node.target.type.fullname
                    elif isinstance(type_value, mypy_types.CallableType):
                        bound_args = type_value.bound_args
                        if bound_args and hasattr(bound_args[0], "type"):
                            fullname = bound_args[0].type.fullname  # type: ignore[union-attr]
                    elif hasattr(key, "node") and isinstance(key.node, mypy_nodes.Var):
                        fullname = key.node.fullname

                    if not fullname:
                        continue

                    in_package = package_name in fullname
            else:
                in_package = package_name in key.fullname
                if in_package:
                    type_value = result_types[key]
                    name = key.name
                else:
                    continue

            # Try to find the original qname (fullname) of the alias
            if in_package:
                if (
                    isinstance(type_value, mypy_types.CallableType)
                    and type_value.bound_args
                    and hasattr(type_value.bound_args[0], "type")
                ):
                    fullname = type_value.bound_args[0].type.fullname  # type: ignore[union-attr]
                elif isinstance(type_value, mypy_types.Instance):
                    fullname = type_value.type.fullname
                elif isinstance(key, mypy_nodes.TypeVarExpr):
                    fullname = key.fullname
                elif isinstance(key, mypy_nodes.NameExpr) and isinstance(key.node, mypy_nodes.Var):
                    fullname = key.node.fullname
                else:  # pragma: no cover
                    msg = f"Received unexpected type while searching for aliases. Skipping for '{name}'."
                    logging.info(msg)
                    continue

                aliases[name].add(fullname)

    return aliases
