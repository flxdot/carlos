"""This module contains code to convert pydantic models into something else."""

__all__ = ["to_environment"]

import json

from pydantic import SecretStr
from pydantic_settings import BaseSettings


def to_environment(settings: BaseSettings) -> dict[str, str]:
    """Converts a BaseSettings object into a dictionary with the configured
    environment variables as keys."""

    # We use `.json()` to use the serialization methods of pydantic for field values
    # This is relevant for lists, dicts, dates, etc...
    environment_values = json.loads(settings.model_dump_json())

    environment = {}
    for field_name, field in settings.model_fields.items():
        native_field_value = getattr(settings, field_name)
        if not isinstance(native_field_value, BaseSettings):
            env_name = settings.model_config["env_prefix"] + field_name
            if not isinstance(native_field_value, SecretStr):
                environment[env_name] = environment_values[field_name]
            else:  # pragma: no cover
                # could not find a better way in the pydantic docs on how to include
                # the value of the secret in the json() method.
                environment[env_name] = native_field_value.get_secret_value()
        else:  # pragma: no cover
            environment |= to_environment(native_field_value)

    if settings.model_config["case_sensitive"]:
        return environment
    return {k.upper(): str(v) for k, v in environment.items()}
