from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import mypy.build as mypy_build
import mypy.main as mypy_main

from safeds_stubgen.docstring_parsing import DocstringStyle, create_docstring_parser

from ._api import API
from ._ast_visitor import MyPyAstVisitor
from ._ast_walker import ASTWalker
from ._files import list_files
from ._package_metadata import distribution, distribution_version, package_root

if TYPE_CHECKING:
    from mypy.nodes import MypyFile


def get_api(
    package_name: str,
    root: Path | None = None,
    docstring_style: DocstringStyle = DocstringStyle.PLAINTEXT,
    is_test_run: bool = False,
) -> API:
    # Check root
    if root is None:
        root = package_root(package_name)

    # Get distribution data
    dist = distribution(package_name) or ""
    dist_version = distribution_version(dist) or ""

    # Setup api walker
    api = API(dist, package_name, dist_version)
    docstring_parser = create_docstring_parser(docstring_style)
    callable_visitor = MyPyAstVisitor(docstring_parser, api)
    walker = ASTWalker(callable_visitor)

    walkable_files = []
    package_paths = []
    for file in list_files(root, ".py"):
        file_path = Path(file)
        logging.info(
            "Working on file {posix_path}",
            extra={"posix_path": file},
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

        walkable_files.append(file)

    mypy_trees = _get_mypy_ast(walkable_files, package_paths, root)
    for tree in mypy_trees:
        walker.walk(tree)

    return callable_visitor.api


def _get_mypy_ast(files: list[str], package_paths: list[Path], root: Path) -> list[MypyFile]:
    if not files:
        raise ValueError("No files found to analyse.")

    # Build mypy checker
    mypyfiles, opt = mypy_main.process_options(files)
    opt.preserve_asts = True  # Disable the memory optimization of freeing ASTs when possible
    opt.fine_grained_incremental = True  # Only check parts of the code that have changed since the last check
    result = mypy_build.build(mypyfiles, options=opt)

    # Check mypy data key root start
    parts = root.parts
    graph_keys = list(result.graph.keys())
    root_start_after = 0
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

    results = []
    for path_key in all_paths:
        tree = result.graph[path_key].tree
        if tree is not None:
            results.append(tree)

    return results
