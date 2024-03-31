__all__ = ["RetryStrategy", "BackOffRetryStrategy"]

from abc import ABC, abstractmethod
from asyncio import sleep
from datetime import timedelta
from typing import Awaitable, Callable, TypeVar

from loguru import logger

FunctionReturn = TypeVar("FunctionReturn")
FunctionToTry = Callable[[], Awaitable[FunctionReturn]]
BackoffFcn = Callable[[timedelta], timedelta]


class RetryStrategy(ABC):
    """Common base class to retry functions until they succeed or a other
    condition is met."""

    @abstractmethod
    async def retry_until_success(
        self,
        func: FunctionToTry,
        expected_exceptions: tuple[type[Exception], ...],
    ) -> FunctionReturn:
        """Retry the function until it succeeds.

        :param func: A sync function without arguments. If your function requires
            arguments, use functools.partial.
        :param expected_exceptions: The exceptions that is expected to be raised.
            Any other exception will be raised immediately.
        """
        raise NotImplementedError()


class BackOffRetryStrategy(RetryStrategy):
    """A retry strategy that retries a function call with a backoff strategy."""

    @staticmethod
    def exponential_backoff_factory(factor: int) -> BackoffFcn:
        """Creates a function that returns the next backoff time based on the
        previous backoff time.

        :param base: The base backoff time.
        :param factor: The factor to increase the backoff time.
        :return: A function that returns the next backoff time.
        """

        def next_backoff(previous_backoff: timedelta) -> timedelta:
            return previous_backoff * factor

        return next_backoff

    def __init__(
        self,
        backoff_fcn: BackoffFcn | None = None,
        start: timedelta = timedelta(seconds=1),
        max_backoff: timedelta | None = timedelta(minutes=5),
    ):
        """Initializes the retry strategy.

        :param backoff_fcn: The backoff function to use.
        :param start: The initial backoff time."""

        self.backoff_fcn = backoff_fcn or self.exponential_backoff_factory(factor=2)
        self.initial_backoff = start
        self.max_backoff = max_backoff

    async def retry_until_success(
        self,
        func: FunctionToTry,
        expected_exceptions: tuple[type[BaseException], ...],
    ):
        """Retry the function until it succeeds.

        :param func: A sync function without arguments. If your function requires
            arguments, use functools.partial.
        :param expected_exceptions: The exception that is expected to be raised.
            Any other exception will be raised immediately.
        """

        backoff_time = timedelta(seconds=self.initial_backoff.total_seconds())

        while True:
            try:
                return await func()
            except expected_exceptions:
                logger.info(
                    f"Failed to run function: {func}. Retrying in"
                    f" {backoff_time.total_seconds()}s."
                )

            await sleep(backoff_time.total_seconds())

            backoff_time = self.backoff_fcn(backoff_time)
            if self.max_backoff is not None:
                backoff_time = min(backoff_time, self.max_backoff)
