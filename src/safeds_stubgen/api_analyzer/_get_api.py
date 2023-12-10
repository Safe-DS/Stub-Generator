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
    graphs = result.graph
    graph_keys = list(graphs.keys())
    root_path = str(root)

    # Get the needed data from mypy. The __init__ files need to be checked first, since we have to get the
    # reexported data for the packages first
    results = []
    init_results = []
    for graph_key in graph_keys:
        graph = graphs[graph_key]
        graph_path = graph.abspath

        if graph_path is None:  # pragma: no cover
            raise ValueError("Could not parse path of a module.")

        tree = graph.tree
        if tree is None or root_path not in graph_path or not graph_path.endswith(".py"):
            continue

        if graph_path.endswith("__init__.py"):
            init_results.append(tree)
        else:
            results.append(tree)

    return init_results + results
