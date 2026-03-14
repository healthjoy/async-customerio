"""
Segment endpoints for the Customer.io App API.

Provides methods to list, create, get, delete segments, and look up
segment membership, customer count, and dependencies.
"""

from __future__ import annotations

import typing as t


if t.TYPE_CHECKING:
    from async_customerio.api._client import AsyncAPIClient


class Segments:
    """Namespace for segment-related App API methods.

    Accessed via ``AsyncAPIClient.segments`` property — not instantiated directly.
    """

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def list(self) -> dict:
        """List all segments in the workspace.

        :returns: dict with a ``segments`` array.

        `API docs <https://docs.customer.io/api/app/#operation/getSegments>`_
        """
        return await self._client._request("GET", "/segments")

    async def get(self, segment_id: int) -> dict:
        """Get a single segment by ID.

        :param segment_id: the segment identifier.
        :returns: dict with a ``segment`` object.

        `API docs <https://docs.customer.io/api/app/#operation/getSegment>`_
        """
        return await self._client._request("GET", f"/segments/{segment_id}")

    async def create(self, name: str, *, description: t.Optional[str] = None) -> dict:
        """Create a manual segment.

        :param name: the name of the segment.
        :param description: an optional description for the segment.
        :returns: dict with the created ``segment`` object.

        `API docs <https://docs.customer.io/api/app/#operation/createSegment>`_
        """
        segment: t.Dict[str, str] = {"name": name}
        if description is not None:
            segment["description"] = description

        return await self._client._request(
            "POST",
            "/segments",
            json_payload={"segment": segment},
        )

    async def delete(self, segment_id: int) -> dict:
        """Delete a segment.

        :param segment_id: the segment identifier.

        `API docs <https://docs.customer.io/api/app/#operation/deleteSegment>`_
        """
        return await self._client._request("DELETE", f"/segments/{segment_id}")

    async def get_customer_count(self, segment_id: int) -> dict:
        """Get the number of customers in a segment.

        :param segment_id: the segment identifier.
        :returns: dict with a ``count`` value.

        `API docs <https://docs.customer.io/api/app/#operation/getSegmentCustomerCount>`_
        """
        return await self._client._request("GET", f"/segments/{segment_id}/customer_count")

    async def get_membership(
        self,
        segment_id: int,
        *,
        start: t.Optional[str] = None,
        limit: t.Optional[int] = None,
    ) -> dict:
        """List customers in a segment.

        :param segment_id: the segment identifier.
        :param start: pagination token.
        :param limit: maximum number of results per page.
        :returns: dict with a list of customer identifiers.

        `API docs <https://docs.customer.io/api/app/#operation/getSegmentMembership>`_
        """
        params: t.Dict[str, t.Any] = {}
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit

        return await self._client._request("GET", f"/segments/{segment_id}/membership", params=params)

    async def get_used_by(self, segment_id: int) -> dict:
        """Get a segment's dependencies (campaigns, broadcasts, etc. that use it).

        :param segment_id: the segment identifier.
        :returns: dict describing what uses this segment.

        `API docs <https://docs.customer.io/api/app/#operation/getSegmentDependencies>`_
        """
        return await self._client._request("GET", f"/segments/{segment_id}/used_by")
