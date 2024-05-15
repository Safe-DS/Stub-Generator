class InferMe:
    ...


class InferMe2:
    ...


class InferMe3:
    ...


class InferMyTypes:
    infer_int = 1
    infer_float = 1.2
    infer_bool = False
    infer_str = "String"
    infer_none = None
    infer_call_expr = InferMe()
    uninferable_callable = InferMe

    def __init__(self, init_param=1):
        self.init_infer = 3

    @staticmethod
    def infer_param_types(
        integer=3,
        boolean=True,
        float_=1.2,
        none=None,
        string="Some String",
        callexpr=InferMe(),
        int_list=[1, 2, 3],
        dictionary={"key": 1, "key2": 1.2},
        string_set={"a", "b"},
        tuple_=(1, "2", True)
    ): ...

    @staticmethod
    def infer_function(infer_param=1, infer_param_2: int = "Something"):
        if infer_param_2:
            return False, 12
        elif infer_param:
            if infer_param:
                return 12
            else:
                return bool

        match infer_param:
            case 1:
                if 4:
                    return InferMyTypes
            case _:
                return None

        while infer_param_2:
            if infer_param_2:
                return 1.23, 1.22, 1.21
            else:
                infer_param_2 = 0

        with open("no path", "r", encoding="utf-8") as _:
            if infer_param_2:
                return "Some String"

        for _ in (1, 2):
            if infer_param_2:
                return InferMe

        try:
            if infer_param_2:
                return InferMe2
        except RuntimeError:
            if infer_param_2:
                return InferMe3

        return int

    @staticmethod
    def infer_function_2(i=2):
        """Test for inferring results with just one possible result, and not a tuple of results."""
        if i:
            return "a"
        else:
            return False

    def infer_call_result_1(self):
        return self.infer_function_2()

    def _(self) -> str: ...

    def infer_call_result_2(self):
        return self._()
