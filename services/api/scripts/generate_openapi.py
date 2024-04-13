import json
from pathlib import Path
from typing import Any

from conftest import build_environment
from devtools.context_manager import EnvironmentContext

OUTPUT_DIR = Path(__file__).parent.parent / "generated"


def write_json(obj: Any, file_name: str):
    with open(OUTPUT_DIR / file_name, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


if __name__ == "__main__":
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    env = (
        build_environment()
    )

    with EnvironmentContext(env):
        from carlos.api.app import app

        write_json(app.openapi(), "openapi.json")