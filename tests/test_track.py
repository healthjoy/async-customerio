import json
from datetime import datetime, timezone

import httpx
import pytest
from pytest_httpx import HTTPXMock

from async_customerio import AsyncCustomerIO, AsyncCustomerIOError, AsyncCustomerIORetryableError
from async_customerio.constants import CIOID, EMAIL, ID
from async_customerio.regions import Regions

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def fake_async_customerio(faker_):
    return AsyncCustomerIO(
        site_id=faker_.pystr(),
        api_key=faker_.pystr(),
        host="fake-track.customerio.io",
        retries=1,
    )


async def test_identify(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.identify(faker_.pyint(min_value=100), first_name="John", last_name="Smith")
    assert response is None


async def test_identify_empty_id(fake_async_customerio):
    with pytest.raises(AsyncCustomerIOError, match="identifier cannot be blank in identify"):
        await fake_async_customerio.identify(0, first_name="John", last_name="Smith")


async def test_track(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.track(
        faker_.pyint(min_value=100),
        name="user_signed_in"
    )
    assert response is None


async def test_track_empty_id(fake_async_customerio):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in track"):
        await fake_async_customerio.track(0, name="user_signed_in")


@pytest.mark.parametrize("anonymous_id", (None, 0, 100, "user-id"))
async def test_track_anonymous(anonymous_id, fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.track_anonymous(
        anonymous_id,
        name="user-redirected"
    )
    assert response is None


async def test_pageview(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.pageview(
        faker_.pyint(min_value=100),
        page="landing-page"
    )
    assert response is None


async def test_pageview_empty_id(fake_async_customerio):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in pageview"):
        await fake_async_customerio.pageview(0, page="landing-page")


async def test_backfill(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.backfill(
        faker_.pyint(min_value=100),
        name="user-ordered-some-product",
        timestamp=datetime.utcnow()
    )
    assert response is None


async def test_backfill_empty_id(fake_async_customerio):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in backfill"):
        await fake_async_customerio.backfill(0, name="landing-page", timestamp=datetime.utcnow())


async def test_delete(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.delete(faker_.pyint(min_value=100))
    assert response is None


async def test_delete_empty_id(fake_async_customerio):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in delete"):
        await fake_async_customerio.delete(0)


async def test_add_device(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.add_device(
        faker_.pyint(min_value=100),
        faker_.pystr(),
        "android"
    )
    assert response is None


async def test_add_device_empty_customer_id(fake_async_customerio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in add_device"):
        await fake_async_customerio.add_device(0, faker_.pystr(), faker_.pystr())


async def test_add_device_empty_device_id(fake_async_customerio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="device_id cannot be blank in add_device"):
        await fake_async_customerio.add_device(faker_.pyint(), "", faker_.pystr())


async def test_add_device_empty_platform(fake_async_customerio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="platform cannot be blank in add_device"):
        await fake_async_customerio.add_device(faker_.pyint(), faker_.pystr(), "")


async def test_delete_device(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.delete_device(faker_.pyint(min_value=100), faker_.pystr())
    assert response is None


async def test_delete_device_empty_customer_id(fake_async_customerio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in delete_device"):
        await fake_async_customerio.delete_device(0, faker_.pystr())


async def test_delete_device_empty_device_id(fake_async_customerio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="device_id cannot be blank in delete_device"):
        await fake_async_customerio.delete_device(faker_.pyint(), "")


async def test_suppress(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.suppress(faker_.pyint(min_value=100))
    assert response is None


async def test_suppress_empty_customer_id(fake_async_customerio):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in suppress"):
        await fake_async_customerio.suppress(0)


async def test_unsuppress(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.unsuppress(faker_.pyint(min_value=100))
    assert response is None


async def test_unsuppress_empty_customer_id(fake_async_customerio):
    with pytest.raises(AsyncCustomerIOError, match="customer_id cannot be blank in unsuppress"):
        await fake_async_customerio.unsuppress(0)


async def test_merge_customers(fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await fake_async_customerio.merge_customers(
        ID,
        faker_.pyint(),
        EMAIL,
        faker_.pyint()
    )
    assert response is None


@pytest.mark.parametrize(
    "primary_id_type, primary_id, secondary_id_type, secondary_id, error_message", (
        ("foo", 2, ID, 200, "invalid primary id type"),
        (EMAIL, 2, "foo", 200, "invalid secondary id type"),
        (EMAIL, 0, CIOID, 200, "primary customer_id cannot be blank"),
        (EMAIL, 10, CIOID, 0, "secondary customer_id cannot be blank"),
    )
)
async def test_merge_customers_empty_customer_id(
    fake_async_customerio, primary_id_type, primary_id, secondary_id_type, secondary_id, error_message
):
    with pytest.raises(AsyncCustomerIOError, match=error_message):
        await fake_async_customerio.merge_customers(primary_id_type, primary_id, secondary_id_type, secondary_id)


@pytest.mark.parametrize(
    "method, method_arguments", (
        ("identify", {"identifier": 1, "name": "Jack"}),
        ("track", {"customer_id": 1, "name": "some-event"}),
        ("track_anonymous", {"anonymous_id": "1111-2", "name": "some-event"}),
        ("pageview", {"customer_id": 1, "page": "home-screen"}),
        ("backfill", {"customer_id": 1, "name": "home-screen", "timestamp": datetime.utcnow()}),
        ("delete", {"customer_id": 1}),
        ("add_device", {"customer_id": 1, "device_id": "some-device-id", "platform": "ios"}),
        ("delete_device", {"customer_id": 1, "device_id": "some-device-id"}),
        ("suppress", {"customer_id": 1}),
        ("unsuppress", {"customer_id": 1}),
        ("merge_customers", {"primary_id_type": CIOID, "primary_id": 1, "secondary_id_type": ID, "secondary_id": 9}),
    )
)
async def test_unauthorized_request(method, method_arguments, fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=401)
    with pytest.raises(AsyncCustomerIOError):
        await getattr(fake_async_customerio, method)(**method_arguments)


@pytest.mark.parametrize("connection_error", (httpx.ConnectError, httpx.ConnectTimeout))
async def test_client_connection_handling(connection_error, fake_async_customerio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(connection_error("something went wrong"))
    with pytest.raises(AsyncCustomerIORetryableError):
        await fake_async_customerio.identify(faker_.pyint(min_value=100))


def test_invalid_region_raises():
    with pytest.raises(AsyncCustomerIOError, match="invalid region provided"):
        AsyncCustomerIO("site", "key", region="CN")


def test_setup_base_url_strips_scheme_and_handles_default_port():
    url = AsyncCustomerIO.setup_base_url("https://example.com", 443, "/api/v1")
    assert url == "https://example.com/api/v1"

    url2 = AsyncCustomerIO.setup_base_url("example.com", 8080, "prefix")
    assert url2 == "https://example.com:8080/prefix"


def test_backfill_invalid_timestamp_raises():
    client = AsyncCustomerIO("site", "key")
    with pytest.raises(AsyncCustomerIOError):
        # pass a non-int, non-datetime timestamp
        pytest.raises(AsyncCustomerIOError)
        # call is synchronous up to validation so no network needed
        import asyncio

        asyncio.get_event_loop().run_until_complete(client.backfill("123", "name", "not-a-timestamp"))


async def test_identify_request_url_and_method(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.identify(42, first_name="John")

    request = httpx_mock.get_request()
    assert request.method == "PUT"
    assert "/api/v1/customers/42" in str(request.url)
    body = json.loads(request.content)
    assert body == {"first_name": "John"}


async def test_identify_url_encodes_special_characters(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.identify("user@domain.com")

    request = httpx_mock.get_request()
    assert "user%40domain.com" in str(request.url)


async def test_track_request_url_and_payload(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.track(42, "purchase", amount=99)

    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert "/api/v1/customers/42/events" in str(request.url)
    body = json.loads(request.content)
    assert body == {"name": "purchase", "data": {"amount": 99}}


async def test_track_anonymous_request_payload(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.track_anonymous("anon-123", "viewed_page", source="google")

    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert "/api/v1/events" in str(request.url)
    body = json.loads(request.content)
    assert body["anonymous_id"] == "anon-123"
    assert body["name"] == "viewed_page"
    assert body["data"]["source"] == "google"


async def test_track_anonymous_omits_anonymous_id_when_falsy(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.track_anonymous("", "event")

    request = httpx_mock.get_request()
    body = json.loads(request.content)
    assert "anonymous_id" not in body


async def test_pageview_request_payload(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.pageview(42, "/pricing", ref="google")

    request = httpx_mock.get_request()
    assert request.method == "POST"
    body = json.loads(request.content)
    assert body["type"] == "page"
    assert body["name"] == "/pricing"
    assert body["data"]["ref"] == "google"


async def test_backfill_request_payload(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.backfill(42, "old", timestamp=1672531199, src="import")

    request = httpx_mock.get_request()
    assert request.method == "POST"
    body = json.loads(request.content)
    assert body["name"] == "old"
    assert body["timestamp"] == 1672531199
    assert body["data"]["src"] == "import"


async def test_backfill_converts_datetime_to_timestamp(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    await fake_async_customerio.backfill(42, "old_event", timestamp=dt)

    request = httpx_mock.get_request()
    body = json.loads(request.content)
    assert isinstance(body["timestamp"], int)
    assert body["timestamp"] == int(dt.timestamp())


async def test_delete_request_url_and_method(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.delete(42)

    request = httpx_mock.get_request()
    assert request.method == "DELETE"
    assert "/api/v1/customers/42" in str(request.url)


async def test_add_device_request_url_and_payload(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.add_device(42, "tok-abc", "ios")

    request = httpx_mock.get_request()
    assert request.method == "PUT"
    assert "/42/devices" in str(request.url)
    body = json.loads(request.content)
    assert body == {"device": {"id": "tok-abc", "platform": "ios"}}


async def test_delete_device_request_url(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.delete_device(42, "tok-abc")

    request = httpx_mock.get_request()
    assert request.method == "DELETE"
    assert "/42/devices/tok-abc" in str(request.url)


async def test_suppress_request_url(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.suppress(42)

    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert "/api/v1/customers/42/suppress" in str(request.url)


async def test_unsuppress_request_url(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.unsuppress(42)

    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert "/api/v1/customers/42/unsuppress" in str(request.url)


async def test_merge_customers_request_payload(fake_async_customerio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_customerio.merge_customers("id", 100, "email", "test@a.com")

    request = httpx_mock.get_request()
    assert request.method == "POST"
    body = json.loads(request.content)
    assert body == {"primary": {"id": 100}, "secondary": {"email": "test@a.com"}}


async def test_auth_credentials_sent(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    client = AsyncCustomerIO(site_id="my_site", api_key="my_key", host="fake-track.customerio.io", retries=1)
    await client.identify(1, name="Test")

    request = httpx_mock.get_request()
    assert request.headers.get("authorization") is not None
    assert "Basic" in request.headers["authorization"]


async def test_eu_region_uses_eu_host(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    client = AsyncCustomerIO(
        site_id="site", api_key="key", region=Regions.EU, host=Regions.EU.track_host, retries=1,
    )
    await client.identify(1, name="EU")

    request = httpx_mock.get_request()
    url = str(request.url)
    assert url.startswith("https://track-eu.customer.io/api/v1/customers/")
