# -*- coding: utf-8 -*-
"""
Utility functions for geolocate.
"""

import requests
from requests.adapters import HTTPAdapter, Retry

from geolocate.constants import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_TRIES,
)


def fetch(
    address: str,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    tries: int = DEFAULT_TRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    **kwargs,
) -> requests.Response:
    """
    Fetch the given address.

    Args:
        address (str): The address to fetch.
        timeout (int): The timeout in seconds.
        tries (int): The number of attempts to fetch the address.
        backoff_factor (float): The backoff factor. Delay will grow by
            `{backoff factor} * (2 ** ({number of total retries} - 1))`.

    Returns:
        requests.Response: The response of the request.
    """
    s = requests.Session()
    retries = Retry(total=tries, backoff_factor=backoff_factor)
    s.mount(address, HTTPAdapter(max_retries=retries))
    return s.get(address, timeout=timeout, **kwargs)
