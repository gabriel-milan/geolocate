# -*- coding: utf-8 -*-
"""
Defining exceptions for geolocate module.
"""


class GeolocateError(Exception):
    """
    Base class for geolocate errors.
    """


class GeolocateNotFoundError(GeolocateError):
    """
    Error raised when a geolocation is not found.
    """


class GeolocateUnknownCallbackError(GeolocateError):
    """
    Error raised when an unknown callback is used.
    """
