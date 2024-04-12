from datetime import datetime

import pytest
from pydantic import BaseModel

from carlos.database.schema import DateTimeWithTimeZone
from carlos.database.utils import utcnow


class TestDateTimeWithTimeZone:

    class TempModel(BaseModel):
        dt: DateTimeWithTimeZone

    def test_validation(self):
        """This test ensures that the `DateTimeWithTimeZone` type annotation
        ensures that each datetime object has a timezone."""

        model = self.TempModel(dt=utcnow())
        assert model.dt.tzinfo is not None
        assert isinstance(model.dt, datetime)

        with pytest.raises(ValueError):
            self.TempModel(dt=datetime.now())
