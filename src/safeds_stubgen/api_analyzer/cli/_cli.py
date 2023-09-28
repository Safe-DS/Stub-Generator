from __future__ import annotations

import argparse
import logging
from pathlib import Path

from safeds_stubgen.api_analyzer import get_api

from ._docstring_style import DocstringStyle


def cli() -> None:
    args = _get_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    _run_api_command(args.package, args.src, args.out, args.docstyle)


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Python code.")

    parser.add_argument("-v", "--verbose", help="show info messages", action="store_true")
    parser.add_argument(
        "-p",
        "--package",
        help="The name of the package.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-s",
        "--src",
        help="Directory containing the Python code of the package. If this is omitted, we try to locate the package "
             "with the given name in the current Python interpreter.",
        type=Path,
        required=False,
        default=None,
    )
    parser.add_argument("-o", "--out", help="Output directory.", type=Path, required=True)
    parser.add_argument(
        "--docstyle",
        help="The docstring style.",
        type=DocstringStyle.from_string,
        choices=list(DocstringStyle),
        required=False,
        default=DocstringStyle.PLAINTEXT.name,
    )

    return parser.parse_args()


def _run_api_command(
    package: str,
    src_dir_path: Path,
    out_dir_path: Path,
    docstring_style: DocstringStyle,
) -> None:
    """
    List the API of a package.

    Parameters
    ----------
    package : str
        The name of the package.
    out_dir_path : Path
        The path to the output directory.
    docstring_style : DocstringStyle
        The style of docstrings that used in the library.
    """
    api = get_api(package, src_dir_path, docstring_style)
    out_file_api = out_dir_path.joinpath(f"{package}__api.json")
    api.to_json_file(out_file_api)
