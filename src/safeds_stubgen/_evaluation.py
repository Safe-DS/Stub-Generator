from dataclasses import dataclass
import os
from time import time
from abc import ABC, abstractmethod

from safeds_stubgen.api_analyzer.purity_analysis.model._module_data import NodeID
from safeds_stubgen.api_analyzer.purity_analysis.model._purity import APIPurity, Impure, Pure

import csv
from pathlib import Path
from datetime import datetime

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

	def evaluate_expression(self, mypy_expr: mp_nodes.Expression, type_from_annotation: str, type_from_comment: str):
		# TODO pm get type and evaluate correctly
		id = ""
		type = ""

		if isinstance(mypy_expr, mp_nodes.OpExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.OpExpr"
		elif isinstance(mypy_expr, mp_nodes.IntExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.IntExpr"
		elif isinstance(mypy_expr, mp_nodes.RefExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.RefExpr"
		elif isinstance(mypy_expr, mp_nodes.SetExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.SetExpr"
		elif isinstance(mypy_expr, mp_nodes.StrExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.StrExpr"
		elif isinstance(mypy_expr, mp_nodes.CallExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.CallExpr"
		elif isinstance(mypy_expr, mp_nodes.CastExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.CastExpr"
		elif isinstance(mypy_expr, mp_nodes.DictExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.DictExpr"
		elif isinstance(mypy_expr, mp_nodes.FakeExpression):
			id = str(mypy_expr.line)
			type = "mp_nodes.FakeExpressio"
		elif isinstance(mypy_expr, mp_nodes.ListExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.ListExp"
		elif isinstance(mypy_expr, mp_nodes.NameExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.NameExpr"
		elif isinstance(mypy_expr, mp_nodes.StarExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.StarExp"
		elif isinstance(mypy_expr, mp_nodes.AwaitExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.AwaitExpr"
		elif isinstance(mypy_expr, mp_nodes.BytesExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.BytesExpr"
		elif isinstance(mypy_expr, mp_nodes.FloatExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.FloatExpr"
		elif isinstance(mypy_expr, mp_nodes.IndexExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.IndexExpr"
		elif isinstance(mypy_expr, mp_nodes.SliceExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.SliceExpr"
		elif isinstance(mypy_expr, mp_nodes.SuperExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.SuperExpr"
		elif isinstance(mypy_expr, mp_nodes.TupleExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.TupleExpr"
		elif isinstance(mypy_expr, mp_nodes.UnaryExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.UnaryExpr"
		elif isinstance(mypy_expr, mp_nodes.LambdaExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.LambdaExpr"
		elif isinstance(mypy_expr, mp_nodes.MemberExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.MemberExpr"
		elif isinstance(mypy_expr, mp_nodes.RevealExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.RevealExpr"
		elif isinstance(mypy_expr, mp_nodes.ComplexExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.ComplexExpr"
		elif isinstance(mypy_expr, mp_nodes.NewTypeExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.NewTypeExpr"
		elif isinstance(mypy_expr, mp_nodes.TypeVarExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.TypeVarExpr"
		elif isinstance(mypy_expr, mp_nodes.PromoteExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.PromoteExpr"
		elif isinstance(mypy_expr, mp_nodes.EllipsisExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.EllipsisExpr"
		elif isinstance(mypy_expr, mp_nodes.EnumCallExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.EnumCallExpr"
		elif isinstance(mypy_expr, mp_nodes.GeneratorExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.GeneratorExpr"
		elif isinstance(mypy_expr, mp_nodes.YieldFromExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.YieldFromExpr"
		elif isinstance(mypy_expr, mp_nodes.AssertTypeExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.AssertTypeExpr"
		elif isinstance(mypy_expr, mp_nodes.AssignmentExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.AssignmentExpr"
		elif isinstance(mypy_expr, mp_nodes.ComparisonExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.ComparisonExpr"
		elif isinstance(mypy_expr, mp_nodes.NamedTupleExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.NamedTupleExpr"
		elif isinstance(mypy_expr, mp_nodes.ConditionalExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.ConditionalExpr"
		elif isinstance(mypy_expr, mp_nodes.TypeVarLikeExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.TypeVarLikeExpr"
		elif isinstance(mypy_expr, mp_nodes.TypeVarTupleExpr):
			id = str(mypy_expr.line)
			type = "mp_nodes.TypeVarTupleExpr"
		
		new_expression = EvaluationExpression(id, type, type_from_annotation, type_from_comment, type_from_comment != type_from_annotation)
		self.expressions.append(new_expression)

	def get_results(self) -> str:
		amount_of_expressions = len(self.expressions)
		amount_of_conflicted_types = 0
		amount_of_only_type_hint = 0
		amount_of_only_comment_type = 0
		amount_of_both_types = 0
		amount_of_no_types = 0
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
			else:
				amount_of_no_types += 1

		# TODO pm compute metrics and how can i be sure that all expressions are found

		filename = "api_evaluation.csv"
		fieldnames = [
			"Library", 
			"Runtime [seconds]",
			"Date",
			"Amount of Expressions",
		]
		fieldnames.extend(test_dict.keys())
		entry: dict[str, str] = {
			"Library": self._package_name, 
			"Runtime [seconds]": str(self._runtime),
			"Date": str(datetime.now()),
			"Amount of Expressions": str(len(self.expressions))
		}

		for key, value in test_dict.items():
			entry[key] = str(value)

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

		result_str = f"Runtime: {self._runtime}\nAmount of expressions: {amount_of_expressions}\n"
		return result_str


@dataclass
class EvaluationExpression:
	id: str
	kind_of_expression: str
	type_from_type_hint: str
	type_from_comment: str
	hasConflictedTypes: bool