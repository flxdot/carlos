import os
from pathlib import Path
from typing import Any, Dict

import pytest

from .context_manager import EnvironmentContext, TemporaryWorkingDirectory


class TestEnvironmentContext:
    @pytest.mark.parametrize(
        "wanted_environment, existing_environment, overwrite_existing, expected_change",
        [
            pytest.param({}, {}, False, {}, id="empty"),
            pytest.param(
                {"var_123": "1"}, {}, False, {"var_123": "1"}, id="new-variable"
            ),
            pytest.param(
                {"var_234": "1"},
                {"var_234": "0"},
                False,
                {},
                id="no-overwrite-existing",
            ),
            pytest.param(
                {"var_345": "1"},
                {"var_345": "0"},
                True,
                {"var_345": "1"},
                id="no-overwrite-existing",
            ),
        ],
    )
    def test(
        self,
        wanted_environment: Dict[str, Any],
        existing_environment: Dict[str, Any],
        overwrite_existing: bool,
        expected_change: Dict[str, Any],
    ):
        """Proofs the functionality of the EnvironmentContext manager."""

        for k, v in existing_environment.items():
            os.environ[k] = str(v)

        starting_environment = dict(os.environ)

        with EnvironmentContext(
            wanted_environment, overwrite_existing=overwrite_existing
        ):
            context_environment = dict(os.environ)
            environment_change = {
                k: v
                for k, v in context_environment.items()
                if k not in starting_environment
                or starting_environment[k] != context_environment[k]
            }
            assert environment_change == expected_change

        # ensure the environment has been reset to its original state
        assert dict(os.environ) == starting_environment


class TestTemporaryWorkingDirectory:
    def test(self, tmp_path):
        # proof that the current working directory is different from the wanted working
        # directory
        start_working_dir = Path.cwd()
        assert start_working_dir != tmp_path

        with TemporaryWorkingDirectory(tmp_path):
            # proof that the context manager switched the working directory to the
            # wanted directory
            assert Path.cwd() == tmp_path

        # proof that the context manager switched back to the original working directory
        assert start_working_dir == Path.cwd()
