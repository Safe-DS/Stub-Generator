from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from safeds_stubgen.api_analyzer import Module


def is_internal(name: str) -> bool:
    """Check if a function / method / class name indicate if it's internal."""
    return name.startswith("_")


def get_reexported_by(qname: str, reexport_map: dict[str, set[Module]]) -> list[Module]:
    """Get all __init__ modules where a given function / class / enum was reexported."""
    path = qname.split(".")

    # Check if there is a reexport entry for each item in the path to the current module
    reexported_by = set()
    for i in range(len(path)):
        reexport_name_forward = ".".join(path[: i + 1])
        # We ignore i = 0, b/c some inner package could import the whole upper package
        if i != 0 and reexport_name_forward in reexport_map:
            for module in reexport_map[reexport_name_forward]:

                # Check if the module or the class/function itself are beeing reexported. If not, it means a
                #  subpackage is beeing reexported.
                last_forward_part = reexport_name_forward.split(".")[-1]
                part_index = path.index(last_forward_part) + 1
                if len(path) - part_index > 1:
                    continue

                reexported_by.add(module)

        reexport_name_backward = ".".join(path[-i - 1 :])
        if reexport_name_backward in reexport_map:
            for module in reexport_map[reexport_name_backward]:

                # Check if the module or the class/function itself are beeing reexported. If not, it means a
                #  subpackage is beeing reexported.
                if module.name == "__init__" and i < len(path) - 1:
                    zipped = list(zip(module.id.split("/"), path, strict=False))
                    # Check if there is a part of the paths that differs
                    if not all(m == p for m, p in zipped):
                        continue

                reexported_by.add(module)

        reexport_name_backward_whitelist = f"{'.'.join(path[-2 - i:-1])}.*"
        if reexport_name_backward_whitelist in reexport_map:
            for module in reexport_map[reexport_name_backward_whitelist]:

                if len(path) > i + 2:
                    # Check if the found module actually references our object. E.g.: It could be the case that the
                    #  file at `path/to/__init__.py` has `from .api import *` and we find this entry, even though we
                    #  are searching for reexports of a class/function in the `path\from\api.py` file.
                    is_wrong_module_path = False
                    for j, module_part in enumerate(module.id.split("/")):
                        if module_part != path[j]:
                            is_wrong_module_path = True
                            break
                    if is_wrong_module_path:
                        continue

                reexported_by.add(module)

    return list(reexported_by)
