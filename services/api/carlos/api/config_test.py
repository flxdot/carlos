import logging
from contextlib import nullcontext
from typing import Any

import pytest
from pydantic import ValidationError

from carlos.api.config import CarlosAPISettings


class TestCarlosAPISettings:

    @pytest.mark.parametrize(
        "field, value, expected",
        [
            pytest.param("LOG_LEVEL", "INFO", logging.INFO, id="log_level: str"),
            pytest.param("LOG_LEVEL", logging.INFO, logging.INFO, id="log_level: int"),
            pytest.param("LOG_LEVEL", 1.2, ValidationError, id="invalid log_level"),
        ],
    )
    def test_validation(self, field: str, value: Any, expected: type[Exception] | Any):
        """This tests the validators of the settings"""

        if isinstance(expected, type) and issubclass(expected, BaseException):
            context = pytest.raises(expected)
        else:
            context = nullcontext()

        with context:
            settings = CarlosAPISettings.model_validate({field: value})
            assert getattr(settings, field) == expected
