"""
Implements the base client that is used by other classes to make requests
"""

import asyncio
import http
import logging
import typing as t
import uuid
from datetime import datetime, timezone
from typing import Optional


try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # type: ignore

import httpx

from async_customerio._config import DEFAULT_REQUEST_LIMITS, DEFAULT_REQUEST_TIMEOUT, RequestLimits, RequestTimeout
from async_customerio.errors import AsyncCustomerIOError, AsyncCustomerIORetryableError
from async_customerio.retry import RetryStrategy
from async_customerio.utils import sanitize


# Cache package version and user agent to avoid repeated metadata lookups
try:
    PACKAGE_VERSION = version("async-customerio")
except Exception:
    PACKAGE_VERSION = "unknown"


CUSTOMERIO_UNAVAILABLE_MESSAGE = """Failed to receive valid response from Customer.io.
Check system status at http://status.customer.io.
Last caught exception -- {klass}: {message}
"""


class AsyncClientBase:
    def __init__(
        self,
        retries: int = 3,
        *,
        request_timeout: RequestTimeout = DEFAULT_REQUEST_TIMEOUT,
        request_limits: RequestLimits = DEFAULT_REQUEST_LIMITS,
        user_agent: Optional[str] = None,
        retry_strategy: Optional[RetryStrategy] = None,
    ):
        """

        :param retries: deprecated, has no effect. Use ``retry_strategy`` instead.
        :param request_timeout: advanced feature that allows to change request timeout.
        :param request_limits: advanced feature that allows to control the connection pool size.
        :param user_agent: custom User-Agent header value. Defaults to ``async-customerio/<version>``.
        :param retry_strategy: an optional :class:`~async_customerio.retry.RetryStrategy` instance
            that wraps each HTTP call with custom retry logic (e.g. exponential backoff via *tenacity*).
            When ``None`` (the default), no automatic retries are performed — the library raises
            :class:`~async_customerio.errors.AsyncCustomerIORetryableError` for transient failures
            so the caller can decide how to retry.
        """

        self._retry_strategy = retry_strategy
        self._request_timeout = request_timeout
        self._request_limits = request_limits
        self._http_client: t.Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()
        self._user_agent = user_agent or "async-customerio/{0}".format(PACKAGE_VERSION)

    def _create_client(self) -> httpx.AsyncClient:
        """Create a new httpx.AsyncClient with a fresh transport."""
        transport = httpx.AsyncHTTPTransport(limits=httpx.Limits(**self._request_limits.__dict__))
        return httpx.AsyncClient(
            timeout=httpx.Timeout(**self._request_timeout.__dict__),
            transport=transport,
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """Return the shared httpx.AsyncClient, creating one if needed.

        Thread-safe via asyncio.Lock to prevent concurrent coroutines from
        creating multiple clients.
        """
        if self._http_client is not None and not self._http_client.is_closed:
            return self._http_client
        async with self._client_lock:
            if self._http_client is None or self._http_client.is_closed:
                self._http_client = self._create_client()
            return self._http_client

    async def close(self) -> None:
        """Close the internal ``httpx.AsyncClient`` if it exists.

        Safe to call multiple times.
        """
        async with self._client_lock:
            if self._http_client is not None and not self._http_client.is_closed:
                await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> "AsyncClientBase":
        # Ensure client is initialized lazily by returning self.
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    @staticmethod
    def _get_request_id():
        """Generate unique request ID."""
        return str(uuid.uuid4())

    def _prepare_headers(self) -> t.Dict[str, str]:
        """Prepare HTTP headers that will be used to request CustomerIO."""
        logging.debug("Preparing HTTP headers for all the subsequent requests")
        return {
            "Content-Type": "application/json",
            "X-Request-Id": self._get_request_id(),
            "X-Timestamp": datetime.now(timezone.utc).isoformat(),
            "User-Agent": self._user_agent,
        }

    async def send_request(
        self,
        method: str,
        url: str,
        *,
        json_payload: Optional[t.Dict[str, t.Any]] = None,
        headers: Optional[t.Dict[str, str]] = None,
        auth: t.Optional[t.Tuple[str, str]] = None,
    ) -> t.Union[dict, str]:
        """
        Sends an HTTP call using the ``httpx`` library.

        :param method: HTTP method to use
        :param url: URL to be requested.
        :param json_payload: request JSON payload
        :param headers: request headers.
        :param auth: Credentials to use when sending requests.
        :return: dict
        """

        if self._retry_strategy is not None:
            return await self._retry_strategy.execute(
                self._do_request, method, url, json_payload=json_payload, headers=headers, auth=auth
            )
        return await self._do_request(method, url, json_payload=json_payload, headers=headers, auth=auth)

    async def _do_request(
        self,
        method: str,
        url: str,
        *,
        json_payload: Optional[t.Dict[str, t.Any]] = None,
        headers: Optional[t.Dict[str, str]] = None,
        auth: t.Optional[t.Tuple[str, str]] = None,
    ) -> t.Union[dict, str]:
        """Execute a single HTTP request with error classification.

        This is the inner implementation called by :meth:`send_request`.
        When a :class:`~async_customerio.retry.RetryStrategy` is configured,
        this method is invoked through the strategy so that transient failures
        (those that raise :class:`~async_customerio.errors.AsyncCustomerIORetryableError`)
        can be retried transparently.
        """

        merged_headers = self._prepare_headers()
        if headers:
            merged_headers.update(headers)

        logging.debug(
            "Requesting method: %s, URL: %s, payload: %s, headers: %s",
            method,
            url,
            json_payload,
            headers,
        )
        try:
            client = await self._get_client()
            raw_cio_response: httpx.Response = await client.request(
                method,
                url,
                json=json_payload and sanitize(json_payload),
                headers=merged_headers,
                auth=auth,
            )
            raw_cio_response.raise_for_status()
        except httpx.TransportError as err:
            # Raise exception alerting user that the system might be
            # experiencing an outage and refer them to system status page.
            raise AsyncCustomerIORetryableError(
                CUSTOMERIO_UNAVAILABLE_MESSAGE.format(klass=type(err), message=err)
            ) from err
        except httpx.HTTPStatusError as err:
            # Check if the status code is retryable
            if err.response.status_code in [
                http.HTTPStatus.BAD_GATEWAY,
                http.HTTPStatus.SERVICE_UNAVAILABLE,
                http.HTTPStatus.GATEWAY_TIMEOUT,
                http.HTTPStatus.TOO_MANY_REQUESTS,
            ]:
                raise AsyncCustomerIORetryableError(
                    CUSTOMERIO_UNAVAILABLE_MESSAGE.format(klass=type(err), message=err)
                ) from err
            else:
                # For non-retryable status codes, raise the base error
                raise AsyncCustomerIOError(f"HTTP {err.response.status_code}: {err.response.text}") from err
        except Exception as err:
            # Raise exception alerting user that the system might be
            # experiencing an outage and refer them to system status page.
            raise AsyncCustomerIOError(CUSTOMERIO_UNAVAILABLE_MESSAGE.format(klass=type(err), message=err)) from err

        logging.debug(
            "Response Code: %s, Time spent to make a request: %s",
            raw_cio_response.status_code,
            raw_cio_response.elapsed,
        )

        # Try to parse JSON, but fall back to text for non-JSON responses.
        try:
            return raw_cio_response.json()
        except ValueError:
            # 204 No Content -> return empty dict for callers expecting a mapping
            if raw_cio_response.status_code == http.HTTPStatus.NO_CONTENT or not raw_cio_response.text:
                return {}
            return raw_cio_response.text
