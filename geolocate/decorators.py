# -*- coding: utf-8 -*-
"""
General decorators for the geolocate package.
"""

from functools import wraps
from time import sleep
from typing import Union


def retry(
    exceptions: Union[tuple, Exception] = Exception,
    tries: int = 5,
    delay: float = 0.5,
    backoff_factor: float = 2,
):
    """
    Calls the decorated function applying an exponential backoff when meeting
    an exception. Adapted from https://bit.ly/36nFyFx.

    Args:
        exceptions (list): The exceptions to catch.
        tries (int): The total number of tries.
        delay (float): The initial wait time in seconds.
        backoff_factor (float): The backoff factor.

    Returns:
        The result of the decorated function.
    """

    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    if not _tries:
                        raise e
                    sleep(_delay)
                    _delay *= backoff_factor

        return func_with_retries

    return retry_decorator
