from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

import mypy.build as mypy_build
import mypy.main as mypy_main
from mypy import nodes as mypy_nodes
from mypy import types as mypy_types

from safeds_stubgen.api_analyzer._type_source_enums import TypeSourcePreference, TypeSourceWarning
from safeds_stubgen.api_analyzer._types import AbstractType, CallableType, DictType, FinalType, ListType, NamedSequenceType, NamedType, SetType, TupleType, UnionType
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
) -> API:
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
    api = API(distribution=dist, package=package_name, version=dist_version)
    docstring_parser = create_docstring_parser(style=docstring_style, package_path=root)
    callable_visitor = MyPyAstVisitor(
        docstring_parser=docstring_parser,
        api=api,
        aliases=aliases,
        type_source_preference=type_source_preference,
        type_source_warning=type_source_warning,
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
            class_to_append = api.classes.get("/".join(super_class_id.split(".")))
            if class_to_append is None:  # super class imported from outside of the analyzed package
                continue
            super_classes.append(class_to_append)
        for super_class in super_classes:
            super_class.subclasses.append(class_def.id)

def _get_named_type_from_nested_type(nested_type: AbstractType) -> NamedType | None:
    """
        Iterates through a nested type recursively, to find a NamedType

        Parameters
        ----------
        nested_type : AbstractType
            Abstract class for types
        
        Returns
        ----------
        type : NamedType | None
    """
    if isinstance(nested_type, NamedType):
        return nested_type
    elif isinstance(nested_type, ListType):
        return _get_named_type_from_nested_type(nested_type.types[0])
    elif isinstance(nested_type, NamedSequenceType):
        return _get_named_type_from_nested_type(nested_type.types[0])
    elif isinstance(nested_type, UnionType):
        return _get_named_type_from_nested_type(nested_type.types[0])
    elif isinstance(nested_type, DictType):
        return _get_named_type_from_nested_type(nested_type.value_type)
    elif isinstance(nested_type, SetType):
        return _get_named_type_from_nested_type(nested_type.types[0])
    elif isinstance(nested_type, FinalType):
        return _get_named_type_from_nested_type(nested_type.type_)
    elif isinstance(nested_type, TupleType):
        return _get_named_type_from_nested_type(nested_type.types[0])
    elif isinstance(nested_type, CallableType):
        return _get_named_type_from_nested_type(nested_type.return_type)


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
            if isinstance(type, NamedType):
                class_of_receiver = api.classes.get("/".join(type.qname.split(".")))
            else:
                class_of_receiver = api.classes.get("/".join(type.type.fullname.split(".")))

            found_correct_class = False
            correct_path = call_reference.receiver.path_to_call_reference[::-1]  # use reverse list
            path_length = len(correct_path) 

            # iterate through path and update class_of_receiver so that after iterating 
            # class_of_receiver is the class, that finally receives the call
            for i, part in enumerate(correct_path): 
                if class_of_receiver is None:
                    break
                if i == 0:  # first part of path is a variable name etc so we can skip 
                    continue
                if part == "()":
                    continue
                try:  # assume the part of the path is a name of a member 
                    attribute_name = part
                    attribute = _find_attribute_in_class_and_super_classes(api, attribute_name, class_of_receiver)
                    if attribute is None:
                        raise KeyError()
                    type_of_attribute = attribute.type
                    if type_of_attribute is None:
                        print("missing type info!")
                        break

                    # attribute can be object (class), list, tuple or dict so we need to extract the namedType from nested types
                    type = _get_named_type_from_nested_type(type_of_attribute)
                    if type is None:
                        print("NamedType not found")
                        break

                    found_class = api.classes.get("/".join(type.qname.split(".")))
                    if found_class is None:
                        print(f"Class {type.name} not found")
                        break
                    class_of_receiver = found_class
                    continue  # next class found, check next part of path

                except KeyError:  # current part of path was not a member so we assume its a method
                    rest_of_path = correct_path[i + 1:]
                    is_last_method = all(item == "()" for item in rest_of_path)  # maybe we need to check for [] as well
                    if is_last_method and i + 2 <= path_length:  # here we have "method()" or "method()()"
                        found_correct_class = True
                        break
                    else:  # here we have something like this "method1().method2()" or "method1().member.method2()" or "method()[0].member.method2()" or "method()()"
                        method_name = part
                        method = _find_method_in_class_and_super_classes(api, method_name, class_of_receiver)
                        if method is None:
                            print(f"Method {method_name} and Attribute {attribute_name} not found in class {class_of_receiver.name} and superclasses!")
                            break

                        result = method.results[0]  # in this case there can only be one result
                        if result.type is None:
                            print(f"Result {result.name} has type None")
                            break

                        # get NamedType from result
                        type = _get_named_type_from_nested_type(result.type)  # will find the type of expressions like "method()[0]"
                        if type is None:
                            print("NamedType not found")
                            break

                        found_class = api.classes.get("/".join(type.qname.split(".")))
                        if found_class is None:
                            print(f"Class {type.name} not found")
                            break
                        class_of_receiver = found_class
                        continue  # next class found, check next part of path

            if found_correct_class:
                call_reference.receiver.found_class = class_of_receiver
            else:
                log_msg = f"The class of the receiver could not be found. This is the path to the call reference {correct_path}. This can lead to functions being classified as impure even though they are pure"
                logging.info(log_msg)
            

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
            if call_reference.receiver.found_class is None:
                continue
            else:
                current_class = call_reference.receiver.found_class
            
            # check if specified class has method with name of callreference
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

            if not specified_class_has_method:  # then python will look for method in super but so we have to do that as well
            # find function in superclasses but only first appearance as python will also only call the first appearance
                super_classes = [api.classes["/".join(x.split("."))] for x in current_class.superclasses]
                _get_referenced_function_from_super_classes(
                    api,
                    call_reference,
                    super_classes,
                    referenced_functions
                )

            call_reference.possibly_referenced_functions = referenced_functions

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
            next_super_classes = [api.classes["/".join(x.split("."))] for x in super_class.superclasses]
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

            if in_package:
                if isinstance(type_value, mypy_types.CallableType) and hasattr(type_value.bound_args[0], "type"):
                    fullname = type_value.bound_args[0].type.fullname  # type: ignore[union-attr]
                elif isinstance(type_value, mypy_types.Instance):
                    fullname = type_value.type.fullname
                elif isinstance(key, mypy_nodes.TypeVarExpr):
                    fullname = key.fullname
                elif isinstance(key, mypy_nodes.NameExpr) and isinstance(key.node, mypy_nodes.Var):
                    fullname = key.node.fullname
                else:  # pragma: no cover
                    raise TypeError("Received unexpected type while searching for aliases.")

                aliases[name].add(fullname)

    return aliases
