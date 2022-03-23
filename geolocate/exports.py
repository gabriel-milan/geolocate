# -*- coding: utf-8 -*-
"""
These are the methods which will be exported on `__init__.py`.
"""

from typing import Callable, Dict, Iterable, List, Union

from geolocate.constants import (
    DEFAULT_ACTION_ON_ERROR,
    DEFAULT_ACTION_ON_NOT_FOUND,
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_TRIES,
)
from geolocate import engines


def geolocate(
    address: str,
    engine: engines.GeolocateEngine = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    tries: int = DEFAULT_TRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    on_not_found: Union[str, Callable] = DEFAULT_ACTION_ON_NOT_FOUND,
    on_error: Union[str, Callable] = DEFAULT_ACTION_ON_ERROR,
) -> Dict[str, float]:
    """
    Geolocate the given address.

    Args:
        address (str): The address to geolocate.
        engine (geolocate.engines.GeolocateEngine): Engine to use for
            geolocating the address. Defaults to `geolocate.engines.WazeEngine`
        timeout (int): The timeout in seconds.
        tries (int): The number of attempts to geolocate the address.
        backoff_factor (float): The backoff factor. Delay will grow by
            `{backoff factor} * (2 ** ({number of total retries} - 1))`.
        on_not_found (str or callable): A callback function for when the
            address is not found. The signature of the callback function
            should be:
                ```
                def callback(address: str):
                    ...
                ```
            where `address` is the address that was not found. The return
            value of the callback function is returned by the geolocate
            function.
        on_error (str or callable): A callback function for when an error
            occurs. The signature of the callback function should be:
                ```
                def callback(address: str, error: Exception):
                    ...
                ```
            where `address` is the address that caused the error and
            `error` is the exception that occurred. The return value of
            the callback function is returned by the geolocate function.

    Returns:
        dict: The geolocation of the address in the format:
            {
                "latitude": float,
                "longitude": float,
            }
    """
    engine = engine or engines.WazeEngine()
    return engine.geolocate(
        address,
        timeout=timeout,
        tries=tries,
        backoff_factor=backoff_factor,
        on_not_found=on_not_found,
        on_error=on_error,
    )


def geolocate_batch(
    addresses: Iterable[str],
    engine: engines.GeolocateEngine = None,
    num_cpus: int = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    tries: int = DEFAULT_TRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    on_not_found: Union[str, Callable] = DEFAULT_ACTION_ON_NOT_FOUND,
    on_error: Union[str, Callable] = DEFAULT_ACTION_ON_ERROR,
) -> List[Dict[str, float]]:
    """
    Geolocate the given addresses.

    Args:
        addresses (list): The addresses to geolocate.
        engine (geolocate.engines.GeolocateEngine): Engine to use for
            geolocating the address. Defaults to `geolocate.engines.WazeEngine`
        num_cpus (int): The number of CPUs to use. If None, the number of
            CPUs will be determined automatically.
        timeout (int): The timeout in seconds.
        tries (int): The number of attempts to geolocate the address.
        backoff_factor (float): The backoff factor. Delay will grow by
            `{backoff factor} * (2 ** ({number of total retries} - 1))`.
        on_not_found (str or callable): A callback function for when the
            address is not found. The signature of the callback function
            should be:
                ```
                def callback(address: str):
                    ...
                ```
            where `address` is the address that was not found. The return
            value of the callback function is returned by the geolocate
            function.
        on_error (str or callable): A callback function for when an error
            occurs. The signature of the callback function should be:
                ```
                def callback(address: str, error: Exception):
                    ...
                ```
            where `address` is the address that caused the error and
            `error` is the exception that occurred. The return value of
            the callback function is returned by the geolocate function.

    Returns:
        list: The geolocations of the addresses in the format:
            [
                {
                    "latitude": float,
                    "longitude": float,
                },
                ...
            ]
    """
    engine = engine or engines.WazeEngine()
    return engine.geolocate_batch(
        addresses,
        num_cpus=num_cpus,
        timeout=timeout,
        tries=tries,
        backoff_factor=backoff_factor,
        on_not_found=on_not_found,
        on_error=on_error,
    )
