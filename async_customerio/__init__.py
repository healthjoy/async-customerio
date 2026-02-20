import logging

from async_customerio.api import (  # noqa
    AsyncAPIClient,
    SendEmailRequest,
    SendInboxMessageRequest,
    SendPushRequest,
    SendSMSRequest,
)
from async_customerio.constants import (  # noqa
    IdentifierCIOObject,
    IdentifierObject,
    ObjectIdentifiers,
    PersonIdentifiers,
)
from async_customerio.errors import AsyncCustomerIOError, AsyncCustomerIORetryableError  # noqa
from async_customerio.regions import Regions  # noqa
from async_customerio.request_validator import validate_signature  # noqa
from async_customerio.track import AsyncCustomerIO  # noqa
from async_customerio.track_v2 import Actions, EntityPayload, TrackAPIV2  # noqa


root_logger = logging.getLogger("async_customerio")
if root_logger.level == logging.NOTSET:
    root_logger.setLevel(logging.WARN)
