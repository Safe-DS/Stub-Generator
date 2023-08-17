import argparse
import logging

# noinspection PyUnresolvedReferences,PyProtectedMember
from argparse import _SubParsersAction
from pathlib import Path

from safeds_stubgen.api_analyzer.cli._run_api import _run_api_command
from ._docstring_style import DocstringStyle

_API_COMMAND = "api"


def cli() -> None:
    args = _get_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    _run_api_command(args.package, args.src, args.out, args.docstyle)


def _get_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Python code.")
    parser.add_argument("-v", "--verbose", help="show info messages", action="store_true")

    # Commands
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

    return parser
