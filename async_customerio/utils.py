import math
import typing as t
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote, urlencode

from .errors import AsyncCustomerIOError


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert a datetime to a unix timestamp (seconds).

    Timezone-naive datetimes are assumed to be UTC.
    Timezone-aware datetimes are properly converted to UTC.

    Raises AsyncCustomerIOError if `dt` is not a datetime instance.
    """
    if not isinstance(dt, datetime):
        raise AsyncCustomerIOError("datetime_to_timestamp expects a datetime instance")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _sanitize_value(v: t.Any) -> t.Any:
    """Sanitize a single value, recursing into dicts and lists."""
    if isinstance(v, datetime):
        return datetime_to_timestamp(v)
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, dict):
        return {k: _sanitize_value(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_sanitize_value(item) for item in v]
    return v


def sanitize(data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    """Return a sanitized copy of ``data`` where datetimes are converted to
    integer timestamps and NaN floats are replaced with None.

    Recurses into nested dicts and lists. Does not mutate the input mapping.
    """
    return {k: _sanitize_value(v) for k, v in data.items()}


def stringify_list(customer_ids: t.List[t.Union[str, int]]) -> t.List[str]:
    customer_string_ids = []
    for value in customer_ids:
        if isinstance(value, str):
            customer_string_ids.append(value)
        elif isinstance(value, int):
            customer_string_ids.append(str(value))
        else:
            raise AsyncCustomerIOError("customer_ids cannot be {type}".format(type=type(value)))
    return customer_string_ids


def join_url(
    base: str,
    *parts: t.Union[str, int],
    params: Optional[dict] = None,
    leading_slash: bool = False,
    trailing_slash: bool = False,
) -> str:
    """Construct a full ("absolute") URL by combining a "base URL" (base) with another URL (url) parts.

    :param base: base URL part
    :param parts: another url parts that should be joined
    :param params: dict with query params
    :param leading_slash: flag to force leading slash
    :param trailing_slash: flag to force trailing slash

    :return: full URL
    """
    # Preserve scheme and leading // by only rstrip'ing the trailing slash
    base = base.rstrip("/")
    if parts:
        # quote individual path segments to avoid accidental encoding of slashes
        encoded_parts = [quote(str(p).strip("/")) for p in parts]
        url = "/".join([base] + encoded_parts)
    else:
        url = base

    # trailing slash can be important
    if trailing_slash and not url.endswith("/"):
        url = f"{url}/"
    # as well as a leading slash
    if leading_slash and not url.startswith("/"):
        url = f"/{url}"

    if params:
        url = f"{url}?{urlencode(params)}"

    return url


def to_dict(field_map: t.Dict[str, str], instance: t.Any, exclude_none: bool = True) -> t.Dict[str, t.Any]:
    """Build a request payload from the object.

    :param field_map: dictionary that defines mapping.
    :param request_instance: insatnce of request object.
    :param exclude_none: defines whether fields with ``None`` should be included into resulting dict.
    :return: dictionary that is a mapping of request attributes according to the field map.
    """

    data = {}
    for field, name in field_map.items():
        value = getattr(instance, field, None)
        if value is None and exclude_none:
            continue
        data[name] = value

    return data
