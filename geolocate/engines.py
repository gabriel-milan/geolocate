# -*- coding: utf-8 -*-
"""
Engines for geolocating addresses.

Every engine implementation must inherit from the `GeolocateEngine` class.
The only method that must be implemented is the `_geolocate` method, which
has the following signature:

```py
def _geolocate(
    self,
    address: str,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    tries: int = DEFAULT_TRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
) -> Dict[str, float]:
    ...
    return {
        "latitude": latitude,
        "longitude": longitude,
    }
```

Those arguments are the same as the ones in the `geolocate.utils.fetch` method.
"""

from abc import ABC, abstractmethod
from functools import partial
from multiprocessing import cpu_count
from typing import Callable, Dict, Iterable, List, Union

from p_tqdm import p_map
from requests import Response

from geolocate.constants import (
    ACTION_IGNORE,
    ACTION_RAISE,
    DEFAULT_ACTION_ON_ERROR,
    DEFAULT_ACTION_ON_NOT_FOUND,
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_TRIES,
)
from geolocate.exceptions import GeolocateNotFoundError, GeolocateUnknownCallbackError
from geolocate.utils import fetch


class GeolocateEngine(ABC):
    """
    Abstract class for geolocating addresses.
    """

    @abstractmethod
    def _geolocate(
        self,
        address: str,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        tries: int = DEFAULT_TRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[str, float]:
        """
        Geolocate the given address.

        Args:
            address (str): The address to geolocate.
            timeout (int): The timeout in seconds.
            tries (int): The number of attempts to geolocate the address.
            backoff_factor (float): The backoff factor. Delay will grow by
                `{backoff factor} * (2 ** ({number of total retries} - 1))`.

        Returns:
            dict: The geolocation of the address in the format:
                {
                    "latitude": float,
                    "longitude": float,
                }
        """

    def geolocate(
        self,
        address: str,
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
        try:
            return self._geolocate(
                address, timeout=timeout, tries=tries, backoff_factor=backoff_factor
            )
        except GeolocateNotFoundError as exc:
            if on_not_found == ACTION_IGNORE:
                return {
                    "latitude": None,
                    "longitude": None,
                }
            elif on_not_found == ACTION_RAISE:
                raise exc
            elif callable(on_not_found):
                return on_not_found(address)
            else:
                raise GeolocateUnknownCallbackError(
                    f"Unknown value for on_not_found: {on_not_found}"
                )
        except Exception as exc:
            if on_error == ACTION_IGNORE:
                return {
                    "latitude": None,
                    "longitude": None,
                }
            elif on_error == ACTION_RAISE:
                raise exc
            elif callable(on_error):
                return on_error(address, exc)
            else:
                raise GeolocateUnknownCallbackError(
                    f"Unknown value for on_error: {on_error}"
                )

    def geolocate_batch(
        self,
        addresses: Iterable[str],
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
        num_cpus = num_cpus or cpu_count()
        func = partial(
            self.geolocate,
            timeout=timeout,
            tries=tries,
            backoff_factor=backoff_factor,
            on_not_found=on_not_found,
            on_error=on_error,
        )
        return p_map(func, addresses, num_cpus=num_cpus)


class WazeEngine(GeolocateEngine):
    """
    Uses Waze public API to geolocate addresses.
    """

    def _geolocate(
        self,
        address: str,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        tries: int = DEFAULT_TRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[str, float]:
        """
        Geolocate the given address.

        Args:
            address (str): The address to geolocate.
            timeout (int): The timeout in seconds.
            tries (int): The number of attempts to geolocate the address.
            backoff_factor (float): The backoff factor. Delay will grow by
                `{backoff factor} * (2 ** ({number of total retries} - 1))`.

        Returns:
            dict: The geolocation of the address in the format:
                {
                    "latitude": float,
                    "longitude": float,
                }
        """
        url = "https://gapi.waze.com/autocomplete/q"
        params = {
            "q": address,
            "e": "ALL",
            "c": "web",
        }
        response: Response = fetch(
            url,
            timeout=timeout,
            tries=tries,
            backoff_factor=backoff_factor,
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        try:
            latitude = data[1][0][3]["y"]
            longitude = data[1][0][3]["x"]
        except IndexError:
            raise GeolocateNotFoundError(address)
        return {
            "latitude": latitude,
            "longitude": longitude,
        }
