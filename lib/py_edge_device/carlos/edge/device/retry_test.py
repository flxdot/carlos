import time
from datetime import datetime, timedelta
from functools import partial

import pytest
from dirty_equals import IsApprox

from .retry import BackOff, NoRetry


class TestNoRetry:

    @pytest.mark.asyncio
    async def test_no_retry(self):
        """This function ensures that the NoRetry class does fail immediately on failure
        but return the results of the function if it succeeds."""

        retry = NoRetry()

        # Test failing function
        async def failing_fcn():
            raise ValueError("I am failing")

        with pytest.raises(ValueError):
            await retry.execute(func=failing_fcn, expected_exceptions=(ValueError,))

        # Test working function
        async def working_fcn():
            return True

        assert (
            await retry.execute(func=working_fcn, expected_exceptions=(ValueError,))
            is True
        )


class TestBackOff:

    @pytest.mark.asyncio
    async def test_backoff(self):
        """This function ensures that the BackOff class does retry the function with a
        backoff strategy."""

        # use 100ms as start time to speed up the test
        retry = BackOff(
            start=timedelta(milliseconds=100),
            backoff_fcn=BackOff.exponential_backoff_factory(2),
            max_backoff=timedelta(milliseconds=250),
        )

        async def succeed_after_3_sec(initial: datetime) -> bool:
            """This function raises a ValueError if the difference between the
            initial time and the current time is less than 3 seconds."""

            if (datetime.now() - initial).total_seconds() < 0.4:
                raise ValueError("I am failing")
            return True

        # Measure the time it task
        t1 = time.time()
        assert (
            await retry.execute(
                func=partial(succeed_after_3_sec, initial=datetime.now()),
                expected_exceptions=(ValueError,),
            )
            is True
        )
        elapsed_time = time.time() - t1

        # We expect the function to take around 400ms to complete:
        # 100ms + 200ms + 250ms = 550ms
        # Due to the max limit of the backoff the 3rd retry is capped at 250ms
        assert elapsed_time == IsApprox(
            approx=0.55, delta=0.05
        ), "The elapsed time should be around 0.3 seconds."
