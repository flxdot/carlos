# Python development dependencies

The purpose of this empty project is to have consistent python development dependencies across all projects.

## Installation

To use these development dependencies in your project, add the following lines to your `pyproject.toml` file:

```toml
...

[tool.poetry.group.dev.dependencies]
"devtools" = {path = "../../lib/py_dev_dependencies"}
...


[tool.isort]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
line_length = 88

[tool.mypy]
plugins = [
    "sqlalchemy.ext.mypy.plugin",
    "pydantic.mypy"
]
exclude = ['.*_test\.py$']

[tool.coverage.report]
exclude_lines = [
    # Have to re-enable the standard pragma
    "pragma: no cover",
    # Don't complain about missing debug-only code:
    "def __repr__",
    "def __hash__",
    # Don't complain if imports are not covered:
    "^import .*",
    "^from .* import .*",
    "__all__ = .*",
    # Don't complain if tests don't hit defensive assertion code:
    "raise NotImplementedError",
    # Don't complain about abstract methods, they aren't run:
    "@(abc\\.)?abstractmethod",
    # Don't complain about guard clauses
    "if __name__ == .__main__.:",
]
omit = [
    # omit all tests
    "*_test.py",
]
```
