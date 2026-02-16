"""
Implements the async client that interacts with Customer.io's Track API version 2.

The v2 API has two endpoints — ``/entity`` and ``/batch`` — and determines what to do
based on the ``type`` and ``action`` keys in the request payload.  Entity types are
``person`` and ``object``; actions include identify, delete, event, page, screen,
device management, relationships, merge, suppress and unsuppress.

This module is accessed through the ``AsyncCustomerIO.v2`` property so that the
underlying HTTP connection, credentials and retry logic are shared with the v1 client.
"""

from __future__ import annotations

import typing as t
from enum import Enum

from async_customerio.constants import ObjectIdentifiers, PersonIdentifiers
from async_customerio.errors import AsyncCustomerIOError
from async_customerio.utils import join_url, sanitize


if t.TYPE_CHECKING:
    from async_customerio.track import AsyncCustomerIO


class Actions(str, Enum):
    """Defines the type of action that can be performed for each entity type."""

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


# ---------------------------------------------------------------------------
# EntityPayload TypedDict (two-class pattern for required/optional fields)
# ---------------------------------------------------------------------------


class _EntityPayloadRequired(t.TypedDict):
    identifiers: t.Union[PersonIdentifiers, ObjectIdentifiers]
    type: str
    action: str


class EntityPayload(_EntityPayloadRequired, total=False):
    """Payload for a single v2 entity operation.  Used as items in ``send_batch``."""

    attributes: t.Dict[str, t.Any]
    name: str
    device: t.Dict[str, t.Any]
    cio_relationships: t.List[t.Dict[str, t.Any]]


# ---------------------------------------------------------------------------
# TrackAPIV2
# ---------------------------------------------------------------------------


class TrackAPIV2:
    """High-level async client for Customer.io Track API v2.

    Accessed via the ``AsyncCustomerIO.v2`` property — not instantiated directly.
    All HTTP requests are delegated to the parent ``AsyncCustomerIO`` instance so
    that the connection pool, credentials and retry configuration are shared.

    The API v2 has only two endpoints, but supports the majority of traditional v1 track
    operations and then some based on the ``type`` and ``action`` keys you set in your request.

    You can use the ``/batch`` call to send multiple requests at the same time.  Unlike the
    v1 API, you can also make requests affecting *objects* and *deliveries*.  Objects are a
    grouping mechanism for people — like an account people belong to or an online course that
    they enroll in.
    """

    ENTITY_ENDPOINT = "/entity"
    BATCH_ENDPOINT = "/batch"

    def __init__(self, client: AsyncCustomerIO) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _base_url(self) -> str:
        return self._client.setup_base_url(
            host=self._client.host,
            port=self._client.port,
            prefix=self._client.API_V2_PREFIX,
        )

    async def send_entity(self, payload: t.Dict[str, t.Any]) -> None:
        """POST a fully-formed payload to ``/api/v2/entity``."""
        await self._client.send_request(
            "POST",
            join_url(self._base_url(), self.ENTITY_ENDPOINT),
            json_payload=payload,
        )

    # ------------------------------------------------------------------
    # Batch
    # ------------------------------------------------------------------

    async def send_batch(self, payload: t.List[EntityPayload]) -> None:
        """Send a batch of entity operations in a single request.

        Each item in *payload* represents an individual entity operation — it describes a
        change for a person, an object or a delivery.  You can mix types in one batch.

        The batch request must be smaller than **500 KB**.  Each individual item must be
        **32 KB** or smaller.

        :param payload: list of entity payloads.
        :return: ``None`` if successful.  Otherwise raises ``AsyncCustomerIOError``.
        """
        await self._client.send_request(
            "POST",
            join_url(self._base_url(), self.BATCH_ENDPOINT),
            json_payload={"batch": payload},
        )

    # ==================================================================
    # Person operations
    # ==================================================================

    async def identify_person(
        self,
        identifiers: PersonIdentifiers,
        **attrs: t.Any,
    ) -> None:
        """Identify (create or update) a person.

        :param identifiers: one of ``{"id": ...}``, ``{"email": ...}`` or ``{"cio_id": ...}``.
        :param attrs: additional attributes to set on the person profile.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in identify_person")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.identify.value,
                "identifiers": identifiers,
                "attributes": sanitize(attrs) if attrs else {},
            }
        )

    async def delete_person(self, identifiers: PersonIdentifiers) -> None:
        """Delete a person profile.

        :param identifiers: person identifier dict.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in delete_person")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.delete.value,
                "identifiers": identifiers,
            }
        )

    async def track_person_event(
        self,
        identifiers: PersonIdentifiers,
        name: str,
        **attrs: t.Any,
    ) -> None:
        """Track an event for a person.

        :param identifiers: person identifier dict.
        :param name: event name — this is how you reference the event in campaigns or segments.
        :param attrs: event data attributes.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in track_person_event")
        if not name:
            raise AsyncCustomerIOError("name cannot be blank in track_person_event")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.event.value,
                "identifiers": identifiers,
                "name": name,
                "attributes": sanitize(attrs) if attrs else {},
            }
        )

    async def person_pageview(
        self,
        identifiers: PersonIdentifiers,
        name: str,
        **attrs: t.Any,
    ) -> None:
        """Track a page view for a person.

        :param identifiers: person identifier dict.
        :param name: the page URL.
        :param attrs: additional page view data.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in person_pageview")
        if not name:
            raise AsyncCustomerIOError("name cannot be blank in person_pageview")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.page.value,
                "identifiers": identifiers,
                "name": name,
                "attributes": sanitize(attrs) if attrs else {},
            }
        )

    async def person_screen(
        self,
        identifiers: PersonIdentifiers,
        name: str,
        **attrs: t.Any,
    ) -> None:
        """Track a screen view for a person (mobile).

        :param identifiers: person identifier dict.
        :param name: the screen name.
        :param attrs: additional screen view data.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in person_screen")
        if not name:
            raise AsyncCustomerIOError("name cannot be blank in person_screen")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.screen.value,
                "identifiers": identifiers,
                "name": name,
                "attributes": sanitize(attrs) if attrs else {},
            }
        )

    async def add_person_device(
        self,
        identifiers: PersonIdentifiers,
        device_id: str,
        platform: str,
        **device_attrs: t.Any,
    ) -> None:
        """Add or update a device for a person.

        :param identifiers: person identifier dict.
        :param device_id: the device token.
        :param platform: the device platform — ``"ios"`` or ``"android"``.
        :param device_attrs: additional device attributes (e.g. ``last_used``).
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in add_person_device")
        if not device_id:
            raise AsyncCustomerIOError("device_id cannot be blank in add_person_device")
        if not platform:
            raise AsyncCustomerIOError("platform cannot be blank in add_person_device")

        device_data: t.Dict[str, t.Any] = {"id": device_id, "platform": platform}
        device_data.update(device_attrs)
        await self.send_entity(
            {
                "type": "person",
                "action": Actions.add_device.value,
                "identifiers": identifiers,
                "device": device_data,
            }
        )

    async def delete_person_device(
        self,
        identifiers: PersonIdentifiers,
        device_id: str,
    ) -> None:
        """Delete a device from a person.

        :param identifiers: person identifier dict.
        :param device_id: the device token to remove.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in delete_person_device")
        if not device_id:
            raise AsyncCustomerIOError("device_id cannot be blank in delete_person_device")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.delete_device.value,
                "identifiers": identifiers,
                "device": {"id": device_id},
            }
        )

    async def suppress_person(self, identifiers: PersonIdentifiers) -> None:
        """Suppress a person.

        Deletes the person profile and prevents the identifier(s) from being re-added.

        :param identifiers: person identifier dict.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in suppress_person")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.suppress.value,
                "identifiers": identifiers,
            }
        )

    async def unsuppress_person(self, identifiers: PersonIdentifiers) -> None:
        """Unsuppress a person.

        Makes the identifier available again so that a new profile can be created.

        :param identifiers: person identifier dict.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in unsuppress_person")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.unsuppress.value,
                "identifiers": identifiers,
            }
        )

    async def merge_persons(
        self,
        primary: PersonIdentifiers,
        secondary: PersonIdentifiers,
    ) -> None:
        """Merge two person profiles.

        The *primary* profile remains after the merge; the *secondary* is deleted.
        This operation is **not reversible**.

        :param primary: identifiers for the person to keep.
        :param secondary: identifiers for the person to merge and delete.
        """
        if not primary:
            raise AsyncCustomerIOError("primary identifiers cannot be blank in merge_persons")
        if not secondary:
            raise AsyncCustomerIOError("secondary identifiers cannot be blank in merge_persons")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.merge.value,
                "identifiers": primary,
                "cio_relationships": [{"identifiers": secondary}],
            }
        )

    async def add_person_relationships(
        self,
        identifiers: PersonIdentifiers,
        relationships: t.List[t.Dict[str, t.Any]],
    ) -> None:
        """Add relationships between a person and one or more objects.

        :param identifiers: person identifier dict.
        :param relationships: list of relationship dicts — each must contain an ``"identifiers"``
            key with ``{"object_type_id": ..., "object_id": ...}``.

        Example::

            await cio.v2.add_person_relationships(
                identifiers={"id": 123},
                relationships=[{"identifiers": {"object_type_id": "1", "object_id": "acme"}}],
            )
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in add_person_relationships")
        if not relationships:
            raise AsyncCustomerIOError("relationships cannot be blank in add_person_relationships")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.add_relationships.value,
                "identifiers": identifiers,
                "cio_relationships": relationships,
            }
        )

    async def delete_person_relationships(
        self,
        identifiers: PersonIdentifiers,
        relationships: t.List[t.Dict[str, t.Any]],
    ) -> None:
        """Delete relationships between a person and one or more objects.

        :param identifiers: person identifier dict.
        :param relationships: list of relationship dicts to remove.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in delete_person_relationships")
        if not relationships:
            raise AsyncCustomerIOError("relationships cannot be blank in delete_person_relationships")

        await self.send_entity(
            {
                "type": "person",
                "action": Actions.delete_relationships.value,
                "identifiers": identifiers,
                "cio_relationships": relationships,
            }
        )

    # ==================================================================
    # Object operations
    # ==================================================================

    async def identify_object(
        self,
        identifiers: ObjectIdentifiers,
        **attrs: t.Any,
    ) -> None:
        """Identify (create or update) an object.

        :param identifiers: ``{"object_type_id": ..., "object_id": ...}`` or ``{"cio_object_id": ...}``.
        :param attrs: additional attributes to set on the object.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in identify_object")

        await self.send_entity(
            {
                "type": "object",
                "action": Actions.identify.value,
                "identifiers": identifiers,
                "attributes": sanitize(attrs) if attrs else {},
            }
        )

    async def delete_object(self, identifiers: ObjectIdentifiers) -> None:
        """Delete an object.

        :param identifiers: object identifier dict.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in delete_object")

        await self.send_entity(
            {
                "type": "object",
                "action": Actions.delete.value,
                "identifiers": identifiers,
            }
        )

    async def track_object_event(
        self,
        identifiers: ObjectIdentifiers,
        name: str,
        **attrs: t.Any,
    ) -> None:
        """Track an event on an object.

        :param identifiers: object identifier dict.
        :param name: the event name.
        :param attrs: event data attributes.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in track_object_event")
        if not name:
            raise AsyncCustomerIOError("name cannot be blank in track_object_event")

        await self.send_entity(
            {
                "type": "object",
                "action": Actions.event.value,
                "identifiers": identifiers,
                "name": name,
                "attributes": sanitize(attrs) if attrs else {},
            }
        )

    async def add_object_relationships(
        self,
        identifiers: ObjectIdentifiers,
        relationships: t.List[t.Dict[str, t.Any]],
    ) -> None:
        """Add relationships between an object and one or more people.

        :param identifiers: object identifier dict.
        :param relationships: list of relationship dicts — each must contain an ``"identifiers"``
            key with person identifiers (``{"id": ...}``, ``{"email": ...}`` or ``{"cio_id": ...}``).
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in add_object_relationships")
        if not relationships:
            raise AsyncCustomerIOError("relationships cannot be blank in add_object_relationships")

        await self.send_entity(
            {
                "type": "object",
                "action": Actions.add_relationships.value,
                "identifiers": identifiers,
                "cio_relationships": relationships,
            }
        )

    async def delete_object_relationships(
        self,
        identifiers: ObjectIdentifiers,
        relationships: t.List[t.Dict[str, t.Any]],
    ) -> None:
        """Delete relationships between an object and one or more people.

        :param identifiers: object identifier dict.
        :param relationships: list of relationship dicts to remove.
        """
        if not identifiers:
            raise AsyncCustomerIOError("identifiers cannot be blank in delete_object_relationships")
        if not relationships:
            raise AsyncCustomerIOError("relationships cannot be blank in delete_object_relationships")

        await self.send_entity(
            {
                "type": "object",
                "action": Actions.delete_relationships.value,
                "identifiers": identifiers,
                "cio_relationships": relationships,
            }
        )
