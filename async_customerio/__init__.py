import logging

from async_customerio.errors import AsyncCustomerIOError
from async_customerio.track import AsyncCustomerIO
from async_customerio.api import AsyncAPIClient, SendEmailRequest
from async_customerio.regions import Regions


root_logger = logging.getLogger("async_customerio")
if root_logger.level == logging.NOTSET:
    root_logger.setLevel(logging.WARN)
