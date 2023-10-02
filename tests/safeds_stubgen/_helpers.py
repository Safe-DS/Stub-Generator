from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy.nodes import FuncDef, ClassDef, MypyFile


def _get_specific_mypy_node(
    mypy_file: MypyFile,
    node_name: str,
) -> ClassDef | FuncDef:
    for definition in mypy_file.defs:
        if definition.name == node_name:
            return definition
    raise ValueError
