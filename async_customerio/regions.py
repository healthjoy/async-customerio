from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    name: str
    track_host: str
    api_host: str


class Regions:
    """Simple container for known regions.

    Access as `Regions.US` and `Regions.EU` to get a `Region` instance.
    """

    US = Region("us", "track.customer.io", "api.customer.io")
    EU = Region("eu", "track-eu.customer.io", "api-eu.customer.io")
