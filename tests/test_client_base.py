import pytest
import httpx

from async_customerio.client_base import AsyncClientBase, AsyncCustomerIOError, AsyncCustomerIORetryableError


pytestmark = pytest.mark.asyncio


async def test_close_closes_client():
    client = AsyncClientBase()
    # Accessing _client should initialize the internal httpx client
    _ = client._client
    assert client._http_client is not None

    await client.close()
    # After close, the internal reference should be cleared
    assert client._http_client is None


async def test_context_manager_closes():
    async with AsyncClientBase() as client:
        _ = client._client
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

    # Replace the underlying client's request method to raise an arbitrary Exception
    client._client.request = _raise

    with pytest.raises(AsyncCustomerIOError):
        await client.send_request("GET", "https://example.test/error")


async def test_lazy_client_recreation_after_closed():
    client = AsyncClientBase()

    # Ensure an internal client exists
    original = client._client
    assert client._http_client is not None

    # Close the underlying httpx client instance without clearing the attribute
    await original.aclose()
    assert original.is_closed

    # Accessing _client should recreate a new AsyncClient instance
    recreated = client._client
    assert recreated is not original
    assert client._http_client is recreated
