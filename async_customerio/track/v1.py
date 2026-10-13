"""
Implements the async client that interacts with Customer.io's Track API version 1
using Site ID and API Keys.

For the v2 Track API, see :mod:`async_customerio.track.v2` (accessed via the ``.v2`` property).
"""

from __future__ import annotations

import typing as t
from datetime import datetime
from typing import Optional
from urllib.parse import quote

from async_customerio._config import DEFAULT_REQUEST_LIMITS, DEFAULT_REQUEST_TIMEOUT, RequestLimits, RequestTimeout
from async_customerio.client_base import AsyncClientBase
from async_customerio.constants import CIOID, EMAIL, ID, IdentifierCIOID, IdentifierEMAIL, IdentifierID
from async_customerio.errors import AsyncCustomerIOError
from async_customerio.regions import Region, Regions
from async_customerio.retry import RetryStrategy
from async_customerio.track.v2 import Actions, EntityPayload, TrackAPIV2  # noqa: F401 - re-export for backwards compat
from async_customerio.utils import datetime_to_timestamp, join_url, sanitize, stringify_list


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
    SEGMENT_ADD_CUSTOMERS_ENDPOINT = "/segments/{segment_id}/add_customers"
    SEGMENT_REMOVE_CUSTOMERS_ENDPOINT = "/segments/{segment_id}/remove_customers"
    REGION_ENDPOINT = "/accounts/region"
    FORM_SUBMIT_ENDPOINT = "/forms/{form_id}/submit"
    METRICS_ENDPOINT = "/metrics"
    PUSH_METRICS_ENDPOINT = "/push/events"
    # Served from the host root, outside of the ``/api/v1`` prefix.
    UNSUBSCRIBE_ENDPOINT = "/unsubscribe/{delivery_id}"

    MAX_SEGMENT_CUSTOMER_IDS = 1000

    def __init__(
        self,
        site_id: str,
        api_key: str,
        host: Optional[str] = None,
        region: Region = Regions.US,
        port: Optional[int] = None,
        retries: int = 3,
        request_timeout: RequestTimeout = DEFAULT_REQUEST_TIMEOUT,
        request_limits: RequestLimits = DEFAULT_REQUEST_LIMITS,
        user_agent: Optional[str] = None,
        retry_strategy: Optional[RetryStrategy] = None,
    ):
        if not isinstance(region, Region):
            raise AsyncCustomerIOError("invalid region provided")

        self.api_key: str = api_key
        self.site_id: str = site_id
        self.host = host or self.DEFAULT_API_HOST
        self.port = port or self.DEFAULT_API_PORT

        super().__init__(
            retries=retries,
            request_timeout=request_timeout,
            request_limits=request_limits,
            user_agent=user_agent,
            retry_strategy=retry_strategy,
        )

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
            join_url(base_url, self.CUSTOMER_DEVICE_ENDPOINT.format(id=customer_id)),
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

    async def unsubscribe(self, delivery_id: str) -> None:
        """
        Custom unsubscribe handling.

        Set a person's ``unsubscribed`` attribute to ``true`` and attribute the unsubscribe to the given delivery.
        Use it to back a custom unsubscribe page. It does not update custom subscription-center attributes; use
        :meth:`identify` for those.
        :param delivery_id: the delivery the person unsubscribed from.
        """
        if not delivery_id:
            raise AsyncCustomerIOError("delivery_id cannot be blank in unsubscribe")

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix="")
        await self.send_request(
            "POST",
            join_url(base_url, self.UNSUBSCRIBE_ENDPOINT.format(delivery_id=delivery_id)),
            json_payload={"unsubscribe": True},
        )

    async def report_metric(
        self,
        delivery_id: str,
        metric: str,
        *,
        href: Optional[str] = None,
        reason: Optional[str] = None,
        recipient: Optional[str] = None,
        timestamp: t.Optional[t.Union[datetime, int]] = None,
    ) -> None:
        """
        Report a delivery metric for any channel (email, push, SMS, in-app, Slack, webhook).

        Use it for channels that aren't native to Customer.io or don't rely on its SDKs.
        :param delivery_id: the ``CIO-Delivery-ID`` of the message the metric belongs to.
        :param metric: the metric to report, e.g. ``delivered``, ``opened``, ``clicked``, ``converted``, ``bounced``.
            Accepted values depend on the channel.
        :param href: for ``clicked`` metrics, the link the recipient clicked.
        :param reason: for failure metrics (like ``bounced``), the reason for the failure.
        :param recipient: the email, ID or device ID of the recipient, depending on the channel.
        :param timestamp: when the metric occurred; datetimes are converted to unix timestamps.
        """
        if not delivery_id:
            raise AsyncCustomerIOError("delivery_id cannot be blank in report_metric")

        if not metric:
            raise AsyncCustomerIOError("metric cannot be blank in report_metric")

        optional_fields = {"href": href, "reason": reason, "recipient": recipient, "timestamp": timestamp}
        post_data: t.Dict[str, t.Any] = {"delivery_id": delivery_id, "metric": metric}
        post_data.update({key: value for key, value in optional_fields.items() if value is not None})
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request("POST", join_url(base_url, self.METRICS_ENDPOINT), json_payload=post_data)

    async def report_push_metric(
        self,
        delivery_id: str,
        device_id: str,
        event: str,
        *,
        timestamp: t.Optional[t.Union[datetime, int]] = None,
    ) -> None:
        """
        Report a device-side push metric.

        Customer.io keeps this endpoint working but recommends :meth:`report_metric`, which covers every channel.
        :param delivery_id: the ``CIO-Delivery-ID`` from the push notification.
        :param device_id: the ``CIO-Delivery-Token`` of the device that received the notification.
        :param event: the push metric, one of ``opened``, ``converted`` or ``delivered``.
        :param timestamp: when the event occurred; datetimes are converted to unix timestamps.
        """
        if not delivery_id:
            raise AsyncCustomerIOError("delivery_id cannot be blank in report_push_metric")

        if not device_id:
            raise AsyncCustomerIOError("device_id cannot be blank in report_push_metric")

        if not event:
            raise AsyncCustomerIOError("event cannot be blank in report_push_metric")

        post_data: t.Dict[str, t.Any] = {"delivery_id": delivery_id, "device_id": device_id, "event": event}
        if timestamp is not None:
            post_data["timestamp"] = timestamp

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request("POST", join_url(base_url, self.PUSH_METRICS_ENDPOINT), json_payload=post_data)

    async def add_to_segment(
        self,
        segment_id: int,
        customer_ids: t.List[t.Union[str, int]],
        id_type: Optional[str] = None,
    ) -> None:
        """
        Add people to a manual segment.

        The segment must already exist; data-driven segments cannot be modified through the API.
        :param segment_id: the ID of the manual segment.
        :param customer_ids: up to 1000 identifiers of people to add. All of them must be of ``id_type``;
            Customer.io ignores values that don't match it.
        :param id_type: the type of ``customer_ids`` — ``id``, ``email`` or ``cio_id``. Defaults to ``id``
            on the server side.
        """
        await self._update_segment_membership(
            self.SEGMENT_ADD_CUSTOMERS_ENDPOINT, segment_id, customer_ids, id_type, "add_to_segment"
        )

    async def remove_from_segment(
        self,
        segment_id: int,
        customer_ids: t.List[t.Union[str, int]],
        id_type: Optional[str] = None,
    ) -> None:
        """
        Remove people from a manual segment.

        Data-driven segments cannot be modified through the API.
        :param segment_id: the ID of the manual segment.
        :param customer_ids: up to 1000 identifiers of people to remove. All of them must be of ``id_type``.
        :param id_type: the type of ``customer_ids`` — ``id``, ``email`` or ``cio_id``. Defaults to ``id``
            on the server side.
        """
        await self._update_segment_membership(
            self.SEGMENT_REMOVE_CUSTOMERS_ENDPOINT, segment_id, customer_ids, id_type, "remove_from_segment"
        )

    async def _update_segment_membership(
        self,
        endpoint: str,
        segment_id: int,
        customer_ids: t.List[t.Union[str, int]],
        id_type: Optional[str],
        method_name: str,
    ) -> None:
        if not segment_id:
            raise AsyncCustomerIOError("segment_id cannot be blank in {0}".format(method_name))

        if not customer_ids:
            raise AsyncCustomerIOError("customer_ids cannot be blank in {0}".format(method_name))

        if len(customer_ids) > self.MAX_SEGMENT_CUSTOMER_IDS:
            raise AsyncCustomerIOError(
                "customer_ids cannot exceed {0} items in {1}".format(self.MAX_SEGMENT_CUSTOMER_IDS, method_name)
            )

        if id_type is not None and not self._is_valid_id_type(id_type):
            raise AsyncCustomerIOError("invalid id_type in {0}".format(method_name))

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "POST",
            join_url(
                base_url,
                endpoint.format(segment_id=segment_id),
                params={"id_type": id_type} if id_type is not None else None,
            ),
            json_payload={"ids": stringify_list(customer_ids)},
        )

    async def get_region(self) -> dict:
        """
        Find the region of the account that the configured credentials belong to.

        Works against either regional Track host. Also useful as a cheap credentials check.
        :return: dict with ``url`` (the Track API URL to use), ``region`` (``us`` or ``eu``) and ``environment_id``
            (the workspace the credentials are valid for).
        """
        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        return t.cast(dict, await self.send_request("GET", join_url(base_url, self.REGION_ENDPOINT)))

    async def submit_form(self, form_id: str, **data) -> None:
        """
        Submit a form response.

        If Customer.io does not recognize ``form_id``, it creates a new form connection. If the respondent does not
        exist yet, they are created.
        :param form_id: an identifier of your choosing; submissions with the same ID belong to the same form.
        :param data: form fields and their values, which Customer.io requires to be strings. Must include exactly
            one of ``id`` or ``email`` (or a field mapped to one of them) to identify the respondent.
        """
        if not form_id:
            raise AsyncCustomerIOError("form_id cannot be blank in submit_form")

        if not data:
            raise AsyncCustomerIOError("data cannot be blank in submit_form")

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_PREFIX)
        await self.send_request(
            "POST",
            join_url(base_url, self.FORM_SUBMIT_ENDPOINT.format(form_id=form_id)),
            json_payload={"data": data},
        )

    @property
    def v2(self) -> TrackAPIV2:
        """Access the v2 Track API client.

        Returns a :class:`~async_customerio.track.v2.TrackAPIV2` instance that shares
        the same HTTP connection, credentials and retry configuration.

        Usage::

            async with AsyncCustomerIO(site_id="...", api_key="...") as cio:
                await cio.v2.identify_person({"id": 123}, name="John")
        """
        if not hasattr(self, "_v2"):
            self._v2 = TrackAPIV2(self)
        return self._v2

    async def send_request(
        self,
        method: str,
        url: str,
        *,
        json_payload: Optional[t.Dict[str, t.Any]] = None,
        headers: Optional[t.Dict[str, str]] = None,
        auth: t.Optional[t.Tuple[str, str]] = None,
    ) -> t.Union[dict, str]:
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
        """Send a single v2 entity operation.

        .. deprecated::
            Use the convenience methods on :attr:`v2` instead (e.g. ``cio.v2.identify_person(...)``).

        :param identifiers: The person you want to perform an action for—one of either ``id``, ``email``, or ``cio_id``.
            Example: ``{"id": 123}`` or ``{"email": "john.doh@domain.com"}``
        :param type: the type of entity you are working with. Should be either ``person`` or ``object``.
        :param action: the action to perform. Should be one of the values defined in ``Actions`` enum.
        :param attrs: additional attributes to set on the entity.
        :return: None if successful. Otherwise raises ``AsyncCustomerIOError``.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in send_entity")

        base_url = self.setup_base_url(host=self.host, port=self.port, prefix=self.API_V2_PREFIX)
        await self.send_request(
            "POST",
            join_url(base_url, TrackAPIV2.ENTITY_ENDPOINT),
            json_payload={
                "type": type,
                "action": action.value,
                "identifiers": identifiers,
                "attributes": attrs,
            },
        )

    async def send_batch(self, payload: t.List[EntityPayload]) -> dict:
        """Send a batch of v2 entity operations.

        .. deprecated::
            Use ``cio.v2.send_batch(...)`` instead.

        :param payload: list of entity payloads.
        :return: parsed JSON response body.
        """
        return await self.v2.send_batch(payload)
