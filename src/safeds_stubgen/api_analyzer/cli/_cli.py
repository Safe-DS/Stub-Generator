from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from safeds_stubgen.api_analyzer import get_api
from safeds_stubgen.stubs_generator import StubsStringGenerator, create_stub_files, generate_stub_data

if TYPE_CHECKING:
    from safeds_stubgen.docstring_parsing import DocstringStyle


def cli() -> None:
    args = _get_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    _run_stub_generator(args.src.resolve(), args.out.resolve(), args.docstyle, args.testrun, args.naming_convert)


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


def _run_stub_generator(
    src_dir_path: Path,
    out_dir_path: Path,
    docstring_style: DocstringStyle,
    is_test_run: bool,
    convert_identifiers: bool,
) -> None:
    """
    Create API data of a package and Safe-DS stub files.

    Parameters
    ----------
    out_dir_path:
        The path to the output directory.
    docstring_style:
        The style of docstrings that used in the library.
    is_test_run:
        Set True if files in test directories should be parsed too.
    """
    # Generate the API data
    api = get_api(root=src_dir_path, docstring_style=docstring_style, is_test_run=is_test_run)
    # Create an API file
    out_file_api = out_dir_path.joinpath(f"{src_dir_path.stem}__api.json")
    api.to_json_file(out_file_api)

    # Generate the stub data
    stubs_generator = StubsStringGenerator(api=api, convert_identifiers=convert_identifiers)
    stub_data = generate_stub_data(stubs_generator=stubs_generator, out_path=out_dir_path)
    # Create the stub files
    create_stub_files(stubs_generator=stubs_generator, stubs_data=stub_data, out_path=out_dir_path)
