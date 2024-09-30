"""NumpyDoc Docstring of the some_class.py module."""

# noinspection PyUnusedLocal
def global_func1_numpy(param1, param2, param3):
    """Lorem ipsum

    Parameters
    --------
    param1 : str
        If "mean", then replace missing values using the mean along each column. 
        If "median", then replace missing values using the median along each column. 
        If "most_frequent", then replace missing using the most frequent value along each column. 
        If "constant", then replace missing values with fill_value.

    param2 : str or bool
        Valid values are [False, None, 'sparse matrix']

    param3 : float
        Damping factor in the range [0.5, 1.0) is the extent to which the current value is maintained relative
        to incoming values (weighted 1 - damping). This in order to avoid numerical oscillations when
        updating these values (messages)."
    """
    pass
