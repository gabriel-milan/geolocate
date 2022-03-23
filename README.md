# Geolocate

Georeferencing large amounts of data for free.

## How?

It's using the very same API that Waze uses to georeference addresses before
it finds the best route to that destination. It requires no API keys, works
really well and has fairly high throughput.

In order to make this package extensible, there's an abstract class
`GeolocateEngine` that defines the interface for the engines. This allows
for the addition of new engines without having to modify the code.

## How do I use it?

First you have to install the `geolocate` package for Python 3.7+:

```
pip3 install geolocate
```

Then, for a single address:

```py
>>> from geolocate import geolocate
>>> geolocate("1 Infinite Loop, Cupertino, CA 95014")
{'latitude': 37.3311841, 'longitude': -122.0287127}
```

Or, if you want to run things in parallel:

```py
>>> from geolocate import geolocate_batch
>>> geolocate_batch(["1 Infinite Loop, Cupertino, CA 95014", "Eiffel Tower"])
100%|███████| 2/2 [00:01<00:00,  1.66it/s]
[{'latitude': 37.3311841, 'longitude': -122.0287127}, {'latitude': 48.8560934, 'longitude': 2.2930458}]
```

### Advanced usage

Both `geolocate` and `geolocate_batch` accept the following keyword arguments:

- engine (`geolocate.engines.GeolocateEngine`): Engine to use for
  geolocating the address. Defaults to `geolocate.engines.WazeEngine`
- timeout (int): The timeout in seconds.
- tries (int): The number of attempts to geolocate the address.
- backoff_factor (float): The backoff factor. Delay will grow by
  `{backoff factor} * (2 ** ({number of total retries} - 1))`.
- on_not_found (str or callable): A callback function for when the
  address is not found. The signature of the callback function
  should be:
  ```py
  def callback(address: str):
      ...
  ```
  where `address` is the address that was not found. The return
  value of the callback function is returned by the geolocate
  function.
- on_error (str or callable): A callback function for when an error
  occurs. The signature of the callback function should be:
  ```py
  def callback(address: str, error: Exception):
      ...
  ```
  where `address` is the address that caused the error and
  `error` is the exception that occurred. The return value of
  the callback function is returned by the geolocate function.

In addition, the `geolocate_batch` function accepts the following
keyword arguments:

- num_cpus (int): The number of CPUs to use. If None, the number of
  CPUs will be determined automatically.
