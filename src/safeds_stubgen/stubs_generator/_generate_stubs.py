from __future__ import annotations

import shutil
from pathlib import Path
from typing import TextIO

from safeds_stubgen.api_analyzer import (
    API,
    Class,
    Enum,
    Function,
    Parameter,
    ParameterAssignment,
    QualifiedImport,
    Result,
    WildcardImport,
)


# Todo Docstrings
class StubsGenerator:
    api: API
    out_path: Path
    current_todo_msgs: set[str]

    def __init__(self, api: API, out_path: Path) -> None:
        self.api = api
        self.out_path = out_path
        self.current_todo_msgs = set()

    def generate_stubs(self) -> None:
        create_directory(Path(self.out_path / self.api.package))
        self._create_module_files()

    def _create_module_files(self) -> None:
        modules = self.api.modules.values()

        for module in modules:
            module_name = module.name
            module_id = module.id

            if module_name == "__init__":
                # Todo Handle __init__ files
                # Todo Handle reexported files that are already created
                self._create_reexported_files()
                continue

            # Create module dir
            module_dir = Path(self.out_path / module_id)
            create_directory(module_dir)

            # Create and open module file
            file_path = Path(module_dir / f"{module_name}.sdsstub")
            Path(file_path).touch()

            with file_path.open("w") as f:
                # Create package info
                package_info = module_id.replace("/", ".")
                f.write(f"package {package_info}\n")

                # Create imports
                self._write_qualified_imports(f, module.qualified_imports)
                self._write_wildcard_imports(f, module.wildcard_imports)

                # Create global functions
                for function in module.global_functions:
                    if function.is_public:
                        function_string = self._create_function_string(function, 0, is_class_method=False)
                        f.write(f"\n{function_string}\n")

                # Create classes, class attr. & class methods
                for class_ in module.classes:
                    if class_.is_public:
                        self._write_class(f, class_, 0)

                # Create enums & enum instances
                for enum in module.enums:
                    self._write_enum(f, enum)

            # Todo Frage:
            # Delete the file, if it has no content besides the "package" information in the first line
            with file_path.open("r") as f:
                delete_file = False
                if sum(1 for _ in f) <= 1:
                    delete_file = True
            if delete_file:
                shutil.rmtree(module_dir)

    def _create_reexported_files(self):
        pass

    def _write_class(self, f: TextIO, class_: Class, indent_quant: int) -> None:
        class_indentation = "\t" * indent_quant
        inner_indentations = class_indentation + "\t"

        # Constructor parameter
        constructor = class_.constructor
        parameter_info = ""
        if constructor:
            parameter_info = self._create_parameter_string(constructor.parameters, is_instance_method=True)

        # Superclasses
        superclasses = class_.superclasses
        superclass_info = ""
        if superclasses:
            superclass_names = [
                split_import_id(superclass)[1]
                for superclass in superclasses
            ]
            superclass_info = f" sub {', '.join(superclass_names)}"

        # Class signature line
        f.write(
            f"\n{class_indentation}{self.create_todo_msg(0)}class "
            f"{class_.name}{parameter_info}{superclass_info} {{",
        )

        # Attributes
        class_attributes: list[str] = []
        for attribute in class_.attributes:
            if not attribute.is_public:
                continue

            attribute_type = None
            if attribute.type:
                attribute_type = attribute.type.to_dict()

            attr_type = self._create_type_string(attribute_type)
            type_string = f": {attr_type}" if attr_type else ""
            class_attributes.append(
                f"{self.create_todo_msg(indent_quant + 1)}"
                f"attr {attribute.name}"
                f"{type_string}",
            )

        if class_attributes:
            attributes = f"\n{inner_indentations}".join(class_attributes)
            f.write(f"\n{inner_indentations}{attributes}\n")

        # Inner classes
        for inner_class in class_.classes:
            self._write_class(f, inner_class, indent_quant + 1)

        # Methods
        class_methods: list[str] = []
        for method in class_.methods:
            if not method.is_public:
                continue
            class_methods.append(
                self._create_function_string(method, indent_quant + 1, is_class_method=True),
            )
        if class_methods:
            methods = f"\n\n{inner_indentations}".join(class_methods)
            f.write(f"\n{inner_indentations}{methods}\n")

        # Close class
        f.write(f"{class_indentation}}}\n")

    def _create_function_string(self, function: Function, indent_quant: int, is_class_method: bool = False) -> str:
        is_static = function.is_static
        static = "static " if is_static else ""

        # Parameters
        is_instance_method = not is_static and is_class_method
        func_params = self._create_parameter_string(function.parameters, is_instance_method)
        if not func_params:
            func_params = "()"

        return (
            f"{self.create_todo_msg(indent_quant)}"
            f"{static}fun {function.name}{func_params}"
            f"{self._create_result_string(function.results)}"
        )

    def _create_result_string(self, function_results: list[Result]) -> str:
        results: list[str] = []
        for result in function_results:
            result_type = result.type.to_dict()
            ret_type = self._create_type_string(result_type)
            type_string = f": {ret_type}" if ret_type else ""
            results.append(
                f"{result.name}"
                f"{type_string}",
            )

        if results:
            if len(results) == 1:
                return f" -> {results[0]}"
            return f" -> ({', '.join(results)})"
        return ""

    def _create_parameter_string(self, parameters: list[Parameter], is_instance_method: bool = False) -> str:
        parameters_data: list[str] = []
        first_loop_skipped = False
        for parameter in parameters:
            # Skip self parameter for functions
            if is_instance_method and not first_loop_skipped:
                first_loop_skipped = True
                continue

            # Default value
            param_value = ""
            param_default_value = parameter.default_value
            parameter_type_data = parameter.type.to_dict()
            if param_default_value is not None:
                if isinstance(param_default_value, str):
                    if parameter_type_data["kind"] == "NamedType" and parameter_type_data["name"] != "str":
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

            # Check if assigned_by is not illegal
            assigned_by = parameter.assigned_by
            if assigned_by == ParameterAssignment.POSITION_ONLY and parameter.default_value is not None:
                self.current_todo_msgs.add("OPT_POS_ONLY")
            elif assigned_by == ParameterAssignment.NAME_ONLY and not parameter.is_optional:
                self.current_todo_msgs.add("REQ_NAME_ONLY")

            # Parameter type
            param_type = self._create_type_string(parameter_type_data)
            type_string = f": {param_type}" if param_type else ""

            # Create string and append to the list
            parameters_data.append(
                f"{parameter.name}"
                f"{type_string}{param_value}",
            )
        if parameters_data:
            return f"({', '.join(parameters_data)})"
        return ""

    @staticmethod
    def _write_qualified_imports(f: TextIO, qualified_imports: list[QualifiedImport]) -> None:
        if not qualified_imports:
            return

        imports: list[str] = []
        for qualified_import in qualified_imports:
            qualified_name = qualified_import.qualified_name
            import_path, name = split_import_id(qualified_name)

            import_path = replace_if_safeds_keyword(import_path)
            name = replace_if_safeds_keyword(name)

            from_path = ""
            if import_path:
                from_path = f"from {import_path} "

            alias = f" as {qualified_import.alias}" if qualified_import.alias else ""

            imports.append(
                f"{from_path}import {name}{alias}",
            )

        all_imports = "\n".join(imports)
        f.write(f"\n{all_imports}\n")

    @staticmethod
    def _write_wildcard_imports(f: TextIO, wildcard_imports: list[WildcardImport]) -> None:
        if not wildcard_imports:
            return

        imports = [
            f"from {wildcard_import.module_name} import *"
            for wildcard_import in wildcard_imports
        ]

        all_imports = "\n".join(imports)
        f.write(f"\n{all_imports}\n")

    @staticmethod
    def _write_enum(f: TextIO, enum_data: Enum) -> None:
        # Signature
        f.write(f"\nenum {enum_data.name} {{\n")

        # Enum instances
        for enum_instance in enum_data.instances:
            f.write(f"\t{enum_instance.name}" + "\n")

        # Close
        f.write("}\n")

    def _create_type_string(self, type_data: dict | None) -> str:
        """Create a SafeDS stubs type string."""
        if type_data is None:
            return ""

        none_type_name = "Nothing?"
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
                    return none_type_name
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
                if len(types) == 2 and none_type_name in types:
                    if types[0] == none_type_name:
                        return f"{types[1]}?"
                    else:
                        return f"{types[0]}?"
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
                todo_msgs.append("Tuple types are not allowed in SafeDS")
            elif msg in {"List", "Set"}:
                todo_msgs.append(f"{msg} type has to many type arguments")
            elif msg == "OPT_POS_ONLY":
                todo_msgs.append("Illegal parameter assignment: Optional but position only")
            elif msg == "REQ_NAME_ONLY":
                todo_msgs.append("Illegal parameter assignment: Required but name only")
            else:
                raise ValueError(f"Unknown todo message: {msg}")

        # Empty the message list
        self.current_todo_msgs = set()

        indentations = "\t" * indenta_quant
        return f"// Todo {', '.join(todo_msgs)}\n{indentations}"


# Todo Frage: An welchem Stellen soll ersetz werden? Auch Variablen und Enum Instanzen?
def replace_if_safeds_keyword(keyword: str) -> str:
    if keyword in {"as", "from", "import", "literal", "union", "where", "yield", "false", "null", "true", "annotation",
                   "attr", "class", "enum", "fun", "package", "pipeline", "schema", "segment", "val", "const", "in",
                   "internal", "out", "private", "static", "and", "not", "or", "sub", "super"}:
        return f"`{keyword}`"
    return keyword


def split_import_id(id_: str) -> tuple[str, str]:
    if "." not in id_:
        return "", id_

    split_qname = id_.split(".")
    name = split_qname.pop(-1)
    import_path = ".".join(split_qname)
    return import_path, name


def create_directory(path: Path) -> None:
    for i, _ in enumerate(path.parts):
        new_path = Path("/".join(path.parts[:i+1]))
        if not new_path.exists():
            Path.mkdir(new_path)