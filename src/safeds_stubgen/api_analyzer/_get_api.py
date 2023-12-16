from __future__ import annotations

import logging
from pathlib import Path

import mypy.build as mypy_build
import mypy.main as mypy_main

from safeds_stubgen.docstring_parsing import DocstringStyle, create_docstring_parser

from ._api import API
from ._ast_visitor import MyPyAstVisitor
from ._ast_walker import ASTWalker
from ._package_metadata import distribution, distribution_version, package_root
from mypy import nodes as mypy_nodes
from mypy import types as mypy_types


def get_api(
    package_name: str,
    root: Path | None = None,
    docstring_style: DocstringStyle = DocstringStyle.PLAINTEXT,
    is_test_run: bool = False,
) -> API:
    # Check root
    if root is None:
        root = package_root(package_name)

    walkable_files = []
    package_paths = []
    for file_path in root.glob(pattern="./**/*.py"):
        logging.info(
            "Working on file {posix_path}",
            extra={"posix_path": str(file_path)},
        )

        # Check if the current path is a test directory
        if not is_test_run and ("test" in file_path.parts or "tests" in file_path.parts):
            logging.info("Skipping test file")
            continue

        # Check if the current file is an init file
        if file_path.parts[-1] == "__init__.py":
            # if a directory contains an __init__.py file it's a package
            package_paths.append(
                file_path.parent,
            )
            continue

        walkable_files.append(str(file_path))

    if not walkable_files:
        raise ValueError("No files found to analyse.")

    # Get distribution data
    dist = distribution(package_name) or ""
    dist_version = distribution_version(dist) or ""

    # Get mypy ast and aliases
    build_result = _get_mypy_build(walkable_files)
    mypy_asts = _get_mypy_asts(build_result, walkable_files, package_paths, root)
    aliases = _get_aliases(build_result.types, package_name)

    # Setup api walker
    api = API(dist, package_name, dist_version)
    docstring_parser = create_docstring_parser(docstring_style)
    callable_visitor = MyPyAstVisitor(docstring_parser, api, aliases)
    walker = ASTWalker(callable_visitor)

    for tree in mypy_asts:
        walker.walk(tree)

    return callable_visitor.api


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
    package_paths: list[Path],
    root: Path,
) -> list[mypy_nodes.MypyFile]:
    # Check mypy data key root start
    parts = root.parts
    graph_keys = list(build_result.graph.keys())
    root_start_after = -1
    for i in range(len(parts)):
        if ".".join(parts[i:]) in graph_keys:
            root_start_after = i
            break

    # Create the keys for getting the corresponding data
    packages = [
        ".".join(
            package_path.parts[root_start_after:],
        ).replace(".py", "")
        for package_path in package_paths
    ]

    modules = [
        ".".join(
            Path(file).parts[root_start_after:],
        ).replace(".py", "")
        for file in files
    ]

    # Get the needed data from mypy. The packages need to be checked first, since we have
    # to get the reexported data first
    all_paths = packages + modules

    asts = []
    for path_key in all_paths:
        tree = build_result.graph[path_key].tree
        if tree is not None:
            asts.append(tree)

    return asts


def _get_aliases(result_types: dict, package_name: str) -> dict[str, set[str]]:
    if not result_types:
        return {}

    aliases = {}
    for key in result_types.keys():
        if isinstance(key, mypy_nodes.NameExpr | mypy_nodes.MemberExpr | mypy_nodes.TypeVarExpr):
            if isinstance(key, mypy_nodes.NameExpr):
                type_value = result_types[key]

                if hasattr(type_value, "type") and getattr(type_value, "type", None) is not None:
                    name = type_value.type.name
                    in_package = package_name in type_value.type.fullname
                elif hasattr(key, "name"):
                    name = key.name
                    fullname = ""

                    if (hasattr(key, "node") and
                            isinstance(key.node, mypy_nodes.TypeAlias) and
                            isinstance(key.node.target, mypy_types.Instance)):
                        fullname = key.node.target.type.fullname
                    elif isinstance(type_value, mypy_types.CallableType):
                        bound_args = type_value.bound_args
                        if bound_args and not isinstance(bound_args[0], mypy_types.TupleType):
                            fullname = bound_args[0].type.fullname
                    elif hasattr(key, "node") and isinstance(key.node, mypy_nodes.Var):
                        fullname = key.node.fullname

                    if not fullname:
                        continue

                    in_package = package_name in fullname
                else:
                    continue
            else:
                in_package = package_name in key.fullname
                if in_package:
                    type_value = result_types[key]
                    name = key.name
                else:
                    continue

            if in_package:
                if isinstance(type_value, mypy_types.CallableType):
                    fullname = type_value.bound_args[0].type.fullname
                elif isinstance(type_value, mypy_types.Instance):
                    fullname = type_value.type.fullname
                elif isinstance(key, mypy_nodes.TypeVarExpr):
                    fullname = key.fullname
                elif isinstance(key, mypy_nodes.NameExpr) and isinstance(key.node, mypy_nodes.Var):
                    fullname = key.node.fullname
                else:  # pragma: no cover
                    raise TypeError("Received unexpected type while searching for aliases.")

                aliases.setdefault(name, set()).add(fullname)

    return aliases
