import logging

from async_customerio.api import AsyncAPIClient, SendEmailRequest, SendPushRequest  # noqa
from async_customerio.errors import AsyncCustomerIOError, AsyncCustomerIORetryableError  # noqa
from async_customerio.regions import Regions  # noqa
from async_customerio.request_validator import validate_signature  # noqa
from async_customerio.track import AsyncCustomerIO  # noqa


root_logger = logging.getLogger("async_customerio")
if root_logger.level == logging.NOTSET:
    root_logger.setLevel(logging.WARN)
