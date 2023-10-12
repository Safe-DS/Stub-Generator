from __future__ import annotations

import importlib
from importlib.metadata import packages_distributions, version
from pathlib import Path


def package_root(package_name: str) -> Path:
    path_as_string = importlib.import_module(package_name).__file__
    if path_as_string is None:
        raise AssertionError(f"Cannot find package root for '{path_as_string}'.")
    return Path(path_as_string).parent


def distribution(package_name: str) -> str | None:
    dist = packages_distributions().get(package_name)
    if dist is None or len(dist) == 0:
        return None

    return dist[0]


def distribution_version(dist: str | None) -> str | None:
    if dist is None or len(dist) == 0:
        return None

    return version(dist)
