"""
Transactional message endpoints for the Customer.io App API.

Provides methods to list transactional messages, read and update their content
variants and translations, and retrieve metrics, link metrics, and deliveries.
"""

from __future__ import annotations

import typing as t


if t.TYPE_CHECKING:
    from async_customerio.api._client import AsyncAPIClient


def _build_content_payload(
    body: t.Optional[str],
    body_amp: t.Optional[str],
    from_id: t.Optional[int],
    headers: t.Optional[t.List[t.Dict[str, str]]],
    preheader_text: t.Optional[str],
    recipient: t.Optional[str],
    reply_to_id: t.Optional[int],
    subject: t.Optional[str],
) -> t.Dict[str, t.Any]:
    """Build an update payload, omitting fields that were not provided."""
    candidates: t.Dict[str, t.Any] = {
        "body": body,
        "body_amp": body_amp,
        "from_id": from_id,
        "headers": headers,
        "preheader_text": preheader_text,
        "recipient": recipient,
        "reply_to_id": reply_to_id,
        "subject": subject,
    }
    return {key: value for key, value in candidates.items() if value is not None}


class Transactional:
    """Namespace for transactional message App API methods.

    Accessed via ``AsyncAPIClient.transactional`` property — not instantiated directly.
    """

    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def list(self) -> dict:
        """List the transactional messages in the workspace.

        Returns the transactional IDs used to trigger individual deliveries — not
        the deliveries themselves. Use :meth:`get_deliveries` for those.

        :returns: dict with a ``messages`` array.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/listTransactional/>`_
        """
        return await self._client._request("GET", "/transactional")

    async def get(self, transactional_id: int) -> dict:
        """Get a single transactional message.

        :param transactional_id: the transactional message identifier.
        :returns: dict with a ``message`` object.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/getTransactional/>`_
        """
        return await self._client._request("GET", f"/transactional/{transactional_id}")

    async def list_variants(self, transactional_id: int) -> dict:
        """List the content variants of a transactional message, one per language.

        :param transactional_id: the transactional message identifier.
        :returns: dict with a ``contents`` array.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/listTransactionalVariants/>`_
        """
        return await self._client._request("GET", f"/transactional/{transactional_id}/contents")

    async def update_content(
        self,
        transactional_id: int,
        content_id: int,
        *,
        body: t.Optional[str] = None,
        body_amp: t.Optional[str] = None,
        from_id: t.Optional[int] = None,
        headers: t.Optional[t.List[t.Dict[str, str]]] = None,
        preheader_text: t.Optional[str] = None,
        recipient: t.Optional[str] = None,
        reply_to_id: t.Optional[int] = None,
        subject: t.Optional[str] = None,
    ) -> dict:
        """Update the content of a transactional message.

        This fully overwrites the content variant, and the updated content is used
        for any future ``/v1/send/email`` request. Content built with Design Studio
        cannot be managed through this endpoint.

        Fields left as ``None`` are omitted from the request.

        :param transactional_id: the transactional message identifier.
        :param content_id: the content variant identifier.
        :param body: the body of the transactional message.
        :param body_amp: AMP-enabled content used when the client supports it.
        :param from_id: the identifier of the "from" sender address.
        :param headers: headers to add or update, as ``{"name": ..., "value": ...}`` dicts.
        :param preheader_text: the preview text shown next to the subject line.
        :param recipient: the recipient address, e.g. ``"{{customer.email}}"``.
        :param reply_to_id: the identifier of the reply-to address.
        :param subject: the subject line.
        :returns: dict with the updated ``content``.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/updateTransactional/>`_
        """
        payload = _build_content_payload(
            body, body_amp, from_id, headers, preheader_text, recipient, reply_to_id, subject
        )
        return await self._client._request(
            "PUT",
            f"/transactional/{transactional_id}/content/{content_id}",
            json_payload=payload,
        )

    async def get_variant(self, transactional_id: int, language: str) -> dict:
        """Get a translation of a transactional message, including its content.

        :param transactional_id: the transactional message identifier.
        :param language: the language tag of the variant. An empty string selects
            the default language.
        :returns: dict with a ``content`` array.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/getTransactionalVariant/>`_
        """
        return await self._client._request("GET", f"/transactional/{transactional_id}/language/{language}")

    async def update_variant(
        self,
        transactional_id: int,
        language: str,
        *,
        body: t.Optional[str] = None,
        body_amp: t.Optional[str] = None,
        from_id: t.Optional[int] = None,
        headers: t.Optional[t.List[t.Dict[str, str]]] = None,
        preheader_text: t.Optional[str] = None,
        recipient: t.Optional[str] = None,
        reply_to_id: t.Optional[int] = None,
        subject: t.Optional[str] = None,
    ) -> dict:
        """Update a translation of a transactional message.

        This fully overwrites the specified language variant. Content built with
        Design Studio cannot be managed through this endpoint.

        Fields left as ``None`` are omitted from the request.

        :param transactional_id: the transactional message identifier.
        :param language: the language tag of the variant. An empty string selects
            the default language.
        :param body: the body of the transactional message.
        :param body_amp: AMP-enabled content used when the client supports it.
        :param from_id: the identifier of the "from" sender address.
        :param headers: headers to add or update, as ``{"name": ..., "value": ...}`` dicts.
        :param preheader_text: the preview text shown next to the subject line.
        :param recipient: the recipient address, e.g. ``"{{customer.email}}"``.
        :param reply_to_id: the identifier of the reply-to address.
        :param subject: the subject line.
        :returns: dict with the updated ``content``.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/updateTransactionalVariant/>`_
        """
        payload = _build_content_payload(
            body, body_amp, from_id, headers, preheader_text, recipient, reply_to_id, subject
        )
        return await self._client._request(
            "PUT",
            f"/transactional/{transactional_id}/language/{language}",
            json_payload=payload,
        )

    async def get_metrics(
        self,
        transactional_id: int,
        *,
        period: t.Optional[str] = None,
        steps: t.Optional[int] = None,
    ) -> dict:
        """Get metrics for a transactional message, in series from oldest to newest.

        :param transactional_id: the transactional message identifier.
        :param period: the unit of time — ``"hours"``, ``"days"``, ``"weeks"``, or
            ``"months"``. Defaults to ``"days"`` on the server side.
        :param steps: the number of periods to return. Maximums are 24 hours,
            45 days, 12 weeks, or 121 months.
        :returns: dict with a ``metric`` object containing a ``series``.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/transactionalMetrics/>`_
        """
        params: t.Dict[str, t.Any] = {}
        if period is not None:
            params["period"] = period
        if steps is not None:
            params["steps"] = steps

        return await self._client._request("GET", f"/transactional/{transactional_id}/metrics", params=params)

    async def get_link_metrics(
        self,
        transactional_id: int,
        *,
        period: t.Optional[str] = None,
        steps: t.Optional[int] = None,
        unique: t.Optional[bool] = None,
    ) -> dict:
        """Get metrics for links clicked in a transactional message.

        :param transactional_id: the transactional message identifier.
        :param period: the unit of time — ``"hours"``, ``"days"``, ``"weeks"``, or
            ``"months"``. Defaults to ``"days"`` on the server side.
        :param steps: the number of periods to return. Maximums are 24 hours,
            45 days, 12 weeks, or 121 months.
        :param unique: if True, count each customer once per link.
        :returns: dict with a ``links`` array.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/transactionalLinks/>`_
        """
        params: t.Dict[str, t.Any] = {}
        if period is not None:
            params["period"] = period
        if steps is not None:
            params["steps"] = steps
        if unique is not None:
            params["unique"] = str(unique).lower()

        return await self._client._request("GET", f"/transactional/{transactional_id}/metrics/links", params=params)

    async def get_deliveries(
        self,
        transactional_id: int,
        *,
        start: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        metric: t.Optional[str] = None,
        state: t.Optional[str] = None,
        start_ts: t.Optional[int] = None,
        end_ts: t.Optional[int] = None,
        get_tracked_responses: t.Optional[bool] = None,
    ) -> dict:
        """List the deliveries sent from a transactional message.

        Without ``start_ts`` and ``end_ts`` the most recent 6 months are returned;
        a range wider than 12 months is truncated to 12 months.

        :param transactional_id: the transactional message identifier.
        :param start: pagination token.
        :param limit: maximum number of results per page.
        :param metric: the metric to filter by, e.g. ``"attempted"``, ``"sent"``,
            ``"delivered"``, ``"opened"``, ``"clicked"``.
        :param state: the delivery state — ``"failed"``, ``"sent"``, ``"drafted"``,
            or ``"attempted"``.
        :param start_ts: beginning unix timestamp for the query.
        :param end_ts: ending unix timestamp for the query.
        :param get_tracked_responses: if True, include ``tracked_responses`` per message.
        :returns: dict with a ``messages`` array.

        `API docs <https://docs.customer.io/integrations/api/app/tag/transactional/transactionalMessages/>`_
        """
        params: t.Dict[str, t.Any] = {}
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit
        if metric is not None:
            params["metric"] = metric
        if state is not None:
            params["state"] = state
        if start_ts is not None:
            params["start_ts"] = start_ts
        if end_ts is not None:
            params["end_ts"] = end_ts
        if get_tracked_responses is not None:
            params["get_tracked_responses"] = str(get_tracked_responses).lower()

        return await self._client._request("GET", f"/transactional/{transactional_id}/messages", params=params)
