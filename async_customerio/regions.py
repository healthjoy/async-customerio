from dataclasses import dataclass, field


@dataclass
class Region:
    name: str
    track_host: str
    api_host: str


@dataclass(frozen=True)
class DefaultRegions:
    US: Region = field(default_factory=lambda: Region("us", "track.customer.io", "api.customer.io"))
    EU: Region = field(default_factory=lambda: Region("eu", "track-eu.customer.io", "api-eu.customer.io"))


Regions = DefaultRegions()
