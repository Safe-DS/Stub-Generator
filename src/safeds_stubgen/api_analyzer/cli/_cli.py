import argparse
import logging

# noinspection PyUnresolvedReferences,PyProtectedMember
from argparse import _SubParsersAction
from pathlib import Path

from safeds_stubgen.api_analyzer.cli._run_api import _run_api_command
from safeds_stubgen.docstring_parsing import DocstringStyle

_API_COMMAND = "api"


def cli() -> None:
    args = _get_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if args.command == _API_COMMAND:
        _run_api_command(args.package, args.src, args.out, args.docstyle)


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Python code.")
    parser.add_argument("-v", "--verbose", help="show info messages", action="store_true")

    # Commands
    subparsers = parser.add_subparsers(dest="command")
    _add_api_subparser(subparsers)

    return parser.parse_args()


def _add_api_subparser(subparsers: _SubParsersAction) -> None:
    api_parser = subparsers.add_parser(_API_COMMAND, help="List the API of a package.")
    api_parser.add_argument(
        "-p",
        "--package",
        help="The name of the package.",
        type=str,
        required=True,
    )
    api_parser.add_argument(
        "-s",
        "--src",
        help="Directory containing the Python code of the package. If this is omitted, we try to locate the package "
        "with the given name in the current Python interpreter.",
        type=Path,
        required=False,
        default=None,
    )
    api_parser.add_argument("-o", "--out", help="Output directory.", type=Path, required=True)
    api_parser.add_argument(
        "--docstyle",
        help="The docstring style.",
        type=DocstringStyle.from_string,
        choices=list(DocstringStyle),
        required=False,
        default=DocstringStyle.PLAINTEXT.name,
    )
