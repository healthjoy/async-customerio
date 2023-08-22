import math
import typing as t
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote, urlencode, urljoin

from .errors import AsyncCustomerIOError


def datetime_to_timestamp(dt) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def sanitize(data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = datetime_to_timestamp(v)
        if isinstance(v, float) and math.isnan(v):
            data[k] = None
    return data


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
    url = base
    if parts:
        url = "/".join([base.strip("/"), quote("/".join(map(lambda x: str(x).strip("/"), parts)))])

    # trailing slash can be important
    if trailing_slash:
        url = f"{url}/"
    # as well as a leading slash
    if leading_slash:
        url = f"/{url}"

    if params:
        url = urljoin(url, "?{}".format(urlencode(params)))

    return url
