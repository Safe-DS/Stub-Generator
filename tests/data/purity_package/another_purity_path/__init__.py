def test_init_py_pure():
  	return 10

global_var = 0
def test_init_py_impure():
  	return global_var

class ClassWithPureStaticMethods:
	@staticmethod
	def test():
		return 10
	
class ClassWithImpureStaticMethods:
	@staticmethod
	def test():
		return global_var