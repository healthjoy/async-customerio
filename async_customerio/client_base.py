"""
Implements the base client that is used by other classes to make requests
"""
import logging
import typing as t
import uuid

import httpx

import pkg_resources
from async_customerio.utils import sanitize


class AsyncClientBase:
    def __init__(self, retries: int = 3, timeout: int = 10):
        self.timeout = timeout
        self.retries = retries

    @staticmethod
    def _get_request_id():
        """Generate unique request ID."""
        return str(uuid.uuid4())

    def _prepare_headers(self):
        """Prepare HTTP headers that will be used to request CustomerIO."""
        logging.debug("Preparing HTTP headers for all the subsequent requests")
        return {
            "Content-Type": "application/json; UTF-8",
            "X-Request-Id": self._get_request_id(),
            "User-Agent": "async-customerio/{0}".format(pkg_resources.get_distribution("async-customerio").version),
        }

    async def send_request(
        self,
        method: str,
        url: str,
        *,
        json_payload: t.Dict[str, t.Any] = None,
        headers: t.Dict[str, str] = None,
        auth: t.Optional[t.Tuple[str, str]] = None
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

        transport = httpx.AsyncHTTPTransport(retries=self.retries)
        async with httpx.AsyncClient(timeout=self.timeout, transport=transport, auth=auth) as client:
            logging.debug(
                "Requesting method: %s, URL: %s, payload: %s, headers: %s",
                method,
                url,
                json_payload,
                headers,
            )
            raw_cio_response: httpx.Response = await client.request(
                method, url, json=json_payload and sanitize(json_payload), headers=merged_headers
            )
            raw_cio_response.raise_for_status()
            logging.debug(
                "Response Code: %s, Time spent to make a request: %s",
                raw_cio_response.status_code,
                raw_cio_response.elapsed,
            )

        return raw_cio_response.json()
