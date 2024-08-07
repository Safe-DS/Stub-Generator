from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from safeds_stubgen.api_analyzer import TypeSourcePreference, TypeSourceWarning, get_api
from safeds_stubgen.stubs_generator import StubsStringGenerator, create_stub_files, generate_stub_data

if TYPE_CHECKING:
    from safeds_stubgen.docstring_parsing import DocstringStyle


def cli() -> None:
    args = _get_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    _run_stub_generator(
        src_dir_path=args.src.resolve(),
        out_dir_path=args.out.resolve(),
        docstring_style=args.docstyle,
        is_test_run=args.testrun,
        convert_identifiers=args.naming_convert,
        type_source_preference=args.type_source_preference,
        type_source_warning=args.show_type_source_warning,
    )


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
    parser.add_argument(
        "-tsp",
        "--type_source_preference",
        help=(
            "Preference if the type should be taken from code type hints or docstrings if they state contrary types."
        ),
        type=TypeSourcePreference.from_string,
        choices=list(TypeSourcePreference),
        required=False,
        default=TypeSourcePreference.CODE.name,
    )
    parser.add_argument(
        "-tsw",
        "--show_type_source_warning",
        help=(
            "Preference if a warning message should be shown if type information from type hints and docstrings differ."
        ),
        type=TypeSourceWarning.from_string,
        choices=list(TypeSourceWarning),
        required=False,
        default=TypeSourceWarning.WARN.name,
    )

    return parser.parse_args()


def _run_stub_generator(
    src_dir_path: Path,
    out_dir_path: Path,
    docstring_style: DocstringStyle,
    is_test_run: bool,
    convert_identifiers: bool,
    type_source_preference: TypeSourcePreference,
    type_source_warning: TypeSourceWarning,
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
    api = get_api(
        root=src_dir_path,
        docstring_style=docstring_style,
        is_test_run=is_test_run,
        type_source_preference=type_source_preference,
        type_source_warning=type_source_warning,
    )
    # Create an API file
    out_file_api = out_dir_path.joinpath(f"{src_dir_path.stem}__api.json")
    api.to_json_file(out_file_api)

    # Generate the stub data
    stubs_generator = StubsStringGenerator(api=api, convert_identifiers=convert_identifiers)
    stub_data = generate_stub_data(stubs_generator=stubs_generator, out_path=out_dir_path)
    # Create the stub files
    create_stub_files(stubs_generator=stubs_generator, stubs_data=stub_data, out_path=out_dir_path)
