import pytest
from pytest_httpx import HTTPXMock

from async_customerio import AsyncAPIClient


pytestmark = pytest.mark.asyncio


@pytest.fixture()
def client(faker_):
    return AsyncAPIClient(key=faker_.pystr(), url="https://fake-api.customerio.io", retries=1)


# ======================================================================
# get_by_email
# ======================================================================


async def test_get_by_email(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        status_code=200,
        json={"results": [{"id": "1", "email": "test@example.com", "cio_id": "a3000001"}]},
    )
    result = await client.customers.get_by_email("test@example.com")
    assert result["results"][0]["email"] == "test@example.com"

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert "email=test%40example.com" in str(request.url)


# ======================================================================
# search
# ======================================================================


async def test_search(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        status_code=200,
        json={"identifiers": [{"id": "1", "email": "test@example.com", "cio_id": "a3000001"}]},
    )
    result = await client.customers.search(
        filter={"and": [{"segment": {"id": 1}}]},
        limit=10,
    )
    assert "identifiers" in result

    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert "limit=10" in str(request.url)


async def test_search_with_pagination(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"identifiers": [], "next": ""})
    await client.customers.search(
        filter={"and": [{"segment": {"id": 1}}]},
        start="abc123",
    )

    request = httpx_mock.get_request()
    assert "start=abc123" in str(request.url)


# ======================================================================
# get_by_ids
# ======================================================================


async def test_get_by_ids(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"customers": [{"customer": {"id": "1"}}]})
    result = await client.customers.get_by_ids([1, 2, 3])
    assert "customers" in result

    request = httpx_mock.get_request()
    assert request.method == "POST"
    import json

    body = json.loads(request.content)
    assert body["ids"] == ["1", "2", "3"]


# ======================================================================
# get_attributes
# ======================================================================


async def test_get_attributes(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"customer": {"id": "42", "attributes": {"name": "John"}}})
    result = await client.customers.get_attributes(42)
    assert result["customer"]["id"] == "42"

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert "/customers/42/attributes" in str(request.url)


async def test_get_attributes_with_id_type(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"customer": {"id": "42"}})
    await client.customers.get_attributes("test@example.com", id_type="email")

    request = httpx_mock.get_request()
    assert "id_type=email" in str(request.url)


# ======================================================================
# get_segments
# ======================================================================


async def test_get_segments(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        status_code=200,
        json={"segments": [{"id": 1, "name": "Active Users"}]},
    )
    result = await client.customers.get_segments(42)
    assert result["segments"][0]["name"] == "Active Users"

    request = httpx_mock.get_request()
    assert "/customers/42/segments" in str(request.url)


async def test_get_segments_with_id_type(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"segments": []})
    await client.customers.get_segments("cio_abc", id_type="cio_id")

    request = httpx_mock.get_request()
    assert "id_type=cio_id" in str(request.url)


# ======================================================================
# get_messages
# ======================================================================


async def test_get_messages(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"messages": [{"id": "msg_1"}]})
    result = await client.customers.get_messages(42)
    assert result["messages"][0]["id"] == "msg_1"

    request = httpx_mock.get_request()
    assert "/customers/42/messages" in str(request.url)


async def test_get_messages_with_filters(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"messages": []})
    await client.customers.get_messages(42, id_type="id", start_ts=1000, end_ts=2000, limit=5)

    request = httpx_mock.get_request()
    url = str(request.url)
    assert "id_type=id" in url
    assert "start_ts=1000" in url
    assert "end_ts=2000" in url
    assert "limit=5" in url


# ======================================================================
# get_activities
# ======================================================================


async def test_get_activities(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"activities": [{"type": "event", "name": "login"}]})
    result = await client.customers.get_activities(42)
    assert result["activities"][0]["type"] == "event"

    request = httpx_mock.get_request()
    assert "/customers/42/activities" in str(request.url)


async def test_get_activities_with_filters(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"activities": []})
    await client.customers.get_activities(42, type="event", name="login", limit=10)

    request = httpx_mock.get_request()
    url = str(request.url)
    assert "type=event" in url
    assert "name=login" in url
    assert "limit=10" in url


# ======================================================================
# get_relationships
# ======================================================================


async def test_get_relationships(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        status_code=200,
        json={"cio_relationships": [{"object_type_id": 1, "identifiers": {"object_id": "acme"}}]},
    )
    result = await client.customers.get_relationships(42)
    assert result["cio_relationships"][0]["identifiers"]["object_id"] == "acme"

    request = httpx_mock.get_request()
    assert "/customers/42/relationships" in str(request.url)


async def test_get_relationships_with_pagination(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"cio_relationships": []})
    await client.customers.get_relationships(42, start="token", limit=20)

    request = httpx_mock.get_request()
    url = str(request.url)
    assert "start=token" in url
    assert "limit=20" in url


# ======================================================================
# get_subscription_preferences
# ======================================================================


async def test_get_subscription_preferences(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"customer": {"id": "42", "topics": []}})
    result = await client.customers.get_subscription_preferences(42)
    assert "customer" in result

    request = httpx_mock.get_request()
    assert "/customers/42/subscription_preferences" in str(request.url)


async def test_get_subscription_preferences_with_params(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"customer": {"id": "42"}})
    await client.customers.get_subscription_preferences(42, id_type="cio_id", language="es")

    request = httpx_mock.get_request()
    url = str(request.url)
    assert "id_type=cio_id" in url
    assert "language=es" in url


# ======================================================================
# customers property — shared instance
# ======================================================================


def test_customers_property_returns_same_instance(client):
    a = client.customers
    b = client.customers
    assert a is b
