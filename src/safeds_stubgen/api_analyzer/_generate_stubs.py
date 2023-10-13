from __future__ import annotations

from pathlib import Path
from typing import Any, TextIO


# Todo: Wir ignorieren self parameter im Init, also sollten wir für __init__ Funktionen is_self für parameter
#  überprüfen und diesen als Namen dann immer "self" geben, damit diese bei der Classen Erstellung ignoriert werden
#  können
# Todo: In der api.json output Datei alle Listen zu dictionaries, da wir sonst immer durch alle Einträge iterieren
#  müssen
class StubsGenerator:
    api_data: dict[str, Any]
    out_path: Path

    def __init__(self, api_data: dict[str, Any], out_path: Path) -> None:
        self.api_data = api_data
        self.out_path = out_path

    def generate_stubs(self) -> None:
        create_directory(Path(self.out_path / self.api_data["package"]))
        self._create_module_files()

    # Todo Handle __init__ files
    #  Dont create modules that start with "_" unless they are reexported with an alias without "_"
    #  or contain a reexported or public class (?)
    def _create_module_files(self) -> None:
        modules = self.api_data["modules"]

        for module in modules:
            if module["name"] == "__init__":
                continue

            module_dir = Path(self.out_path / module["id"])
            create_directory(module_dir)

            file_path = Path(self.out_path / module["id"] / f"{module["name"]}.sdsstub")
            create_file(file_path)

            with file_path.open("w") as f:
                # Create package info
                package_info = module["id"].replace("/", ".")
                f.write(f"package {package_info}\n\n")

                # Create imports
                self._write_qualified_imports(f, module["qualified_imports"])
                self._write_wildcard_imports(f, module["wildcard_imports"])
                f.write("\n\n")

                # Create global functions
                for function in self.api_data["functions"]:
                    if function["is_public"] and function["id"] in module["functions"]:
                        function_string = self._create_function_string(function)
                        f.write(f"{function_string}\n\n")

                # Create classes, class attr. & class methods
                for class_ in self.api_data["classes"]:
                    if class_["is_public"] and class_["id"] in module["classes"]:
                        self._write_class(f, class_)

                # Create enums & enum instances
                for enum in self.api_data["enums"]:
                    if enum["id"] in module["enums"]:
                        self._write_enum(f, enum)

    # Todo assigned_by, constructors, subclassing
    def _write_class(self, f: TextIO, class_data: dict):
        # Constructor parameter
        class_parameter: list[str] = []
        constructor = class_data["constructor"]
        if constructor:
            for parameter_id in constructor["parameters"]:
                parameter_data = get_data_by_id(self.api_data["parameters"], parameter_id)
                if parameter_data["name"] == "self":
                    continue
                class_parameter.append(f"{parameter_data['name']}: {parameter_data['type']['name']}")

        # Class signature line
        parameter = ", ".join(class_parameter)
        class_sign = f"class {class_data['name']}({parameter}) {{"
        f.write(class_sign)

        # Attributes
        class_attributes: list[str] = []
        for attribute_id in class_data["attributes"]:
            attribute_data = get_data_by_id(self.api_data["attributes"], attribute_id)
            if not attribute_data["is_public"]:
                continue

            attr_type = create_type_string(attribute_data["type"])
            type_string = f": {attr_type}" if attr_type else ""
            class_attributes.append(
                f"attr {attribute_data['name']}"
                f"{type_string}",
            )

        attributes = "\n\t".join(class_attributes)
        f.write(f"\n\t{attributes}")

        # Methods
        class_methods: list[str] = []
        for method_id in class_data["methods"]:
            method_data = get_data_by_id(self.api_data["functions"], method_id)
            if not method_data["is_public"]:
                continue
            class_methods.append(self._create_function_string(method_data))
        methods = "\n\n\t".join(class_methods)
        f.write(f"\n\n\t{methods}")

        # Close class
        f.write("\n}")

    def _create_function_string(self, method_data: dict) -> str:
        static = "static " if method_data["is_static"] else ""

        # Parameters
        parameters: list[str] = []
        for parameter_id in method_data["parameters"]:
            parameter_data = get_data_by_id(self.api_data["parameters"], parameter_id)
            if parameter_data["name"] == "self":
                continue
            param_type = create_type_string(parameter_data["type"])
            type_string = f": {param_type}" if param_type else ""
            parameters.append(
                f"{parameter_data['name']}"
                f"{type_string}",
            )
        method_params = ", ".join(parameters)

        # Results
        results: list[str] = []
        for result_id in method_data["results"]:
            result_data = get_data_by_id(self.api_data["results"], result_id)
            ret_type = create_type_string(result_data["type"])
            type_string = f": {ret_type}" if ret_type else ""
            results.append(
                f"{result_data['name']}"
                f"{type_string}",
            )
        method_results = f" -> {', '.join(results)}" if results else ""

        return f"{static}fun {method_data['name']}({method_params}){method_results}"

    @staticmethod
    def _write_qualified_imports(f: TextIO, qualified_imports: list) -> None:
        if not qualified_imports:
            return

        imports: list[str] = []
        for qualified_import in qualified_imports:
            qualified_name = qualified_import["qualified_name"]
            split_qname = qualified_name.split(".")
            name = split_qname.pop(-1)
            import_path = ".".join(split_qname)
            from_path = ""
            if import_path:
                from_path = f"from {import_path} "

            alias = f" as {qualified_import['alias']}" if qualified_import["alias"] else ""

            imports.append(
                f"{from_path}import {name}{alias}",
            )

        f.write(f"{'\n'.join(imports)}")

    @staticmethod
    def _write_wildcard_imports(f: TextIO, wildcard_imports: list) -> None:
        if not wildcard_imports:
            return

        imports = [
            f"from {wildcard_import['module_name']} import *"
            for wildcard_import in wildcard_imports
        ]

        f.write(f"{'\n'.join(imports)}")

    def _write_enum(self, f: TextIO, enum_data: dict) -> None:
        # Signature
        f.write(f"enum {enum_data['name']} {{\n")

        # Enum instances
        for enum_instance_id in enum_data["instances"]:
            instance = get_data_by_id(self.api_data["enum_instances"], enum_instance_id)
            f.write(f"\t{instance['name']},\n")

        # Close
        f.write("}\n\n")


def create_type_string(type_data: dict | None):
    if type_data is None:
        return ""

    kind = type_data["kind"]
    if kind == "NamedType":
        name = type_data["name"]
        match name:
            case "tuple":
                return "Tuple"
            case "int":
                return "Int"
            case "str":
                return "String"
            case "bool":
                return "Boolean"
            case "float":
                return "Float"
            case _:
                return name
    elif kind in {"OptionalType", "FinalType"}:
        # Cut out the "Type" in the kind name
        name = kind[0:-4]
        return f"{name}[{create_type_string(type_data)}]"
    elif kind in {"TupleType", "SetType", "ListType", "UnionType"}:
        types = [
            create_type_string(type_)
            for type_ in type_data["types"]
        ]
        # Cut out the "Type" in the kind name
        name = kind[0:-4]
        types_string = ""
        if types:
            types_string = f"[{', '.join(types)}]"
        return f"{name}{types_string}"
    elif kind == "DictType":
        key_data = create_type_string(type_data["key_type"])
        value_data = create_type_string(type_data["value_type"])
        key_value_data = ""
        if key_data:
            if value_data:
                key_value_data = f"[{key_data}, {value_data}]"
            else:
                key_value_data = f"[{key_data}]"
        return f"Dict{key_value_data}"
    elif kind == "LiteralType":
        return f"Literal[{', '.join(type_data['literals'])}]"

    raise ValueError(f"Unexpected type: {kind}")


def create_directory(path: Path) -> None:
    if not Path.exists(path):
        Path.mkdir(path)


def create_file(path: Path) -> None:
    Path(path).touch()


def get_data_by_id(data: list[dict], item_id: str) -> dict:
    for item in data:
        if item["id"] == item_id:
            return item
    raise ValueError("Data not found.")
