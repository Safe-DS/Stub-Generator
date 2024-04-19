from __future__ import annotations

from importlib.metadata import packages_distributions, version


def distribution(package_name: str) -> str | None:
    dist = packages_distributions().get(package_name)
    if dist is None or len(dist) == 0:
        return None

    return dist[0]


def distribution_version(dist: str | None) -> str | None:
    if dist is None or len(dist) == 0:
        return None

    return version(dist)
