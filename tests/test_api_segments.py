import json

import pytest
from pytest_httpx import HTTPXMock

from async_customerio import AsyncAPIClient


pytestmark = pytest.mark.asyncio


@pytest.fixture()
def client(faker_):
    return AsyncAPIClient(key=faker_.pystr(), url="https://fake-api.customerio.io", retries=1)


# ======================================================================
# list
# ======================================================================


async def test_list(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"segments": [{"id": 1, "name": "Active"}]})
    result = await client.segments.list()
    assert result["segments"][0]["name"] == "Active"

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/segments")


# ======================================================================
# get
# ======================================================================


async def test_get(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"segment": {"id": 1, "name": "Active"}})
    result = await client.segments.get(1)
    assert result["segment"]["id"] == 1

    request = httpx_mock.get_request()
    assert "/segments/1" in str(request.url)


# ======================================================================
# create
# ======================================================================


async def test_create(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"segment": {"id": 5, "name": "New Segment"}})
    result = await client.segments.create("New Segment")
    assert result["segment"]["name"] == "New Segment"

    request = httpx_mock.get_request()
    assert request.method == "POST"
    body = json.loads(request.content)
    assert body == {"segment": {"name": "New Segment"}}


async def test_create_with_description(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"segment": {"id": 5}})
    await client.segments.create("VIP Users", description="High-value customers")

    request = httpx_mock.get_request()
    body = json.loads(request.content)
    assert body == {"segment": {"name": "VIP Users", "description": "High-value customers"}}


# ======================================================================
# delete
# ======================================================================


async def test_delete(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={})
    await client.segments.delete(1)

    request = httpx_mock.get_request()
    assert request.method == "DELETE"
    assert "/segments/1" in str(request.url)


# ======================================================================
# get_customer_count
# ======================================================================


async def test_get_customer_count(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"count": 42})
    result = await client.segments.get_customer_count(1)
    assert result["count"] == 42

    request = httpx_mock.get_request()
    assert "/segments/1/customer_count" in str(request.url)


# ======================================================================
# get_membership
# ======================================================================


async def test_get_membership(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        status_code=200,
        json={"identifiers": [{"id": "1", "email": "test@example.com", "cio_id": "a3000001"}]},
    )
    result = await client.segments.get_membership(1)
    assert "identifiers" in result

    request = httpx_mock.get_request()
    assert "/segments/1/membership" in str(request.url)


async def test_get_membership_with_pagination(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"identifiers": []})
    await client.segments.get_membership(1, start="token", limit=25)

    request = httpx_mock.get_request()
    url = str(request.url)
    assert "start=token" in url
    assert "limit=25" in url


# ======================================================================
# get_used_by
# ======================================================================


async def test_get_used_by(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        status_code=200,
        json={"used_by": {"campaigns": [{"id": 1, "name": "Welcome"}]}},
    )
    result = await client.segments.get_used_by(1)
    assert "used_by" in result

    request = httpx_mock.get_request()
    assert "/segments/1/used_by" in str(request.url)


# ======================================================================
# segments property — shared instance
# ======================================================================


def test_segments_property_returns_same_instance(client):
    a = client.segments
    b = client.segments
    assert a is b
