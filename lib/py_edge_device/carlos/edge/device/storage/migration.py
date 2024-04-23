__all__ = ["build_alembic_config", "alembic_upgrade", "alembic_downgrade"]

from enum import Enum

from alembic import command
from alembic.config import Config

from carlos.edge.device.storage._migrations import ALEMBIC_DIRECTORY
from carlos.edge.device.storage.connection import build_storage_url


class Revision(str, Enum):
    HEAD = "head"
    BASE = "base"

    def __str__(self) -> str:
        return self.value


ALEMBIC_FILE_TEMPLATE = "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s"


def build_alembic_config(connection_url: str) -> Config:
    """Builds a new alembic config programmatically."""

    alembic_cfg = Config()
    alembic_cfg.set_main_option(name="sqlalchemy.url", value=connection_url)

    # path to migration scripts
    alembic_cfg.set_main_option("script_location", str(ALEMBIC_DIRECTORY))

    # template used to generate migration files
    alembic_cfg.set_main_option("file_template", ALEMBIC_FILE_TEMPLATE)

    # sys.path path, will be prepended to sys.path if present.
    # defaults to the current working directory.
    alembic_cfg.set_main_option("prepend_sys_path", ".")

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

    return alembic_cfg


DEFAULT_ALEMBIC_CONFIG = build_alembic_config(connection_url=build_storage_url())


def alembic_upgrade(alembic_config: Config, revision: str | Revision | None = None):
    """Adjusts the Database via alembic to the specified revision.
    If no revision is given, it will be upgraded to `head`."""

    command.upgrade(
        config=alembic_config or DEFAULT_ALEMBIC_CONFIG,
        revision=str(revision or Revision.HEAD),
    )


def alembic_downgrade(alembic_config: Config, revision: str | Revision | None = None):
    """Adjusts the Database via alembic to the specified revision.
    If no revision is given, it will be upgraded to `head`."""

    command.downgrade(
        config=alembic_config or DEFAULT_ALEMBIC_CONFIG,
        revision=str(revision or Revision.BASE),
    )
