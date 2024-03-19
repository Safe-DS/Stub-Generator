from __future__ import annotations

from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING

from safeds_stubgen.api_analyzer import (
    API,
    Attribute,
    Class,
    Enum,
    Function,
    Module,
    Parameter,
    ParameterAssignment,
    Result,
    UnionType,
    VarianceKind,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from safeds_stubgen.docstring_parsing import AttributeDocstring, ClassDocstring, FunctionDocstring


class NamingConvention(IntEnum):
    PYTHON = 1
    SAFE_DS = 2


def generate_stubs(api: API, out_path: Path, convert_identifiers: bool) -> None:
    """Generate Safe-DS stubs.

    Generates stub files from an API object and writes them to the out_path path.

    Parameters
    ----------
    api
        The API object from which the stubs
    out_path
        The path in which the stub files should be created. If no such path exists this function creates the directory
        files.
    convert_identifiers
        Set this True if the identifiers should be converted to Safe-DS standard (UpperCamelCase for classes and
        camelCase for everything else).
    """
    naming_convention = NamingConvention.SAFE_DS if convert_identifiers else NamingConvention.PYTHON
    stubs_generator = StubsStringGenerator(api, naming_convention)
    stubs_data = _generate_stubs_data(api, out_path, stubs_generator)
    _generate_stubs_files(stubs_data, out_path, stubs_generator, naming_convention)


def _generate_stubs_data(
    api: API,
    out_path: Path,
    stubs_generator: StubsStringGenerator,
) -> list[tuple[Path, str, str]]:
    stubs_data: list[tuple[Path, str, str]] = []
    for module in api.modules.values():
        if module.name == "__init__":
            continue

        module_text = stubs_generator(module)

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

        module_dir = Path(out_path / module.id)
        stubs_data.append((module_dir, module.name, module_text))
    return stubs_data


def _generate_stubs_files(
    stubs_data: list[tuple[Path, str, str]],
    out_path: Path,
    stubs_generator: StubsStringGenerator,
    naming_convention: NamingConvention,
) -> None:
    for module_dir, module_name, module_text in stubs_data:
        # Create module dir
        module_dir.mkdir(parents=True, exist_ok=True)

        # Create and open module file
        file_path = Path(module_dir / f"{module_name}.sdsstub")
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


class StubsStringGenerator:
    """Generate Safe-DS stub strings.

    Generates stub string for Safe-DS. Each part has its own method, but it all starts with the create_module_string
    method.
    """

    def __init__(self, api: API, naming_convention: NamingConvention) -> None:
        self.api = api
        self.naming_convention = naming_convention
        self.classes_outside_package: set[str] = set()

    def __call__(self, module: Module) -> str:
        self.module_imports: set[str] = set()
        self._current_todo_msgs: set[str] = set()
        self.module = module
        self.class_generics: list = []
        return self._create_module_string()

    def _create_module_string(self) -> str:
        # Create package info
        package_info = self._get_shortest_public_reexport()
        package_info_camel_case = _convert_name_to_convention(package_info, self.naming_convention)
        module_name_info = ""
        module_text = ""
        if package_info != package_info_camel_case:
            module_name_info = f'@PythonModule("{package_info}")\n'
        module_header = f"{module_name_info}package {package_info_camel_case}\n"

        # Create docstring
        docstring = self._create_sds_docstring_description(self.module.docstring, "")
        if docstring:
            docstring += "\n"

        # Create global functions and properties
        for function in self.module.global_functions:
            if function.is_public:
                module_text += f"\n{self._create_function_string(function, is_method=False)}\n"

        # Create classes, class attr. & class methods
        for class_ in self.module.classes:
            if class_.is_public and not class_.inherits_from_exception:
                module_text += f"\n{self._create_class_string(class_)}\n"

        # Create enums & enum instances
        for enum in self.module.enums:
            module_text += f"\n{self._create_enum_string(enum)}\n"

        # Create imports - We have to create them last, since we have to check all used types in this module first
        module_header += self._create_imports_string()

        return docstring + module_header + module_text

    def _create_imports_string(self) -> str:
        if not self.module_imports:
            return ""

        import_strings = []

        for import_ in self.module_imports:
            import_parts = import_.split(".")

            from_ = ".".join(import_parts[0:-1])
            from_ = _convert_name_to_convention(from_, self.naming_convention)
            from_ = _replace_if_safeds_keyword(from_)

            name = import_parts[-1]
            name = _convert_name_to_convention(name, self.naming_convention)
            name = _replace_if_safeds_keyword(name)

            import_strings.append(f"from {from_} import {name}")

        # We have to sort for the snapshot tests
        import_strings.sort()

        import_string = "\n".join(import_strings)
        return f"\n{import_string}\n"

    def _create_class_string(self, class_: Class, class_indentation: str = "") -> str:
        inner_indentations = class_indentation + "\t"

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
        superclass_methods_text = ""
        if superclasses and not class_.is_abstract:
            superclass_names = []
            for superclass in superclasses:
                superclass_name = superclass.split(".")[-1]
                self._add_to_imports(superclass)

                if superclass not in self.module_imports and is_internal(superclass_name):
                    # If the superclass was not added to the module_imports through the _add_to_imports method, it means
                    # that the superclass is a class from the same module.
                    # For internal superclasses, we have to add their public members to subclasses.
                    superclass_methods_text += self._create_internal_class_methods_string(
                        superclass=superclass,
                        inner_indentations=inner_indentations,
                    )
                else:
                    superclass_names.append(superclass_name)

            superclass_info = f" sub {', '.join(superclass_names)}" if superclass_names else ""

        if len(superclasses) > 1:
            self._current_todo_msgs.add("multiple_inheritance")

        # Type parameters
        constraints_info = ""
        variance_info = ""

        constructor_type_vars = None
        if class_.constructor:
            constructor_type_vars = class_.constructor.type_var_types

        if class_.type_parameters or constructor_type_vars:
            # We collect the class generics for the methods later
            self.class_generics = []
            for variance in class_.type_parameters:
                variance_direction = {
                    VarianceKind.INVARIANT.name: "",
                    VarianceKind.COVARIANT.name: "out ",
                    VarianceKind.CONTRAVARIANT.name: "in ",
                }[variance.variance.name]

                # Convert name to camelCase and check for keywords
                variance_name_camel_case = _convert_name_to_convention(variance.name, self.naming_convention)
                variance_name_camel_case = _replace_if_safeds_keyword(variance_name_camel_case)

                variance_item = f"{variance_direction}{variance_name_camel_case}"
                if variance.type is not None:
                    variance_item = f"{variance_item} sub {self._create_type_string(variance.type.to_dict())}"
                self.class_generics.append(variance_item)

            if constructor_type_vars:
                for constructor_type_var in constructor_type_vars:
                    if constructor_type_var.name not in self.class_generics:
                        self.class_generics.append(constructor_type_var.name)

            if self.class_generics:
                variance_info = f"<{', '.join(self.class_generics)}>"

        # Class name - Convert to camelCase and check for keywords
        class_name = class_.name
        python_name_info = ""
        class_name_camel_case = _convert_name_to_convention(class_name, self.naming_convention, is_class_name=True)
        if class_name_camel_case != class_name:
            python_name_info = f"{class_indentation}{_create_name_annotation(class_name)}\n"
        class_name_camel_case = _replace_if_safeds_keyword(class_name_camel_case)

        # Class signature line
        class_signature = (
            f"{python_name_info}{class_indentation}{self._create_todo_msg(class_indentation)}class "
            f"{class_name_camel_case}{variance_info}{constructor_info}{superclass_info}{constraints_info}"
        )

        # Attributes
        class_text = self._create_class_attribute_string(class_.attributes, inner_indentations)

        # Inner classes
        for inner_class in class_.classes:
            class_text += f"\n{self._create_class_string(inner_class, inner_indentations)}\n"

        # Superclass methods, if the superclass is an internal class
        class_text += superclass_methods_text

        # Methods
        class_text += self._create_class_method_string(class_.methods, inner_indentations)

        # Docstring
        docstring = self._create_sds_docstring(class_.docstring, "", node=class_)

        # If the does not have a body, we just return the docstring and signature line
        if not class_text:
            return docstring + class_signature

        # Close class
        class_text += f"{class_indentation}}}"

        return f"{docstring}{class_signature} {{{class_text}"

    def _create_class_method_string(
        self,
        methods: list[Function],
        inner_indentations: str,
        is_internal_class: bool = False,
    ) -> str:
        class_methods: list[str] = []
        class_property_methods: list[str] = []
        for method in methods:
            # Add methods of internal classes that are inherited if the methods themselfe are public
            if not method.is_public and (not is_internal_class or (is_internal_class and is_internal(method.name))):
                continue
            elif method.is_property:
                class_property_methods.append(
                    self._create_property_function_string(method, inner_indentations),
                )
            else:
                class_methods.append(
                    self._create_function_string(method, inner_indentations, is_method=True),
                )

        method_text = ""
        if class_property_methods:
            properties = "\n".join(class_property_methods)
            method_text += f"\n{properties}\n"

        if class_methods:
            method_infos = "\n\n".join(class_methods)
            method_text += f"\n{method_infos}\n"

        return method_text

    def _create_class_attribute_string(self, attributes: list[Attribute], inner_indentations: str) -> str:
        class_attributes: list[str] = []
        for attribute in attributes:
            if not attribute.is_public:
                continue

            attribute_type = None
            if attribute.type:
                attribute_type = attribute.type.to_dict()

                # Don't create TypeVar attributes
                if attribute_type["kind"] == "TypeVarType":
                    continue

            static_string = "static " if attribute.is_static else ""

            # Convert name to camelCase and add PythonName annotation
            attr_name = attribute.name
            attr_name_camel_case = _convert_name_to_convention(attr_name, self.naming_convention)
            attr_name_annotation = ""
            if attr_name_camel_case != attr_name:
                attr_name_annotation = f"{_create_name_annotation(attr_name)}\n{inner_indentations}"

            # Check if name is a Safe-DS keyword and escape it if necessary
            attr_name_camel_case = _replace_if_safeds_keyword(attr_name_camel_case)

            # Create type information
            attr_type = self._create_type_string(attribute_type)
            type_string = f": {attr_type}" if attr_type else ""
            if not type_string:
                self._current_todo_msgs.add("attr without type")

            # Create docstring text
            docstring = self._create_sds_docstring(attribute.docstring, inner_indentations)

            # Create attribute string
            class_attributes.append(
                f"{self._create_todo_msg(inner_indentations)}"
                f"{docstring}{inner_indentations}{attr_name_annotation}"
                f"{static_string}attr {attr_name_camel_case}"
                f"{type_string}",
            )

        attribute_text = ""
        if class_attributes:
            attribute_infos = "\n".join(class_attributes)
            attribute_text += f"\n{attribute_infos}\n"
        return attribute_text

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

        # TypeVar
        type_var_info = ""
        if function.type_var_types:
            type_var_names = []
            for type_var in function.type_var_types:
                type_var_name = _convert_name_to_convention(type_var.name, self.naming_convention)
                type_var_name = _replace_if_safeds_keyword(type_var_name)

                # We don't have to display generic types in methods if they were already displayed in the class
                if not is_method or (is_method and type_var_name not in self.class_generics):
                    if type_var.upper_bound is not None:
                        type_var_name += f" sub {self._create_type_string(type_var.upper_bound.to_dict())}"
                    type_var_names.append(type_var_name)

            if type_var_names:
                type_var_string = ", ".join(type_var_names)
                type_var_info = f"<{type_var_string}>"

        # Docstring
        docstring = self._create_sds_docstring(function.docstring, indentations, function)

        # Convert function name to camelCase
        name = function.name
        camel_case_name = _convert_name_to_convention(name, self.naming_convention)
        function_name_annotation = ""
        if camel_case_name != name:
            function_name_annotation = f"{indentations}{_create_name_annotation(name)}\n"

        # Escape keywords
        camel_case_name = _replace_if_safeds_keyword(camel_case_name)

        result_string = self._create_result_string(function.results)

        # Create string and return
        return (
            f"{self._create_todo_msg(indentations)}"
            f"{docstring}"
            f"{indentations}@Pure\n"
            f"{function_name_annotation}"
            f"{indentations}{static}fun {camel_case_name}{type_var_info}"
            f"({func_params}){result_string}"
        )

    def _create_property_function_string(self, function: Function, indentations: str = "") -> str:
        """Create a string for functions with @property decorator.

        Functions or methods with the @property decorator are handled the same way as class attributes.
        """
        name = function.name
        camel_case_name = _convert_name_to_convention(name, self.naming_convention)
        function_name_annotation = ""
        if camel_case_name != name:
            function_name_annotation = f"{_create_name_annotation(name)} "

        # Escape keywords
        camel_case_name = _replace_if_safeds_keyword(camel_case_name)

        # Docstring
        docstring = self._create_sds_docstring_description(function.docstring.description, indentations)

        # Create type information
        result_types = [result.type for result in function.results if result.type is not None]
        result_union = UnionType(types=result_types)
        types_data = result_union.to_dict()
        property_type = self._create_type_string(types_data)
        type_string = f": {property_type}" if property_type else ""

        return (
            f"{self._create_todo_msg(indentations)}"
            f"{docstring}"
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
            result_name = _convert_name_to_convention(result.name, self.naming_convention)
            result_name = _replace_if_safeds_keyword(result_name)
            if type_string:
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
                        default_value = f"{param_default_value}"
                    elif isinstance(param_default_value, bool):
                        # Bool values have to be written in lower case
                        default_value = "true" if param_default_value else "false"
                    elif param_default_value is None:
                        default_value = "null"
                    else:
                        default_value = f"{param_default_value}"
                    param_value = f" = {default_value}"

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
            camel_case_name = _convert_name_to_convention(name, self.naming_convention)
            name_annotation = ""
            if camel_case_name != name:
                # Memorize the changed name for the @PythonName() annotation
                name_annotation = f"{_create_name_annotation(name)} "

            # Check if it's a Safe-DS keyword and escape it
            camel_case_name = _replace_if_safeds_keyword(camel_case_name)

            # Create string and append to the list
            parameters_data.append(
                f"{name_annotation}{camel_case_name}{type_string}{param_value}",
            )

        inner_indentations = indentations + "\t"
        if parameters_data:
            inner_param_data = f",\n{inner_indentations}".join(parameters_data)
            return f"\n{inner_indentations}{inner_param_data}\n{indentations}"
        return ""

    def _create_enum_string(self, enum_data: Enum) -> str:
        # Docstring
        docstring = self._create_sds_docstring(enum_data.docstring, "")

        # Signature
        enum_signature = f"{docstring}enum {enum_data.name}"

        # Enum body
        enum_text = ""
        instances = enum_data.instances
        if instances:
            enum_text += "\n"

            for enum_instance in instances:
                name = enum_instance.name

                # Convert snake_case names to camelCase
                camel_case_name = _convert_name_to_convention(name, self.naming_convention)
                annotation = ""
                if camel_case_name != name:
                    annotation = f"{_create_name_annotation(name)} "

                # Check if the name is a Safe-DS keyword and escape it
                camel_case_name = _replace_if_safeds_keyword(camel_case_name)

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
                    self._add_to_imports(type_data["qname"])

                    # inner classes that are private should not be used as types, therefore we add a todo
                    if name[0] == "_" and type_data["qname"] not in self.module_imports:
                        self._current_todo_msgs.add("internal class as type")

                    return name
        elif kind == "FinalType":
            return self._create_type_string(type_data["type"])
        elif kind == "CallableType":
            name_generator = _callable_type_name_generator()

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

            if name == "Set":
                self._current_todo_msgs.add("no set support")

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
                    if types[0] == none_type_name:
                        return f"{types[1]}?"
                    return f"{types[0]}?"

                # If the union contains only one type, return the type instead of creating a union
                elif len(types) == 1:
                    return types[0]

                return f"union<{', '.join(types)}>"
            return ""
        elif kind == "TupleType":
            self._current_todo_msgs.add("no tuple support")
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
                elif isinstance(literal_type, bool):
                    if literal_type:
                        types.append("true")
                    else:
                        types.append("false")
                else:
                    types.append(f"{literal_type}")
            return f"literal<{', '.join(types)}>"
        elif kind == "TypeVarType":
            name = _convert_name_to_convention(type_data["name"], self.naming_convention)
            return _replace_if_safeds_keyword(name)

        raise ValueError(f"Unexpected type: {kind}")  # pragma: no cover

    def _create_internal_class_methods_string(self, superclass: str, inner_indentations: str) -> str:
        superclass_name = superclass.split(".")[-1]

        superclass_class = self._get_class_in_module(superclass_name)
        superclass_methods_text = self._create_class_method_string(
            superclass_class.methods,
            inner_indentations,
            is_internal_class=True,
        )

        for superclass_superclass in superclass_class.superclasses:
            name = superclass_superclass.split(".")[-1]
            if is_internal(name):
                superclass_methods_text += self._create_internal_class_methods_string(
                    superclass_superclass,
                    inner_indentations,
                )

        return superclass_methods_text

    # ############################### Utilities ############################### #

    def _add_to_imports(self, qname: str) -> None:
        """Check if the qname of a type is defined in the current module, if not, create an import for it.

        Paramters
        ---------
        qname
            The qualified name of a module/class/etc.
        """
        if qname == "":  # pragma: no cover
            raise ValueError("Type has no import source.")

        qname_parts = qname.split(".")
        if qname_parts[0] == "builtins" and len(qname_parts) == 2:
            return

        module_id = self.module.id.replace("/", ".")
        if module_id not in qname:
            # We need the full path for an import from the same package, but we sometimes don't get enough information,
            # therefore we have to search for the class and get its id
            qname_path = qname.replace(".", "/")
            in_package = False
            for class_ in self.api.classes:
                if class_.endswith(qname_path):
                    qname = class_.replace("/", ".")
                    qname = _convert_name_to_convention(qname, self.naming_convention)
                    in_package = True
                    break

            if not in_package:
                self.classes_outside_package.add(qname)

            self.module_imports.add(qname)

    def _create_todo_msg(self, indentations: str) -> str:
        if not self._current_todo_msgs:
            return ""

        todo_msgs = [
            "// TODO "
            + {
                "no tuple support": "Safe-DS does not support tuple types.",
                "no set support": "Safe-DS does not support set types.",
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
                "internal class as type": "An internal class must not be used as a type in a public class.",
            }[msg]
            for msg in self._current_todo_msgs
        ]
        todo_msgs.sort()

        # Empty the message list
        self._current_todo_msgs = set()

        return indentations + f"\n{indentations}".join(todo_msgs) + "\n"

    def _get_class_in_module(self, class_name: str) -> Class:
        if f"{self.module.id}/{class_name}" in self.api.classes:
            return self.api.classes[f"{self.module.id}/{class_name}"]

        # If the class is a nested class
        for class_ in self.api.classes:
            if class_.startswith(self.module.id) and class_.endswith(class_name):
                return self.api.classes[class_]

        raise LookupError(f"Expected finding class '{class_name}' in module '{self.module.id}'.")  # pragma: no cover

    def _get_shortest_public_reexport(self) -> str:
        module_qname = self.module.id.replace("/", ".")
        module_name = self.module.name
        reexports = self.api.reexport_map

        def _module_name_check(name: str, string: str) -> bool:
            return (
                string == name
                or (f".{name}" in string and (string.endswith(f".{name}") or f"{name}." in string))
                or (f"{name}." in string and (string.startswith(f"{name}.") or f".{name}" in string))
            )

        keys = [reexport_key for reexport_key in reexports if _module_name_check(module_name, reexport_key)]

        module_ids = set()
        for key in keys:
            for module in reexports[key]:
                added_module_id = False

                for qualified_import in module.qualified_imports:
                    if _module_name_check(module_name, qualified_import.qualified_name):
                        module_ids.add(module.id)
                        added_module_id = True
                        break

                if added_module_id:
                    continue

                for wildcard_import in module.wildcard_imports:
                    if _module_name_check(module_name, wildcard_import.module_name):
                        module_ids.add(module.id)
                        break

        # Adjust all ids
        fixed_module_ids_parts = [module_id.split("/") for module_id in module_ids]

        shortest_id = None
        for fixed_module_id_parts in fixed_module_ids_parts:
            if shortest_id is None or len(fixed_module_id_parts) < len(shortest_id):
                shortest_id = fixed_module_id_parts

                if len(shortest_id) == 1:
                    break

        if shortest_id is None:
            return module_qname
        return ".".join(shortest_id)

    @staticmethod
    def _create_sds_docstring_description(description: str, indentations: str) -> str:
        if not description:
            return ""

        description = description.rstrip("\n")
        description = description.lstrip("\n")
        description = description.replace("\n", f"\n{indentations} * ")
        return f"{indentations}/**\n{indentations} * {description}\n{indentations} */\n"

    def _create_sds_docstring(
        self,
        docstring: ClassDocstring | FunctionDocstring | AttributeDocstring,
        indentations: str,
        node: Class | Function | None = None,
    ) -> str:
        full_docstring = ""

        # Description
        if docstring.description:
            docstring_description = docstring.description.rstrip("\n")
            docstring_description = docstring_description.lstrip("\n")
            docstring_description = docstring_description.replace("\n", f"\n{indentations} * ")
            full_docstring += f"{indentations} * {docstring_description}\n"

        # Parameters
        full_parameter_docstring = ""
        if node is not None:
            parameters = []
            if isinstance(node, Class):
                if node.constructor is not None:
                    parameters = node.constructor.parameters
            else:
                parameters = node.parameters

            if parameters:
                parameter_docstrings = []
                for parameter in parameters:
                    param_desc = parameter.docstring.description
                    if not param_desc:
                        continue

                    param_desc = f"\n{indentations} * ".join(param_desc.split("\n"))

                    parameter_name = _convert_name_to_convention(parameter.name, self.naming_convention)
                    parameter_docstrings.append(f"{indentations} * @param {parameter_name} {param_desc}\n")

                full_parameter_docstring = "".join(parameter_docstrings)

                if full_parameter_docstring and full_docstring:
                    full_parameter_docstring = f"{indentations} *\n{full_parameter_docstring}"
        full_docstring += full_parameter_docstring

        # Results
        full_result_docstring = ""
        if isinstance(node, Function):
            result_docstrings = []
            for result in node.results:
                result_desc = result.docstring.description
                if not result_desc:
                    continue

                result_desc = f"\n{indentations} * ".join(result_desc.split("\n"))

                result_name = _convert_name_to_convention(result.name, self.naming_convention)
                result_docstrings.append(f"{indentations} * @result {result_name} {result_desc}\n")

            full_result_docstring = "".join(result_docstrings)

            if full_result_docstring and full_docstring:
                full_result_docstring = f"{indentations} *\n{full_result_docstring}"
        full_docstring += full_result_docstring

        # Open and close the docstring
        if full_docstring:
            full_docstring = f"{indentations}/**\n{full_docstring}{indentations} */\n"

        return full_docstring


def _callable_type_name_generator() -> Generator:
    """Generate a name for callable type parameters starting from 'a' until 'zz'."""
    while True:
        for x in range(1, 1000):
            yield f"param{x}"


def _create_name_annotation(name: str) -> str:
    return f'@PythonName("{name}")'


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


def is_internal(name: str) -> bool:
    return name.startswith("_")


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
