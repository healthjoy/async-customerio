import base64

import httpx
import pytest
from pytest_httpx import HTTPXMock

from async_customerio import (
    AsyncAPIClient,
    AsyncCustomerIOError,
    AsyncCustomerIORetryableError,
    SendEmailRequest,
    SendPushRequest,
    SendSMSRequest,
)

pytestmark = pytest.mark.asyncio


class FakeSendRequest:
    def __init__(self, to, from_, body):
        pass


@pytest.fixture()
def fake_async_api_client(faker_):
    return AsyncAPIClient(key=faker_.pystr(), url="https://fake-track.customerio.io", retries=1)


@pytest.mark.parametrize(
    "send_email_request", (
        SendEmailRequest(to="johnsmith@doh.com", _from="johndoh@smith.com", body="Hi there!"),
        SendEmailRequest(to="bunny@luneytunes.com", _from="bigfan@domain.com", subject="That's Amazing"),
        SendEmailRequest(
            to="agent007@company.com",
            _from="agent006",
            subject="Top Secret",
            attachments={
                "file_1": base64.b64encode(b"QQQQQQQQQQ").decode(),
                "file_2": base64.b64encode(b"WWWWWWWWWW").decode()
            }
        )
    )
)
async def test_send_email(send_email_request, fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    response = await fake_async_api_client.send_email(send_email_request)
    assert response


@pytest.mark.parametrize(
    "invalid_request", (
        {"to": "to@to.com", "from": "from@from.com", "body": '"body'},
        FakeSendRequest("john@doh.com", "billy@jean.com", "Whiskey"),
    )
)
async def test_send_email_invalid_request(invalid_request, fake_async_api_client):
    with pytest.raises(AsyncCustomerIOError, match="invalid request provided"):
        await fake_async_api_client.send_email(invalid_request)


async def test_wrong_region_provided(faker_):
    with pytest.raises(AsyncCustomerIOError, match="invalid region provided"):
        AsyncAPIClient(faker_.pystr(), region="CN")


async def test_unauthorized_request(fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=401)
    with pytest.raises(AsyncCustomerIOError):
        await fake_async_api_client.send_email(
            SendEmailRequest(to="johnsmith@doh.com", _from="johndoh@smith.com", body="Hi there!")
        )


@pytest.mark.parametrize("connection_error", (httpx.ConnectError, httpx.ConnectTimeout))
async def test_client_connection_handling(connection_error, fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(connection_error("something went wrong"))
    with pytest.raises(AsyncCustomerIORetryableError):
        await fake_async_api_client.send_email(
            SendEmailRequest(to="johnsmith@doh.com", _from="johndoh@smith.com", body="Hi there!")
        )


async def test_read_error_handling(fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(httpx.ReadError("failed to read response"))
    with pytest.raises(AsyncCustomerIORetryableError):
        await fake_async_api_client.send_email(
            SendEmailRequest(to="johnsmith@doh.com", _from="johndoh@smith.com", body="Hi there!")
        )


async def test_bad_gateway_error_handling(fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=502)
    with pytest.raises(AsyncCustomerIORetryableError):
        await fake_async_api_client.send_email(
            SendEmailRequest(to="johnsmith@doh.com", _from="johndoh@smith.com", body="Hi there!")
        )


@pytest.mark.parametrize(
    "send_push_request", (
        SendPushRequest(transactional_message_id="3", identifiers={"id": "2"}),
        SendPushRequest(transactional_message_id="3", to="last_used"),
        SendPushRequest(
            transactional_message_id="3",
            custom_device={
                "token": "XXXqwsdae123x213",
                "platform": "android",
                "last_used": 1701435945,
            }
        )
    )
)
async def test_send_push(send_push_request, fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    response = await fake_async_api_client.send_push(send_push_request)
    assert response


@pytest.mark.parametrize(
    "invalid_request", (
        {"to": "to@to.com", "from": "from@from.com", "body": '"body'},
        FakeSendRequest("john@doh.com", "billy@jean.com", "Whiskey"),
    )
)
async def test_send_push_invalid_request(invalid_request, fake_async_api_client):
    with pytest.raises(AsyncCustomerIOError, match="invalid request provided"):
        await fake_async_api_client.send_push(invalid_request)


@pytest.mark.parametrize(
    "send_sms_request", (
        SendSMSRequest(transactional_message_id="3", identifiers={"id": "2"}),
        SendSMSRequest(transactional_message_id="3", to="+15551234567"),
        SendSMSRequest(
            transactional_message_id="3",
            message_data={
                "attr_1": "value_1",
                "attr_2": "value_2",
            }
        )
    )
)
async def test_send_sms(send_sms_request, fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    response = await fake_async_api_client.send_sms(send_sms_request)
    assert response


@pytest.mark.parametrize(
    "invalid_request", (
        {"to": "0999888777", "from": "+15551234567"},
        FakeSendRequest("john@doh.com", "billy@jean.com", "Whiskey"),
    )
)
async def test_send_sms_invalid_request(invalid_request, fake_async_api_client):
    with pytest.raises(AsyncCustomerIOError, match="invalid request provided"):
        await fake_async_api_client.send_sms(invalid_request)
