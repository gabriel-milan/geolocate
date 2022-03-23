# -*- coding: utf-8 -*-
"""
Engines for geolocating addresses.
"""

from abc import ABC, abstractmethod
import json
from typing import Dict, Iterable, List

from p_tqdm import p_map
import requests

from geolocate.decorators import retry


class GeolocateEngine(ABC):
    """
    Abstract class for geolocating addresses.
    """

    @abstractmethod
    def _geolocate(self, address: str) -> Dict[str, float]:
        """
        Geolocate the given address.

        Args:
            address (str): The address to geolocate.

        Returns:
            dict: The geolocation of the address in the format:
                {
                    "latitude": float,
                    "longitude": float,
                }
        """
        pass

    @retry(tries=3, delay=1)
    def geolocate(self, address: str) -> Dict[str, float]:
        """
        Geolocate the given address.

        Args:
            address (str): The address to geolocate.

        Returns:
            dict: The geolocation of the address in the format:
                {
                    "latitude": float,
                    "longitude": float,
                }
        """
        return self._geolocate(address)

    def geolocate_batch(self, addresses: Iterable[str]) -> List[Dict[str, float]]:
        """
        Geolocate the given addresses.

        Args:
            addresses (list): The addresses to geolocate.

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
        return p_map(self.geolocate, addresses)


class WazeEngine(GeolocateEngine):
    """
    Uses Waze public API to geolocate addresses.
    """

    def _geolocate(self, address: str) -> Dict[str, float]:
        """
        Geolocate the given address.

        Args:
            address (str): The address to geolocate.

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
        response = requests.get(url, params=params, timeout=2)
        response.raise_for_status()
        data = response.json()
        latitude = data[1][0][3]["y"]
        longitude = data[1][0][3]["x"]
        return {
            "latitude": latitude,
            "longitude": longitude,
        }


class GoogleMapsEngine(GeolocateEngine):
    """
    Uses Google Maps search to geolocate addresses
    """

    def _geolocate(self, address: str) -> Dict[str, float]:
        """
        Geolocate the given address.

        Args:
            address (str): The address to geolocate.

        Returns:
            dict: The geolocation of the address in the format:
                {
                    "latitude": float,
                    "longitude": float,
                }
        """
        url = "https://www.google.com/search"
        params = {
            "tbm": "map",
            "q": address,
            "oq": address,
        }
        response = requests.get(url, params=params, timeout=2)
        response.raise_for_status()
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            text = response.text.split("\n")[1]
            data = json.loads(text)
        latitude = data[0][1][0][14][9][2]
        longitude = data[0][1][0][14][9][3]
        return {
            "latitude": latitude,
            "longitude": longitude,
        }
