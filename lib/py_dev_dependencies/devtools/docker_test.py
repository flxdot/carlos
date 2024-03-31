from contextlib import nullcontext
from typing import Any

import pytest
from pydantic import ValidationError

from devtools.docker import ContainerDefinition


class TestContainerDefinition:

    @pytest.mark.parametrize(
        "field, value, expected_exception",
        [
            pytest.param("image", "", ValidationError, id="empty"),
            pytest.param("image", ":latest", ValidationError, id="empty image"),
            pytest.param("image", "naginx:", ValidationError, id="empty tag"),
            pytest.param(
                "image", "nginx", ValidationError, id="missing tag from image"
            ),
            pytest.param("ports", {"80": 80}, ValidationError, id="missing protocol"),
            pytest.param(
                "ports", {"80/prot": 80}, ValidationError, id="invalid protocol"
            ),
            pytest.param(
                "ports",
                {"eighty/tcp": 80},
                ValidationError,
                id="invalid container port",
            ),
        ],
    )
    def test_validation(
        self, field: str, value: Any, expected_exception: type[Exception] | None
    ):
        """This test ensures that the `ContainerDefinition` class validates the
        input correctly."""

        if expected_exception is None:
            context = nullcontext()
        else:
            context = pytest.raises(expected_exception)

        container_def_data = {
            "name": "nginx-1",
            "image": "nginx:latest",
            field: value,
        }

        with context:
            ContainerDefinition.model_validate(container_def_data)
