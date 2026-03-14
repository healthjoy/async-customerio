"""
Customer endpoints for the Customer.io App API.

Provides methods to look up customers by email, search/filter customers,
retrieve customer attributes, activities, messages, segments, relationships,
and subscription preferences.
"""

from __future__ import annotations

import typing as t


if t.TYPE_CHECKING:
    from async_customerio.api._client import AsyncAPIClient


class Customers:
    """Namespace for customer-related App API methods.

    Accessed via ``AsyncAPIClient.customers`` property — not instantiated directly.
    """

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def get_by_email(self, email: str) -> dict:
        """Look up customers by email address.

        :param email: the email address to search for.
        :returns: dict with a ``results`` list of matching customers.

        `API docs <https://docs.customer.io/api/app/#operation/getPeopleEmail>`_
        """
        return await self._client._request("GET", "/customers", params={"email": email})

    async def search(
        self,
        filter: t.Dict[str, t.Any],
        *,
        start: t.Optional[str] = None,
        limit: t.Optional[int] = None,
    ) -> dict:
        """Search for customers using a filter.

        :param filter: an audience filter object. Can contain ``and``, ``or``, ``not``,
            ``segment``, and ``attribute`` conditions.
        :param start: pagination token from a previous response's ``next`` field.
        :param limit: maximum number of results per page.
        :returns: dict with ``identifiers`` and ``ids`` arrays.

        `API docs <https://docs.customer.io/api/app/#operation/getPeopleFilter>`_
        """
        params: t.Dict[str, t.Any] = {}
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit

        return await self._client._request(
            "POST",
            "/customers",
            json_payload={"filter": filter},
            params=params,
        )

    async def get_by_ids(self, ids: t.List[t.Union[str, int]]) -> dict:
        """List customers with their attributes and devices by IDs.

        :param ids: list of up to 100 customer IDs.
        :returns: dict with a ``customers`` array.

        `API docs <https://docs.customer.io/api/app/#operation/getPeopleById>`_
        """
        return await self._client._request(
            "POST",
            "/customers/attributes",
            json_payload={"ids": [str(i) for i in ids]},
        )

    async def get_attributes(
        self,
        customer_id: t.Union[str, int],
        *,
        id_type: t.Optional[str] = None,
    ) -> dict:
        """Look up a customer's attributes.

        :param customer_id: the customer identifier.
        :param id_type: the type of identifier — ``"id"``, ``"email"``, or ``"cio_id"``.
            Defaults to ``"id"`` on the server side.
        :returns: dict with a ``customer`` object containing attributes.

        `API docs <https://docs.customer.io/api/app/#operation/getPersonAttributes>`_
        """
        params: t.Dict[str, str] = {}
        if id_type is not None:
            params["id_type"] = id_type

        return await self._client._request("GET", f"/customers/{customer_id}/attributes", params=params)

    async def get_segments(
        self,
        customer_id: t.Union[str, int],
        *,
        id_type: t.Optional[str] = None,
    ) -> dict:
        """Look up a customer's segments.

        :param customer_id: the customer identifier.
        :param id_type: the type of identifier — ``"id"``, ``"email"``, or ``"cio_id"``.
        :returns: dict with a ``segments`` array.

        `API docs <https://docs.customer.io/api/app/#operation/getPersonSegments>`_
        """
        params: t.Dict[str, str] = {}
        if id_type is not None:
            params["id_type"] = id_type

        return await self._client._request("GET", f"/customers/{customer_id}/segments", params=params)

    async def get_messages(
        self,
        customer_id: t.Union[str, int],
        *,
        id_type: t.Optional[str] = None,
        start: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        start_ts: t.Optional[int] = None,
        end_ts: t.Optional[int] = None,
    ) -> dict:
        """Look up messages sent to a customer.

        :param customer_id: the customer identifier.
        :param id_type: the type of identifier — ``"id"``, ``"email"``, or ``"cio_id"``.
        :param start: pagination token.
        :param limit: maximum number of results per page.
        :param start_ts: beginning unix timestamp for the query.
        :param end_ts: ending unix timestamp for the query.
        :returns: dict with a ``messages`` array.

        `API docs <https://docs.customer.io/api/app/#operation/getPersonMessages>`_
        """
        params: t.Dict[str, t.Any] = {}
        if id_type is not None:
            params["id_type"] = id_type
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit
        if start_ts is not None:
            params["start_ts"] = start_ts
        if end_ts is not None:
            params["end_ts"] = end_ts

        return await self._client._request("GET", f"/customers/{customer_id}/messages", params=params)

    async def get_activities(
        self,
        customer_id: t.Union[str, int],
        *,
        id_type: t.Optional[str] = None,
        start: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        type: t.Optional[str] = None,
        name: t.Optional[str] = None,
    ) -> dict:
        """Look up a customer's activities.

        :param customer_id: the customer identifier.
        :param id_type: the type of identifier — ``"id"``, ``"email"``, or ``"cio_id"``.
        :param start: pagination token.
        :param limit: maximum number of results per page.
        :param type: the activity type to filter by (e.g. ``"event"``, ``"attribute_update"``).
        :param name: for ``event`` and ``attribute_update`` types, filter by name.
        :returns: dict with an ``activities`` array.

        `API docs <https://docs.customer.io/api/app/#operation/getPersonActivities>`_
        """
        params: t.Dict[str, t.Any] = {}
        if id_type is not None:
            params["id_type"] = id_type
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit
        if type is not None:
            params["type"] = type
        if name is not None:
            params["name"] = name

        return await self._client._request("GET", f"/customers/{customer_id}/activities", params=params)

    async def get_relationships(
        self,
        customer_id: t.Union[str, int],
        *,
        start: t.Optional[str] = None,
        limit: t.Optional[int] = None,
    ) -> dict:
        """Look up a customer's relationships to objects.

        :param customer_id: the customer identifier.
        :param start: pagination token.
        :param limit: maximum number of results per page.
        :returns: dict with a ``cio_relationships`` array.

        `API docs <https://docs.customer.io/api/app/#operation/getPersonRelationships>`_
        """
        params: t.Dict[str, t.Any] = {}
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit

        return await self._client._request("GET", f"/customers/{customer_id}/relationships", params=params)

    async def get_subscription_preferences(
        self,
        customer_id: t.Union[str, int],
        *,
        id_type: t.Optional[str] = None,
        language: t.Optional[str] = None,
    ) -> dict:
        """Look up a customer's subscription topic preferences.

        :param customer_id: the customer identifier.
        :param id_type: the type of identifier — ``"id"``, ``"email"``, or ``"cio_id"``.
        :param language: a language tag for translated content.
        :returns: dict with a ``customer`` object containing subscription preferences.

        `API docs <https://docs.customer.io/api/app/#operation/getPersonSubscriptionPreferences>`_
        """
        params: t.Dict[str, str] = {}
        if id_type is not None:
            params["id_type"] = id_type
        if language is not None:
            params["language"] = language

        return await self._client._request("GET", f"/customers/{customer_id}/subscription_preferences", params=params)
