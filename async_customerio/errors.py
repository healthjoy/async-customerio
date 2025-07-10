"""Async CustomerIO errors."""


class BaseAsyncCustomerIOError(Exception):
    """Base error for Async CustomerIO."""


class AsyncCustomerIOError(BaseAsyncCustomerIOError):
    pass


class AsyncCustomerIORetryableError(BaseAsyncCustomerIOError):
    pass
