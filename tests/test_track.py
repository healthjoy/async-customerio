from datetime import datetime

import httpx
import pytest
from pytest_httpx import HTTPXMock

from async_customerio import AsyncCustomerIO, AsyncCustomerIOError
from async_customerio.constants import CIOID, EMAIL, ID

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
    with pytest.raises(AsyncCustomerIOError, match="id_ cannot be blank in identify"):
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
        ("identify", {"id_": 1, "name": "Jack"}),
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
    with pytest.raises(AsyncCustomerIOError):
        await fake_async_customerio.identify(faker_.pyint(min_value=100))
