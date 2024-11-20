from dataclasses import dataclass
from time import time

class EvaluationDataCollector(object):
	def __new__(cls):
		if not hasattr(cls, "instance"):
			cls.instance = super(EvaluationDataCollector, cls).__new__(cls)
		return cls.instance
	
	def __init__(self):
		self.start_time = 0
		self.end_time = 0
		self.runtime = 0
		self.expressions: list[EvaluationExpression] = []

	def start_timing(self):
		self.start_time = time()
	
	def end_timing(self):
		self.end_time = time()
		self.runtime = self.end_time - self.start_time

	def evaluate_expression(self, expr):
		# TODO pm get type and evaluate correctly
		new_expression = EvaluationExpression("testId", "IntExpr", "str", "str", False)
		self.expressions.append(new_expression)

	def get_results(self) -> str:
		amount_of_expressions = len(self.expressions)
		amount_of_conflicted_types = 0
		amount_of_only_type_hint = 0
		amount_of_only_comment_type = 0
		amount_of_both_types = 0
		amount_of_no_types = 0
		test_dict = {}
		for expr in self.expressions:
			test_dict[expr.kind_of_expression] += 1
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

		result_str = f"Runtime: {self.runtime}\nAmount of expressions: {amount_of_expressions}\n"
		return result_str


@dataclass
class EvaluationExpression:
	id: str
	kind_of_expression: str
	type_from_type_hint: str
	type_from_comment: str
	hasConflictedTypes: bool