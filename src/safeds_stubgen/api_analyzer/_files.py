from __future__ import annotations

import os
from pathlib import Path


def list_files(root_dir: Path, extension: str = "") -> list[str]:
    """
    List all files in a directory and its subdirectories.

    Parameters
    ----------
    root_dir: Path
        The directory containing the files.
    extension: str
        The extension the files should have.

    Returns
    -------
    files: list[str]
        A list with absolute paths to the files.
    """
    result: list[str] = []

    for root, _, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith(extension):
                result.append(str(Path(root) / filename))

    return result
