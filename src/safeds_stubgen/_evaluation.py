from dataclasses import dataclass
import os
from time import time
from abc import ABC, abstractmethod

from safeds_stubgen.api_analyzer._api import Parameter
from safeds_stubgen.api_analyzer._types import AbstractType, BoundaryType, CallableType, DictType, EnumType, FinalType, ListType, LiteralType, NamedSequenceType, NamedType, SetType, TupleType, TypeVarType, UnionType, UnknownType
from safeds_stubgen.api_analyzer.purity_analysis.model._module_data import NodeID
from safeds_stubgen.api_analyzer.purity_analysis.model._purity import APIPurity, Impure, Pure

import csv
from pathlib import Path
from datetime import datetime

import mypy.types as mp_types
import mypy.nodes as mp_nodes

class Evaluation(ABC):
	def start_timing(self):
		self._start_time = time()
	
	def end_timing(self):
		self._end_time = time()
		self._runtime = self._end_time - self._start_time

	@abstractmethod
	def get_results(self):
		pass


class PurityEvaluation(Evaluation):
	def __init__(self, package_name: str, old_purity_analysis: bool, out_dir_path: Path):
		self._start_time = 0
		self._end_time = 0
		self._runtime = 0
		self.old = old_purity_analysis
		self._out_dir_path = out_dir_path
		self._package_name = package_name

	def get_results(self, ground_truth: dict[NodeID, dict[NodeID, str]] | None, purity_results: APIPurity):
		amount_of_classified_pure_functions = 0
		amount_of_classified_impure_functions = 0
		true_positives = 0
		true_negatives = 0
		false_positives = 0
		false_negatives = 0
		precision = 0
		recall = 0
		accuracy = 0
		balanced_accuracy = 0

		if ground_truth is not None:
			for module_id, module_data in ground_truth.items():
				for function_id, purity in module_data.items():
					purity_result = purity_results.purity_results[module_id][function_id]
					if isinstance(purity_result, Pure) and purity == "pure":
						true_positives += 1
					if isinstance(purity_result, Impure) and purity == "impure":
						true_negatives += 1
					if isinstance(purity_result, Pure) and purity == "impure":
						false_positives += 1
					if isinstance(purity_result, Impure) and purity == "pure":
						false_negatives += 1
			recall = true_positives / (true_positives + false_negatives)
			precision = true_positives / (true_positives + false_positives)
			accuracy = (true_positives + true_negatives) / (true_positives + true_negatives + false_negatives + false_positives)
			balanced_accuracy = ((true_positives / (true_positives + false_negatives)) + (true_negatives / (true_negatives + false_positives))) / 2

		for purity_result_of_module in purity_results.purity_results.values():
			for purity_result in purity_result_of_module.values():
				if isinstance(purity_result, Pure):
					amount_of_classified_pure_functions += 1
				elif isinstance(purity_result, Impure):
					amount_of_classified_impure_functions += 1

		filename = "purity_evaluation.csv"
		fieldnames = [
			"Type-Aware?",
			"Library", 
			"Runtime [seconds]", 
			"Classified as Pure", 
			"Classified as Impure", 
			"Amount of functions",
			"True Positive",
			"True Negative",
			"False Positive", 
			"False Negative",
			"Recall",
			"Precision",
			"Accuracy",
			"Balanced Accuracy",
			"Date"
		]
		data = [
			{
				"Type-Aware?": "Yes" if not self.old else "No",
				"Library": self._package_name, 
				"Runtime [seconds]": self._runtime, 
				"Classified as Pure": amount_of_classified_pure_functions,
				"Classified as Impure": amount_of_classified_impure_functions,
				"Amount of functions": amount_of_classified_impure_functions + amount_of_classified_pure_functions,
				"True Positive": true_positives,
				"True Negative": true_negatives,
				"False Positive": false_positives,
				"False Negative": false_negatives,
				"Recall": recall,
				"Precision": precision,
				"Accuracy": accuracy,
				"Balanced Accuracy": balanced_accuracy,
				"Date": str(datetime.now())
			},
		]

		file_exists = os.path.isfile(filename)

		# Open the file in write mode
		with open(filename, "a", newline="") as csvfile:
			# Define fieldnames (keys of the dictionary)

			# Create a DictWriter object
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			# Write the header
			if not file_exists:
				writer.writeheader()

			# Write the data rows
			writer.writerows(data)

class ApiEvaluation(Evaluation):
	# def __new__(cls):
	# 	if not hasattr(cls, "instance"):
	# 		cls.instance = super(EvaluationDataCollector, cls).__new__(cls)
	# 	return cls.instance
	
	def __init__(self, package_name: str):
		self._start_time = 0
		self._end_time = 0
		self._runtime = 0
		self.expressions: list[EvaluationExpression] = []
		self._package_name = package_name
		self.expression_ids = {}

	def get_id_from_expr(self, mypy_expr: mp_nodes.Expression, expr_kind: str, module_id: str):
		id_str = f"{module_id}.{mypy_expr.line}.{mypy_expr.column}.{expr_kind}"
		id_existed = self.expression_ids.get(id_str, -1) != -1
		if id_existed:
			return -1
			raise ValueError(f"ID: '{id_str}' Existed")
		else:
			self.expression_ids[id_str] = True
			return id_str

	def extract_type_name_from_abstract_type(self, abstract_type: AbstractType) -> str:
		if isinstance(abstract_type, UnknownType):
			return "UnknownType"
		elif isinstance(abstract_type, NamedType):
			return abstract_type.name
		elif isinstance(abstract_type, NamedSequenceType):
			return abstract_type.name
		elif isinstance(abstract_type, EnumType):
			return list(abstract_type.values)[0]  # TODO pm 
		elif isinstance(abstract_type, BoundaryType):
			return abstract_type.base_type
		elif isinstance(abstract_type, UnionType):
			types = [self.extract_type_name_from_abstract_type(type) for type in abstract_type.types]
			types_str = ", ".join(types)
			return f"UnionType[{types_str}]"
		elif isinstance(abstract_type, ListType):
			types = [self.extract_type_name_from_abstract_type(type) for type in abstract_type.types]
			types_str = ", ".join(types)
			return f"List[{types_str}]"
		elif isinstance(abstract_type, DictType):
			return f"Dict[{self.extract_type_name_from_abstract_type(abstract_type.key_type)}, {self.extract_type_name_from_abstract_type(abstract_type.value_type)}]"
		elif isinstance(abstract_type, CallableType):
			parameter_types = [self.extract_type_name_from_abstract_type(type) for type in abstract_type.parameter_types]
			parameter_types_str = ", ".join(parameter_types)
			return_type = self.extract_type_name_from_abstract_type(abstract_type.return_type)
			return f"Callable[[{parameter_types_str}], {return_type}]"
		elif isinstance(abstract_type, SetType):
			types = [self.extract_type_name_from_abstract_type(type) for type in abstract_type.types]
			return f"List[{types[0]}]"
		elif isinstance(abstract_type, LiteralType):
			literals = ", ".join(map(lambda x: str(x), abstract_type.literals))
			return f"Literal[{literals}]"
		elif isinstance(abstract_type, FinalType):
			return self.extract_type_name_from_abstract_type(abstract_type.type_)
		elif isinstance(abstract_type, TupleType):
			types = [self.extract_type_name_from_abstract_type(type) for type in abstract_type.types]
			types_str = ", ".join(types)
			return f"Tuple[{types_str}]"
		elif isinstance(abstract_type, TypeVarType):
			return abstract_type.name
		else:
			return ""
		
	def extract_type_name_from_mypy_type(self, mypy_type: mp_types.Type | None) -> str:  # TODO pm extract from Expression not from Type !!!!!!
		if mypy_type is None:
			return ""
		if isinstance(mypy_type, mp_types.TupleType):
			types = [self.extract_type_name_from_mypy_type(type) for type in mypy_type.items]
			types_str = ", ".join(types)
			return f"Tuple[{types_str}]"
		elif hasattr(mypy_type, "type"):
			return mypy_type.type.name
		elif hasattr(mypy_type, "args"):
			if len(mypy_type.args) == 2: # type: ignore
				return f"Dict[{self.extract_type_name_from_mypy_type(mypy_type.args[0])}, {self.extract_type_name_from_mypy_type(mypy_type.args[1])}]"  # type: ignore # this is for dict
			else:
				return f"List[{self.extract_type_name_from_mypy_type(mypy_type.args[0])}]"  # type: ignore # this is for list
		return ""
		
	def get_fullname(self, mypy_expr: mp_nodes.Expression) -> str:
		"""
			Assumes that for each expression, where a NameExpr can be found, 
			the type can be accessed if the parameter type is available
			Example:
				instance.same_name() has three expressions
				1. call expression: instance.same_name()
				2. member expression: instance.same_name
				3. name expression: instance
		"""
		if isinstance(mypy_expr, mp_nodes.NameExpr):
			if mypy_expr.node is not None:
				return mypy_expr.node.fullname
			return ""
		fullname = ""
		# fullnames = []
		for member_name in dir(mypy_expr):
			if not member_name.startswith("__"):
				member = getattr(mypy_expr, member_name)
				if isinstance(member, mp_nodes.Expression):
					fullname = self.get_fullname(member)	
				# elif isinstance(member, list) and len(member) > 0 and isinstance(member[0], mp_nodes.Expression):
				# 	for expr in member:
				# 		fullnames.append(self.get_fullname(expr))
		# TODO pm what about multiple fullnames???
		return fullname

	def evaluate_expression(self, mypy_expr: mp_nodes.Expression, parameters: dict[str, Parameter], module_id: str):
		type_from_annotation = ""
		type_from_comment = ""
		parameter = parameters.get(self.get_fullname(mypy_expr), None)
		if parameter is not None and parameter.type is not None:
			type_from_annotation = self.extract_type_name_from_abstract_type(parameter.type)
		if parameter is not None and parameter.docstring.type is not None:
			type_from_comment = self.extract_type_name_from_abstract_type(parameter.docstring.type)
		self.evaluate_expression_helper(mypy_expr, type_from_annotation, type_from_comment, module_id)

	def evaluate_expression_helper(self, mypy_expr: mp_nodes.Expression, type_from_annotation: str, type_from_comment: str, module_id: str):
		# TODO pm get type and evaluate correctly
		id = ""
		type = ""
		mypy_inferred_type = ""

		if isinstance(mypy_expr, mp_nodes.OpExpr):
			type = "mp_nodes.OpExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.IntExpr):
			type = "mp_nodes.IntExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "int"
		# elif isinstance(mypy_expr, mp_nodes.RefExpr):  # this is the base class of MemberExpr and NameExpr so we dont need it
		# 	type = "mp_nodes.RefExpr"
		# 	id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.SetExpr):
			type = "mp_nodes.SetExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "set"
		elif isinstance(mypy_expr, mp_nodes.StrExpr):
			type = "mp_nodes.StrExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "str"
		elif isinstance(mypy_expr, mp_nodes.CallExpr):
			type = "mp_nodes.CallExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "Call"
		elif isinstance(mypy_expr, mp_nodes.CastExpr):
			type = "mp_nodes.CastExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.DictExpr):
			type = "mp_nodes.DictExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "Dict"
		elif isinstance(mypy_expr, mp_nodes.FakeExpression):
			type = "mp_nodes.FakeExpressio"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.ListExpr):
			type = "mp_nodes.ListExp"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "List"
		elif isinstance(mypy_expr, mp_nodes.NameExpr):
			type = "mp_nodes.NameExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			if isinstance(mypy_expr.node, mp_nodes.Var):
				mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.node.type)
			if isinstance(mypy_expr.node, mp_nodes.TypeInfo):
				mypy_inferred_type = mypy_expr.node.name
		elif isinstance(mypy_expr, mp_nodes.StarExpr):
			type = "mp_nodes.StarExp"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.AwaitExpr):
			type = "mp_nodes.AwaitExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.BytesExpr):
			type = "mp_nodes.BytesExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.FloatExpr):
			type = "mp_nodes.FloatExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "float"
		elif isinstance(mypy_expr, mp_nodes.IndexExpr):
			type = "mp_nodes.IndexExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.SliceExpr):
			type = "mp_nodes.SliceExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.SuperExpr):
			type = "mp_nodes.SuperExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.TupleExpr):
			type = "mp_nodes.TupleExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "tuple"
		elif isinstance(mypy_expr, mp_nodes.UnaryExpr):
			type = "mp_nodes.UnaryExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.LambdaExpr):
			type = "mp_nodes.LambdaExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.MemberExpr):
			type = "mp_nodes.MemberExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			if isinstance(mypy_expr.node, mp_nodes.Var):
				mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.node.type)
			if isinstance(mypy_expr.expr, mp_nodes.NameExpr):  # TODO pm refactor this recursively
				if isinstance(mypy_expr.expr.node, mp_nodes.Var):
					mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.expr.node.type)
				if isinstance(mypy_expr.expr.node, mp_nodes.TypeInfo):
					mypy_inferred_type = mypy_expr.expr.node.name
		elif isinstance(mypy_expr, mp_nodes.RevealExpr):
			type = "mp_nodes.RevealExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.ComplexExpr):
			type = "mp_nodes.ComplexExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "complex"
		elif isinstance(mypy_expr, mp_nodes.NewTypeExpr):
			type = "mp_nodes.NewTypeExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.old_type)
		elif isinstance(mypy_expr, mp_nodes.TypeVarExpr):
			type = "mp_nodes.TypeVarExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.default)
		elif isinstance(mypy_expr, mp_nodes.PromoteExpr):
			type = "mp_nodes.PromoteExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.type)
		elif isinstance(mypy_expr, mp_nodes.EllipsisExpr):
			type = "mp_nodes.EllipsisExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.EnumCallExpr):
			type = "mp_nodes.EnumCallExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "EnumCallExpr"
		elif isinstance(mypy_expr, mp_nodes.GeneratorExpr):
			type = "mp_nodes.GeneratorExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.YieldFromExpr):
			type = "mp_nodes.YieldFromExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.AssertTypeExpr):
			type = "mp_nodes.AssertTypeExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.type)
		elif isinstance(mypy_expr, mp_nodes.AssignmentExpr):
			type = "mp_nodes.AssignmentExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.ComparisonExpr):
			type = "mp_nodes.ComparisonExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = "bool"
		elif isinstance(mypy_expr, mp_nodes.NamedTupleExpr):
			type = "mp_nodes.NamedTupleExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.info.tuple_type)
		elif isinstance(mypy_expr, mp_nodes.ConditionalExpr):
			type = "mp_nodes.ConditionalExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
		elif isinstance(mypy_expr, mp_nodes.TypeVarLikeExpr):
			type = "mp_nodes.TypeVarLikeExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.upper_bound)
		elif isinstance(mypy_expr, mp_nodes.TypeVarTupleExpr):
			type = "mp_nodes.TypeVarTupleExpr"
			id = self.get_id_from_expr(mypy_expr, type, module_id)
			mypy_inferred_type = self.extract_type_name_from_mypy_type(mypy_expr.upper_bound)
		
		if (id == -1):
			return
		conflicted_types = False

		# there are three type sources: 1. annotation 2. docstring and 3. inferred
		# so we need to check each combination for conflicting types
		if (type_from_comment != "" and type_from_annotation != "" and mypy_inferred_type != ""):
			conflicted_types = not (type_from_annotation == type_from_comment and type_from_comment == mypy_inferred_type)

		elif (type_from_comment == "" and type_from_annotation != "" and mypy_inferred_type != ""):
			conflicted_types = type_from_annotation != mypy_inferred_type

		elif (type_from_comment != "" and type_from_annotation == "" and mypy_inferred_type != ""):
			conflicted_types = mypy_inferred_type != type_from_comment

		elif (type_from_comment != "" and type_from_annotation != "" and mypy_inferred_type == ""):
			conflicted_types = type_from_annotation != type_from_comment

		if conflicted_types:
			pass  # TODO pm store conflicts so that a dev can fix this conflicting type
		if (type_from_comment == "" and type_from_annotation == "" and mypy_inferred_type == ""):
			pass  # TODO pm store missing types 
		new_expression = EvaluationExpression(id, type, type_from_annotation, type_from_comment, mypy_inferred_type, conflicted_types)
		self.expressions.append(new_expression)

	def get_results(self):
		amount_of_expressions = len(self.expressions)
		amount_of_conflicted_types = 0
		amount_of_only_type_hint = 0
		amount_of_only_comment_type = 0
		amount_of_both_types = 0
		amount_of_no_types = 0
		amount_of_inferred_types = 0
		test_dict: dict[str, int] = {}
		for expr in self.expressions:
			has_expression = test_dict.get(expr.kind_of_expression, -1) != -1
			if has_expression:
				test_dict[expr.kind_of_expression] += 1
			else:
				test_dict[expr.kind_of_expression] = 1

			if expr.hasConflictedTypes:
				amount_of_conflicted_types += 1
			if expr.type_from_comment != "" and expr.type_from_type_hint != "":
				amount_of_both_types += 1
			elif expr.type_from_comment != "":
				amount_of_only_comment_type += 1
			elif expr.type_from_type_hint != "":
				amount_of_only_type_hint += 1
			elif expr.inferred_type != "":
				amount_of_inferred_types += 1
			else:
				amount_of_no_types += 1

		# TODO pm compute metrics and how can i be sure that all expressions are found

		filename = "api_evaluation.csv"
		fieldnames = [
			"Library", 
			"Runtime [seconds]",
			"Expressions",
			"Conflicted Types",
			"Expressions without type info",
			"Expressions with both type hint and docstring",
			"Expressions with only type hint",
			"Expressions with only comment type info",
			"Expressions with inferred type info",
		]
		fieldnames.extend(test_dict.keys())
		fieldnames.append("Date")
		entry: dict[str, str] = {
			"Library": self._package_name, 
			"Runtime [seconds]": str(self._runtime),
			"Expressions": str(amount_of_expressions),
			"Conflicted Types": str(amount_of_conflicted_types),
			"Expressions without type info": str(amount_of_no_types),
			"Expressions with both type hint and docstring": str(amount_of_both_types),
			"Expressions with only type hint": str(amount_of_only_type_hint),
			"Expressions with only comment type info": str(amount_of_only_comment_type),
			"Expressions with inferred type info": str(amount_of_inferred_types),
		}

		for key, value in test_dict.items():
			entry[key] = str(value)

		entry["Date"] = str(datetime.now())
		data = [entry]

		file_exists = os.path.isfile(filename)

		# Open the file in write mode
		with open(filename, "a", newline="") as csvfile:
			# Define fieldnames (keys of the dictionary)

			# Create a DictWriter object
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			# Write the header
			if not file_exists:
				writer.writeheader()

			# Write the data rows
			writer.writerows(data)


@dataclass
class EvaluationExpression:
	id: str
	kind_of_expression: str
	type_from_type_hint: str
	type_from_comment: str
	inferred_type: str
	hasConflictedTypes: bool