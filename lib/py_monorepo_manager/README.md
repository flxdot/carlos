# Monorepo Manager

This is a tool to help manage the Carlos Monorepository.

It aims to reduce the amount of manual work required to maintain the monorepo by
automating the following tasks:

- Project boilerplate generation: `Makefile`, `poetry.toml`, ... (depends on language)
- Generation of CI configuration files: `.github/workflows/...`

## Installation

```bash
poetry add ../../lib/py_monorepo_manager
```

## Usage

The monorepo manager is a CLI tool:

```
Usage: monorepo_manager [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  all      Run the manager for all projects.
  project  Run the manager for a specific project.
```

### Updating the monorepo

```bash
make boilerplate
```

This will check for new projects and regenerate all managed boilerplate files.
This command is run automatically on every open Pull Request.

### Updating a specific project

```bash
poetry run monorepo_manager project lib/py_monorepo_manager
```

This will update the boilerplate files of a specific project.

## Configuration

It stores its configuration in a file
called `.monorepo_manager.yaml` in the root of the monorepo.

This file contains a list of services and libraries (project) that are part of the monorepo. New
projects are added automatically via a GitHub Action when a Pull request introduces a
new project.

The format of the configuration file is as follows:

_Default options wrapped are in square brackets `[]` and may be omitted from the
config file. `[[]]` refers to an empty list._

```yaml
{RELATIVE_PROJECT_PATH}:
    language: python | javascript | rust | binary
    continuous_integration:
      additional_files_to_watch: [[]]
```

Where the `RELATIVE_PROJECT_PATH` is the path to the project relative to the root of
the monorepo, for example `lib/py_monorepo_manager`.

Depending on the `language` attribute the configuration options are different.
The following sections describe the configuration options for each language.

### Python

```yaml
{RELATIVE_PROJECT_PATH}:
    language: python
    coverage:
        enabled: [true] | false
        threshold: [100]
    pylint:
        enabled: [true] | false
        config: [../../pyproject.toml]
    mypy:
        enabled: [true] | false
    deptry:
        enabled: true | [false]
    makefile:
       update_venv:
          - rm -rf .venv && poetry install
       update_dependencies:
          - rm -rf .venv && poetry lock && poetry install
```

- `makefile` (Optional)
  May be used to define additional entries in the Makefile of the project.
  The keys are used as the name of the target in the Makefile.
  The value is a list of commands that will be executed when the target is called.

### JavaScript

```yaml
```

### Rust

```yaml
```

### Binary

```yaml
```
