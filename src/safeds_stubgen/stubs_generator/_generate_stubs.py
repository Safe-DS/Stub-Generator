from __future__ import annotations

import string
from pathlib import Path
from typing import TYPE_CHECKING

from safeds_stubgen.api_analyzer import (
    API,
    Class,
    Enum,
    Function,
    Module,
    Parameter,
    ParameterAssignment,
    QualifiedImport,
    Result,
    UnionType,
    VarianceKind,
    WildcardImport,
)

if TYPE_CHECKING:
    from collections.abc import Generator


def generate_stubs(api: API, out_path: Path, convert_identifiers: bool) -> None:
    """Generate Safe-DS stubs.

    Generates stub files from an API object and writes them to the out_path path.

    Parameters
    ----------
    api : API
        The API object from which the stubs
    out_path : Path
        The path in which the stub files should be created. If no such path exists this function creates the directory
        files.
    convert_identifiers : bool
        Set this True if the identifiers should be converted to Safe-DS standard (UpperCamelCase for classes and
        camelCase for everything else).
    """
    modules = api.modules.values()

    Path(out_path / api.package).mkdir(parents=True, exist_ok=True)
    generator = StubsStringGenerator(convert_identifiers)

    for module in modules:
        module_name = module.name

        if module_name == "__init__":
            continue

        module_text = generator.create_module_string(module)

        # Each text block we create ends with "\n", therefore, is there is only the package information
        # the file would look like this: "package path.to.myPackage\n" or this:
        # '@PythonModule("path.to.my_package")\npackage path.to.myPackage\n'. With the split we check if the module
        # has enough information, if not, we won't create it.
        splitted_text = module_text.split("\n")
        if len(splitted_text) <= 2 or (len(splitted_text) == 3 and splitted_text[1].startswith("package ")):
            continue

        # Create module dir
        module_dir = Path(out_path / module.id)
        module_dir.mkdir(parents=True, exist_ok=True)

        # Create and open module file
        file_path = Path(module_dir / f"{module_name}.sdsstub")
        Path(file_path).touch()

        with file_path.open("w") as f:
            f.write(module_text)


class StubsStringGenerator:
    """Generate Safe-DS stub strings.

    Generates stub string for Safe-DS. Each part has its own method, but it all starts with the create_module_string
    method.
    """

    def __init__(self, convert_identifiers: bool) -> None:
        self._current_todo_msgs: set[str] = set()
        self.convert_identifiers = convert_identifiers

    def create_module_string(self, module: Module) -> str:
        # Create package info
        package_info = module.id.replace("/", ".")
        package_info_camel_case = self._convert_snake_to_camel_case(package_info)
        module_name_info = ""
        if package_info != package_info_camel_case:
            module_name_info = f'@PythonModule("{package_info}")\n'
        module_text = f"{module_name_info}package {package_info_camel_case}\n"

        # Create imports
        qualified_imports = self._create_qualified_imports_string(module.qualified_imports)
        if qualified_imports:
            module_text += f"\n{qualified_imports}\n"

        wildcard_imports = self._create_wildcard_imports_string(module.wildcard_imports)
        if wildcard_imports:
            module_text += f"\n{wildcard_imports}\n"

        # Create global functions and properties
        for function in module.global_functions:
            if function.is_public:
                module_text += f"\n{self._create_function_string(function, is_method=False)}\n"

        # Create classes, class attr. & class methods
        for class_ in module.classes:
            if class_.is_public:
                module_text += f"\n{self._create_class_string(class_)}\n"

        # Create enums & enum instances
        for enum in module.enums:
            module_text += f"\n{self._create_enum_string(enum)}\n"

        return module_text

    def _create_class_string(self, class_: Class, class_indentation: str = "") -> str:
        inner_indentations = class_indentation + "\t"
        class_text = ""

        # Constructor parameter
        if class_.is_abstract:
            # Abstract classes have no constructor
            constructor_info = ""
        else:
            constructor = class_.constructor
            parameter_info = ""
            if constructor:
                parameter_info = self._create_parameter_string(
                    constructor.parameters,
                    class_indentation,
                    is_instance_method=True,
                )

            constructor_info = f"({parameter_info})"

        # Superclasses
        superclasses = class_.superclasses
        superclass_info = ""
        if superclasses and not class_.is_abstract:
            superclass_names = [self._split_import_id(superclass)[1] for superclass in superclasses]
            superclass_info = f" sub {', '.join(superclass_names)}"

        if len(superclasses) > 1:
            self._current_todo_msgs.add("multiple_inheritance")

        # Type parameters
        constraints_info = ""
        variance_info = ""
        if class_.type_parameters:
            constraints = []
            variances = []
            for variance in class_.type_parameters:
                match variance.variance.name:
                    case VarianceKind.INVARIANT.name:
                        variance_inheritance = ""
                        variance_direction = ""
                    case VarianceKind.COVARIANT.name:
                        variance_inheritance = "sub"
                        variance_direction = "out "
                    case VarianceKind.CONTRAVARIANT.name:
                        variance_inheritance = "super"
                        variance_direction = "in "
                    case _:  # pragma: no cover
                        raise ValueError(f"Expected variance kind, got {variance.variance.name}.")

                # Convert name to camelCase and check for keywords
                variance_name_camel_case = self._convert_snake_to_camel_case(variance.name)
                variance_name_camel_case = self._replace_if_safeds_keyword(variance_name_camel_case)

                variances.append(f"{variance_direction}{variance_name_camel_case}")
                if variance_inheritance:
                    constraints.append(
                        f"{variance_name_camel_case} {variance_inheritance} "
                        f"{self._create_type_string(variance.type.to_dict())}",
                    )

            if variances:
                variance_info = f"<{', '.join(variances)}>"

            if constraints:
                constraints_info_inner = f",\n{inner_indentations}".join(constraints)
                constraints_info = f" where {{\n{inner_indentations}{constraints_info_inner}\n}}"

        # Class name - Convert to camelCase and check for keywords
        class_name = class_.name
        python_name_info = ""
        class_name_camel_case = self._convert_snake_to_camel_case(class_name, is_class_name=True)
        if class_name_camel_case != class_name:
            python_name_info = f"{class_indentation}{self._create_name_annotation(class_name)}\n"
        class_name_camel_case = self._replace_if_safeds_keyword(class_name_camel_case)

        # Class signature line
        class_signature = (
            f"{python_name_info}{class_indentation}{self._create_todo_msg(class_indentation)}class "
            f"{class_name_camel_case}{variance_info}{constructor_info}{superclass_info}{constraints_info}"
        )

        # Attributes
        class_attributes: list[str] = []
        for attribute in class_.attributes:
            if not attribute.is_public:
                continue

            attribute_type = None
            if attribute.type:
                attribute_type = attribute.type.to_dict()
            else:
                self._current_todo_msgs.add("attr without type")

            static_string = "static " if attribute.is_static else ""

            # Convert name to camelCase and add PythonName annotation
            attr_name = attribute.name
            attr_name_camel_case = self._convert_snake_to_camel_case(attr_name)
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
                f"{self._create_todo_msg(inner_indentations)}"
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
        class_property_methods: list[str] = []
        for method in class_.methods:
            if not method.is_public:
                continue
            elif method.is_property:
                class_property_methods.append(
                    self._create_property_function_string(method, inner_indentations),
                )
            else:
                class_methods.append(
                    self._create_function_string(method, inner_indentations, is_method=True),
                )

        if class_property_methods:
            properties = "\n".join(class_property_methods)
            class_text += f"\n{properties}\n"

        if class_methods:
            methods = "\n\n".join(class_methods)
            class_text += f"\n{methods}\n"

        # If the does not have a body, we just return the signature line
        if not class_text:
            return class_signature

        # Close class
        class_text += f"{class_indentation}}}"

        return f"{class_signature} {{{class_text}"

    def _create_function_string(self, function: Function, indentations: str = "", is_method: bool = False) -> str:
        """Create a function string for Safe-DS stubs."""
        # Check if static or class method
        is_static = function.is_static
        is_class_method = function.is_class_method

        static = ""
        if is_class_method or is_static:
            static = "static "

            if is_class_method:
                self._current_todo_msgs.add("class_method")

        # Parameters
        func_params = self._create_parameter_string(
            parameters=function.parameters,
            indentations=indentations,
            is_instance_method=not is_static and is_method,
        )

        # Convert function name to camelCase
        name = function.name
        camel_case_name = self._convert_snake_to_camel_case(name)
        function_name_annotation = ""
        if camel_case_name != name:
            function_name_annotation = f"{indentations}{self._create_name_annotation(name)}\n"

        # Escape keywords
        camel_case_name = self._replace_if_safeds_keyword(camel_case_name)

        result_string = self._create_result_string(function.results)

        # Create string and return
        return (
            f"{self._create_todo_msg(indentations)}"
            f"{indentations}@Pure\n"
            f"{function_name_annotation}"
            f"{indentations}{static}fun {camel_case_name}({func_params})"
            f"{result_string}"
        )

    def _create_property_function_string(self, function: Function, indentations: str = "") -> str:
        """Create a string for functions with @property decorator.

        Functions or methods with the @property decorator are handled the same way as class attributes.
        """
        name = function.name
        camel_case_name = self._convert_snake_to_camel_case(name)
        function_name_annotation = ""
        if camel_case_name != name:
            function_name_annotation = f"{self._create_name_annotation(name)} "

        # Escape keywords
        camel_case_name = self._replace_if_safeds_keyword(camel_case_name)

        # Create type information
        result_types = [result.type for result in function.results if result.type is not None]
        result_union = UnionType(types=result_types)
        types_data = result_union.to_dict()
        property_type = self._create_type_string(types_data)
        type_string = f": {property_type}" if property_type else ""

        return (
            f"{self._create_todo_msg(indentations)}"
            f"{indentations}{function_name_annotation}"
            f"attr {camel_case_name}{type_string}"
        )

    def _create_result_string(self, function_results: list[Result]) -> str:
        results: list[str] = []
        for result in function_results:
            if result.type is None:  # pragma: no cover
                continue

            result_type = result.type.to_dict()
            ret_type = self._create_type_string(result_type)
            type_string = f": {ret_type}" if ret_type else ""
            result_name = self._convert_snake_to_camel_case(result.name)
            result_name = self._replace_if_safeds_keyword(result_name)
            results.append(
                f"{result_name}{type_string}",
            )

        if results:
            if len(results) == 1:
                return f" -> {results[0]}"
            return f" -> ({', '.join(results)})"
        self._current_todo_msgs.add("result without type")
        return ""

    def _create_parameter_string(
        self,
        parameters: list[Parameter],
        indentations: str,
        is_instance_method: bool = False,
    ) -> str:
        parameters_data: list[str] = []
        first_loop_skipped = False
        for parameter in parameters:
            # Skip self parameter for functions
            if is_instance_method and not first_loop_skipped:
                first_loop_skipped = True
                continue

            assigned_by = parameter.assigned_by
            type_string = ""
            param_value = ""

            # Parameter type
            if parameter.type is not None:
                param_default_value = parameter.default_value
                parameter_type_data = parameter.type.to_dict()

                # Default value
                if parameter.is_optional:
                    if isinstance(param_default_value, str):
                        if parameter_type_data["kind"] == "NamedType" and parameter_type_data["name"] != "str":
                            default_value = f"{param_default_value}"
                        else:
                            default_value = f'"{param_default_value}"'
                    elif isinstance(param_default_value, bool):
                        # Bool values have to be written in lower case
                        default_value = "true" if param_default_value else "false"
                    elif param_default_value is None:
                        default_value = "null"
                    else:
                        default_value = f"{param_default_value}"
                    param_value = f" = {default_value}"
                elif parameter.is_optional and param_default_value is None:
                    param_value = " = null"

                # Mypy assignes *args parameters the tuple type, which is not supported in Safe-DS. Therefor we
                # overwrite it and set the type to a list.
                if assigned_by == ParameterAssignment.POSITIONAL_VARARG:
                    parameter_type_data["kind"] = "ListType"

                # Parameter type
                param_type = self._create_type_string(parameter_type_data)
                type_string = f": {param_type}" if param_type else ""
            else:
                self._current_todo_msgs.add("param without type")

                if assigned_by == ParameterAssignment.POSITIONAL_VARARG:
                    type_string = ": List<Any>"
                elif assigned_by == ParameterAssignment.NAMED_VARARG:
                    type_string = ": Map<String, Any>"

            # Check if assigned_by is not illegal
            if assigned_by == ParameterAssignment.POSITION_ONLY and parameter.default_value is not None:
                self._current_todo_msgs.add("OPT_POS_ONLY")
            elif assigned_by == ParameterAssignment.NAME_ONLY and not parameter.is_optional:
                self._current_todo_msgs.add("REQ_NAME_ONLY")

            # Safe-DS does not support variadic parameters.
            if assigned_by in {ParameterAssignment.POSITIONAL_VARARG, ParameterAssignment.NAMED_VARARG}:
                self._current_todo_msgs.add("variadic")

            # Convert to camelCase if necessary
            name = parameter.name
            camel_case_name = self._convert_snake_to_camel_case(name)
            name_annotation = ""
            if camel_case_name != name:
                # Memorize the changed name for the @PythonName() annotation
                name_annotation = f"{self._create_name_annotation(name)} "

            # Check if it's a Safe-DS keyword and escape it
            camel_case_name = self._replace_if_safeds_keyword(camel_case_name)

            # Create string and append to the list
            parameters_data.append(
                f"{name_annotation}{camel_case_name}{type_string}{param_value}",
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
            import_path, name = self._split_import_id(qualified_name)

            # Ignore enum imports, since those are build in types in Safe-DS stubs
            if import_path == "enum" and name in {"Enum", "IntEnum"}:
                continue

            # Create string and check if Safe-DS keywords are used and escape them if necessary
            from_path = f"from {self._replace_if_safeds_keyword(import_path)} " if import_path else ""
            alias = f" as {self._replace_if_safeds_keyword(qualified_import.alias)}" if qualified_import.alias else ""

            imports.append(
                f"{from_path}import {self._replace_if_safeds_keyword(name)}{alias}",
            )

        return "\n".join(imports)

    def _create_wildcard_imports_string(self, wildcard_imports: list[WildcardImport]) -> str:
        if not wildcard_imports:
            return ""

        imports = [
            f"from {self._replace_if_safeds_keyword(wildcard_import.module_name)} import *"
            for wildcard_import in wildcard_imports
        ]

        return "\n".join(imports)

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

                # Convert snake_case names to camelCase
                camel_case_name = self._convert_snake_to_camel_case(name)
                annotation = ""
                if camel_case_name != name:
                    annotation = f"{self._create_name_annotation(name)} "

                # Check if the name is a Safe-DS keyword and escape it
                camel_case_name = self._replace_if_safeds_keyword(camel_case_name)

                enum_text += f"\t{annotation}{camel_case_name}\n"
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
            return self._create_type_string(type_data["type"])
        elif kind == "CallableType":
            name_generator = self._callable_type_name_generator()

            params = [
                f"{next(name_generator)}: {self._create_type_string(parameter_type)}"
                for parameter_type in type_data["parameter_types"]
            ]

            return_type = type_data["return_type"]
            if return_type["kind"] == "TupleType":
                return_types = [
                    f"{next(name_generator)}: {self._create_type_string(type_)}" for type_ in return_type["types"]
                ]
                return_type_string = f"({', '.join(return_types)})"
            else:
                return_type_string = f"{next(name_generator)}: {self._create_type_string(return_type)}"

            return f"({', '.join(params)}) -> {return_type_string}"
        elif kind in {"SetType", "ListType"}:
            types = [self._create_type_string(type_) for type_ in type_data["types"]]

            # Cut out the "Type" in the kind name
            name = kind[0:-4]

            if types:
                if len(types) >= 2:
                    self._current_todo_msgs.add(name)
                return f"{name}<{', '.join(types)}>"
            return f"{name}<Any>"
        elif kind == "UnionType":
            # In Mypy LiteralTypes are getting seperated into unions of LiteralTypes,
            # and we have to join them for the stubs.
            literal_data = []
            other_type_data = []
            for type_information in type_data["types"]:
                if type_information["kind"] == "LiteralType":
                    literal_data.append(type_information)
                else:
                    other_type_data.append(type_information)

            if len(literal_data) >= 2:
                all_literals = [literal_type for literal in literal_data for literal_type in literal["literals"]]

                # We overwrite the old types of the union with the joined literal types
                type_data["types"] = other_type_data
                type_data["types"].append({
                    "kind": "LiteralType",
                    "literals": all_literals,
                })

            # Union items have to be unique, therefore we use sets. But the types set has to be a sorted list, since
            # otherwise the snapshot tests would fail b/c element order in sets is non-deterministic.
            types = list({self._create_type_string(type_) for type_ in type_data["types"]})
            types.sort()

            if types:
                if len(types) == 2 and none_type_name in types:
                    # if None is at least one of the two possible types, we can remove the None and just return the
                    # other type with a question mark
                    return f"{types[0]}?"

                # If the union contains only one type, return the type instead of creating a union
                elif len(types) == 1:
                    return types[0]

                return f"union<{', '.join(types)}>"
            return ""
        elif kind == "TupleType":
            self._current_todo_msgs.add("Tuple")
            types = [self._create_type_string(type_) for type_ in type_data["types"]]

            return f"Tuple<{', '.join(types)}>"
        elif kind == "DictType":
            key_data = self._create_type_string(type_data["key_type"])
            value_data = self._create_type_string(type_data["value_type"])
            return f"Map<{key_data}, {value_data}>"
        elif kind == "LiteralType":
            types = []
            for literal_type in type_data["literals"]:
                if isinstance(literal_type, str):
                    types.append(f'"{literal_type}"')
                else:
                    types.append(f"{literal_type}")
            return f"literal<{', '.join(types)}>"

        raise ValueError(f"Unexpected type: {kind}")  # pragma: no cover

    # ############################### Utilities ############################### #

    @staticmethod
    def _callable_type_name_generator() -> Generator:
        """Generate a name for callable type parameters starting from 'a' until 'zz'."""
        while True:
            for x in range(1, 27):
                yield string.ascii_lowercase[x - 1]
            for x in range(1, 27):  # pragma: no cover
                for y in range(1, 27):
                    yield string.ascii_lowercase[x - 1] + string.ascii_lowercase[y - 1]

    def _create_todo_msg(self, indentations: str) -> str:
        if not self._current_todo_msgs:
            return ""

        todo_msgs = [
            "// TODO "
            + {
                "Tuple": "Safe-DS does not support tuple types.",
                "List": "List type has to many type arguments.",
                "Set": "Set type has to many type arguments.",
                "OPT_POS_ONLY": "Safe-DS does not support optional but position only parameter assignments.",
                "REQ_NAME_ONLY": "Safe-DS does not support required but name only parameter assignments.",
                "multiple_inheritance": "Safe-DS does not support multiple inheritance.",
                "variadic": "Safe-DS does not support variadic parameters.",
                "class_method": "Safe-DS does not support class methods.",
                "param without type": "Some parameter have no type information.",
                "attr without type": "Attribute has no type information.",
                "result without type": "Result type information missing.",
            }[msg]
            for msg in self._current_todo_msgs
        ]
        todo_msgs.sort()

        # Empty the message list
        self._current_todo_msgs = set()

        return indentations + f"\n{indentations}".join(todo_msgs) + "\n"

    @staticmethod
    def _split_import_id(id_: str) -> tuple[str, str]:
        if "." not in id_:
            return "", id_

        split_qname = id_.split(".")
        name = split_qname.pop(-1)
        import_path = ".".join(split_qname)
        return import_path, name

    @staticmethod
    def _create_name_annotation(name: str) -> str:
        return f'@PythonName("{name}")'

    @staticmethod
    def _replace_if_safeds_keyword(keyword: str) -> str:
        if keyword in {
            "as",
            "from",
            "import",
            "literal",
            "union",
            "where",
            "yield",
            "false",
            "null",
            "true",
            "annotation",
            "attr",
            "class",
            "enum",
            "fun",
            "package",
            "pipeline",
            "schema",
            "segment",
            "val",
            "const",
            "in",
            "internal",
            "out",
            "private",
            "static",
            "and",
            "not",
            "or",
            "sub",
            "super",
            "_",
        }:
            return f"`{keyword}`"
        return keyword

    def _convert_snake_to_camel_case(self, name: str, is_class_name: bool = False) -> str:
        if not self.convert_identifiers:
            return name

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

        # UpperCamelCase for class names
        if is_class_name:
            return "".join(part[0].upper() + part[1:] for part in name_parts if part)

        # Normal camelCase for everything else
        return name_parts[0] + "".join(part[0].upper() + part[1:] for part in name_parts[1:] if part)
