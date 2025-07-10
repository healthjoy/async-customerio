"""
Implements the base client that is used by other classes to make requests
"""

import http
import logging
import typing as t
import uuid
from datetime import datetime
from typing import Optional


try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # type: ignore

import httpx

from async_customerio._config import DEFAULT_REQUEST_LIMITS, DEFAULT_REQUEST_TIMEOUT, RequestLimits, RequestTimeout
from async_customerio.errors import AsyncCustomerIOError, AsyncCustomerIORetryableError
from async_customerio.utils import sanitize


CUSTOMERIO_UNAVAILABLE_MESSAGE = """Failed to receive valid response after {count} retries.
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
    ):
        """

        :param retries: set number of retries before give up
        :param request_timeout: advanced feature that allows to change request timeout.
        :param request_limits: advanced feature that allows to control the connection pool size.
        """

        self._retries = retries
        self._request_timeout = request_timeout
        self._request_transport = httpx.AsyncHTTPTransport(limits=httpx.Limits(**request_limits.__dict__))
        self._http_client: t.Optional[httpx.AsyncClient] = None

    @property
    def _client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(**self._request_timeout.__dict__),
                transport=self._request_transport,
            )
        return self._http_client

    @staticmethod
    def _get_request_id():
        """Generate unique request ID."""
        return str(uuid.uuid4())

    def _prepare_headers(self):
        """Prepare HTTP headers that will be used to request CustomerIO."""
        logging.debug("Preparing HTTP headers for all the subsequent requests")
        return {
            "Content-Type": "application/json",
            "X-Request-Id": self._get_request_id(),
            "X-Timestamp": datetime.utcnow().isoformat(),
            "User-Agent": "async-customerio/{0}".format(version("async-customerio")),
        }

    async def send_request(
        self,
        method: str,
        url: str,
        *,
        json_payload: Optional[t.Dict[str, t.Any]] = None,
        headers: Optional[t.Dict[str, str]] = None,
        auth: t.Optional[t.Tuple[str, str]] = None,
    ) -> t.Union[dict]:
        """
        Sends an HTTP call using the ``httpx`` library.

        :param method: HTTP method to use
        :param url: URL to be requested.
        :param json_payload: request JSON payload
        :param headers: request headers.
        :param auth: Credentials to use when sending requests.
        :return: dict
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
            raw_cio_response: httpx.Response = await self._client.request(
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
                CUSTOMERIO_UNAVAILABLE_MESSAGE.format(klass=type(err), message=err, count=self._retries)
            )
        except httpx.HTTPStatusError as err:
            # Check if the status code is retryable
            if err.response.status_code in [
                http.HTTPStatus.BAD_GATEWAY,
                http.HTTPStatus.SERVICE_UNAVAILABLE,
                http.HTTPStatus.GATEWAY_TIMEOUT,
                http.HTTPStatus.TOO_MANY_REQUESTS,
            ]:
                raise AsyncCustomerIORetryableError(
                    CUSTOMERIO_UNAVAILABLE_MESSAGE.format(klass=type(err), message=err, count=self._retries)
                )
            else:
                # For non-retryable status codes, raise the base error
                raise AsyncCustomerIOError(f"HTTP {err.response.status_code}: {err.response.text}")
        except Exception as err:
            # Raise exception alerting user that the system might be
            # experiencing an outage and refer them to system status page.
            raise AsyncCustomerIOError(
                CUSTOMERIO_UNAVAILABLE_MESSAGE.format(klass=type(err), message=err, count=self._retries)
            )

        logging.debug(
            "Response Code: %s, Time spent to make a request: %s",
            raw_cio_response.status_code,
            raw_cio_response.elapsed,
        )

        return raw_cio_response.json()
