"""
Implements the client that interacts with Customer.io"s App API using app keys.
"""

import base64

from async_customerio._config import DEFAULT_REQUEST_TIMEOUT, RequestTimeout


try:
    from typing import Dict, Literal, Optional, TypedDict, Union
except ImportError:
    from typing_extensions import Dict, Literal, Optional, TypedDict, Union  # type: ignore

from async_customerio.client_base import AsyncClientBase
from async_customerio.errors import AsyncCustomerIOError
from async_customerio.regions import Region, Regions
from async_customerio.utils import join_url


IdentifierID = TypedDict("IdentifierID", {"id": Union[str, int]})
IdentifierEMAIL = TypedDict("IdentifierEMAIL", {"email": str})
IdentifierCIOID = TypedDict("IdentifierCIOID", {"cio_id": Union[str, int]})
CustomDevice = TypedDict(
    "CustomDevice",
    {
        "token": str,
        "platform": Literal["ios", "android"],
        "last_used": Optional[int],
        "attributes": dict,
    },
)


class SendEmailRequest:
    """An object with all the options available for triggering a transactional message"""

    def __init__(
        self,
        transactional_message_id: Optional[Union[str, int]] = None,
        to: Optional[str] = None,
        identifiers: Optional[Union[IdentifierID, IdentifierEMAIL, IdentifierCIOID]] = None,
        _from: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        reply_to: Optional[str] = None,
        bcc: Optional[str] = None,
        subject: Optional[str] = None,
        preheader: Optional[str] = None,
        body: Optional[str] = None,
        body_amp: Optional[str] = None,
        body_plain: Optional[str] = None,
        fake_bcc: Optional[str] = None,
        disable_message_retention: bool = False,
        send_to_unsubscribed: bool = True,
        tracked: bool = True,
        queue_draft: bool = False,
        message_data: Optional[dict] = None,
        attachments: Optional[Dict[str, str]] = None,
        disable_css_preproceessing: bool = False,
        send_at: Optional[int] = None,
        language: Optional[str] = None,
    ):
        self.transactional_message_id = transactional_message_id
        self.to = to
        self.identifiers = identifiers
        self._from = _from
        self.headers = headers
        self.reply_to = reply_to
        self.bcc = bcc
        self.subject = subject
        self.preheader = preheader
        self.body = body
        self.body_plain = body_plain
        self.body_amp = body_amp
        self.fake_bcc = fake_bcc
        self.disable_message_retention = disable_message_retention
        self.send_to_unsubscribed = send_to_unsubscribed
        self.tracked = tracked
        self.queue_draft = queue_draft
        self.message_data = message_data
        self.attachments = attachments
        self.disable_css_preproceessing = disable_css_preproceessing
        self.send_at = send_at
        self.language = language

    def attach(self, name: str, content: str, encode: bool = True) -> None:
        """Helper method to add base64 encode the attachments"""
        if not self.attachments:
            self.attachments = {}

        if self.attachments.get(name, None):
            raise AsyncCustomerIOError("attachment {name} already exists".format(name=name))

        if encode:
            if isinstance(content, str):
                content = base64.b64encode(content.encode("utf-8")).decode()
            else:
                content = base64.b64encode(content).decode()

        self.attachments[name] = content

    def to_dict(self):
        """Build a request payload from the object"""
        field_map = dict(
            # `from` is reserved keyword hence the object has the field
            # `_from` but in the request payload we map it to `from`
            _from="from",
            # field name is the same as the payload field name
            transactional_message_id="transactional_message_id",
            to="to",
            identifiers="identifiers",
            headers="headers",
            reply_to="reply_to",
            bcc="bcc",
            subject="subject",
            preheader="preheader",
            body="body",
            body_amp="body_amp",
            body_plain="body_plain",
            fake_bcc="fake_bcc",
            disable_message_retention="disable_message_retention",
            send_to_unsubscribed="send_to_unsubscribed",
            tracked="tracked",
            queue_draft="queue_draft",
            message_data="message_data",
            attachments="attachments",
            disable_css_preproceessing="disable_css_preproceessing",
            send_at="send_at",
            language="language",
        )

        data = {}
        for field, name in field_map.items():
            value = getattr(self, field, None)
            if value is not None:
                data[name] = value

        return data


class SendPushRequest:
    """An object with all the options available for triggering a transactional push message."""

    def __init__(
        self,
        transactional_message_id: Optional[Union[str, int]] = None,
        to: Union[Literal["all", "last_used"], str] = "all",
        identifiers: Optional[Union[IdentifierID, IdentifierEMAIL, IdentifierCIOID]] = None,
        title: Optional[str] = None,
        message: Optional[str] = None,
        disable_message_retention: bool = False,
        send_to_unsubscribed: bool = True,
        queue_draft: bool = False,
        message_data: Optional[dict] = None,
        send_at: Optional[int] = None,
        language: Optional[str] = None,
        image_url: Optional[str] = None,
        link: Optional[str] = None,
        custom_data: Optional[dict] = None,
        custom_device: Optional[CustomDevice] = None,
        custom_payload: Optional[dict] = None,
        sound: str = "default",
    ) -> None:
        self.transactional_message_id = transactional_message_id
        self.to = to
        self.identifiers = identifiers
        self.disable_message_retention = disable_message_retention
        self.send_to_unsubscribed = send_to_unsubscribed
        self.queue_draft = queue_draft
        self.message_data = message_data
        self.send_at = send_at
        self.language = language

        self.title = title
        self.message = message
        self.image_url = image_url
        self.link = link
        self.custom_data = custom_data
        self.custom_device = custom_device
        self.custom_payload = custom_payload
        self.sound = sound

    def to_dict(self):
        """Build a request payload from the object."""
        field_map = dict(
            # field name is the same as the payload field name
            transactional_message_id="transactional_message_id",
            to="to",
            identifiers="identifiers",
            disable_message_retention="disable_message_retention",
            send_to_unsubscribed="send_to_unsubscribed",
            queue_draft="queue_draft",
            message_data="message_data",
            send_at="send_at",
            language="language",
            title="title",
            message="message",
            image_url="image_url",
            link="link",
            custom_data="custom_data",
            custom_payload="custom_payload",
            device="custom_device",
            sound="sound",
        )

        data = {}
        for field, name in field_map.items():
            value = getattr(self, field, None)
            if value is not None:
                data[name] = value

        return data


class AsyncAPIClient(AsyncClientBase):
    API_PREFIX = "/v1"
    SEND_EMAIL_ENDPOINT = "/send/email"
    SEND_PUSH_NOTIFICATION_ENDPOINT = "/send/push"

    def __init__(
        self,
        key: str,
        url: Optional[str] = None,
        region: Region = Regions.US,
        retries: int = 3,
        request_timeout: RequestTimeout = DEFAULT_REQUEST_TIMEOUT,
    ):
        if not isinstance(region, Region):
            raise AsyncCustomerIOError("invalid region provided")

        self.key = key
        self.base_url = url or "https://{host}".format(host=region.api_host)
        super().__init__(retries=retries, request_timeout=request_timeout)

    async def send_email(self, request: SendEmailRequest) -> dict:
        if not isinstance(request, SendEmailRequest):
            raise AsyncCustomerIOError("invalid request provided")

        return await self.send_request(
            "POST",
            join_url(self.base_url, self.API_PREFIX, self.SEND_EMAIL_ENDPOINT),
            json_payload=request.to_dict(),
            headers={"Authorization": "Bearer {key}".format(key=self.key)},
        )

    async def send_push(self, request: SendPushRequest) -> dict:
        if not isinstance(request, SendPushRequest):
            raise AsyncCustomerIOError("invalid request provided")

        return await self.send_request(
            "POST",
            join_url(self.base_url, self.API_PREFIX, self.SEND_PUSH_NOTIFICATION_ENDPOINT),
            json_payload=request.to_dict(),
            headers={"Authorization": "Bearer {key}".format(key=self.key)},
        )
