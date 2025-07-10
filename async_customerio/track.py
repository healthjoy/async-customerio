"""
Implements the async client that interacts with Customer.io's Track API using Site ID and API Keys.
"""

import typing as t
from datetime import datetime
from typing import Optional
from urllib.parse import quote

from async_customerio._config import DEFAULT_REQUEST_TIMEOUT, RequestTimeout
from async_customerio.client_base import AsyncClientBase
from async_customerio.constants import CIOID, EMAIL, ID
from async_customerio.errors import AsyncCustomerIOError
from async_customerio.regions import Region, Regions
from async_customerio.utils import datetime_to_timestamp, join_url, sanitize


class AsyncCustomerIO(AsyncClientBase):
    """Async wrapper for CustomerIO."""

    API_PREFIX: str = "/api/v1"
    DEFAULT_API_PORT: int = 443
    DEFAULT_API_HOST: str = Regions.US.track_host

    # Endpoints
    CUSTOMER_ENDPOINT = "/customers/{id}"
    CUSTOMER_EVENT_ENDPOINT = "{customer_endpoint}/events".format(customer_endpoint=CUSTOMER_ENDPOINT)
    CUSTOMER_DEVICE_ENDPOINT = "{customer_endpoint}/devices".format(customer_endpoint=CUSTOMER_ENDPOINT)
    CUSTOMER_SUPPRESS_ENDPOINT = "{customer_endpoint}/suppress".format(customer_endpoint=CUSTOMER_ENDPOINT)
    CUSTOMER_UNSUPRESS_ENDPOINT = "{customer_endpoint}/unsuppress".format(customer_endpoint=CUSTOMER_ENDPOINT)
    EVENTS_ENDPOINT = "/events"
    MERGE_CUSTOMERS_ENDPOINT = "/merge_customers"

    def __init__(
        self,
        site_id: str,
        api_key: str,
        host: Optional[str] = None,
        region: Region = Regions.US,
        port: Optional[int] = None,
        url_prefix: Optional[str] = None,
        retries: int = 3,
        request_timeout: RequestTimeout = DEFAULT_REQUEST_TIMEOUT,
    ):
        if not isinstance(region, Region):
            raise AsyncCustomerIOError("invalid region provided")

        self.api_key: str = api_key
        self.site_id: str = site_id

        self.base_url = self.setup_base_url(
            host=host or self.DEFAULT_API_HOST,
            port=port or self.DEFAULT_API_PORT,
            prefix=url_prefix or self.API_PREFIX,
        )
        super().__init__(retries=retries, request_timeout=request_timeout)

    @staticmethod
    def _url_encode(id_: t.Union[str, int]) -> str:
        return quote(str(id_), safe="")

    @staticmethod
    def _is_valid_id_type(input_: str) -> bool:
        return input_ in frozenset((ID, EMAIL, CIOID))

    @staticmethod
    def setup_base_url(host: str, port: int, prefix: str) -> str:
        template = "https://{host}:{port}/{prefix}"
        if port == 443:
            template = "https://{host}/{prefix}"

        if "://" in host:
            host = host.split("://")[1]

        return template.format(host=host.strip("/"), port=port, prefix=prefix.strip("/"))

    async def identify(self, identifier: t.Union[str, int], **attrs) -> None:
        """
        Identify a single customer by their unique id, and optionally add attributes.

        :param identifier: the unique value representing a person. The values you use to identify a person may be an
            ``id``, ``email`` address, or the ``cio_id`` (when updating people), depending on your workspace settings.
            When you reference people by ``cio_id``, you must prefix the value with ``cio_``.
        """
        if not identifier:
            raise AsyncCustomerIOError("identifier cannot be blank in identify")
        await self.send_request(
            "PUT",
            join_url(self.base_url, self.CUSTOMER_ENDPOINT.format(id=identifier)),
            json_payload=attrs,
        )

    async def track(self, customer_id: t.Union[str, int], name: str, **data) -> None:
        """
        Track an event for a given customer_id.

        :param customer_id: the unique value representing a person. The values you use to identify a person may be an
            ``id``, ``email`` address, or the ``cio_id`` (when updating people), depending on your workspace settings.
            When you reference people by ``cio_id``, you must prefix the value with ``cio_``.
        :param name: the name of the event. This is how you'll reference the event in campaigns or segments.
        """
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in track")

        post_data = {"name": name, "data": sanitize(data)}
        await self.send_request(
            "POST",
            join_url(self.base_url, self.CUSTOMER_EVENT_ENDPOINT.format(id=customer_id)),
            json_payload=post_data,
        )

    async def track_anonymous(self, anonymous_id: str, name: str, **data) -> None:
        """
        Track an event for a given anonymous_id.

        An anonymous event represents a person you haven't identified yet.
        :param anonymous_id: an identifier for an anonymous event.
        :param name: the name of the event.
        """
        post_data = {"name": name, "data": sanitize(data)}
        if anonymous_id:
            post_data["anonymous_id"] = anonymous_id

        await self.send_request(
            "POST",
            join_url(self.base_url, self.EVENTS_ENDPOINT),
            json_payload=post_data,
        )

    async def pageview(self, customer_id: t.Union[str, int], page: str, **data) -> None:
        """Track a pageview for a given customer_id."""
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in pageview")

        post_data = {"type": "page", "name": page, "data": sanitize(data)}
        await self.send_request(
            "POST",
            join_url(self.base_url, self.CUSTOMER_EVENT_ENDPOINT.format(id=customer_id)),
            json_payload=post_data,
        )

    async def backfill(
        self,
        customer_id: t.Union[str, int],
        name: str,
        timestamp: t.Union[datetime, int],
        **data,
    ) -> None:
        """Backfill an event (track with timestamp) for a given customer_id."""
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in backfill")

        if isinstance(timestamp, datetime):
            timestamp = datetime_to_timestamp(timestamp)
        elif not isinstance(timestamp, int):
            raise AsyncCustomerIOError("{timestamp} is not a valid timestamp".format(timestamp=timestamp))

        post_data = {"name": name, "data": sanitize(data), "timestamp": timestamp}

        await self.send_request(
            "POST",
            join_url(self.base_url, self.CUSTOMER_EVENT_ENDPOINT.format(id=customer_id)),
            json_payload=post_data,
        )

    async def delete(self, customer_id: t.Union[str, int]) -> None:
        """
        Delete a customer profile.

        Deleting a customer removes them, and all of their information, from Customer.io.
        :param customer_id: the unique value representing a person. The values you use to identify a person may be an
            ``id``, ``email`` address, or the ``cio_id`` (when updating people), depending on your workspace settings.
            When you reference people by ``cio_id``, you must prefix the value with ``cio_``.
        """
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in delete")

        await self.send_request(
            "DELETE",
            join_url(self.base_url, self.CUSTOMER_ENDPOINT.format(id=customer_id)),
        )

    async def add_device(self, customer_id: t.Union[str, int], device_id: str, platform: str, **data) -> None:
        """
        Add or update a device to a customer profile.

        Customers can have more than one device.
        :param customer_id: the unique value representing a person. The values you use to identify a person may be an
            ``id``, ``email`` address, or the ``cio_id`` (when updating people), depending on your workspace settings.
            When you reference people by ``cio_id``, you must prefix the value with ``cio_``.
        :param device_id: the device token.
        :param platform: the device/messaging platform. Should be either **ios** or **android**
        """
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in add_device")

        if not device_id:
            raise AsyncCustomerIOError("device_id cannot be blank in add_device")

        if not platform:
            raise AsyncCustomerIOError("platform cannot be blank in add_device")

        data.update({"id": device_id, "platform": platform})
        payload = {"device": data}
        await self.send_request(
            "PUT",
            join_url(self.base_url, self.CUSTOMER_DEVICE_ENDPOINT).format(id=customer_id),
            json_payload=payload,
        )

    async def delete_device(self, customer_id: t.Union[str, int], device_id: str) -> None:
        """
        Delete a customer device.

        Delete a device from a customer profile.
        :param customer_id: the unique value representing a person. The values you use to identify a person may be an
            ``id``, ``email`` address, or the ``cio_id`` (when updating people), depending on your workspace settings.
            When you reference people by ``cio_id``, you must prefix the value with ``cio_``.
        :param device_id: the ID of the device you want to delete.
        """
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in delete_device")

        if not device_id:
            raise AsyncCustomerIOError("device_id cannot be blank in delete_device")

        await self.send_request(
            "DELETE",
            join_url(
                self.base_url,
                self.CUSTOMER_DEVICE_ENDPOINT.format(id=customer_id),
                self._url_encode(device_id),
            ),
        )

    async def suppress(self, customer_id: t.Union[str, int]) -> None:
        """
        Suppress a customer profile.

        Delete a customer profile and prevent the person's identifier(s) from being re-added to your workspace.
        :param customer_id: the unique value representing a person. The values you use to identify a person may be an
            ``id``, ``email`` address, or the ``cio_id`` (when updating people), depending on your workspace settings.
            When you reference people by ``cio_id``, you must prefix the value with ``cio_``.
        """
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in suppress")

        await self.send_request(
            "POST",
            join_url(self.base_url, self.CUSTOMER_SUPPRESS_ENDPOINT.format(id=customer_id)),
        )

    async def unsuppress(self, customer_id: t.Union[str, int]) -> None:
        """
        Unsuppress a customer profile.

        Unsuppressing a profile allows you to add the customer back to Customer.io. Unsuppressing a profile does not
        recreate the profile that you previously suppressed. Rather, it just makes the identifier available again.
        Identifying a person after unsuppressing them creates a new profile, with none of the history of the previously
        suppressed identifier.
        :param customer_id: the unique value representing a person. The values you use to identify a person may be an
            ``id``, ``email`` address, or the ``cio_id`` (when updating people), depending on your workspace settings.
            When you reference people by ``cio_id``, you must prefix the value with ``cio_``.
        """
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in unsuppress")

        await self.send_request(
            "POST",
            join_url(self.base_url, self.CUSTOMER_UNSUPRESS_ENDPOINT.format(id=customer_id)),
        )

    async def merge_customers(
        self,
        primary_id_type: str,
        primary_id: t.Union[str, int],
        secondary_id_type: str,
        secondary_id: t.Union[str, int],
    ) -> None:
        """
        Merge duplicate profiles.

        Merge two customer profiles together. The payload contains ``primary`` and ``secondary`` profile objects.
        The primary profile remains after the merge and the secondary is deleted. This operation is not reversible.
        :param primary_id_type: type of the identifiers, should be one of ``id``, ``email`` or ``cio
        :param primary_id: the person that you want to remain after the merge.
        :param secondary_id_type: type of the identifiers, should be one of ``id``, ``email`` or ``cio
        :param secondary_id: the person that you want to delete after the merge,
        """
        if not self._is_valid_id_type(primary_id_type):
            raise AsyncCustomerIOError("invalid primary id type")

        if not self._is_valid_id_type(secondary_id_type):
            raise AsyncCustomerIOError("invalid secondary id type")

        if not primary_id:
            raise AsyncCustomerIOError("primary customer_id cannot be blank")

        if not secondary_id:
            raise AsyncCustomerIOError("secondary customer_id cannot be blank")

        post_data = {
            "primary": {primary_id_type: primary_id},
            "secondary": {secondary_id_type: secondary_id},
        }
        await self.send_request(
            "POST",
            join_url(self.base_url, self.MERGE_CUSTOMERS_ENDPOINT),
            json_payload=post_data,
        )

    async def send_request(
        self,
        method: str,
        url: str,
        *,
        json_payload: Optional[t.Dict[str, t.Any]] = None,
        headers: Optional[t.Dict[str, str]] = None,
        auth: t.Optional[t.Tuple[str, str]] = None,
    ) -> t.Union[dict]:
        return await super().send_request(
            method,
            url,
            json_payload=json_payload,
            headers=headers,
            auth=(self.site_id, self.api_key),
        )
