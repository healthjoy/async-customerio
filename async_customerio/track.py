"""
Implements the async client that interacts with Customer.io's Track API version 1 and version 2
using Site ID and API Keys.
"""

import typing as t
from datetime import datetime
from enum import Enum
from typing import Optional
from urllib.parse import quote

from async_customerio._config import DEFAULT_REQUEST_TIMEOUT, RequestTimeout
from async_customerio.client_base import AsyncClientBase
from async_customerio.constants import CIOID, EMAIL, ID, IdentifierCIOID, IdentifierEMAIL, IdentifierID
from async_customerio.errors import AsyncCustomerIOError
from async_customerio.regions import Region, Regions
from async_customerio.utils import datetime_to_timestamp, join_url, sanitize


class Actions(str, Enum):
    """Defines type of action that can be performed for each type. Used in V2 API."""

    identify = "identify"
    delete = "delete"
    event = "event"
    screen = "screen"
    page = "page"
    add_relationships = "add_relationships"
    delete_relationships = "delete_relationships"
    add_device = "add_device"
    delete_device = "delete_device"
    merge = "merge"
    suppress = "suppress"
    unsuppress = "unsuppress"


class EntityPayload(t.TypedDict):
    identifiers: t.Union[IdentifierID, IdentifierEMAIL, IdentifierCIOID]
    type: str
    action: Actions
    # Extra attributes for the entity are allowed and can be passed as normal key-value pairs.
    # phone_number="123-456-7890", address="123 Main St" etc.


class AsyncCustomerIO(AsyncClientBase):
    """
    Async wrapper for communication with CustomerIO Track V1 and V2 APIs.

    Track API provides ways to send real-time customer data to defined Customer.io workspace.

    The API v2 has only two endpoints, but supports the majority of traditional v1 track operations
    and then some based on the type and action keys that you set in your request.

    You can use the ``/batch`` call to send multiple requests at the same time. Unlike the v1 API, you can also
    make requests affecting objects and deliveries. Objects are a grouping mechanism for people—like an account
    people belong to or an online course that they enroll in. Deliveries are events based on messages
    sent from Customer.io.
    """

    API_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    DEFAULT_API_PORT: int = 443
    DEFAULT_API_HOST: str = Regions.US.track_host

    # Track V1 endpoints
    CUSTOMER_ENDPOINT = "/customers/{id}"
    CUSTOMER_EVENT_ENDPOINT = "{customer_endpoint}/events".format(customer_endpoint=CUSTOMER_ENDPOINT)
    CUSTOMER_DEVICE_ENDPOINT = "{customer_endpoint}/devices".format(customer_endpoint=CUSTOMER_ENDPOINT)
    CUSTOMER_SUPPRESS_ENDPOINT = "{customer_endpoint}/suppress".format(customer_endpoint=CUSTOMER_ENDPOINT)
    CUSTOMER_UNSUPRESS_ENDPOINT = "{customer_endpoint}/unsuppress".format(customer_endpoint=CUSTOMER_ENDPOINT)
    EVENTS_ENDPOINT = "/events"
    MERGE_CUSTOMERS_ENDPOINT = "/merge_customers"

    # Track V2 endpoints
    ENTITY_ENDPOINT = "/entity"
    BATCH_ENDPOINT = "/batch"

    def __init__(
        self,
        site_id: str,
        api_key: str,
        host: Optional[str] = None,
        region: Region = Regions.US,
        port: Optional[int] = None,
        retries: int = 3,
        request_timeout: RequestTimeout = DEFAULT_REQUEST_TIMEOUT,
    ):
        if not isinstance(region, Region):
            raise AsyncCustomerIOError("invalid region provided")

        self.api_key: str = api_key
        self.site_id: str = site_id
        self.host = host or self.DEFAULT_API_HOST
        self.port = port or self.DEFAULT_API_PORT

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

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "PUT",
            join_url(base_url, self.CUSTOMER_ENDPOINT.format(id=identifier)),
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

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        post_data = {"name": name, "data": sanitize(data)}
        await self.send_request(
            "POST",
            join_url(base_url, self.CUSTOMER_EVENT_ENDPOINT.format(id=customer_id)),
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

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request("POST", join_url(base_url, self.EVENTS_ENDPOINT), json_payload=post_data)

    async def pageview(self, customer_id: t.Union[str, int], page: str, **data) -> None:
        """Track a pageview for a given customer_id."""
        if not customer_id:
            raise AsyncCustomerIOError("customer_id cannot be blank in pageview")

        post_data = {"type": "page", "name": page, "data": sanitize(data)}
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "POST",
            join_url(base_url, self.CUSTOMER_EVENT_ENDPOINT.format(id=customer_id)),
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
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "POST",
            join_url(base_url, self.CUSTOMER_EVENT_ENDPOINT.format(id=customer_id)),
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

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request("DELETE", join_url(base_url, self.CUSTOMER_ENDPOINT.format(id=customer_id)))

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
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "PUT",
            join_url(base_url, self.CUSTOMER_DEVICE_ENDPOINT).format(id=customer_id),
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

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "DELETE",
            join_url(
                base_url,
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

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request("POST", join_url(base_url, self.CUSTOMER_SUPPRESS_ENDPOINT.format(id=customer_id)))

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

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request("POST", join_url(base_url, self.CUSTOMER_UNSUPRESS_ENDPOINT.format(id=customer_id)))

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
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "POST",
            join_url(base_url, self.MERGE_CUSTOMERS_ENDPOINT),
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

    async def send_entity(
        self, identifiers: t.Union[IdentifierID, IdentifierEMAIL, IdentifierCIOID], type: str, action: Actions, **attrs
    ) -> None:
        """
        This endpoint lets you create, update, or delete a single person or object—including
        managing relationships between objects and people.

        :param identifiers: The person you want to perform an action for—one of either ``id``, ``email``, or ``cio_id``.
            Example: ``{"id": 123}`` or ``{"email": "john.doh@domain.com"}``
        :param entity_type: the type of entity you are working with. Should be either ``person`` or ``object``.
        :param action: the action to perform. Should be one of the values defined in ``Actions`` enum.
        :param attrs: additional attributes to set on the entity.
        :return: None if successful. Otherwise raises ``AsyncCustomerIOError``.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in send_entity")

        post_data = {
            "type": type,
            "action": action.value,
            "identifiers": identifiers,
            "attributes": attrs,
        }
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_V2_PREFIX)
        await self.send_request("POST", join_url(base_url, self.ENTITY_ENDPOINT), json_payload=post_data)

    async def send_batch(self, payload: t.List[EntityPayload]) -> None:
        """
        This endpoint lets batch requests for different people and objects in a single request. Each object in array
        represents an individual "entity" operation—it represents a change for a person, an object, or a delivery.

        You can mix types in this request; you are not limited to a batch containing only objects or only people.
        An "object" is a non-person entity that you want to associate with one or more people—like a company,
        an educational course that people enroll in, etc.

        The batch request must be smaller than 500kb. Each of the requests within the batch must also be 32kb
        or smaller.

        :param payload: list of entity payloads.
        :return: None if successful. Otherwise raises ``AsyncCustomerIOError``.
        """

        post_data = {"batch": payload}
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_V2_PREFIX)
        await self.send_request("POST", join_url(base_url, self.BATCH_ENDPOINT), json_payload=post_data)
