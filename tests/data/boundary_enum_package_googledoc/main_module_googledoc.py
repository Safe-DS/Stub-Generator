"""GoogleDoc Docstring of the main_module_googledoc.py module."""

test = 10


# noinspection PyUnusedLocal
def global_func1_google(param1, param2, param3, param4):
    """Lorem ipsum

    Args:
        param1 (str): If "mean", then replace missing values using the mean along each column. 
            If "median", then replace missing values using the median along each column. 
            If "most_frequent", then replace missing using the most frequent value along each column. 
            If "constant", then replace missing values with fill_value.
        param2 (str or bool): Valid values are [False, None, 'sparse matrix']
        param3 (float): Damping factor in the range [0.5, 1.0) is the extent to which the current value is maintained relative
            to incoming values (weighted 1 - damping). This in order to avoid numerical oscillations when
            updating these values (messages).
        param4 (int or float): If bootstrap is True, the number of samples to draw from X to train each base estimator.
            If None (default), then draw X.shape[0] samples.
            If int, then max_samples values in [0, 10].
            If float, then draw max_samples * X.shape[0] samples. Thus, max_samples should be in the interval (0.0, 1.0].
    """
    return test

class ClassWithAttributes:
    """
    ClassAndConstructorWithParameters

    Dolor sit amet.

    Attributes:
        attribute1 (float):
            Damping factor in the range [0.5, 1.0) is the extent to which the current value is maintained relative
            to incoming values (weighted 1 - damping). This in order to avoid numerical oscillations when
            updating these values (messages).
        attribute2 (str):
            If "mean", then replace missing values using the mean along each column. 
            If "median", then replace missing values using the median along each column. 
            If "most_frequent", then replace missing using the most frequent value along each column. 
            If "constant", then replace missing values with fill_value.
    """
    def __init__(self) -> None:
        """
        Attributes:
            attribute1 (float):
                Damping factor in the range [0.5, 1.0) is the extent to which the current value is maintained relative
                to incoming values (weighted 1 - damping). This in order to avoid numerical oscillations when
                updating these values (messages).
            attribute2 (str):
                If "mean", then replace missing values using the mean along each column. 
                If "median", then replace missing values using the median along each column. 
                If "most_frequent", then replace missing using the most frequent value along each column. 
                If "constant", then replace missing values with fill_value.
        """
        self.attribute1: float
        self.attribute2: str
