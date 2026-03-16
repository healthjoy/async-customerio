"""Pluggable retry strategy for async-customerio."""

import typing as t

from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class RetryStrategy(Protocol):
    """Protocol that any retry strategy must implement.

    The strategy receives an async callable and must return its result,
    applying whatever retry logic it sees fit (backoff, jitter, max attempts, etc.).

    Only calls that raise ``AsyncCustomerIORetryableError`` should be retried;
    any other exception must be re-raised immediately.

    Example — wrapping *tenacity*::

        from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

        from async_customerio import AsyncCustomerIORetryableError, RetryStrategy

        class TenacityRetryStrategy:
            def __init__(self, **kwargs):
                self._kwargs = kwargs

            async def execute(self, func, *args, **kwargs):
                async for attempt in AsyncRetrying(
                    retry=retry_if_exception_type(AsyncCustomerIORetryableError),
                    **self._kwargs,
                ):
                    with attempt:
                        return await func(*args, **kwargs)
    """

    async def execute(
        self,
        func: t.Callable[..., t.Awaitable[t.Any]],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> t.Any:
        """Execute *func* with retry logic.

        :param func: the async callable to invoke.
        :param args: positional arguments forwarded to *func*.
        :param kwargs: keyword arguments forwarded to *func*.
        :return: the return value of *func*.
        """
        ...
