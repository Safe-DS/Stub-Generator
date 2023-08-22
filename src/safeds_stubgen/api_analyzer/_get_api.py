import logging
from pathlib import Path

import mypy.build as mypy_build
import mypy.main as mypy_main
from mypy.nodes import MypyFile

from ._api import API
from ._ast_walker import ASTWalker

from ._ast_visitor_mypy import MyPyAstVisitor
from ._file_filters import _is_test_file, _is_init_file
from ._package_metadata import (
    distribution,
    distribution_version,
    package_files,
    package_root,
)
from safeds_stubgen.docstring_parsing import DocstringStyle, create_docstring_parser


def get_api(
    package_name: str,
    root: Path | None = None,
    docstring_style: DocstringStyle = DocstringStyle.PLAINTEXT,
) -> API:
    # Check root
    if root is None:
        root = package_root(package_name)

    # Get dist data
    dist = distribution(package_name) or ""
    dist_version = distribution_version(dist) or ""

    # Setup api walker
    api = API(dist, package_name, dist_version)
    docstring_parser = create_docstring_parser(docstring_style)
    callable_visitor = MyPyAstVisitor(docstring_parser, api)
    walker = ASTWalker(callable_visitor)

    for file in package_files(root):
        logging.info(
            "Working on file {posix_path}",
            extra={"posix_path": file},
        )

        # Todo klappt aktuell nicht mehr
        if _is_test_file(file):
            logging.info("Skipping test file")
            continue

        # Todo entscheid dich für eins
        if file.endswith("__init__.py") or _is_init_file(file):
            logging.info("Skipping init file")
            continue

        walker.walk(_get_mypy_ast(file))

    return callable_visitor.api


def _get_mypy_ast(file: str) -> MypyFile:
    files, opt = mypy_main.process_options([file])
    opt.preserve_asts = True
    opt.fine_grained_incremental = True
    result = mypy_build.build(files, options=opt)
    mod = Path(file).parts[-1].replace(".py", "")
    return result.graph[mod].tree


def __module_name(root: Path, file: Path) -> str:
    relative_path = file.relative_to(root.parent).as_posix()
    return str(relative_path).replace(".py", "").replace("/", ".")
