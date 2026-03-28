import asyncio
import json
import uuid
from datetime import datetime, timezone

import pytest
import httpx

from async_customerio.client_base import AsyncClientBase, AsyncCustomerIOError, AsyncCustomerIORetryableError, PACKAGE_VERSION
from async_customerio.retry import RetryStrategy


pytestmark = pytest.mark.asyncio


class FakeRetryStrategy:
    """A simple retry strategy that retries a fixed number of times."""

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self.attempts = 0

    async def execute(self, func, *args, **kwargs):
        last_err = None
        for _ in range(self.max_retries + 1):
            self.attempts += 1
            try:
                return await func(*args, **kwargs)
            except AsyncCustomerIORetryableError as err:
                last_err = err
        raise last_err


async def test_close_closes_client():
    client = AsyncClientBase()
    # Calling _get_client should initialize the internal httpx client
    _ = await client._get_client()
    assert client._http_client is not None

    await client.close()
    # After close, the internal reference should be cleared
    assert client._http_client is None


async def test_context_manager_closes():
    async with AsyncClientBase() as client:
        _ = await client._get_client()
        assert client._http_client is not None

    # After exiting the context manager, client should be closed
    assert client._http_client is None


async def test_json_fallback_text_response(httpx_mock):
    client = AsyncClientBase()
    # Return plain text with text/plain content type
    httpx_mock.add_response(status_code=200, content=b"plain text", headers={"content-type": "text/plain"})

    res = await client.send_request("GET", "https://example.test/text")
    assert res == "plain text"


async def test_no_content_returns_empty_dict(httpx_mock):
    client = AsyncClientBase()
    httpx_mock.add_response(status_code=204, content=b"")

    res = await client.send_request("GET", "https://example.test/no-content")
    assert res == {}


async def test_transport_error_raises_retryable(httpx_mock):
    client = AsyncClientBase(retries=1)
    httpx_mock.add_exception(httpx.ConnectError("boom"))

    with pytest.raises(AsyncCustomerIORetryableError):
        await client.send_request("GET", "https://example.test/boom")


async def test_generic_exception_raised_as_asynccustomerioerror(monkeypatch):
    client = AsyncClientBase()

    async def _raise(*args, **kwargs):
        raise Exception("unexpected")

    # Initialize the client, then replace its request method to raise an arbitrary Exception
    http_client = await client._get_client()
    http_client.request = _raise

    with pytest.raises(AsyncCustomerIOError):
        await client.send_request("GET", "https://example.test/error")


async def test_lazy_client_recreation_after_closed():
    client = AsyncClientBase()

    # Ensure an internal client exists
    original = await client._get_client()
    assert client._http_client is not None

    # Close the underlying httpx client instance without clearing the attribute
    await original.aclose()
    assert original.is_closed

    # _get_client should recreate a new AsyncClient instance
    recreated = await client._get_client()
    assert recreated is not original
    assert client._http_client is recreated


def test_default_user_agent():
    client = AsyncClientBase()
    headers = client._prepare_headers()
    assert headers["User-Agent"] == f"async-customerio/{PACKAGE_VERSION}"


def test_custom_user_agent():
    client = AsyncClientBase(user_agent="my-app/1.0")
    headers = client._prepare_headers()
    assert headers["User-Agent"] == "my-app/1.0"


def test_fake_retry_strategy_satisfies_protocol():
    strategy = FakeRetryStrategy()
    assert isinstance(strategy, RetryStrategy)


async def test_retry_strategy_is_invoked_on_success(httpx_mock):
    strategy = FakeRetryStrategy(max_retries=2)
    client = AsyncClientBase(retry_strategy=strategy)
    httpx_mock.add_response(status_code=200, json={"ok": True})

    res = await client.send_request("GET", "https://example.test/ok")
    assert res == {"ok": True}
    assert strategy.attempts == 1


async def test_retry_strategy_retries_on_retryable_error(httpx_mock):
    strategy = FakeRetryStrategy(max_retries=2)
    client = AsyncClientBase(retry_strategy=strategy)

    # First two calls fail with transport error, third succeeds
    httpx_mock.add_exception(httpx.ConnectError("fail-1"))
    httpx_mock.add_exception(httpx.ConnectError("fail-2"))
    httpx_mock.add_response(status_code=200, json={"recovered": True})

    res = await client.send_request("GET", "https://example.test/flaky")
    assert res == {"recovered": True}
    assert strategy.attempts == 3


async def test_retry_strategy_gives_up_after_max_retries(httpx_mock):
    strategy = FakeRetryStrategy(max_retries=1)
    client = AsyncClientBase(retry_strategy=strategy)

    httpx_mock.add_exception(httpx.ConnectError("fail-1"))
    httpx_mock.add_exception(httpx.ConnectError("fail-2"))

    with pytest.raises(AsyncCustomerIORetryableError):
        await client.send_request("GET", "https://example.test/down")
    assert strategy.attempts == 2


async def test_retry_strategy_does_not_retry_non_retryable(httpx_mock):
    strategy = FakeRetryStrategy(max_retries=3)
    client = AsyncClientBase(retry_strategy=strategy)

    httpx_mock.add_response(status_code=400, content=b"bad request")

    with pytest.raises(AsyncCustomerIOError):
        await client.send_request("GET", "https://example.test/bad")
    # Non-retryable errors propagate immediately (only 1 attempt)
    assert strategy.attempts == 1


async def test_no_retry_strategy_preserves_default_behavior(httpx_mock):
    client = AsyncClientBase()
    httpx_mock.add_exception(httpx.ConnectError("boom"))

    with pytest.raises(AsyncCustomerIORetryableError):
        await client.send_request("GET", "https://example.test/boom")


async def test_concurrent_get_client_creates_only_one_instance():
    client = AsyncClientBase()
    results = await asyncio.gather(*(client._get_client() for _ in range(10)))
    assert all(r is results[0] for r in results)
    await client.close()


def test_prepare_headers_contains_required_fields():
    client = AsyncClientBase()
    headers = client._prepare_headers()
    assert headers["Content-Type"] == "application/json"
    uuid.UUID(headers["X-Request-Id"])
    assert "T" in headers["X-Timestamp"]
    assert "User-Agent" in headers


@pytest.mark.parametrize("status_code", [429, 502, 503, 504])
async def test_retryable_status_codes(httpx_mock, status_code):
    client = AsyncClientBase()
    httpx_mock.add_response(status_code=status_code, content=b"error")
    with pytest.raises(AsyncCustomerIORetryableError):
        await client.send_request("GET", "https://example.test/retry")


@pytest.mark.parametrize("status_code", [400, 403, 404, 409, 422])
async def test_non_retryable_status_codes(httpx_mock, status_code):
    client = AsyncClientBase()
    httpx_mock.add_response(status_code=status_code, content=b"error")
    with pytest.raises(AsyncCustomerIOError) as exc_info:
        await client.send_request("GET", "https://example.test/fail")
    assert not isinstance(exc_info.value, AsyncCustomerIORetryableError)


async def test_close_idempotent():
    client = AsyncClientBase()
    _ = await client._get_client()
    await client.close()
    await client.close()
    assert client._http_client is None


async def test_close_before_any_use():
    client = AsyncClientBase()
    await client.close()
    assert client._http_client is None


async def test_close_then_reuse_creates_new_transport(httpx_mock):
    client = AsyncClientBase()
    _ = await client._get_client()
    await client.close()
    httpx_mock.add_response(status_code=200, json={"ok": True})
    res = await client.send_request("GET", "https://example.test/reuse")
    assert res == {"ok": True}


async def test_send_request_sanitizes_payload(httpx_mock):
    client = AsyncClientBase()
    httpx_mock.add_response(status_code=200, json={"ok": True})
    dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
    await client.send_request(
        "POST", "https://example.test/sanitize", json_payload={"ts": dt}
    )
    request = httpx_mock.get_request()
    body = json.loads(request.content)
    assert body["ts"] == 1672531200
