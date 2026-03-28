import base64
import json

import httpx
import pytest
from pytest_httpx import HTTPXMock

from async_customerio import (
    AsyncAPIClient,
    AsyncCustomerIOError,
    AsyncCustomerIORetryableError,
    SendEmailRequest,
    SendInboxMessageRequest,
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


@pytest.mark.parametrize(
    "send_inbox_message_request", (
        SendInboxMessageRequest(transactional_message_id="3", identifiers={"id": "2"}),
        SendInboxMessageRequest(
            transactional_message_id="3",
            identifiers={"email": "test@example.com"},
        ),
        SendInboxMessageRequest(
            transactional_message_id="3",
            identifiers={"id": "2"},
            message_data={
                "attr_1": "value_1",
                "attr_2": "value_2",
            },
        ),
    )
)
async def test_send_inbox_message(send_inbox_message_request, fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    response = await fake_async_api_client.send_inbox_message(send_inbox_message_request)
    assert response


@pytest.mark.parametrize(
    "invalid_request", (
        {"transactional_message_id": "3", "identifiers": {"id": "2"}},
        FakeSendRequest("john@doh.com", "billy@jean.com", "Whiskey"),
    )
)
async def test_send_inbox_message_invalid_request(invalid_request, fake_async_api_client):
    with pytest.raises(AsyncCustomerIOError, match="invalid request provided"):
        await fake_async_api_client.send_inbox_message(invalid_request)


async def test_send_email_request_to_dict_full():
    req = SendEmailRequest(
        transactional_message_id="42",
        to="user@example.com",
        identifiers={"id": "123"},
        _from="sender@example.com",
        headers={"X-Custom": "value"},
        reply_to="reply@example.com",
        bcc="bcc@example.com",
        subject="Hello",
        preheader="Preview text",
        body="<h1>Hi</h1>",
        body_amp="<h1>AMP</h1>",
        body_plain="Hi plain",
        fake_bcc=True,
        disable_message_retention=True,
        send_to_unsubscribed=False,
        tracked=False,
        queue_draft=True,
        message_data={"key": "val"},
        attachments={"doc.pdf": "base64data"},
        disable_css_preprocessing=True,
        send_at=1700000000,
        language="en",
    )
    result = req.to_dict()

    assert "from" in result
    assert result["from"] == "sender@example.com"
    assert "_from" not in result

    assert "disable_css_preprocessing" in result
    assert "disable_css_preproceessing" not in result

    assert result["fake_bcc"] is True

    assert result["transactional_message_id"] == "42"
    assert result["to"] == "user@example.com"
    assert result["identifiers"] == {"id": "123"}
    assert result["headers"] == {"X-Custom": "value"}
    assert result["reply_to"] == "reply@example.com"
    assert result["bcc"] == "bcc@example.com"
    assert result["subject"] == "Hello"
    assert result["preheader"] == "Preview text"
    assert result["body"] == "<h1>Hi</h1>"
    assert result["body_amp"] == "<h1>AMP</h1>"
    assert result["body_plain"] == "Hi plain"
    assert result["disable_message_retention"] is True
    assert result["send_to_unsubscribed"] is False
    assert result["tracked"] is False
    assert result["queue_draft"] is True
    assert result["message_data"] == {"key": "val"}
    assert result["attachments"] == {"doc.pdf": "base64data"}
    assert result["disable_css_preprocessing"] is True
    assert result["send_at"] == 1700000000
    assert result["language"] == "en"


async def test_send_email_request_to_dict_minimal():
    req = SendEmailRequest(to="a@b.com")
    result = req.to_dict()

    assert result["to"] == "a@b.com"

    for key in ("from", "transactional_message_id", "identifiers", "headers",
                "reply_to", "bcc", "subject", "preheader", "body", "body_amp",
                "body_plain", "fake_bcc", "message_data", "attachments",
                "send_at", "language"):
        assert key not in result, f"Expected key '{key}' to be excluded when None"


async def test_send_email_request_to_dict_from_mapping():
    req = SendEmailRequest(_from="sender@test.com")
    result = req.to_dict()

    assert "from" in result
    assert result["from"] == "sender@test.com"
    assert "_from" not in result


async def test_send_email_request_to_dict_fake_bcc_is_bool():
    req = SendEmailRequest(fake_bcc=True)
    result = req.to_dict()

    assert isinstance(result["fake_bcc"], bool)
    assert result["fake_bcc"] is True


async def test_send_email_request_to_dict_disable_css_preprocessing_key():
    req = SendEmailRequest(disable_css_preprocessing=True)
    result = req.to_dict()

    assert "disable_css_preprocessing" in result


async def test_send_email_attach_base64_encodes():
    req = SendEmailRequest(to="a@b.com")
    req.attach("f.txt", "hello")

    expected = base64.b64encode(b"hello").decode()
    assert req.attachments["f.txt"] == expected


async def test_send_email_attach_no_encode():
    req = SendEmailRequest(to="a@b.com")
    req.attach("f.txt", "already-encoded", encode=False)

    assert req.attachments["f.txt"] == "already-encoded"


async def test_send_email_attach_duplicate_raises():
    req = SendEmailRequest(to="a@b.com")
    req.attach("f.txt", "hello")

    with pytest.raises(AsyncCustomerIOError, match="attachment f.txt already exists"):
        req.attach("f.txt", "world")


async def test_send_email_attach_bytes_content():
    req = SendEmailRequest(to="a@b.com")
    req.attach("f.bin", b"\x00\x01\x02")

    expected = base64.b64encode(b"\x00\x01\x02").decode()
    assert req.attachments["f.bin"] == expected


async def test_send_push_request_to_dict():
    device = {
        "token": "abc123",
        "platform": "android",
        "last_used": 1701435945,
    }
    req = SendPushRequest(
        transactional_message_id="10",
        to="last_used",
        identifiers={"id": "user1"},
        title="Alert",
        message="You have a notification",
        disable_message_retention=True,
        send_to_unsubscribed=False,
        queue_draft=True,
        message_data={"k": "v"},
        send_at=1700000000,
        language="es",
        image_url="https://img.example.com/pic.png",
        link="https://example.com/action",
        custom_data={"extra": "data"},
        custom_device=device,
        custom_payload={"apns": {"aps": {"sound": "chime"}}},
        sound="chime",
    )
    result = req.to_dict()

    assert result["transactional_message_id"] == "10"
    assert result["to"] == "last_used"
    assert result["identifiers"] == {"id": "user1"}
    assert result["title"] == "Alert"
    assert result["message"] == "You have a notification"
    assert result["disable_message_retention"] is True
    assert result["send_to_unsubscribed"] is False
    assert result["queue_draft"] is True
    assert result["message_data"] == {"k": "v"}
    assert result["send_at"] == 1700000000
    assert result["language"] == "es"
    assert result["image_url"] == "https://img.example.com/pic.png"
    assert result["link"] == "https://example.com/action"
    assert result["custom_data"] == {"extra": "data"}
    assert result["custom_device"] == device
    assert result["custom_payload"] == {"apns": {"aps": {"sound": "chime"}}}
    assert result["sound"] == "chime"


async def test_send_sms_request_to_dict_from_mapping():
    req = SendSMSRequest(_from="+15551234")
    result = req.to_dict()

    assert "from" in result
    assert result["from"] == "+15551234"
    assert "_from" not in result


async def test_send_inbox_message_request_to_dict():
    req = SendInboxMessageRequest(
        transactional_message_id="7",
        identifiers={"email": "test@example.com"},
        disable_message_retention=True,
        queue_draft=True,
        message_data={"greeting": "Hello"},
        send_at=1700000000,
        language="fr",
    )
    result = req.to_dict()

    assert result["transactional_message_id"] == "7"
    assert result["identifiers"] == {"email": "test@example.com"}
    assert result["disable_message_retention"] is True
    assert result["queue_draft"] is True
    assert result["message_data"] == {"greeting": "Hello"}
    assert result["send_at"] == 1700000000
    assert result["language"] == "fr"


async def test_send_email_request_url_and_method(fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_api_client.send_email(
        SendEmailRequest(to="user@example.com", body="Hi")
    )
    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert request.url.path == "/v1/send/email"


async def test_send_push_request_url_and_method(fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_api_client.send_push(
        SendPushRequest(transactional_message_id="1", identifiers={"id": "2"})
    )
    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert request.url.path == "/v1/send/push"


async def test_send_sms_request_url_and_method(fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_api_client.send_sms(
        SendSMSRequest(transactional_message_id="1", to="+15551234567")
    )
    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert request.url.path == "/v1/send/sms"


async def test_send_inbox_message_request_url_and_method(fake_async_api_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})
    await fake_async_api_client.send_inbox_message(
        SendInboxMessageRequest(transactional_message_id="1", identifiers={"id": "2"})
    )
    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert request.url.path == "/v1/send/inbox_message"


async def test_auth_header_uses_bearer_token(httpx_mock: HTTPXMock):
    known_key = "my-secret-api-key"
    client = AsyncAPIClient(key=known_key, url="https://fake-track.customerio.io", retries=1)
    httpx_mock.add_response(status_code=200, json={"success": True})
    await client.send_email(
        SendEmailRequest(to="user@example.com", body="Hi")
    )
    request = httpx_mock.get_request()
    assert request.headers["authorization"] == f"Bearer {known_key}"
    await client.close()
