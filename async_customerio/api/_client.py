"""
Implements the client that interacts with Customer.io's App API using app keys.
"""

from typing import Any, Dict, Optional, Protocol

from async_customerio._config import DEFAULT_REQUEST_TIMEOUT, RequestTimeout
from async_customerio.client_base import AsyncClientBase
from async_customerio.errors import AsyncCustomerIOError
from async_customerio.regions import Region, Regions
from async_customerio.retry import RetryStrategy
from async_customerio.utils import join_url

from .customers import Customers
from .segments import Segments
from .send import SendEmailRequest, SendInboxMessageRequest, SendPushRequest, SendSMSRequest


class HasToDict(Protocol):
    def to_dict(self) -> Dict[str, Any]: ...


class AsyncAPIClient(AsyncClientBase):
    API_PREFIX = "/v1"
    SEND_EMAIL_ENDPOINT = "/send/email"
    SEND_PUSH_NOTIFICATION_ENDPOINT = "/send/push"
    SEND_SMS_ENDPOINT = "/send/sms"
    SEND_INBOX_MESSAGE_ENDPOINT = "/send/inbox_message"

    def __init__(
        self,
        key: str,
        url: Optional[str] = None,
        region: Region = Regions.US,
        retries: int = 3,
        request_timeout: RequestTimeout = DEFAULT_REQUEST_TIMEOUT,
        user_agent: Optional[str] = None,
        retry_strategy: Optional[RetryStrategy] = None,
    ):
        if not isinstance(region, Region):
            raise AsyncCustomerIOError("invalid region provided")

        self.key = key
        self.base_url = url or "https://{host}".format(host=region.api_host)
        super().__init__(retries=retries, request_timeout=request_timeout, user_agent=user_agent, retry_strategy=retry_strategy)

    @property
    def customers(self) -> Customers:
        """Access customer-related API methods.

        Usage::

            async with AsyncAPIClient(key="...") as client:
                result = await client.customers.get_by_email("test@example.com")
        """
        if not hasattr(self, "_customers"):
            self._customers = Customers(self)
        return self._customers

    @property
    def segments(self) -> Segments:
        """Access segment-related API methods.

        Usage::

            async with AsyncAPIClient(key="...") as client:
                result = await client.segments.list()
        """
        if not hasattr(self, "_segments"):
            self._segments = Segments(self)
        return self._segments

    def _build_url(self, endpoint: str) -> str:
        """Build a full URL for the given endpoint path."""
        return join_url(self.base_url, self.API_PREFIX, endpoint)

    def _auth_headers(self) -> Dict[str, str]:
        """Return the authorization header for App API requests."""
        return {"Authorization": f"Bearer {self.key}"}

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json_payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Send an authenticated request to the App API.

        This is the shared entry point used by all namespace methods.

        :param method: HTTP method.
        :param endpoint: API path relative to ``/v1`` (e.g. ``"/customers"``).
        :param json_payload: optional JSON body.
        :param params: optional query parameters.
        """
        url = self._build_url(endpoint)
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url = join_url(url, params=clean)

        return await self.send_request(
            method,
            url,
            json_payload=json_payload,
            headers=self._auth_headers(),
        )

    async def send_email(self, request: SendEmailRequest) -> dict:
        # prefer duck-typing: require a `to_dict` method rather than strict class check
        if not hasattr(request, "to_dict"):
            raise AsyncCustomerIOError("invalid request provided")

        return await self._request("POST", self.SEND_EMAIL_ENDPOINT, json_payload=request.to_dict())

    async def send_push(self, request: SendPushRequest) -> dict:
        if not hasattr(request, "to_dict"):
            raise AsyncCustomerIOError("invalid request provided")

        return await self._request("POST", self.SEND_PUSH_NOTIFICATION_ENDPOINT, json_payload=request.to_dict())

    async def send_sms(self, request: SendSMSRequest) -> dict:
        if not hasattr(request, "to_dict"):
            raise AsyncCustomerIOError("invalid request provided")

        return await self._request("POST", self.SEND_SMS_ENDPOINT, json_payload=request.to_dict())

    async def send_inbox_message(self, request: SendInboxMessageRequest) -> dict:
        if not hasattr(request, "to_dict"):
            raise AsyncCustomerIOError("invalid request provided")

        return await self._request("POST", self.SEND_INBOX_MESSAGE_ENDPOINT, json_payload=request.to_dict())
