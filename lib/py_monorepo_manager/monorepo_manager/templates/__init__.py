__all__ = ["GENERAL_JINJA_ENVIRONMENT", "GENERAL_TEMPLATE_TO_PATH"]

from pathlib import Path

from monorepo_manager.jinja_environment import build_environment

GENERAL_JINJA_ENVIRONMENT = build_environment(Path(__file__).parent)

GENERAL_TEMPLATE_TO_PATH = {
    "update_all_python_venvs.sh.jinja2": ("/scripts/update_all_python_venvs.sh"),
}
