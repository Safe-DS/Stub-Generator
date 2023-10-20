from __future__ import annotations

from pathlib import Path
from typing import Any, TextIO


# Todo Zugriff auf Daten der API per API-Class, damit man direkt auf die Dictionaries zugreifen kann und nicht über alle
#  Listen iterieren muss
# // TODO: Tuples are not allowed in SafeDS.
# // TODO: This List has more than one inner type, which is not allowed.
class StubsGenerator:
    api_data: dict[str, Any]
    out_path: Path
    current_todo_msgs: set[str]

    def __init__(self, api_data: dict[str, Any], out_path: Path) -> None:
        self.api_data = api_data
        self.out_path = out_path
        self.current_todo_msgs = set()

    def generate_stubs(self) -> None:
        create_directory(Path(self.out_path / self.api_data["package"]))
        self._create_module_files()

    # Todo Handle __init__ files
    def _create_module_files(self) -> None:
        modules = self.api_data["modules"]

        for module in modules:
            if module["name"] == "__init__":
                # self._create_reexport_files()
                continue

            # Create module dir
            module_dir = Path(self.out_path / module["id"])
            create_directory(module_dir)

            # Create and open module file
            file_path = Path(self.out_path / module["id"] / f"{module['name']}.sdsstub")
            Path(file_path).touch()

            with file_path.open("w") as f:
                # Create package info
                package_info = module["id"].replace("/", ".")
                f.write(f"package {package_info}\n\n")

                # Create imports
                self._write_qualified_imports(f, module["qualified_imports"])
                self._write_wildcard_imports(f, module["wildcard_imports"])
                f.write("\n")

                # Create global functions
                for function in self.api_data["functions"]:
                    if function["is_public"] and function["id"] in module["functions"]:
                        function_string = self._create_function_string(function, 0, is_class_method=False)
                        f.write(f"{function_string}\n\n")

                # Create classes, class attr. & class methods
                for class_ in self.api_data["classes"]:
                    if class_["is_public"] and class_["id"] in module["classes"]:
                        self._write_class(f, class_, 0)

                # Create enums & enum instances
                for enum in self.api_data["enums"]:
                    if enum["id"] in module["enums"]:
                        self._write_enum(f, enum)

    # Todo assigned by https://dsl.safeds.com/en/latest/language/common/parameters/#matching-optionality -> Siehe E-Mail
    #  -> "// Todo Falsch blabla" über die Zeile generieren
    # Todo create inner class
    def _write_class(self, f: TextIO, class_data: dict, indent_quant: int) -> None:
        # Constructor parameter
        constructor = class_data["constructor"]
        parameter_info = ""
        if constructor:
            parameter_info = self._create_parameter_string(constructor["parameters"], is_instance_method=True)

        # Superclasses
        superclasses = class_data["superclasses"]
        superclass_info = ""
        if superclasses:
            superclass_names = []
            for superclass in superclasses:
                superclass_names.append(split_import_id(superclass)[1])
            superclass_info = f" sub {', '.join(superclass_names)}"

        # Class signature line
        class_sign = f"{self.create_todo_msg(0)}class {class_data['name']}{parameter_info}{superclass_info} {{"
        f.write(class_sign)

        # Attributes
        class_attributes: list[str] = []
        for attribute_id in class_data["attributes"]:
            attribute_data = get_data_by_id(self.api_data["attributes"], attribute_id)
            if not attribute_data["is_public"]:
                continue

            attr_type = self._create_type_string(attribute_data["type"])
            type_string = f": {attr_type}" if attr_type else ""
            class_attributes.append(
                f"{self.create_todo_msg(indent_quant + 1)}"
                f"attr {attribute_data['name']}"
                f"{type_string}",
            )

        indentations = "\t" * (indent_quant + 1)
        attributes = f"\n{indentations}".join(class_attributes)
        f.write(f"\n\t{attributes}")

        # Todo Classes

        # Methods
        class_methods: list[str] = []
        for method_id in class_data["methods"]:
            method_data = get_data_by_id(self.api_data["functions"], method_id)
            if not method_data["is_public"]:
                continue
            class_methods.append(
                self._create_function_string(method_data, indent_quant + 1, is_class_method=True),
            )
        methods = "\n\n\t".join(class_methods)
        f.write(f"\n\n\t{methods}")

        # Close class
        f.write("\n}")

    def _create_function_string(self, func_data: dict, indent_quant: int, is_class_method: bool = False) -> str:
        is_static = func_data["is_static"]
        static = "static " if is_static else ""

        # Parameters
        is_instance_method = not is_static and is_class_method
        func_params = self._create_parameter_string(func_data["parameters"], is_instance_method)
        if not func_params:
            func_params = "()"

        return (
            f"{self.create_todo_msg(indent_quant)}"
            f"{static}fun {func_data['name']}{func_params}"
            f"{self._create_result_string(func_data['results'])}"
        )

    def _create_result_string(self, function_result_ids: list[str]) -> str:
        results: list[str] = []
        for result_id in function_result_ids:
            result_data = get_data_by_id(self.api_data["results"], result_id)
            ret_type = self._create_type_string(result_data["type"])
            type_string = f": {ret_type}" if ret_type else ""
            results.append(
                f"{result_data['name']}"
                f"{type_string}",
            )

        if results:
            if len(results) == 1:
                return f" -> {results[0]}"
            return f" -> ({', '.join(results)})"
        return ""

    def _create_parameter_string(self, param_ids: list[str], is_instance_method: bool = False) -> str:
        parameters: list[str] = []
        first_loop_skipped = False
        for param_id in param_ids:
            # Skip self parameter for functions
            if is_instance_method and not first_loop_skipped:
                first_loop_skipped = True
                continue

            param_data = get_data_by_id(self.api_data["parameters"], param_id)

            # Default value
            param_value = ""
            param_default_value = param_data["default_value"]
            if param_default_value is not None:
                if isinstance(param_default_value, str):
                    if param_data["type"]["kind"] == "NamedType" and param_data["type"]["name"] != "str":
                        if param_default_value == "False":
                            default_value = "false"
                        elif param_default_value == "True":
                            default_value = "true"
                        else:
                            default_value = f"{param_default_value}"
                    else:
                        default_value = f'"{param_default_value}"'
                else:
                    default_value = param_default_value
                param_value = f" = {default_value}"

            # Parameter type
            param_type = self._create_type_string(param_data["type"])
            type_string = f": {param_type}" if param_type else ""

            # Create string and append to the list
            parameters.append(
                f"{param_data['name']}"
                f"{type_string}{param_value}",
            )
        if parameters:
            return f"({', '.join(parameters)})"
        return ""

    @staticmethod
    def _write_qualified_imports(f: TextIO, qualified_imports: list) -> None:
        if not qualified_imports:
            return

        imports: list[str] = []
        for qualified_import in qualified_imports:
            qualified_name = qualified_import["qualified_name"]
            import_path, name = split_import_id(qualified_name)
            from_path = ""
            if import_path:
                from_path = f"from {import_path} "

            alias = f" as {qualified_import['alias']}" if qualified_import["alias"] else ""

            imports.append(
                f"{from_path}import {name}{alias}",
            )

        all_imports = "\n".join(imports)
        f.write(f"{all_imports}\n")

    @staticmethod
    def _write_wildcard_imports(f: TextIO, wildcard_imports: list) -> None:
        if not wildcard_imports:
            return

        imports = [
            f"from {wildcard_import['module_name']} import *"
            for wildcard_import in wildcard_imports
        ]

        all_imports = "\n".join(imports)
        f.write(f"{all_imports}\n")

    def _write_enum(self, f: TextIO, enum_data: dict) -> None:
        # Signature
        f.write(f"enum {enum_data['name']} {{\n")

        # Enum instances
        for enum_instance_id in enum_data["instances"]:
            instance = get_data_by_id(self.api_data["enum_instances"], enum_instance_id)
            f.write(f"\t{instance['name']}" + ",\n")

        # Close
        f.write("}\n\n")

    # Todo AnotherClass? anstatt union<AnotherClass, null>
    def _create_type_string(self, type_data: dict | None) -> str:
        """Create a SafeDS stubs type string."""
        if type_data is None:
            return ""

        kind = type_data["kind"]
        if kind == "NamedType":
            name = type_data["name"]
            match name:
                case "tuple":
                    self.current_todo_msgs.add("Tuple")
                    return "Tuple"
                case "int":
                    return "Int"
                case "str":
                    return "String"
                case "bool":
                    return "Boolean"
                case "float":
                    return "Float"
                case "None":
                    return "null"
                case _:
                    return name
        elif kind == "FinalType":
            return self._create_type_string(type_data)
        elif kind == "OptionalType":
            return f"{self._create_type_string(type_data)}?"
        elif kind in {"SetType", "ListType"}:
            types = [
                self._create_type_string(type_)
                for type_ in type_data["types"]
            ]

            # Cut out the "Type" in the kind name
            name = kind[0:-4]

            if types:
                if len(types) >= 2:
                    self.current_todo_msgs.add(name)
                return f"{name}<{', '.join(types)}>"
            return f"{name}<Any>"
        elif kind == "UnionType":
            types = [
                self._create_type_string(type_)
                for type_ in type_data["types"]
            ]

            if types:
                return f"union<{', '.join(types)}>"
            return ""
        elif kind == "TupleType":
            self.current_todo_msgs.add("Tuple")
            types = [
                self._create_type_string(type_)
                for type_ in type_data["types"]
            ]

            if types:
                return f"Tuple<{', '.join(types)}>"
            return "Tuple"
        elif kind == "DictType":
            key_data = self._create_type_string(type_data["key_type"])
            value_data = self._create_type_string(type_data["value_type"])
            if key_data:
                if value_data:
                    return f"Map<{key_data}, {value_data}>"
                return f"Map<{key_data}>"
            return "Map"
        elif kind == "LiteralType":
            return f"literal<{', '.join(type_data['literals'])}>"

        raise ValueError(f"Unexpected type: {kind}")

    def create_todo_msg(self, indenta_quant: int) -> str:
        if not self.current_todo_msgs:
            return ""

        todo_msgs = []
        for msg in self.current_todo_msgs:
            if msg == "Tuple":
                todo_msgs.append("Tuple types are not allowed")
            elif msg in {"List", "Set"}:
                todo_msgs.append(f"{msg} type has to many type arguments")
            else:
                raise ValueError(f"Unknown todo message: {msg}")

        # Empty the message list
        self.current_todo_msgs = set()

        indentations = "\t" * indenta_quant
        return f"// Todo {', '.join(todo_msgs)}\n{indentations}"


def split_import_id(id_: str) -> tuple[str, str]:
    if "." not in id_:
        return "", id_

    split_qname = id_.split(".")
    name = split_qname.pop(-1)
    import_path = ".".join(split_qname)
    return import_path, name


def create_directory(path: Path) -> None:
    if not Path.exists(path):
        Path.mkdir(path)


def get_data_by_id(data: list[dict], item_id: str) -> dict:
    for item in data:
        if item["id"] == item_id:
            return item
    raise ValueError("Data not found.")
