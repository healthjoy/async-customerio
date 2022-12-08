import base64

import pytest
from pytest_httpx import HTTPXMock

from async_customerio import AsyncAPIClient, SendEmailRequest, AsyncCustomerIOError

pytestmark = pytest.mark.asyncio


class FakeSendRequest:
    def __init__(self, to, from_, body):
        pass


@pytest.fixture()
def fake_async_api_client(faker_):
    return AsyncAPIClient(key=faker_.pystr(), url="https://fake-track.customerio.io")


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


