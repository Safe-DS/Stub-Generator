"""Test module for docstring tests.

A module for testing the various docstring types.
"""


class EpydocDocstringClass:
    """
    A class with a variety of different methods for calculations. (Epydoc).

    @ivar attr_1: Attribute of the calculator. (Epydoc)
    @type attr_1: str
    @param param_1: Parameter of the calculator. (Epydoc)
    @type param_1: str
    """

    attr_1: str

    def __init__(self, param_1: str):
        pass

    def epydoc_docstring_func(self, x: int, y: int) -> bool:
        """
        This function checks if the sum of x and y is less than the value 10 and returns True if it is. (Epydoc).

        @param x: First integer value for the calculation. (Epydoc)
        @type x: int
        @param y: Second integer value for the calculation. (Epydoc)
        @type y: int
        @return: Checks if the sum of x and y is greater than 10. (Epydoc)
        @rtype: bool
        """
        z = x + y
        return z < 10


class RestDocstringClass:
    """
    A class with a variety of different methods for calculations. (ReST).

    :param attr_1: Attribute of the calculator. (ReST)
    :type attr_1: str
    :param param_1: Parameter of the calculator. (ReST)
    :type param_1: str
    """

    attr_1: str

    def __init__(self, param_1: str):
        pass

    def rest_docstring_func(self, x: int, y: int) -> bool:
        """
        This function checks if the sum of x and y is less than the value 10
        and returns True if it is. (ReST).

        :param x: First integer value for the calculation. (ReST)
        :type x: int
        :param y: Second integer value for the calculation. (ReST)
        :type y: int
        :returns: Checks if the sum of x and y is greater than 10. (ReST)
        :rtype: bool
        """
        z = x + y
        return z < 10


class NumpyDocstringClass:
    """A class that calculates stuff. (Numpy).

    A class with a variety of different methods for calculations. (Numpy)

    Attributes
    ----------
    attr_1 : str
        Attribute of the calculator. (Numpy)

    Parameters
    ----------
    param_1 : str
        Parameter of the calculator. (Numpy)
    """

    attr_1: str

    def __init__(self, param_1: str):
        pass

    def numpy_docstring_func(self, x: int, y: int) -> bool:
        """Checks if the sum of two variables is over the value of 10. (Numpy).

        This function checks if the sum of `x` and `y` is less than the value 10 and returns True if it is. (Numpy)

        Parameters
        ----------
        x : int
            First integer value for the calculation. (Numpy)
        y : int
            Second integer value for the calculation. (Numpy)

        Returns
        -------
        bool
            Checks if the sum of `x` and `y` is greater than 10. (Numpy)
        """
        z = x + y
        return z < 10


class GoogleDocstringClass:
    """A class that calculates stuff. (Google Style).

    A class with a variety of different methods for calculations. (Google Style)

    Attributes:
        attr_1 (str): Attribute of the calculator. (Google Style)

    Args:
        param_1 (str): Parameter of the calculator. (Google Style)
    """

    attr_1: str

    def __init__(self, param_1: str):
        pass

    def google_docstring_func(self, x: int, y: int) -> bool:
        """Checks if the sum of two variables is over the value of 10. (Google Style).

        This function checks if the sum of x and y is less than the value 10
        and returns True if it is. (Google Style)

        Args:
            x (int): First integer value for the calculation. (Google Style)
            y (int): Second integer value for the calculation. (Google Style)

        Returns:
            bool: Checks if the sum of x and y is greater than 10 and returns
                  a boolean value. (Google Style)
        """
        z = x + y
        return z < 10
