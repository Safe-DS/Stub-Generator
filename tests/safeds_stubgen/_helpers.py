from __future__ import annotations

from typing import TYPE_CHECKING

from mypy.nodes import ClassDef, FuncDef

if TYPE_CHECKING:
    from mypy.nodes import MypyFile


def get_specific_mypy_node(
    mypy_file: MypyFile,
    node_name: str,
) -> ClassDef | FuncDef:
    for definition in mypy_file.defs:
        if isinstance(definition, ClassDef | FuncDef) and definition.name == node_name:
            return definition
    raise ValueError
