from __future__ import annotations

import argparse
from datetime import datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from safeds_stubgen._evaluation import ApiEvaluation, PurityEvaluation
from safeds_stubgen.api_analyzer.purity_analysis._infer_purity import get_purity_results
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
        old_purity_analysis=args.old_purity_analysis,
        purity_evaluation=args.evaluate_purity,
        api_evaluation=args.evaluate_api,
        runtime_evaluation=args.evaluate_runtime,
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
    parser.add_argument(
        "-old",
        "--old_purity_analysis",
        help="Set this flag to run the old purity analysis.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-evalP",
        "--evaluate_purity",
        help="Set this flag to run the purity evaluation.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-evalA",
        "--evaluate_api",
        help="Set this flag to run the api evaluation.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-runtime",
        "--evaluate_runtime",
        help="Set this flag to run only the runtime evaluation of Api or Purity.",
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
    type_source_preference: TypeSourcePreference,
    type_source_warning: TypeSourceWarning,
    old_purity_analysis: bool = False,
    purity_evaluation: bool = False,
    api_evaluation: bool = False,
    runtime_evaluation: bool = False,
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
    # TODO pm generate Evaluation object depending on cli parameters, add these cli parameters
    # track time for get_purity_results, track type data of all expressions in get_api or track time of get_api 
    api_evaluator = None
    purity_evaluator = None
    if api_evaluation:
        api_evaluator = ApiEvaluation(src_dir_path.stem)
    if purity_evaluation:
        purity_evaluator = PurityEvaluation(src_dir_path.stem, old_purity_analysis, out_dir_path=out_dir_path)

    if api_evaluator is not None:
        api_evaluator.start_timing()
    # Generate the API data
    api = get_api(
        root=src_dir_path,
        docstring_style=docstring_style,
        is_test_run=is_test_run,
        type_source_preference=type_source_preference,
        type_source_warning=type_source_warning,
        evaluation=api_evaluator if not runtime_evaluation else None,
        old_purity_analysis=old_purity_analysis
    )
    if api_evaluator is not None:
        api_evaluator.end_timing()
        api_evaluator.get_results()

    with open(f"evaluation/evaluation_tracking.txt", newline='', mode="a") as file:
        file.write(f"Analyzing API finished {datetime.now()} \n")

    # Create an API file
    out_file_api = out_dir_path.joinpath(f"{src_dir_path.stem}__api.json")
    api.to_json_file(out_file_api)
    
    if purity_evaluator is not None:
        purity_evaluator.start_timing()
    api_purity = get_purity_results(
        src_dir_path, api_data=api,
        test_run=is_test_run,
        old_purity_analysis=old_purity_analysis,
        evaluation=purity_evaluator if not runtime_evaluation else None
    )
    if purity_evaluator is not None:
        purity_evaluator.end_timing()
        purity_evaluator.get_results(api_purity)

    out_file_api_purity = out_dir_path.joinpath(f"{src_dir_path.stem}__api_purity.json")
    api_purity.to_json_file(
        out_file_api_purity,
        shorten=True
    )  # Shorten is set to True by default, therefore the results will only contain the count of each reason.

    if not api_evaluation and not purity_evaluation:
        # Generate the stub data
        stubs_generator = StubsStringGenerator(api=api, purity_api=api_purity, convert_identifiers=convert_identifiers)
        stub_data = generate_stub_data(stubs_generator=stubs_generator, out_path=out_dir_path)
        # Create the stub files
        create_stub_files(stubs_generator=stubs_generator, stubs_data=stub_data, out_path=out_dir_path)
