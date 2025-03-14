from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from safeds_stubgen._helpers import get_reexported_by

if TYPE_CHECKING:
    from safeds_stubgen.api_analyzer import Module

INDENTATION = "    "


class NamingConvention(IntEnum):
    PYTHON = 1
    SAFE_DS = 2


def _convert_name_to_convention(
    name: str,
    naming_convention: NamingConvention,
    is_class_name: bool = False,
) -> str:
    if name == "_" or naming_convention == NamingConvention.PYTHON:
        return name

    # Count underscores in front and behind the name
    underscore_count_start = len(name) - len(name.lstrip("_"))
    underscore_count_end = len(name) - len(name.rstrip("_"))

    if underscore_count_end == 0:
        cleaned_name = name[underscore_count_start:]
    else:
        cleaned_name = name[underscore_count_start:-underscore_count_end]

    # Remove underscores and join in camelCase
    name_parts = cleaned_name.split("_")

    # UpperCamelCase for class names
    if is_class_name:
        return "".join(part[0].upper() + part[1:] for part in name_parts if part)

    # Normal camelCase for everything else
    return name_parts[0] + "".join(part[0].upper() + part[1:] for part in name_parts[1:] if part)


def _get_shortest_public_reexport_and_alias(
    reexport_map: dict[str, set[Module]],
    name: str,
    qname: str,
    is_module: bool,
) -> tuple[str, str]:
    parent_name = ""
    qname = qname.replace("/", ".")
    qname_parts = qname.split(".")
    if not is_module and qname and len(qname_parts) > 2:
        parent_name = qname_parts[-2]

    def _import_check(text: str, is_wildcard: bool = False) -> bool:
        if is_module:
            return text.endswith(f".{name}") or text == name
        elif is_wildcard:
            return text.endswith(f".{parent_name}") or text == parent_name
        return (
            text == name
            or (f".{name}" in text and (text.endswith(f".{name}") or f"{name}." in text))
            or (f"{name}." in text and (text.startswith(f"{name}.") or f".{name}" in text))
            or (parent_name != "" and text.endswith(f"{parent_name}.*"))
        )

    found_modules = get_reexported_by(qname=qname, reexport_map=reexport_map)

    module_ids = set()
    for module in found_modules:
        for qualified_import in module.qualified_imports:
            if _import_check(qualified_import.qualified_name):
                module_ids.add((module.id, qualified_import.alias))
                break

        for wildcard_import in module.wildcard_imports:
            if _import_check(wildcard_import.module_name, is_wildcard=True):
                module_ids.add((module.id, None))
                break

    shortest_id = None
    alias = None
    for module_id_tuple in module_ids:
        module_id_parts = module_id_tuple[0].split("/")
        if shortest_id is None or len(module_id_parts) < len(shortest_id):
            shortest_id = module_id_parts
            alias = module_id_tuple[1]

    if shortest_id is None:
        return "", ""
    return ".".join(shortest_id), alias or ""


def _create_name_annotation(name: str) -> str:
    return f'@PythonName("{name}")'


def _replace_if_safeds_keyword(keyword: str) -> str:
    if keyword in {
        "_",
        "and",
        "annotation",
        "as",
        "attr",
        "class",
        "const",
        "enum",
        "false",
        "from",
        "fun",
        "import",
        "in",
        "internal",
        "literal",
        "not",
        "null",
        "or",
        "out",
        "package",
        "pipeline",
        "private",
        "schema",
        "static",
        "segment",
        "sub",
        "this",
        "true",
        "union",
        "unknown",
        "val",
        "where",
        "yield",
    }:
        return f"`{keyword}`"
    return keyword


def _name_convention_and_keyword_check(name: str, naming_convention: NamingConvention) -> str:
    name = _convert_name_to_convention(name=name, naming_convention=naming_convention)
    return _replace_if_safeds_keyword(keyword=name)
