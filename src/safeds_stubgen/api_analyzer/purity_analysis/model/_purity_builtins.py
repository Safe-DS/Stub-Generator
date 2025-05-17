import astroid

from safeds_stubgen.api_analyzer.purity_analysis.model import (
    ClassScope,
    ClassVariable,
    FileRead,
    FileWrite,
    GlobalVariable,
    Impure,
    NodeID,
    NonLocalVariableRead,
    NonLocalVariableWrite,
    OpenMode,
    Pure,
    PurityResult,
    StringLiteral,
    UnknownSymbol,
)

BUILTIN_FUNCTIONS: dict[str, PurityResult] = {  # all errors and warnings are pure
    "ArithmeticError": Pure(),
    "AssertionError": Pure(),
    "AttributeError": Pure(),
    "BaseException": Impure(set()),
    "BaseExceptionGroup": Impure(set()),
    "BlockingIOError": Pure(),
    "BrokenPipeError": Pure(),
    "BufferError": Pure(),
    "BytesWarning": Pure(),
    "ChildProcessError": Pure(),
    "ConnectionAbortedError": Pure(),
    "ConnectionError": Pure(),
    "ConnectionRefusedError": Pure(),
    "ConnectionResetError": Pure(),
    "DeprecationWarning": Pure(),
    "EOFError": Pure(),
    "Ellipsis": Impure(set()),
    "EncodingWarning": Pure(),
    "EnvironmentError": Pure(),
    "Exception": Impure(set()),
    "ExceptionGroup": Impure(set()),
    "False": Pure(),
    "FileExistsError": Pure(),
    "FileNotFoundError": Pure(),
    "FloatingPointError": Pure(),
    "FutureWarning": Pure(),
    "GeneratorExit": Impure(set()),
    "IOError": Pure(),
    "ImportError": Pure(),
    "ImportWarning": Pure(),
    "IndentationError": Pure(),
    "IndexError": Pure(),
    "InterruptedError": Pure(),
    "IsADirectoryError": Pure(),
    "KeyError": Pure(),
    "KeyboardInterrupt": Impure(set()),
    "LookupError": Pure(),
    "MemoryError": Pure(),
    "ModuleNotFoundError": Pure(),
    "NameError": Pure(),
    "None": Impure(set()),
    "NotADirectoryError": Pure(),
    "NotImplemented": Impure(set()),
    "NotImplementedError": Pure(),
    "OSError": Pure(),
    "OverflowError": Pure(),
    "PendingDeprecationWarning": Pure(),
    "PermissionError": Pure(),
    "ProcessLookupError": Pure(),
    "RecursionError": Pure(),
    "ReferenceError": Pure(),
    "ResourceWarning": Pure(),
    "RuntimeError": Pure(),
    "RuntimeWarning": Pure(),
    "StopAsyncIteration": Impure(set()),
    "StopIteration": Impure(set()),
    "SyntaxError": Pure(),
    "SyntaxWarning": Pure(),
    "SystemError": Pure(),
    "SystemExit": Impure(set()),
    "TabError": Pure(),
    "TimeoutError": Pure(),
    "True": Pure(),
    "TypeError": Pure(),
    "UnboundLocalError": Pure(),
    "UnicodeDecodeError": Pure(),
    "UnicodeEncodeError": Pure(),
    "UnicodeError": Pure(),
    "UnicodeTranslateError": Pure(),
    "UnicodeWarning": Pure(),
    "UserWarning": Pure(),
    "ValueError": Pure(),
    "Warning": Pure(),
    "WindowsError": Pure(),
    "ZeroDivisionError": Pure(),
    "__build_class__": Impure(set()),
    "__debug__": Impure(set()),
    "__doc__": Impure(set()),
    "__import__": Impure(set()),
    "__loader__": Impure(set()),
    "__name__": Impure(set()),
    "__package__": Impure(set()),
    "__spec__": Impure(set()),
    "abs": Pure(),
    "aiter": Pure(),
    "all": Pure(),
    "anext": Pure(),
    "any": Pure(),
    "ascii": Pure(),
    "bin": Pure(),
    "bool": Pure(),
    "breakpoint": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
            FileRead(StringLiteral("UNKNOWN")),
            FileWrite(StringLiteral("UNKNOWN")),
        },
    ),
    "bytearray": Pure(),
    "bytes": Pure(),
    "callable": Pure(),
    "chr": Pure(),
    "classmethod": Pure(),
    "compile": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
            FileRead(StringLiteral("UNKNOWN")),
            FileWrite(StringLiteral("UNKNOWN")),
        },
    ),  # Can execute arbitrary code
    "complex": Pure(),
    "delattr": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
        },
    ),  # Can modify objects
    "dict": Pure(),
    "dir": Pure(),
    "divmod": Pure(),
    "enumerate": Pure(),
    "eval": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
            FileRead(StringLiteral("UNKNOWN")),
            FileWrite(StringLiteral("UNKNOWN")),
        },
    ),  # Can execute arbitrary code
    "exec": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
            FileRead(StringLiteral("UNKNOWN")),
            FileWrite(StringLiteral("UNKNOWN")),
        },
    ),  # Can execute arbitrary code
    "filter": Pure(),
    "float": Pure(),
    "format": Pure(),
    "frozenset": Pure(),
    "getattr": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
        },
    ),  # Can raise exceptions or interact with external resources
    "globals": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
        },
    ),  # May interact with external resources
    "hasattr": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
        },
    ),  # Calls the getattr function
    "hash": Pure(),
    "help": Impure({FileWrite(StringLiteral("stdout"))}),  # Interacts with external resources
    "hex": Pure(),
    "id": Pure(),
    "input": Impure({FileRead(StringLiteral("stdin"))}),  # Reads user input
    "int": Pure(),
    "isinstance": Pure(),
    "issubclass": Pure(),
    "iter": Pure(),
    "len": Pure(),
    "list": Pure(),
    "locals": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
        },
    ),  # May interact with external resources
    "map": Pure(),
    "max": Pure(),
    "memoryview": Pure(),
    "min": Pure(),
    "next": Pure(),
    "object": Pure(),
    "oct": Pure(),
    "ord": Pure(),
    "pow": Pure(),
    "print": Impure({FileWrite(StringLiteral("stdout"))}),
    "property": Pure(),
    "range": Pure(),
    "repr": Pure(),
    "reversed": Pure(),
    "round": Pure(),
    "set": Pure(),
    "setattr": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
        },
    ),  # Can modify objects
    "slice": Pure(),
    "sorted": Pure(),
    "staticmethod": Pure(),
    "str": Pure(),
    "sum": Pure(),
    "super": Pure(),
    "tuple": Pure(),
    "type": Pure(),
    "vars": Impure(
        {
            NonLocalVariableRead(UnknownSymbol()),
            NonLocalVariableWrite(UnknownSymbol()),
        },
    ),  # May interact with external resources
    "zip": Pure(),
}

OPEN_MODES = {
    "": OpenMode.READ,
    "r": OpenMode.READ,
    "rb": OpenMode.READ,
    "rt": OpenMode.READ,
    "w": OpenMode.WRITE,
    "wb": OpenMode.WRITE,
    "wt": OpenMode.WRITE,
    "a": OpenMode.WRITE,
    "ab": OpenMode.WRITE,
    "at": OpenMode.WRITE,
    "x": OpenMode.WRITE,
    "xb": OpenMode.WRITE,
    "xt": OpenMode.WRITE,
    "r+": OpenMode.READ_WRITE,
    "rb+": OpenMode.READ_WRITE,
    "w+": OpenMode.READ_WRITE,
    "wb+": OpenMode.READ_WRITE,
    "a+": OpenMode.READ_WRITE,
    "ab+": OpenMode.READ_WRITE,
    "x+": OpenMode.READ_WRITE,
    "xb+": OpenMode.READ_WRITE,
    "r+b": OpenMode.READ_WRITE,
    "rb+b": OpenMode.READ_WRITE,
    "w+b": OpenMode.READ_WRITE,
    "wb+b": OpenMode.READ_WRITE,
    "a+b": OpenMode.READ_WRITE,
    "ab+b": OpenMode.READ_WRITE,
    "x+b": OpenMode.READ_WRITE,
    "xb+b": OpenMode.READ_WRITE,
}


BUILTIN_CLASSSCOPES = {
    "BaseException": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "BaseException", 859, 0),
            "BaseException",
        ),
        [],
        None,
        {
            "add_note": [
                ClassVariable(
                    astroid.FunctionDef(name="add_note", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "add_note", 861, 4),
                    "add_note",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "with_traceback": [
                ClassVariable(
                    astroid.FunctionDef(name="with_traceback", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "with_traceback", 868, 4),
                    "with_traceback",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__delattr__": [
                ClassVariable(
                    astroid.FunctionDef(name="__delattr__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__delattr__", 875, 4),
                    "__delattr__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__getattribute__": [
                ClassVariable(
                    astroid.FunctionDef(name="__getattribute__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__getattribute__", 879, 4),
                    "__getattribute__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 883, 4),
                    "__init__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 886, 4),
                    "__new__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__reduce__": [
                ClassVariable(
                    astroid.FunctionDef(name="__reduce__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__reduce__", 891, 4),
                    "__reduce__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__repr__": [
                ClassVariable(
                    astroid.FunctionDef(name="__repr__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__repr__", 894, 4),
                    "__repr__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__setattr__": [
                ClassVariable(
                    astroid.FunctionDef(name="__setattr__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__setattr__", 898, 4),
                    "__setattr__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__setstate__": [
                ClassVariable(
                    astroid.FunctionDef(name="__setstate__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__setstate__", 902, 4),
                    "__setstate__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 905, 4),
                    "__str__",
                    astroid.ClassDef(name="BaseException", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "Exception": ClassScope(
        GlobalVariable(astroid.ClassDef(name="Exception", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "Exception", 925, 0), "Exception"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 927, 4),
                    "__init__",
                    astroid.ClassDef(name="Exception", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 930, 4),
                    "__new__",
                    astroid.ClassDef(name="Exception", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ArithmeticError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ArithmeticError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ArithmeticError", 936, 0),
            "ArithmeticError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 938, 4),
                    "__init__",
                    astroid.ClassDef(name="ArithmeticError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 941, 4),
                    "__new__",
                    astroid.ClassDef(name="ArithmeticError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "AssertionError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="AssertionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "AssertionError", 947, 0),
            "AssertionError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 949, 4),
                    "__init__",
                    astroid.ClassDef(name="AssertionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 952, 4),
                    "__new__",
                    astroid.ClassDef(name="AssertionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "AttributeError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="AttributeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "AttributeError", 958, 0),
            "AttributeError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 960, 4),
                    "__init__",
                    astroid.ClassDef(name="AttributeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 963, 4),
                    "__str__",
                    astroid.ClassDef(name="AttributeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "BaseExceptionGroup": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "BaseExceptionGroup", 975, 0),
            "BaseExceptionGroup",
        ),
        [],
        None,
        {
            "derive": [
                ClassVariable(
                    astroid.FunctionDef(name="derive", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "derive", 977, 4),
                    "derive",
                    astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "split": [
                ClassVariable(
                    astroid.FunctionDef(name="split", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "split", 980, 4),
                    "split",
                    astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "subgroup": [
                ClassVariable(
                    astroid.FunctionDef(name="subgroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "subgroup", 983, 4),
                    "subgroup",
                    astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__class_getitem__": [
                ClassVariable(
                    astroid.FunctionDef(name="__class_getitem__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__class_getitem__", 986, 4),
                    "__class_getitem__",
                    astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 990, 4),
                    "__init__",
                    astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 993, 4),
                    "__new__",
                    astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 998, 4),
                    "__str__",
                    astroid.ClassDef(name="BaseExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "WindowsError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="WindowsError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "WindowsError", 1010, 0),
            "WindowsError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 1012, 4),
                    "__init__",
                    astroid.ClassDef(name="WindowsError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 1015, 4),
                    "__new__",
                    astroid.ClassDef(name="WindowsError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__reduce__": [
                ClassVariable(
                    astroid.FunctionDef(name="__reduce__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__reduce__", 1020, 4),
                    "__reduce__",
                    astroid.ClassDef(name="WindowsError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 1023, 4),
                    "__str__",
                    astroid.ClassDef(name="WindowsError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "BlockingIOError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="BlockingIOError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "BlockingIOError", 1055, 0),
            "BlockingIOError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 1057, 4),
                    "__init__",
                    astroid.ClassDef(name="BlockingIOError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ConnectionError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ConnectionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ConnectionError", 1450, 0),
            "ConnectionError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 1452, 4),
                    "__init__",
                    astroid.ClassDef(name="ConnectionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "BrokenPipeError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="BrokenPipeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "BrokenPipeError", 1456, 0),
            "BrokenPipeError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 1458, 4),
                    "__init__",
                    astroid.ClassDef(name="BrokenPipeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "BufferError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="BufferError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "BufferError", 1462, 0), "BufferError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 1464, 4),
                    "__init__",
                    astroid.ClassDef(name="BufferError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 1467, 4),
                    "__new__",
                    astroid.ClassDef(name="BufferError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "Warning": ClassScope(
        GlobalVariable(astroid.ClassDef(name="Warning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "Warning", 2688, 0), "Warning"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 2690, 4),
                    "__init__",
                    astroid.ClassDef(name="Warning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 2693, 4),
                    "__new__",
                    astroid.ClassDef(name="Warning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "BytesWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="BytesWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "BytesWarning", 2699, 0),
            "BytesWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 2704, 4),
                    "__init__",
                    astroid.ClassDef(name="BytesWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 2707, 4),
                    "__new__",
                    astroid.ClassDef(name="BytesWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ChildProcessError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ChildProcessError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ChildProcessError", 2713, 0),
            "ChildProcessError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 2715, 4),
                    "__init__",
                    astroid.ClassDef(name="ChildProcessError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ConnectionAbortedError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ConnectionAbortedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ConnectionAbortedError", 2903, 0),
            "ConnectionAbortedError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 2905, 4),
                    "__init__",
                    astroid.ClassDef(name="ConnectionAbortedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ConnectionRefusedError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ConnectionRefusedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ConnectionRefusedError", 2909, 0),
            "ConnectionRefusedError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 2911, 4),
                    "__init__",
                    astroid.ClassDef(name="ConnectionRefusedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ConnectionResetError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ConnectionResetError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ConnectionResetError", 2915, 0),
            "ConnectionResetError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 2917, 4),
                    "__init__",
                    astroid.ClassDef(name="ConnectionResetError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "DeprecationWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="DeprecationWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "DeprecationWarning", 2921, 0),
            "DeprecationWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 2923, 4),
                    "__init__",
                    astroid.ClassDef(name="DeprecationWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 2926, 4),
                    "__new__",
                    astroid.ClassDef(name="DeprecationWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "EncodingWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="EncodingWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "EncodingWarning", 3111, 0),
            "EncodingWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3113, 4),
                    "__init__",
                    astroid.ClassDef(name="EncodingWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3116, 4),
                    "__new__",
                    astroid.ClassDef(name="EncodingWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "EOFError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="EOFError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "EOFError", 3165, 0), "EOFError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3167, 4),
                    "__init__",
                    astroid.ClassDef(name="EOFError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3170, 4),
                    "__new__",
                    astroid.ClassDef(name="EOFError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ExceptionGroup": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ExceptionGroup", 3176, 0),
            "ExceptionGroup",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3178, 4),
                    "__init__",
                    astroid.ClassDef(name="ExceptionGroup", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "FileExistsError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="FileExistsError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "FileExistsError", 3186, 0),
            "FileExistsError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3188, 4),
                    "__init__",
                    astroid.ClassDef(name="FileExistsError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "FileNotFoundError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="FileNotFoundError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "FileNotFoundError", 3192, 0),
            "FileNotFoundError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3194, 4),
                    "__init__",
                    astroid.ClassDef(name="FileNotFoundError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "FloatingPointError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="FloatingPointError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "FloatingPointError", 3463, 0),
            "FloatingPointError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3465, 4),
                    "__init__",
                    astroid.ClassDef(name="FloatingPointError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3468, 4),
                    "__new__",
                    astroid.ClassDef(name="FloatingPointError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "FutureWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="FutureWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "FutureWarning", 3631, 0),
            "FutureWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3636, 4),
                    "__init__",
                    astroid.ClassDef(name="FutureWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3639, 4),
                    "__new__",
                    astroid.ClassDef(name="FutureWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "GeneratorExit": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="GeneratorExit", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "GeneratorExit", 3645, 0),
            "GeneratorExit",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3647, 4),
                    "__init__",
                    astroid.ClassDef(name="GeneratorExit", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3650, 4),
                    "__new__",
                    astroid.ClassDef(name="GeneratorExit", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ImportError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="ImportError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "ImportError", 3656, 0), "ImportError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3658, 4),
                    "__init__",
                    astroid.ClassDef(name="ImportError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__reduce__": [
                ClassVariable(
                    astroid.FunctionDef(name="__reduce__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__reduce__", 3661, 4),
                    "__reduce__",
                    astroid.ClassDef(name="ImportError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 3664, 4),
                    "__str__",
                    astroid.ClassDef(name="ImportError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ImportWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ImportWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ImportWarning", 3679, 0),
            "ImportWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3681, 4),
                    "__init__",
                    astroid.ClassDef(name="ImportWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3684, 4),
                    "__new__",
                    astroid.ClassDef(name="ImportWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "SyntaxError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="SyntaxError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "SyntaxError", 3690, 0), "SyntaxError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3692, 4),
                    "__init__",
                    astroid.ClassDef(name="SyntaxError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 3695, 4),
                    "__str__",
                    astroid.ClassDef(name="SyntaxError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "IndentationError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="IndentationError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "IndentationError", 3725, 0),
            "IndentationError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3727, 4),
                    "__init__",
                    astroid.ClassDef(name="IndentationError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "LookupError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="LookupError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "LookupError", 3731, 0), "LookupError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3733, 4),
                    "__init__",
                    astroid.ClassDef(name="LookupError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3736, 4),
                    "__new__",
                    astroid.ClassDef(name="LookupError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "IndexError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="IndexError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "IndexError", 3742, 0), "IndexError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3744, 4),
                    "__init__",
                    astroid.ClassDef(name="IndexError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3747, 4),
                    "__new__",
                    astroid.ClassDef(name="IndexError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "InterruptedError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="InterruptedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "InterruptedError", 3753, 0),
            "InterruptedError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3755, 4),
                    "__init__",
                    astroid.ClassDef(name="InterruptedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "IsADirectoryError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="IsADirectoryError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "IsADirectoryError", 3759, 0),
            "IsADirectoryError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3761, 4),
                    "__init__",
                    astroid.ClassDef(name="IsADirectoryError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "KeyboardInterrupt": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="KeyboardInterrupt", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "KeyboardInterrupt", 3765, 0),
            "KeyboardInterrupt",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3767, 4),
                    "__init__",
                    astroid.ClassDef(name="KeyboardInterrupt", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 3770, 4),
                    "__new__",
                    astroid.ClassDef(name="KeyboardInterrupt", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "KeyError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="KeyError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "KeyError", 3776, 0), "KeyError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3778, 4),
                    "__init__",
                    astroid.ClassDef(name="KeyError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 3781, 4),
                    "__str__",
                    astroid.ClassDef(name="KeyError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "MemoryError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="MemoryError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "MemoryError", 3997, 0), "MemoryError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 3999, 4),
                    "__init__",
                    astroid.ClassDef(name="MemoryError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4002, 4),
                    "__new__",
                    astroid.ClassDef(name="MemoryError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ModuleNotFoundError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ModuleNotFoundError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ModuleNotFoundError", 4174, 0),
            "ModuleNotFoundError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4176, 4),
                    "__init__",
                    astroid.ClassDef(name="ModuleNotFoundError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "NameError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="NameError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "NameError", 4180, 0), "NameError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4182, 4),
                    "__init__",
                    astroid.ClassDef(name="NameError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 4185, 4),
                    "__str__",
                    astroid.ClassDef(name="NameError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "NotADirectoryError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="NotADirectoryError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "NotADirectoryError", 4194, 0),
            "NotADirectoryError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4196, 4),
                    "__init__",
                    astroid.ClassDef(name="NotADirectoryError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "RuntimeError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="RuntimeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "RuntimeError", 4200, 0),
            "RuntimeError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4202, 4),
                    "__init__",
                    astroid.ClassDef(name="RuntimeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4205, 4),
                    "__new__",
                    astroid.ClassDef(name="RuntimeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "NotImplementedError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="NotImplementedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "NotImplementedError", 4211, 0),
            "NotImplementedError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4213, 4),
                    "__init__",
                    astroid.ClassDef(name="NotImplementedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4216, 4),
                    "__new__",
                    astroid.ClassDef(name="NotImplementedError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "OverflowError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="OverflowError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "OverflowError", 4222, 0),
            "OverflowError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4224, 4),
                    "__init__",
                    astroid.ClassDef(name="OverflowError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4227, 4),
                    "__new__",
                    astroid.ClassDef(name="OverflowError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "PendingDeprecationWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="PendingDeprecationWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "PendingDeprecationWarning", 4233, 0),
            "PendingDeprecationWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4238, 4),
                    "__init__",
                    astroid.ClassDef(name="PendingDeprecationWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4241, 4),
                    "__new__",
                    astroid.ClassDef(name="PendingDeprecationWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "PermissionError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="PermissionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "PermissionError", 4247, 0),
            "PermissionError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4249, 4),
                    "__init__",
                    astroid.ClassDef(name="PermissionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ProcessLookupError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ProcessLookupError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ProcessLookupError", 4253, 0),
            "ProcessLookupError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4255, 4),
                    "__init__",
                    astroid.ClassDef(name="ProcessLookupError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "RecursionError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="RecursionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "RecursionError", 4480, 0),
            "RecursionError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4482, 4),
                    "__init__",
                    astroid.ClassDef(name="RecursionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4485, 4),
                    "__new__",
                    astroid.ClassDef(name="RecursionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ReferenceError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ReferenceError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ReferenceError", 4491, 0),
            "ReferenceError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4493, 4),
                    "__init__",
                    astroid.ClassDef(name="ReferenceError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4496, 4),
                    "__new__",
                    astroid.ClassDef(name="ReferenceError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ResourceWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ResourceWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ResourceWarning", 4502, 0),
            "ResourceWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4504, 4),
                    "__init__",
                    astroid.ClassDef(name="ResourceWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4507, 4),
                    "__new__",
                    astroid.ClassDef(name="ResourceWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "RuntimeWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="RuntimeWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "RuntimeWarning", 4548, 0),
            "RuntimeWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4550, 4),
                    "__init__",
                    astroid.ClassDef(name="RuntimeWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4553, 4),
                    "__new__",
                    astroid.ClassDef(name="RuntimeWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "StopAsyncIteration": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="StopAsyncIteration", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "StopAsyncIteration", 4914, 0),
            "StopAsyncIteration",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4916, 4),
                    "__init__",
                    astroid.ClassDef(name="StopAsyncIteration", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 4919, 4),
                    "__new__",
                    astroid.ClassDef(name="StopAsyncIteration", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "StopIteration": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="StopIteration", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "StopIteration", 4925, 0),
            "StopIteration",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 4927, 4),
                    "__init__",
                    astroid.ClassDef(name="StopIteration", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "SyntaxWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="SyntaxWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "SyntaxWarning", 5593, 0),
            "SyntaxWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5595, 4),
                    "__init__",
                    astroid.ClassDef(name="SyntaxWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5598, 4),
                    "__new__",
                    astroid.ClassDef(name="SyntaxWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "SystemError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="SystemError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "SystemError", 5604, 0), "SystemError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5611, 4),
                    "__init__",
                    astroid.ClassDef(name="SystemError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5614, 4),
                    "__new__",
                    astroid.ClassDef(name="SystemError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "SystemExit": ClassScope(
        GlobalVariable(astroid.ClassDef(name="SystemExit", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "SystemExit", 5620, 0), "SystemExit"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5622, 4),
                    "__init__",
                    astroid.ClassDef(name="SystemExit", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "TabError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="TabError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "TabError", 5630, 0), "TabError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5632, 4),
                    "__init__",
                    astroid.ClassDef(name="TabError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "TimeoutError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="TimeoutError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "TimeoutError", 5636, 0),
            "TimeoutError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5638, 4),
                    "__init__",
                    astroid.ClassDef(name="TimeoutError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "TypeError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="TypeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "TypeError", 5853, 0), "TypeError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5855, 4),
                    "__init__",
                    astroid.ClassDef(name="TypeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5858, 4),
                    "__new__",
                    astroid.ClassDef(name="TypeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "UnboundLocalError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="UnboundLocalError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "UnboundLocalError", 5864, 0),
            "UnboundLocalError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5866, 4),
                    "__init__",
                    astroid.ClassDef(name="UnboundLocalError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ValueError": ClassScope(
        GlobalVariable(astroid.ClassDef(name="ValueError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "ValueError", 5870, 0), "ValueError"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5872, 4),
                    "__init__",
                    astroid.ClassDef(name="ValueError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5875, 4),
                    "__new__",
                    astroid.ClassDef(name="ValueError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "UnicodeError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="UnicodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "UnicodeError", 5881, 0),
            "UnicodeError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5883, 4),
                    "__init__",
                    astroid.ClassDef(name="UnicodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5886, 4),
                    "__new__",
                    astroid.ClassDef(name="UnicodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "UnicodeDecodeError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="UnicodeDecodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "UnicodeDecodeError", 5892, 0),
            "UnicodeDecodeError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5894, 4),
                    "__init__",
                    astroid.ClassDef(name="UnicodeDecodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5897, 4),
                    "__new__",
                    astroid.ClassDef(name="UnicodeDecodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 5902, 4),
                    "__str__",
                    astroid.ClassDef(name="UnicodeDecodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "UnicodeEncodeError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="UnicodeEncodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "UnicodeEncodeError", 5923, 0),
            "UnicodeEncodeError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5925, 4),
                    "__init__",
                    astroid.ClassDef(name="UnicodeEncodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5928, 4),
                    "__new__",
                    astroid.ClassDef(name="UnicodeEncodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 5933, 4),
                    "__str__",
                    astroid.ClassDef(name="UnicodeEncodeError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "UnicodeTranslateError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="UnicodeTranslateError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "UnicodeTranslateError", 5954, 0),
            "UnicodeTranslateError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5956, 4),
                    "__init__",
                    astroid.ClassDef(name="UnicodeTranslateError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5959, 4),
                    "__new__",
                    astroid.ClassDef(name="UnicodeTranslateError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__str__": [
                ClassVariable(
                    astroid.FunctionDef(name="__str__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__str__", 5964, 4),
                    "__str__",
                    astroid.ClassDef(name="UnicodeTranslateError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "UnicodeWarning": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="UnicodeWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "UnicodeWarning", 5985, 0),
            "UnicodeWarning",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 5990, 4),
                    "__init__",
                    astroid.ClassDef(name="UnicodeWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 5993, 4),
                    "__new__",
                    astroid.ClassDef(name="UnicodeWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "UserWarning": ClassScope(
        GlobalVariable(astroid.ClassDef(name="UserWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0), NodeID("BUILTIN", "UserWarning", 5999, 0), "UserWarning"),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 6001, 4),
                    "__init__",
                    astroid.ClassDef(name="UserWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 6004, 4),
                    "__new__",
                    astroid.ClassDef(name="UserWarning", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
    "ZeroDivisionError": ClassScope(
        GlobalVariable(
            astroid.ClassDef(name="ZeroDivisionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
            NodeID("BUILTIN", "ZeroDivisionError", 6010, 0),
            "ZeroDivisionError",
        ),
        [],
        None,
        {
            "__init__": [
                ClassVariable(
                    astroid.FunctionDef(name="__init__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__init__", 6012, 4),
                    "__init__",
                    astroid.ClassDef(name="ZeroDivisionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
            "__new__": [
                ClassVariable(
                    astroid.FunctionDef(name="__new__", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                    NodeID("BUILTIN", "__new__", 6015, 4),
                    "__new__",
                    astroid.ClassDef(name="ZeroDivisionError", col_offset=0, lineno=0, parent=None, end_col_offset=0, end_lineno=0),
                ),
            ],
        },
    ),
}

BUILTIN_SPECIALS = {
    "get": Pure(),  # dict
    "update": Pure(),  # dict, set
    "pop": Pure(),  # dict, list, set
    "popitem": Pure(),  # dict
    "clear": Pure(),  # dict, # list, set
    "copy": Pure(),  # dict, # list, set
    "fromkeys": Pure(),  # dict
    "items": Pure(),  # dict
    "keys": Pure(),  # dict
    "values": Pure(),  # dict
    "setdefault": Pure(),  # dict
    "append": Pure(),  # list
    "count": Pure(),  # list, str
    "extend": Pure(),  # list
    "index": Pure(),  # list, str
    "insert": Pure(),  # list
    "remove": Pure(),  # list, set
    "reverse": Pure(),  # list
    "sort": Pure(),  # list
    "add": Pure(),  # set
    "difference": Pure(),  # set
    "difference_update": Pure(),  # set
    "discard": Pure(),  # set
    "intersection": Pure(),  # set
    "intersection_update": Pure(),  # set
    "isdisjoint": Pure(),  # set
    "issubset": Pure(),  # set
    "issuperset": Pure(),  # set
    "symmetric_difference": Pure(),  # set
    "symmetric_difference_update": Pure(),  # set
    "union": Pure(),  # set
    "capitalize": Pure(),  # str
    "casefold": Pure(),  # str
    "center": Pure(),  # str
    "encode": Pure(),  # str
    "endswith": Pure(),  # str
    "expandtabs": Pure(),  # str
    "find": Pure(),  # str
    "format": Pure(),  # str
    "format_map": Pure(),  # str
    "isalnum": Pure(),  # str
    "isalpha": Pure(),  # str
    "isascii": Pure(),  # str
    "isdecimal": Pure(),  # str
    "isdigit": Pure(),  # str
    "isidentifier": Pure(),  # str
    "islower": Pure(),  # str
    "isnumeric": Pure(),  # str
    "isprintable": Pure(),  # str
    "isspace": Pure(),  # str
    "istitle": Pure(),  # str
    "isupper": Pure(),  # str
    "join": Pure(),  # str
    "ljust": Pure(),  # str
    "lower": Pure(),  # str
    "lstrip": Pure(),  # str
    "maketrans": Pure(),  # str
    "partition": Pure(),  # str
    "removeprefix": Pure(),  # str
    "removesuffix": Pure(),  # str
    "replace": Pure(),  # str
    "rfind": Pure(),  # str
    "rindex": Pure(),  # str
    "rjust": Pure(),  # str
    "rpartition": Pure(),  # str
    "rsplit": Pure(),  # str
    "rstrip": Pure(),  # str
    "split": Pure(),  # str
    "splitlines": Pure(),  # str
    "startswith": Pure(),  # str
    "strip": Pure(),  # str
    "swapcase": Pure(),  # str
    "title": Pure(),  # str
    "translate": Pure(),  # str
    "upper": Pure(),  # str
    "zfill": Pure(),  # str
    "GenericAlias": Pure(),
    "UnionType": Pure(),
    "EllipsisType": Pure(),
    "NoneType": Pure(),
    "NotImplementedType": Pure(),
}
