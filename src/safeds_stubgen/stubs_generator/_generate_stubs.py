from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ._helper import (
    NamingConvention,
    _convert_name_to_convention,
    _create_name_annotation,
    _get_shortest_public_reexport,
    _replace_if_safeds_keyword,
)

if TYPE_CHECKING:
    from ._stub_string_generator import StubsStringGenerator


def generate_stub_data(
    stubs_generator: StubsStringGenerator,
    out_path: Path,
) -> list[tuple[Path, str, str, bool]]:
    """Generate Safe-DS stubs.

    Generates stub data from an API object.

    Parameters
    ----------
    stubs_generator:
        The class for generating the stubs.
    out_path:
        The path in which the stub files should be created. If no such path exists this function creates the directory
        files.

    Returns
    -------
    virtual_files:
        A list of tuples, which are 1. the path of the stub file, 2. the name of the stub file, 3. its content and 4. if
        it's a package file (created through init reexports).
    """
    api = stubs_generator.api
    stubs_data: list[tuple[Path, str, str, bool]] = []
    for module in api.modules.values():
        if module.name == "__init__":
            continue

        log_msg = f"Creating stub data for {module.id}"
        logging.info(log_msg)

        module_text, package_info = stubs_generator(module)

        # Each text block we create ends with "\n", therefore, if there is only the package information
        # the file would look like this: "package path.to.myPackage\n" or this:
        # '@PythonModule("path.to.my_package")\npackage path.to.myPackage\n'. With the split we check if the module
        # has enough information, if not, we won't create it.
        _module_text = module_text
        if _module_text.startswith("/**"):
            # Remove docstring
            _module_text = "*/\n".join(_module_text.split("*/\n\n")[1:])
        splitted_text = _module_text.split("\n")
        if len(splitted_text) <= 2 or (len(splitted_text) == 3 and splitted_text[1].startswith("package ")):
            continue

        shortest_path, alias = _get_shortest_public_reexport(
            reexport_map=api.reexport_map,
            name=module.name,
            qname="",
            is_module=True,
        )
        if shortest_path:
            shortest_path = shortest_path.replace(".", "/")

        module_id = shortest_path if shortest_path else package_info.replace(".", "/")
        module_name = alias if alias else module.name

        module_dir = Path(out_path / module_id)
        stubs_data.append((module_dir, module_name, module_text, False))

    reexport_module_data = stubs_generator.create_reexport_module_strings(out_path=out_path)

    return stubs_data + reexport_module_data


def create_stub_files(
    stubs_generator: StubsStringGenerator,
    stubs_data: list[tuple[Path, str, str, bool]],
    out_path: Path,
) -> None:
    naming_convention = stubs_generator.naming_convention
    # A "package module" is a module which is created though the reexported classes and functions in the __init__.py
    for module_dir, module_name, module_text, is_package_module in stubs_data:
        if is_package_module:
            # Cut out the last part of the path, since we don't want "path/to/package/package.sdsstubs" but
            # "path/to/package.sdsstubs" so that "package" is not doubled
            corrected_module_dir = Path("/".join(module_dir.parts[:-1]))
        else:
            corrected_module_dir = module_dir

        log_msg = f"Creating stub file for {corrected_module_dir}"
        logging.info(log_msg)

        # Create module dir
        corrected_module_dir.mkdir(parents=True, exist_ok=True)

        # Create and open module file
        public_module_name = module_name.lstrip("_")
        file_path = Path(corrected_module_dir / f"{public_module_name}.sdsstub")
        Path(file_path).touch()

        with file_path.open("w") as f:
            f.write(module_text)

    created_module_paths: set[str] = set()
    classes_outside_package = list(stubs_generator.classes_outside_package)
    classes_outside_package.sort()
    for class_ in classes_outside_package:
        created_module_paths = _create_outside_package_class(class_, out_path, naming_convention, created_module_paths)


def _create_outside_package_class(
    class_path: str,
    out_path: Path,
    naming_convention: NamingConvention,
    created_module_paths: set[str],
) -> set[str]:
    path_parts = class_path.split(".")
    class_name = path_parts.pop(-1)
    module_name = path_parts[-1]
    module_path = "/".join(path_parts)

    first_creation = False
    if module_path not in created_module_paths:
        created_module_paths.add(module_path)
        first_creation = True

    module_dir = Path(out_path / module_path)
    module_dir.mkdir(parents=True, exist_ok=True)

    file_path = Path(module_dir / f"{module_name}.sdsstub")
    if Path.exists(file_path) and not first_creation:
        with file_path.open("a") as f:
            f.write(_create_outside_package_class_text(class_name, naming_convention))
    else:
        with file_path.open("w") as f:
            module_text = ""

            # package name & annotation
            python_module_path = ".".join(path_parts)
            module_path_camel_case = _convert_name_to_convention(python_module_path, naming_convention)
            module_name_info = ""
            if python_module_path != module_path_camel_case:
                module_text += f'@PythonModule("{python_module_path}")\n'
            module_text += f"{module_name_info}package {module_path_camel_case}\n"

            module_text += _create_outside_package_class_text(class_name, naming_convention)

            f.write(module_text)

    return created_module_paths


def _create_outside_package_class_text(class_name: str, naming_convention: NamingConvention) -> str:
    # to camel case
    camel_case_name = _convert_name_to_convention(class_name, naming_convention, is_class_name=True)

    # add name annotation
    class_annotation = ""
    if class_name != camel_case_name:
        class_annotation = f"\n{_create_name_annotation(class_name)}"

    # check for identifiers
    safe_class_name = _replace_if_safeds_keyword(camel_case_name)

    return f"{class_annotation}\nclass {safe_class_name}\n"
