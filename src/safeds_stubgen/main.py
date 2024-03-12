"""The entrypoint to the program."""

from __future__ import annotations

import time

from safeds_stubgen.api_analyzer.cli import cli


def main() -> None:
    """Launch the program."""
    start_time = time.time()

    cli()

    print("\n============================================================")  # noqa: T201
    print(f"Program ran in {time.time() - start_time}s")  # noqa: T201


if __name__ == "__main__":  # pragma: no cover
    main()
