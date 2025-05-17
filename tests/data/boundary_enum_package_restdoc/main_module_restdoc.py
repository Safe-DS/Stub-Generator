"""ReST Docstring of the main_module_restdoc.py module."""

test = 10

# noinspection PyUnusedLocal
def global_func1_rest(param1, param2, param3, param4):
    """Lorem ipsum

    :param param1: 
        If "mean", then replace missing values using the mean along each column. 
        If "median", then replace missing values using the median along each column. 
        If "most_frequent", then replace missing using the most frequent value along each column. 
        If "constant", then replace missing values with fill_value.
    :type param1: int
    :param param2: Valid values are [False, None, 'sparse matrix']
    :type param2: str or bool
    :param param3: 
        Damping factor in the range [0.5, 1.0) is the extent to which the current value is maintained relative
        to incoming values (weighted 1 - damping). This in order to avoid numerical oscillations when
        updating these values (messages).
    :type param3: float
    :param param4:
        If bootstrap is True, the number of samples to draw from X to train each base estimator.
        If None (default), then draw X.shape[0] samples.
        If int, then max_samples values in [0, 10].
        If float, then draw max_samples * X.shape[0] samples. Thus, max_samples should be in the interval (0.0, 1.0].
    :type param4: int or float
    """
    return test

# TODO Currently disabled, since Griffe can't analyze ReST (Sphinx) attributes (see issue #98)
# that is why the stub generator wont generate the class stub correctly
class ClassWithAttributes:
    """
    ClassAndConstructorWithParameters

    Dolor sit amet.

    :param attribute1:
        Damping factor in the range [0.5, 1.0) is the extent to which the current value is maintained relative
        to incoming values (weighted 1 - damping). This in order to avoid numerical oscillations when
        updating these values (messages).
    :type attribute1: float
    :param attribute2:
        If "mean", then replace missing values using the mean along each column. 
        If "median", then replace missing values using the median along each column. 
        If "most_frequent", then replace missing using the most frequent value along each column. 
        If "constant", then replace missing values with fill_value.
    :type attribute2: str
    """
    def __init__(self) -> None:
        """
        :param attribute1:
            Damping factor in the range [0.5, 1.0) is the extent to which the current value is maintained relative
            to incoming values (weighted 1 - damping). This in order to avoid numerical oscillations when
            updating these values (messages).
        :type attribute1: float
        :param attribute2:
            If "mean", then replace missing values using the mean along each column. 
            If "median", then replace missing values using the median along each column. 
            If "most_frequent", then replace missing using the most frequent value along each column. 
            If "constant", then replace missing values with fill_value.
        :type attribute2: str
        """
        self.attribute1: float
        self.attribute2: str