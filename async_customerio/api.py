"""
Implements the client that interacts with Customer.io"s App API using app keys.
"""
import base64
import typing as t

from typing_extensions import TypedDict

from async_customerio.client_base import AsyncClientBase
from async_customerio.errors import AsyncCustomerIOError
from async_customerio.regions import Region, Regions
from async_customerio.utils import join_url


IdentifierID = TypedDict("IdentifierID", {"id": t.Union[str, int]})
IdentifierEMAIL = TypedDict("IdentifierEMAIL", {"email": str})
IdentifierCIOID = TypedDict("IdentifierCIOID", {"cio_id": t.Union[str, int]})


class SendEmailRequest:
    """An object with all the options available for triggering a transactional message"""

    def __init__(
        self,
        transactional_message_id: t.Union[str, int] = None,
        to: str = None,
        identifiers: t.Union[IdentifierID, IdentifierEMAIL, IdentifierCIOID] = None,
        _from: str = None,
        headers: t.Dict[str, str] = None,
        reply_to: str = None,
        bcc: str = None,
        subject: str = None,
        preheader: str = None,
        body: str = None,
        plaintext_body: str = None,
        amp_body: str = None,
        fake_bcc: str = None,
        disable_message_retention: bool = None,
        send_to_unsubscribed: bool = None,
        tracked: bool = None,
        queue_draft: bool = None,
        message_data: dict = None,
        attachments: t.Dict[str, str] = None,
        disable_css_preproceessing: bool = None,
        send_at: int = None,
        language: str = None,
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
        self.plaintext_body = plaintext_body
        self.amp_body = amp_body
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
            plaintext_body="plaintext_body",
            amp_body="amp_body",
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


class AsyncAPIClient(AsyncClientBase):
    API_PREFIX = "/v1"
    SEND_EMAIL_ENDPOINT = "/send/email"

    def __init__(
        self, key: str, url: t.Optional[str] = None, region: Region = Regions.US, retries: int = 3, timeout: int = 10
    ):
        if not isinstance(region, Region):
            raise AsyncCustomerIOError("invalid region provided")

        self.key = key
        self.base_url = url or "https://{host}".format(host=region.api_host)
        super().__init__(retries=retries, timeout=timeout)

    async def send_email(self, request: SendEmailRequest) -> dict:
        if not isinstance(request, SendEmailRequest):
            raise AsyncCustomerIOError("invalid request provided")

        return await self.send_request(
            "POST",
            join_url(self.base_url, self.API_PREFIX, self.SEND_EMAIL_ENDPOINT),
            json_payload=request.to_dict(),
            headers={"Authorization": "Bearer {key}".format(key=self.key)},
        )
