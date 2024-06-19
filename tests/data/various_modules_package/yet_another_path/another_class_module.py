from tests.data.various_modules_package.another_path.another_module import _AnotherPrivateClass
from tests.data.various_modules_package.another_path import _YetAnotherPrivateClass


class SuperclassClass(_AnotherPrivateClass, _YetAnotherPrivateClass):
    ...
