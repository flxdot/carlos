__all__ = ["PYTHON_JINJA_ENVIRONMENT", "PYTHON_TEMPLATE_TO_PATH"]

from pathlib import Path

from monorepo_manager.jinja_environment import build_environment

PYTHON_JINJA_ENVIRONMENT = build_environment(Path(__file__).parent)

PYTHON_TEMPLATE_TO_PATH = {
    "Makefile.jinja2": "Makefile",
    "poetry.toml.jinja2": "poetry.toml",
    "ci.yml.jinja2": (
        "/.github/workflows/test-{{ project.path_from_root|replace('/', '-') }}.yml"
    ),
}
