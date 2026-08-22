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
    httpx_mock.add_response(status_code=200, json={"messages": [{"id": 2, "name": "password reset"}]})
    result = await client.transactional.list()
    assert result["messages"][0]["name"] == "password reset"

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/transactional")


# ======================================================================
# get
# ======================================================================


async def test_get(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"message": {"id": 2, "name": "password reset"}})
    result = await client.transactional.get(2)
    assert result["message"]["id"] == 2

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/transactional/2")


# ======================================================================
# list_variants
# ======================================================================


async def test_list_variants(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"contents": [{"id": 96, "language": "fr"}]})
    result = await client.transactional.list_variants(3)
    assert result["contents"][0]["language"] == "fr"

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/transactional/3/contents")


# ======================================================================
# update_content
# ======================================================================


async def test_update_content(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"content": [{"id": 139}]})
    result = await client.transactional.update_content(3, 139, subject="Reset your password")
    assert result["content"][0]["id"] == 139

    request = httpx_mock.get_request()
    assert request.method == "PUT"
    assert str(request.url).endswith("/v1/transactional/3/content/139")
    assert json.loads(request.content) == {"subject": "Reset your password"}


async def test_update_content_sends_only_provided_fields(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"content": []})
    await client.transactional.update_content(
        3,
        139,
        body="<html>hi</html>",
        body_amp="<amp>hi</amp>",
        from_id=1,
        headers=[{"name": "X-Mailgun-Tag", "value": "my-cool-tag"}],
        preheader_text="preview",
        recipient="{{customer.email}}",
        reply_to_id=38,
        subject="Did you get that thing I sent you?",
    )

    request = httpx_mock.get_request()
    assert json.loads(request.content) == {
        "body": "<html>hi</html>",
        "body_amp": "<amp>hi</amp>",
        "from_id": 1,
        "headers": [{"name": "X-Mailgun-Tag", "value": "my-cool-tag"}],
        "preheader_text": "preview",
        "recipient": "{{customer.email}}",
        "reply_to_id": 38,
        "subject": "Did you get that thing I sent you?",
    }


async def test_update_content_omits_unset_fields(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"content": []})
    await client.transactional.update_content(3, 139)

    request = httpx_mock.get_request()
    assert json.loads(request.content) == {}


# ======================================================================
# get_variant
# ======================================================================


async def test_get_variant(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"content": [{"id": 96, "language": "fr"}]})
    result = await client.transactional.get_variant(3, "fr")
    assert result["content"][0]["language"] == "fr"

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/transactional/3/language/fr")


# ======================================================================
# update_variant
# ======================================================================


async def test_update_variant(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"content": [{"id": 96, "language": "fr"}]})
    result = await client.transactional.update_variant(3, "fr", body="<html>bonjour</html>")
    assert result["content"][0]["language"] == "fr"

    request = httpx_mock.get_request()
    assert request.method == "PUT"
    assert str(request.url).endswith("/v1/transactional/3/language/fr")
    assert json.loads(request.content) == {"body": "<html>bonjour</html>"}


async def test_update_variant_sends_only_provided_fields(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"content": []})
    await client.transactional.update_variant(
        3,
        "fr",
        body="<html>bonjour</html>",
        body_amp="<amp>bonjour</amp>",
        from_id=1,
        headers=[{"name": "X-Custom-Header", "value": "custom-value"}],
        preheader_text="apercu",
        recipient="{{customer.email}}",
        reply_to_id=38,
        subject="Bonjour",
    )

    request = httpx_mock.get_request()
    assert json.loads(request.content) == {
        "body": "<html>bonjour</html>",
        "body_amp": "<amp>bonjour</amp>",
        "from_id": 1,
        "headers": [{"name": "X-Custom-Header", "value": "custom-value"}],
        "preheader_text": "apercu",
        "recipient": "{{customer.email}}",
        "reply_to_id": 38,
        "subject": "Bonjour",
    }


# ======================================================================
# get_metrics
# ======================================================================


async def test_get_metrics(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"metric": {"series": {"sent": [1]}}})
    result = await client.transactional.get_metrics(1)
    assert result["metric"]["series"]["sent"] == [1]

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/transactional/1/metrics")


async def test_get_metrics_with_period_and_steps(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"metric": {"series": {}}})
    await client.transactional.get_metrics(1, period="weeks", steps=12)

    url = str(httpx_mock.get_request().url)
    assert "period=weeks" in url
    assert "steps=12" in url


# ======================================================================
# get_link_metrics
# ======================================================================


async def test_get_link_metrics(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"links": [{"link": {"id": 1234}}]})
    result = await client.transactional.get_link_metrics(1)
    assert result["links"][0]["link"]["id"] == 1234

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/transactional/1/metrics/links")


async def test_get_link_metrics_with_params(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"links": []})
    await client.transactional.get_link_metrics(1, period="hours", steps=24, unique=True)

    url = str(httpx_mock.get_request().url)
    assert "period=hours" in url
    assert "steps=24" in url
    assert "unique=true" in url


async def test_get_link_metrics_unique_false_is_sent(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"links": []})
    await client.transactional.get_link_metrics(1, unique=False)

    assert "unique=false" in str(httpx_mock.get_request().url)


# ======================================================================
# get_deliveries
# ======================================================================


async def test_get_deliveries(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"messages": [{"id": "abc"}]})
    result = await client.transactional.get_deliveries(1)
    assert result["messages"][0]["id"] == "abc"

    request = httpx_mock.get_request()
    assert request.method == "GET"
    assert str(request.url).endswith("/v1/transactional/1/messages")


async def test_get_deliveries_with_params(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"messages": []})
    await client.transactional.get_deliveries(
        1,
        start="token",
        limit=50,
        metric="delivered",
        state="sent",
        start_ts=1609957805,
        end_ts=1609957872,
        get_tracked_responses=True,
    )

    url = str(httpx_mock.get_request().url)
    assert "start=token" in url
    assert "limit=50" in url
    assert "metric=delivered" in url
    assert "state=sent" in url
    assert "start_ts=1609957805" in url
    assert "end_ts=1609957872" in url
    assert "get_tracked_responses=true" in url


async def test_get_deliveries_tracked_responses_false_is_sent(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"messages": []})
    await client.transactional.get_deliveries(1, get_tracked_responses=False)

    assert "get_tracked_responses=false" in str(httpx_mock.get_request().url)


# ======================================================================
# transactional property — shared instance
# ======================================================================


def test_transactional_property_returns_same_instance(client):
    a = client.transactional
    b = client.transactional
    assert a is b
