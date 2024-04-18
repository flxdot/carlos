import importlib
from pathlib import Path


def load_supported_io():
    """Loads all supported IO modules."""
    for module in Path(__file__).parent.glob("*.py"):
        if not module.name.startswith("_"):
            importlib.import_module(f"{__package__}.{module.stem}")
