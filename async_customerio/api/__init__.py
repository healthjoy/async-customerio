"""App API client package for Customer.io.

This package provides the client for interacting with Customer.io's App API,
including transactional messaging (email, push, SMS, inbox messages).
"""

from async_customerio.api._client import AsyncAPIClient
from async_customerio.api.send import (
    CustomDevice,
    SendEmailRequest,
    SendInboxMessageRequest,
    SendPushRequest,
    SendSMSRequest,
)


__all__ = [
    "AsyncAPIClient",
    "CustomDevice",
    "SendEmailRequest",
    "SendInboxMessageRequest",
    "SendPushRequest",
    "SendSMSRequest",
]
