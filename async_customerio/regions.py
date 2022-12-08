from dataclasses import dataclass


@dataclass()
class Region:
    name: str
    track_host: str
    api_host: str


@dataclass(frozen=True, eq=False, init=False)
class Regions:
    US: Region = Region("us", "track.customer.io", "api.customer.io")
    EU: Region = Region("eu", "track-eu.customer.io", "api-eu.customer.io")
