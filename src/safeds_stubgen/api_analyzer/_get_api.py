from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

import mypy.build as mypy_build
import mypy.main as mypy_main
from mypy import nodes as mypy_nodes
from mypy import types as mypy_types

from safeds_stubgen.api_analyzer._type_source_enums import TypeSourcePreference, TypeSourceWarning
from safeds_stubgen.docstring_parsing import DocstringStyle, create_docstring_parser

from ._api import API, CallReference, Function
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
    _find_all_referenced_functions_for_all_call_references(api)

    return api

def _update_class_subclass_relation(api: API) -> None:
    # for each class, update each superclass by appending the id of the class to subclasses list of the superclass
    for class_def in api.classes.values():
        super_classes = [api.classes["/".join(x.split("."))] for x in class_def.superclasses]
        for super_class in super_classes:
            super_class.subclasses.append(class_def.id)

def _find_all_referenced_functions_for_all_call_references(api: API) -> None:
    for function in api.functions2.values():
        for call_reference in function.body.call_references.values():
            type = call_reference.receiver.type
            class_of_receiver = api.classes["/".join(type.type.fullname.split("."))]
            referenced_functions = []
            _get_referenced_functions_from_class_and_subclasses(
                api, 
                call_reference,
                class_of_receiver.id,
                [],
                referenced_functions
            )

            # find function in superclasses but only first appearance as python will also only call the first appearance
            if len(referenced_functions) == 0:
                super_classes = [api.classes["/".join(x.split("."))] for x in class_of_receiver.superclasses]
                for super_class in super_classes:
                    found_method = False
                    for method in super_class.methods:
                        if method.name == call_reference.function_name:
                            referenced_functions.append(method)
                            found_method = True
                            break
                    if found_method:
                        break

            call_reference.possible_referenced_functions = referenced_functions
            

def _get_referenced_functions_from_class_and_subclasses(
    api: API, 
    call_reference: CallReference, 
    current_class_id: str, 
    visited_classes: list[str], 
    referenced_functions: list[Function]
) -> None:
    current_class = api.classes[current_class_id]
    visited_classes.append(current_class_id)
    methods = current_class.methods
    for method in methods:
        if method.name == call_reference.function_name:
            referenced_functions.append(method)

    # find all additional function defs with same name in sub classes as they could also be called
    # for that i should add a subclasses attribute to Class so that i can recursively get the subclasses
    # but keep track of already visited classes !!

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
