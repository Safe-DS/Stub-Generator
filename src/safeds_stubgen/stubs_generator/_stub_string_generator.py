from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from types import NoneType
from typing import TYPE_CHECKING

from safeds_stubgen import is_internal
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
    result_name_generator,
)
from safeds_stubgen.docstring_parsing import AttributeDocstring

from ._helper import (
    INDENTATION,
    NamingConvention,
    _convert_name_to_convention,
    _create_name_annotation,
    _get_shortest_public_reexport,
    _replace_if_safeds_keyword,
)

if TYPE_CHECKING:
    from safeds_stubgen.docstring_parsing import ClassDocstring, FunctionDocstring


class StubsStringGenerator:
    """Generate Safe-DS stub strings.

    Generates stub string for Safe-DS. Each part has its own method, but it all starts with the create_module_string
    method.
    """

    def __init__(self, api: API, convert_identifiers: bool) -> None:
        self.module_id: str = ""
        self.class_generics: list = []
        self.module_imports: set[str] = set()

        self.api = api
        self.naming_convention = NamingConvention.SAFE_DS if convert_identifiers else NamingConvention.PYTHON
        self.classes_outside_package: set[str] = set()
        self.reexport_modules: dict[str, list[Class | Function]] = defaultdict(list)

    def __call__(self, module: Module) -> tuple[str, str]:
        self.module_id = module.id
        self.class_generics = []
        self.module_imports = set()

        self._current_todo_msgs: set[str] = set()
        return self._create_module_string(module)

    def create_reexport_module_strings(self, out_path: Path) -> list[tuple[Path, str, str, bool]]:
        module_data = []
        for module_id in self.reexport_modules:
            elements: list[Class | Function] = self.reexport_modules[module_id]

            # We sort for the snapshot tests
            elements.sort(key=lambda x: x.name)

            for element in elements:
                # Reset the objects that we normally would reset in the __call__
                self.module_imports = set()
                self.class_generics = []

                module_name = element.name
                self.module_id = f"{module_id}/{module_name}"

                # Create module header
                package_info = ".".join(self.module_id.split("/")[:-1])
                package_info_camel_case = _convert_name_to_convention(package_info, self.naming_convention)
                module_name_info = ""
                if package_info != package_info_camel_case:
                    module_name_info = f'@PythonModule("{package_info}")\n'
                module_header = f"{module_name_info}package {package_info_camel_case}\n"

                # Create body text
                if isinstance(element, Class):
                    module_text = f"\n{self._create_class_string(class_=element, in_reexport_module=True)}\n"
                elif isinstance(element, Function):
                    module_text = f"\n{self._create_function_string(function=element, in_reexport_module=True)}\n"
                else:  # pragma: no cover
                    msg = f"Could not create a module for {element.id}. Unsupported type {type(element)}."
                    logging.warning(msg)
                    continue

                # Create imports
                #  We have to create them last, since we have to check all used types in this module first
                module_header += self._create_imports_string()
                module_text = module_header + module_text
                module_data.append((Path(out_path / self.module_id), module_name, module_text, True))

        return module_data

    def _create_module_string(self, module: Module) -> tuple[str, str]:
        module_text = ""

        # Create package info
        package_info, _ = _get_shortest_public_reexport(
            reexport_map=self.api.reexport_map,
            name=module.name,
            qname="",
            is_module=True,
        )

        in_reexport_module = bool(package_info)

        if not package_info:
            package_info = ".".join(module.id.split("/"))

        package_info_camel_case = _convert_name_to_convention(package_info, self.naming_convention)
        module_name_info = ""
        if package_info != package_info_camel_case:
            module_name_info = f'@PythonModule("{package_info}")\n'
        module_header = f"{module_name_info}package {package_info_camel_case}\n"

        # Create docstring
        docstring = self._create_sds_docstring_description(module.docstring, "")
        if docstring:
            docstring += "\n"

        # Create global functions and properties
        for function in module.global_functions:
            if function.is_public:
                function_string = self._create_function_string(
                    function=function,
                    is_method=False,
                    in_reexport_module=in_reexport_module,
                )
                if function_string:
                    module_text += f"\n{function_string}\n"

        # Create classes, class attr. & class methods
        for class_ in module.classes:
            if class_.is_public and not class_.inherits_from_exception:
                class_string = self._create_class_string(class_=class_, in_reexport_module=in_reexport_module)
                if class_string:
                    module_text += f"\n{class_string}\n"

        # Create enums & enum instances
        for enum in module.enums:
            module_text += f"\n{self._create_enum_string(enum)}\n"

        # Create imports - We have to create them last, since we have to check all used types in this module first
        module_header += self._create_imports_string()

        return f"{docstring}{module_header}{module_text}", package_info

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

    def _create_class_string(self, class_: Class, class_indentation: str = "", in_reexport_module: bool = False) -> str:
        if not in_reexport_module and self._has_node_shorter_reexport(node=class_):
            return ""

        # Set indentation
        inner_indentations = class_indentation + INDENTATION

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
            class_string = self._create_class_string(
                class_=inner_class,
                class_indentation=inner_indentations,
                in_reexport_module=in_reexport_module,
            )
            class_text += f"\n{class_string}\n"

        # Superclass methods, if the superclass is an internal class
        class_text += superclass_methods_text

        # Methods
        class_text += self._create_class_method_string(class_.methods, inner_indentations)

        # Docstring
        docstring = self._create_sds_docstring(class_.docstring, class_indentation, node=class_)

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
                    self._create_function_string(function=method, indentations=inner_indentations, is_method=True),
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

    def _create_function_string(
        self,
        function: Function,
        indentations: str = "",
        is_method: bool = False,
        in_reexport_module: bool = False,
    ) -> str:
        """Create a function string for Safe-DS stubs."""
        if not is_method and not in_reexport_module and self._has_node_shorter_reexport(node=function):
            return ""

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

            if result_type["kind"] == "NamedType" and result_type["qname"] == "builtins.None":
                return ""

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

        inner_indentations = indentations + INDENTATION
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

                enum_text += f"{INDENTATION}{annotation}{camel_case_name}\n"
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

                    # inner classes that are private should not be used as types, therefore we add a TOD0
                    if name[0] == "_" and type_data["qname"] not in self.module_imports:
                        self._current_todo_msgs.add("internal class as type")

                    return name
        elif kind == "FinalType":
            return self._create_type_string(type_data["type"])
        elif kind == "CallableType":
            params = [
                (
                    f"{_convert_name_to_convention('param_' + str(i + 1), self.naming_convention)}: "
                    f"{self._create_type_string(parameter_type)}"
                )
                for i, parameter_type in enumerate(type_data["parameter_types"])
            ]

            return_type = type_data["return_type"]
            if return_type["kind"] == "TupleType":
                return_types = [
                    (
                        f"{_convert_name_to_convention('result_' + str(i+1), self.naming_convention)}: "
                        f"{self._create_type_string(type_)}"
                    )
                    for i, type_ in enumerate(return_type["types"])
                ]
                return_type_string = f"({', '.join(return_types)})"
            elif return_type["kind"] == "NamedType" and return_type["name"] == "None":
                return f"({', '.join(params)}) -> ()"
            else:
                result_name = _convert_name_to_convention("result_1", self.naming_convention)
                return_type_string = f"{result_name}: {self._create_type_string(return_type)}"

            return f"({', '.join(params)}) -> {return_type_string}"
        elif kind in {"SetType", "ListType", "NamedSequenceType"}:
            types = [self._create_type_string(type_) for type_ in type_data["types"]]

            # Cut out the "Type" in the kind name
            name = kind[0:-4]

            if name == "Set":
                self._current_todo_msgs.add("no set support")
            elif name == "NamedSequence":
                name = type_data["name"]

            if types:
                if len(types) >= 2 and name in {"Set", "List"}:
                    self._current_todo_msgs.add(name)
                return f"{name}<{', '.join(types)}>"
            return f"{name}<Any>"
        elif kind == "UnknownType":  # pragma: no cover
            self._current_todo_msgs.add("unknown")
            return "unknown"
        elif kind == "UnionType":
            # In Mypy LiteralTypes are getting seperated into unions of LiteralTypes,
            # and we have to join them for the stubs.
            literal_data = []
            other_type_data = []
            has_named_type = False
            for type_information in type_data["types"]:
                if type_information["kind"] == "LiteralType":
                    literal_data.append(type_information)
                else:
                    other_type_data.append(type_information)

                if type_information["kind"] in {"NamedType", "TupleType", "ListType", "SetType", "DictType"} and not (
                    type_information["kind"] == "NamedType" and type_information["qname"] == "builtins.None"
                ):
                    has_named_type = True

            if len(literal_data) >= 2:
                all_literals = [literal_type for literal in literal_data for literal_type in literal["literals"]]

                # We overwrite the old types of the union with the joined literal types
                type_data["types"] = other_type_data
                type_data["types"].append(
                    {
                        "kind": "LiteralType",
                        "literals": all_literals,
                    },
                )

            if len(type_data["types"]) == 2 and literal_data:
                # If we have a LiteralType and a None we combine them to a "Literal[..., null]"
                has_none = (type_data["types"][0]["kind"] == "NamedType" and type_data["types"][0]["kind"]) or (
                    type_data["types"][1]["kind"] == "NamedType" and type_data["types"][1]["kind"]
                )
                if has_none:
                    _types = type_data["types"]
                    literal_type_data = _types[0] if _types[0]["kind"] == "LiteralType" else _types[1]

                    literal_type_data["literals"].append(None)
                    return self._create_type_string(literal_type_data)

            # Union items have to be unique, therefore we use sets. But the types set has to be a sorted list, since
            # otherwise the snapshot tests would fail b/c element order in sets is non-deterministic.
            types = list({self._create_type_string(type_) for type_ in type_data["types"]})
            types.sort()

            if types:
                if len(types) == 2 and none_type_name in types and has_named_type:
                    # if None is at least one of the two possible types, we can remove the None and just return the
                    # other type with a question mark. But only named types (class/enum/enum variant) support the ?
                    # syntax for nullability in Safe-DS, therefore we handle callable types here.
                    if types[0] == none_type_name:
                        return f"{types[1]}?"
                    return f"{types[0]}?"

                # If the union contains only one type, return the type instead of creating a union
                elif len(types) == 1:
                    return types[0]

                if none_type_name in types and types[-1] != none_type_name:
                    # Make sure Nones are always at the end of Unions
                    types.pop(types.index(none_type_name))
                    types.append(none_type_name)

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
                elif isinstance(literal_type, NoneType):
                    types.append("null")
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

    def _create_sds_docstring_description(self, description: str, indentations: str) -> str:
        if not description:
            return ""

        full_docstring = self._create_docstring_description_part(description, indentations)
        return f"{indentations}/**\n{indentations} * {full_docstring}{indentations} */\n"

    def _create_sds_docstring(
        self,
        docstring: ClassDocstring | FunctionDocstring | AttributeDocstring,
        indentations: str,
        node: Class | Function | None = None,
    ) -> str:
        full_docstring = ""

        # Description
        if docstring.description:
            full_docstring = f"{indentations} * "
            full_docstring += self._create_docstring_description_part(docstring.description, indentations)

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

                    param_desc = self._create_docstring_description_part(param_desc, indentations)

                    parameter_name = _convert_name_to_convention(parameter.name, self.naming_convention)
                    parameter_docstrings.append(f"{indentations} * @param {parameter_name} {param_desc}")

                full_parameter_docstring = "".join(parameter_docstrings)

                if full_parameter_docstring and full_docstring:
                    full_parameter_docstring = f"{indentations} *\n{full_parameter_docstring}"
        full_docstring += full_parameter_docstring

        # Results
        full_result_docstring = ""
        if isinstance(node, Function):
            name_generator = result_name_generator()

            for result_docstring in node.result_docstrings:
                result_desc = result_docstring.description
                if result_desc:
                    result_desc = f"\n{indentations} * ".join(result_desc.split("\n"))

                    result_name = result_docstring.name if result_docstring.name else next(name_generator)
                    result_name = _convert_name_to_convention(result_name, self.naming_convention)

                    full_result_docstring += f"{indentations} * @result {result_name} {result_desc}\n"

            if full_result_docstring and full_docstring:
                full_result_docstring = f"{indentations} *\n{full_result_docstring}"
        full_docstring += full_result_docstring

        # Example
        example = ""
        if not isinstance(docstring, AttributeDocstring) and docstring.example:
            example = f"{indentations} * @example\n{indentations} * pipeline example {{\n"
            for example_part in docstring.example.split("\n"):
                if example_part.startswith(">>>"):
                    example += f"{indentations} *     {example_part.replace('>>>', '//')}\n"
                elif example_part.startswith("..."):
                    example += f"{indentations} *     {example_part.replace('...', '//')}\n"
            example += f"{indentations} * }}\n"
        if full_docstring and example:
            full_docstring += f"{indentations} *\n"
        full_docstring += example

        # Open and close the docstring
        if full_docstring:
            full_docstring = f"{indentations}/**\n{full_docstring}{indentations} */\n"

        return full_docstring

    # ############################### Utilities ############################### #

    def _has_node_shorter_reexport(self, node: Class | Function) -> bool:
        # Check if this node is beeing reexported from a shorter path. If it is, we create it there, not in this module
        shortest_reexport_module_id = self.module_id
        shortest_reexport_module: Module | None = None
        for reexport_module in node.reexported_by:
            if len(reexport_module.id.split("/")) < len(shortest_reexport_module_id.split("/")):
                shortest_reexport_module_id = reexport_module.id
                shortest_reexport_module = reexport_module

        if shortest_reexport_module_id != self.module_id and shortest_reexport_module is not None:
            # Get alias
            alias = None
            for qualified_import in shortest_reexport_module.qualified_imports:
                if qualified_import.qualified_name.endswith(node.name):
                    alias = qualified_import.alias

            if alias:
                node.name = alias

            self.reexport_modules[shortest_reexport_module_id].append(node)
            return True
        return False

    def _is_path_connected_to_class(self, path: str, class_path: str) -> bool:
        if class_path.endswith(path):
            return True

        name = path.split("/")[-1]
        class_name = class_path.split("/")[-1]
        for reexport in self.api.reexport_map:
            if reexport.endswith(name):
                for module in self.api.reexport_map[reexport]:
                    # Added "no cover" since I can't recreate this in the tests
                    if (
                        path.startswith(module.id)
                        and class_path.startswith(module.id)
                        and path.lstrip(module.id).lstrip("/") == name == class_name
                    ):  # pragma: no cover
                        return True

        return False

    def _add_to_imports(self, import_qname: str) -> None:
        """Check if the qname of a type is defined in the current module, if not, create an import for it.

        Paramters
        ---------
        qname:
            The qualified name of a module/class/etc.
        """
        if import_qname == "":  # pragma: no cover
            raise ValueError("Type has no import source.")

        qname_parts = import_qname.split(".")
        if (qname_parts[0] == "builtins" and len(qname_parts) == 2) or import_qname == "typing.Any":
            return

        module_id = self.module_id.replace("/", ".")
        if module_id not in import_qname:
            # We need the full path for an import from the same package, but we sometimes don't get enough information,
            # therefore we have to search for the class and get its id
            import_qname_path = import_qname.replace(".", "/")
            in_package = False
            qname = ""
            for class_id in self.api.classes:
                if self._is_path_connected_to_class(import_qname_path, class_id):
                    qname = class_id.replace("/", ".")

                    name = qname.split(".")[-1]
                    shortest_qname, _ = _get_shortest_public_reexport(
                        reexport_map=self.api.reexport_map,
                        name=name,
                        qname=qname,
                        is_module=False,
                    )

                    if shortest_qname:
                        qname = f"{shortest_qname}.{name}"

                    in_package = True
                    break

            qname = qname or import_qname

            if not in_package:
                self.classes_outside_package.add(qname)

            if qname.replace(".", "/") != self.module_id:
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
                "unknown": "Unknown type - Type could not be parsed.",
            }[msg]
            for msg in self._current_todo_msgs
        ]
        todo_msgs.sort()

        # Empty the message list
        self._current_todo_msgs = set()

        return indentations + f"\n{indentations}".join(todo_msgs) + "\n"

    def _get_class_in_module(self, class_name: str) -> Class:
        if f"{self.module_id}/{class_name}" in self.api.classes:
            return self.api.classes[f"{self.module_id}/{class_name}"]

        # If the class is a nested class
        for class_ in self.api.classes:
            if class_.startswith(self.module_id) and class_.endswith(class_name):
                return self.api.classes[class_]

        raise LookupError(f"Expected finding class '{class_name}' in module '{self.module_id}'.")  # pragma: no cover

    @staticmethod
    def _create_docstring_description_part(description: str, indentations: str) -> str:
        description = description.rstrip("\n")
        description = description.lstrip("\n")
        splitted_docstring = description.split("\n")

        full_docstring = ""
        for i, docstring_part in enumerate(splitted_docstring):
            if i == 0:
                full_docstring = f"{docstring_part}"
            elif docstring_part:
                full_docstring += f"\n{indentations} * {docstring_part}"
            else:
                full_docstring += f"\n{indentations} *"

        return full_docstring + "\n"
