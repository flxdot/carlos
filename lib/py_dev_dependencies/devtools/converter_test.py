import secrets
from typing import Type

import pytest
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .context_manager import EnvironmentContext
from .converter import to_environment


class MockedSettings(BaseSettings):
    lower_case: str = Field("")
    UPPER_CASE: str = Field("")
    value_b: str = Field("")
    VALUE_A: str = Field("")


class MockedSettingsCaseSensitive(MockedSettings):
    model_config = SettingsConfigDict(case_sensitive=True)


class MockedSettingsWithPrefix(MockedSettings):
    model_config = SettingsConfigDict(env_prefix="TEST_PREFIX_")


class MockedSettingsWithPrefixCaseSensitive(MockedSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="TEST_PREFIX_")


@pytest.mark.parametrize(
    "settings_class",
    [
        MockedSettings,
        MockedSettingsCaseSensitive,
        MockedSettingsWithPrefix,
        MockedSettingsWithPrefixCaseSensitive,
    ],
)
def test_to_environment(settings_class: Type[MockedSettings]):
    settings = settings_class(
        lower_case=secrets.token_hex(4),
        UPPER_CASE=secrets.token_hex(4),
        value_b=secrets.token_hex(4),
        VALUE_A=secrets.token_hex(4),
    )

    environment = to_environment(settings)
    with EnvironmentContext(environment, overwrite_existing=True):
        settings_from_env = settings_class()
        assert settings_from_env == settings
