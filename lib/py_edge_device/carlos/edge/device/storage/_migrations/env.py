"""Initialiy created by Alembic.

This file is used for database migrations. It is not intended to be used
directly. Instead, use the `alembic` command line tool to run migrations.
"""

# Pylint has a false positive for `no-member` on all the `context` calls.
# pylint: disable=no-member

from __future__ import with_statement

from alembic import context
from sqlalchemy import engine_from_config, pool

from carlos.edge.device.storage.orm import CarlosDeviceModelBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = context.config

# add your model's MetaData object here
target_metadata = CarlosDeviceModelBase.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def context_configure_kwargs():
    """Returns the shared context configure keyword arguments."""
    return {
        "compare_type": True,
        "include_schemas": True,
        "target_metadata": target_metadata,
        "version_table": "carlos_device_schema_version",
    }


def run_migrations_offline():  # pragma: no cover
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **context_configure_kwargs()
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, **context_configure_kwargs())

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()  # pragma: no cover
else:
    run_migrations_online()
