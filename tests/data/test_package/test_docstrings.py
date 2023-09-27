class EpydocDocstringClass:
    """
    A class with a vary of different methods for calculations.

    @ivar attr_1: Attribute of the calculator
    @type attr_1: str
    @param param_1: Parameter of the calculator
    @type param_1: str
    """
    attr_1: str

    def __init__(self, param_1: str):
        pass

    def epydoc_docstring_func(self, x: int, y: int) -> bool:
        """
        This function checks if the sum of x and y is less than the value 10
        and returns True if it is.

        @param x: First integer value for the calculation
        @type x: int
        @param y: Second integer value for the calculation
        @type y: int
        @return: Checks if the sum of x and y is greater than 10
        @rtype: bool
        """
        z = x + y
        return z < 10


class RestDocstringClass:
    """
    A class with a vary of different methods for calculations.

    :param attr_1: Attribute of the calculator
    :type attr_1: str
    :param param_1: Parameter of the calculator
    :type param_1: str
    """
    attr_1: str

    def __init__(self, param_1: str):
        pass

    def rest_docstring_func(self, x: int, y: int) -> bool:
        """
        This function checks if the sum of x and y is less than the value 10
        and returns True if it is.

        :param x: First integer value for the calculation
        :type x: int
        :param y: Second integer value for the calculation
        :type y: int
        :returns: Checks if the sum of x and y is greater than 10
        :rtype: bool
        """
        z = x + y
        return z < 10


class NumpyDocstringClass:
    """A class that calculates stuff

    A class with a vary of different methods for calculations.

    Attributes
    ----------
    attr_1 : str
        Attribute of the calculator

    Parameters
    ----------
    param_1 : str
        Parameter of the calculator
    """
    attr_1: str

    def __init__(self, param_1: str):
        pass

    def numpy_docstring_func(self, x: int, y: int) -> bool:
        """Checks if the sum of two variables is over the value of 10.

        This function checks if the sum of `x` and `y` is less than the value
        10 and returns True if it is.

        Parameters
        ----------
        x : int
            First integer value for the calculation
        y : int
            Second integer value for the calculation

        Returns
        -------
        bool
            Checks if the sum of `x` and `y` is greater than 10
        """
        z = x + y
        return z < 10


class GoogleDocstringClass:
    """A class that calculates stuff

    A class with a vary of different methods for calculations.

    Attributes:
        attr_1 (str): Attribute of the calculator

    Args:
        param_1 (str): Parameter of the calculator
    """
    attr_1: str

    def __init__(self, param_1: str):
        pass

    def google_docstring_func(self, x: int, y: int) -> bool:
        """Checks if the sum of two variables is over the value of 10.

        This function checks if the sum of x and y is less than the value 10
        and returns True if it is.

        Args:
            x (int): First integer value for the calculation
            y (int): Second integer value for the calculation

        Returns:
            bool: Checks if the sum of x and y is greater than 10 and returns
                  a boolean value
        """
        z = x + y
        return z < 10
