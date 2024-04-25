from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from safeds_stubgen.api_analyzer import get_api
from safeds_stubgen.stubs_generator import generate_stubs

if TYPE_CHECKING:
    from safeds_stubgen.docstring_parsing import DocstringStyle


def cli() -> None:
    args = _get_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    _run_api_command(args.src, args.out, args.docstyle, args.testrun, args.naming_convert)


def _get_args() -> argparse.Namespace:
    from safeds_stubgen.docstring_parsing import DocstringStyle

    parser = argparse.ArgumentParser(description="Analyze Python code.")

    parser.add_argument("-v", "--verbose", help="show info messages", action="store_true")
    parser.add_argument(
        "-s",
        "--src",
        help="Source directory containing the Python code of the package.",
        type=Path,
        required=True,
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
    parser.add_argument(
        "-tr",
        "--testrun",
        help="Set this flag if files in /test or /tests directories should be included.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-nc",
        "--naming_convert",
        help=(
            "Set this flag if the name identifiers should be converted to Safe-DS standard (UpperCamelCase for classes "
            "and camelCase for everything else)."
        ),
        required=False,
        action="store_true",
    )

    return parser.parse_args()


def _run_api_command(
    src_dir_path: Path,
    out_dir_path: Path,
    docstring_style: DocstringStyle,
    is_test_run: bool,
    convert_identifiers: bool,
) -> None:
    """
    List the API of a package.

    Parameters
    ----------
    out_dir_path : Path
        The path to the output directory.
    docstring_style : DocstringStyle
        The style of docstrings that used in the library.
    is_test_run : bool
        Set True if files in test directories should be parsed too.
    """
    api = get_api(src_dir_path, docstring_style, is_test_run)
    out_file_api = out_dir_path.joinpath(f"{src_dir_path.stem}__api.json")
    api.to_json_file(out_file_api)

    generate_stubs(api, out_dir_path, convert_identifiers)
