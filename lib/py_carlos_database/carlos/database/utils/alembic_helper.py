from configparser import ConfigParser
from contextlib import contextmanager
from enum import Enum
from logging.config import fileConfig
from pathlib import Path
from typing import Union

from alembic import command
from alembic.config import Config
from loguru import logger

from carlos.database.config import DatabaseConnectionSettings

__all__ = [
    "Direction",
    "Revision",
    "alembic_downgrade",
    "alembic_upgrade",
    "build_alembic_config",
]


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"

    def __str__(self):
        return self.value


class Revision(str, Enum):
    HEAD = "head"
    BASE = "base"

    def __str__(self):
        return self.value


ALEMBIC_FILE_TEMPLATE = "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s"


def build_alembic_config(
    connection_settings: DatabaseConnectionSettings, migration_directory: Path
) -> Config:
    """Builds a new alembic config programmatically."""

    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        "sqlalchemy.url", connection_settings.url.render_as_string(hide_password=False)
    )

    # path to migration scripts
    alembic_cfg.set_main_option("script_location", str(migration_directory))

    # template used to generate migration files
    alembic_cfg.set_main_option("file_template", ALEMBIC_FILE_TEMPLATE)

    # sys.path path, will be prepended to sys.path if present.
    # defaults to the current working directory.
    alembic_cfg.set_main_option("prepend_sys_path", ".")

    # timezone to use when rendering the date within the migration file
    # as well as the filename.
    # If specified, requires the python-dateutil library that can be
    # installed by adding `alembic[tz]` to the pip requirements
    # string value is passed to dateutil.tz.gettz()
    # leave blank for localtime
    # timezone =

    # max length of characters to apply to the
    # "slug" field
    # truncate_slug_length = 40

    # set to 'true' to run the environment during
    # the 'revision' command, regardless of autogenerate
    # revision_environment = false

    # set to 'true' to allow .pyc and .pyo files without
    # a source .py file to be detected as revisions in the
    # versions/ directory
    # sourceless = false

    # version location specification; This defaults
    # to db/migrations/versions.  When using multiple version
    # directories, initial revisions must be specified with --version-path.
    # The path separator used here should be the separator specified by
    # "version_path_separator" below.
    # version_locations = %(here)s/bar:%(here)s/bat:db/migrations/versions

    # version path separator; As mentioned above, this is the character used to split
    # version_locations. The default within new alembic.ini files is "os", which
    # uses os.pathsep. If this key is omitted entirely, it falls back to the legacy
    # behavior of splitting on spaces and/or commas.
    #
    # Valid values for version_path_separator are:
    # version_path_separator = :
    # version_path_separator = ;
    # version_path_separator = space
    # Use os.pathsep. Default configuration used for new projects.
    alembic_cfg.set_main_option("version_path_separator", "os")

    # the output encoding used when revision files
    # are written from script.py.mako
    # output_encoding = utf-8

    _set_post_write_hooks(alembic_cfg)
    _set_alembic_logger()

    return alembic_cfg


def _set_alembic_logger():
    """Set's the wanted logging options for the alembic migrations."""

    cfg_parser = ConfigParser(interpolation=None)

    cfg_parser.add_section("loggers")
    cfg_parser.add_section("handlers")
    cfg_parser.add_section("formatters")
    cfg_parser.set("loggers", "keys", "root,sqlalchemy,alembic")
    cfg_parser.set("handlers", "keys", "console")
    cfg_parser.set("formatters", "keys", "generic")

    cfg_parser.add_section("logger_root")
    cfg_parser.set("logger_root", "level", "INFO")
    cfg_parser.set("logger_root", "handlers", "console")
    cfg_parser.set("logger_root", "qualname", "")

    cfg_parser.add_section("logger_sqlalchemy")
    cfg_parser.set("logger_sqlalchemy", "level", "WARNING")
    cfg_parser.set("logger_sqlalchemy", "handlers", "")
    cfg_parser.set("logger_sqlalchemy", "qualname", "sqlalchemy.engine")

    cfg_parser.add_section("logger_alembic")
    cfg_parser.set("logger_alembic", "level", "INFO")
    cfg_parser.set("logger_alembic", "handlers", "")
    cfg_parser.set("logger_alembic", "qualname", "alembic")

    cfg_parser.add_section("handler_console")
    cfg_parser.set("handler_console", "class", "StreamHandler")
    cfg_parser.set("handler_console", "args", "(sys.stderr,)")
    cfg_parser.set("handler_console", "level", "INFO")
    cfg_parser.set("handler_console", "formatter", "generic")

    # Note that this value is passed to ConfigParser.set, which supports variable
    # interpolation using pyformat (e.g. %(some_value)s). A raw percent sign not part
    # of an interpolation symbol must therefore be escaped, e.g. %%. The given value
    # may refer to another value already in the file using the interpolation format.
    # see:
    # https://alembic.sqlalchemy.org/en/latest/api/config.html#alembic.config.Config.set_section_option
    cfg_parser.add_section("formatter_generic")
    cfg_parser.set(
        "formatter_generic", "format", "%(levelname)-5.5s [%(name)s] %(message)s"
    )
    cfg_parser.set("formatter_generic", "datefmt", "%H:%M:%S")

    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    fileConfig(cfg_parser)


def _set_post_write_hooks(alembic_cfg):
    """post_write_hooks defines scripts or Python functions that are run on newly
    generated revision scripts. See the documentation for further detail and examples"""

    alembic_cfg.set_section_option("post_write_hooks", "hooks", "black, isort")

    alembic_cfg.set_section_option("post_write_hooks", "black.type", "console_scripts")
    alembic_cfg.set_section_option("post_write_hooks", "black.entrypoint", "black")
    alembic_cfg.set_section_option(
        "post_write_hooks", "black.options", "REVISION_SCRIPT_FILENAME"
    )

    alembic_cfg.set_section_option("post_write_hooks", "isort.type", "console_scripts")
    alembic_cfg.set_section_option("post_write_hooks", "isort.entrypoint", "isort")
    alembic_cfg.set_section_option(
        "post_write_hooks", "isort.options", "--profile black REVISION_SCRIPT_FILENAME"
    )


def alembic_upgrade(alembic_config: Config, revision: str | None = None):
    """Adjusts the Database via alembic to the specified revision.
    If no revision is given, it will be upgraded to `head`."""

    revision = revision or Revision.HEAD
    with _log_alembic_migrate(direction=Direction.UP, revision=revision):
        command.upgrade(alembic_config, revision)


def alembic_downgrade(alembic_config: Config, revision: str | None = None):
    """Adjusts the Database via alembic to the specified revision.
    If no revision is given, it will be upgraded to `head`."""

    revision = revision or Revision.BASE
    with _log_alembic_migrate(direction=Direction.DOWN, revision=revision):
        command.downgrade(alembic_config, revision)


@contextmanager
def _log_alembic_migrate(
    direction: Direction,
    revision: Union[Revision, str],
):
    """Little helper to keep the code DRY."""
    logger.info(f"Running Alembic {direction}grade revision to '{revision}'")
    yield
    logger.info(f"Finished Alembic {direction}grade revision to '{revision}'")
