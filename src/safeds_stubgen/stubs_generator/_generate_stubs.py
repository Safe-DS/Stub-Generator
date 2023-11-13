from __future__ import annotations

import shutil
from pathlib import Path

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


# Todo Docstrings / Descriptions
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
                module_text = f"package {package_info}\n"

                # Create imports
                qualified_imports = self._create_qualified_imports_string(module.qualified_imports)
                if qualified_imports:
                    module_text += f"\n{qualified_imports}\n"

                wildcard_imports = self._create_wildcard_imports_string(module.wildcard_imports)
                if wildcard_imports:
                    module_text += f"\n{wildcard_imports}\n"

                # Create global functions
                for function in module.global_functions:
                    if function.is_public:
                        module_text += f"\n{self._create_function_string(function, is_class_method=False)}\n"

                # Create classes, class attr. & class methods
                for class_ in module.classes:
                    if class_.is_public:
                        module_text += f"\n{self._create_class_string(class_)}\n"

                # Create enums & enum instances
                for enum in module.enums:
                    module_text += f"\n{self._create_enum_string(enum)}\n"

                # Write module
                f.write(module_text)

            # Todo Frage:
            # Delete the file, if it has no content besides the "package" information in the first line
            with file_path.open("r") as f:
                delete_file = False
                if sum(1 for _ in f) <= 1:
                    delete_file = True
            if delete_file:
                shutil.rmtree(module_dir)

    def _create_class_string(self, class_: Class, class_indentation: str = "") -> str:
        inner_indentations = class_indentation + "\t"
        class_text = ""

        # Constructor parameter
        constructor = class_.constructor
        parameter_info = ""
        if constructor:
            parameter_info = self._create_parameter_string(
                constructor.parameters, class_indentation, is_instance_method=True
            )

        # Superclasses
        superclasses = class_.superclasses
        superclass_info = ""
        if superclasses:
            superclass_names = [
                split_import_id(superclass)[1]
                for superclass in superclasses
            ]
            superclass_info = f" sub {', '.join(superclass_names)}"

        if len(superclasses) > 1:
            self.current_todo_msgs.add("multiple_inheritance")

        # Class signature line
        class_signature = (
            f"{class_indentation}{self.create_todo_msg(class_indentation)}class "
            f"{class_.name}({parameter_info}){superclass_info}"
        )

        # Attributes
        class_attributes: list[str] = []
        for attribute in class_.attributes:
            if not attribute.is_public:
                continue

            attribute_type = None
            if attribute.type:
                attribute_type = attribute.type.to_dict()

            static_string = "static " if attribute.is_static else ""

            # Convert name to camelCase and add PythonName annotation
            attr_name = attribute.name
            attr_name_camel_case = _convert_snake_to_camel_case(attr_name)
            attr_name_annotation = ""
            if attr_name_camel_case != attr_name:
                attr_name_annotation = f"{self._create_name_annotation(attr_name)}\n{inner_indentations}"

            # Check if name is a Safe-DS keyword and escape it if necessary
            attr_name_camel_case = self._replace_if_safeds_keyword(attr_name_camel_case)

            # Create type information
            attr_type = self._create_type_string(attribute_type)
            type_string = f": {attr_type}" if attr_type else ""

            # Create attribute string
            class_attributes.append(
                f"{self.create_todo_msg(inner_indentations)}"
                f"{inner_indentations}{attr_name_annotation}"
                f"{static_string}attr {attr_name_camel_case}"
                f"{type_string}",
            )

        if class_attributes:
            attributes = "\n".join(class_attributes)
            class_text += f"\n{attributes}\n"

        # Inner classes
        for inner_class in class_.classes:
            class_text += f"\n{self._create_class_string(inner_class, inner_indentations)}\n"

        # Methods
        class_methods: list[str] = []
        for method in class_.methods:
            if not method.is_public:
                continue
            class_methods.append(
                self._create_function_string(method, inner_indentations, is_class_method=True),
            )
        if class_methods:
            methods = "\n\n".join(class_methods)
            class_text += f"\n{methods}\n"

        # If the does not have a body, we just return the signature line
        if not class_text:
            return class_signature

        # Close class
        class_text += f"{class_indentation}}}"

        return f"{class_signature} {{{class_text}"

    def _create_function_string(self, function: Function, indentations: str = "", is_class_method: bool = False) -> str:
        """Create a function string for Safe-DS stubs."""
        is_static = function.is_static
        static = "static " if is_static else ""

        # Parameters
        is_instance_method = not is_static and is_class_method
        func_params = self._create_parameter_string(function.parameters, indentations, is_instance_method)

        # Convert function name to camelCase
        name = function.name
        camel_case_name = _convert_snake_to_camel_case(name)
        function_name_annotation = ""
        if camel_case_name != name:
            function_name_annotation = f"{indentations}{self._create_name_annotation(name)}\n"

        # Create string and return
        return (
            f"{self.create_todo_msg(indentations)}"
            f"{function_name_annotation}"
            f"{indentations}{static}fun {camel_case_name}({func_params})"
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

    def _create_parameter_string(
        self, parameters: list[Parameter], indentations: str, is_instance_method: bool = False
    ) -> str:
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

            # Mypy assignes *args parameters the tuple type, which is not supported in Safe-DS. Therefor we overwrite it
            # and set the type to a list.
            if assigned_by == ParameterAssignment.POSITIONAL_VARARG:
                parameter_type_data["kind"] = "ListType"

            # Safe-DS does not support variadic parameters.
            if assigned_by in {ParameterAssignment.POSITIONAL_VARARG, ParameterAssignment.NAMED_VARARG}:
                self.current_todo_msgs.add("variadic")

            # Parameter type
            param_type = self._create_type_string(parameter_type_data)
            type_string = f": {param_type}" if param_type else ""

            # Convert to camelCase if necessary
            name = parameter.name
            camel_case_name = _convert_snake_to_camel_case(name)
            name_annotation = ""
            if camel_case_name != name:
                # Memorize the changed name for the @PythonName() annotation
                name_annotation = f"{self._create_name_annotation(name)} "

            # Check if it's a Safe-DS keyword and escape it
            camel_case_name = self._replace_if_safeds_keyword(camel_case_name)

            # Create string and append to the list
            parameters_data.append(
                f"{name_annotation}{camel_case_name}"
                f"{type_string}{param_value}",
            )

        inner_indentations = indentations + "\t"
        if parameters_data:
            inner_param_data = f",\n{inner_indentations}".join(parameters_data)
            return f"\n{inner_indentations}{inner_param_data}\n{indentations}"
        return ""

    def _create_qualified_imports_string(self, qualified_imports: list[QualifiedImport]) -> str:
        if not qualified_imports:
            return ""

        imports: list[str] = []
        for qualified_import in qualified_imports:
            qualified_name = qualified_import.qualified_name
            import_path, name = split_import_id(qualified_name)

            import_path = self._replace_if_safeds_keyword(import_path)
            name = self._replace_if_safeds_keyword(name)

            # Ignore enum imports, since those are build in types in Safe-DS stubs
            if import_path == "enum" and name in {"Enum", "IntEnum"}:
                continue

            from_path = ""
            if import_path:
                from_path = f"from {import_path} "

            alias = f" as {qualified_import.alias}" if qualified_import.alias else ""

            imports.append(
                f"{from_path}import {name}{alias}",
            )

        return "\n".join(imports)

    @staticmethod
    def _create_wildcard_imports_string(wildcard_imports: list[WildcardImport]) -> str:
        if not wildcard_imports:
            return ""

        imports = [
            f"from {wildcard_import.module_name} import *"
            for wildcard_import in wildcard_imports
        ]

        return "\n".join(imports)

    # Todo Frage: Wir unterstützen keine Schachtelungen von Enums, richtig? Weder in Enums noch in Klassen
    def _create_enum_string(self, enum_data: Enum) -> str:
        # Signature
        enum_signature = f"enum {enum_data.name}"

        # Enum body
        enum_text = ""
        instances = enum_data.instances
        if instances:
            enum_text += "\n"

            for enum_instance in instances:
                name = enum_instance.name

                # Todo Frage: Sicher, dass wir Enum Instancen umschreiben?
                # Convert snake_case names to camelCase
                camel_case_name = _convert_snake_to_camel_case(name)
                annotation = ""
                if camel_case_name != name:
                    annotation = f"\t{self._create_name_annotation(name)}\n"

                # Check if the name is a Safe-DS keyword and escape it
                camel_case_name = self._replace_if_safeds_keyword(camel_case_name)

                enum_text += f"{annotation}\t{camel_case_name}\n"
            return f"{enum_signature} {{{enum_text}}}"

        return enum_signature

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

    def create_todo_msg(self, indentations: str) -> str:
        if not self.current_todo_msgs:
            return ""

        todo_msgs = [
            "// TODO " + {
                "Tuple": "Safe-DS does not support tuple types.",
                "List": "List type has to many type arguments.",
                "Set": "Set type has to many type arguments.",
                "OPT_POS_ONLY": "Safe-DS does not support optional but position only parameter assignments.",
                "REQ_NAME_ONLY": "Safe-DS does not support required but name only parameter assignments.",
                "multiple_inheritance": "Safe-DS does not support multiple inheritance.",
                "variadic": "Safe-DS does not support variadic parameters.",
            }[msg]
            for msg in self.current_todo_msgs
        ]

        # Empty the message list
        self.current_todo_msgs = set()

        return indentations + f"\n{indentations}".join(todo_msgs) + "\n"

    @staticmethod
    def _create_name_annotation(name: str) -> str:
        return f'@PythonName("{name}")'

    @staticmethod
    def _replace_if_safeds_keyword(keyword: str) -> str:
        if keyword in {"as", "from", "import", "literal", "union", "where", "yield", "false", "null", "true",
                       "annotation",
                       "attr", "class", "enum", "fun", "package", "pipeline", "schema", "segment", "val", "const", "in",
                       "internal", "out", "private", "static", "and", "not", "or", "sub", "super"}:
            return f"`{keyword}`"
        return keyword


# Todo Frage: mixed_snake_camelCase_naMe -> mixedSnakeCamelCaseNaMe | _ -> _ ? Special cases? Results (Darstellung)?
def _convert_snake_to_camel_case(name: str) -> str:
    if name == "_":
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
    return name_parts[0] + "".join(
        part[0].upper() + part[1:]
        for part in name_parts[1:]
        if part
    )


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
