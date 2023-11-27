class InferMyTypes:
    infer_attr = 1

    def __init__(self, init_param=1):
        self.init_infer = 3

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

        with open("no path", "r") as _:
            if infer_param_2:
                return "Some String"

        for _ in (1, 2):
            if infer_param_2:
                return ModuleClass

        return int
