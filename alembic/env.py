import sys
import os
import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# add project root to path so app imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging — but only when logging is not
# already configured. When migrations run in-process from the app (the root
# logger already has our handler from app.core.logging_config.setup_logging),
# calling fileConfig() would attach a second handler and double every log line.
# For standalone `alembic` CLI use, root has no handlers so this runs normally.
if config.config_file_name is not None and not logging.getLogger().hasHandlers():
    fileConfig(config.config_file_name)

# Import the app's SQLAlchemy metadata
from app.db.database import Base
from app.core.config import settings

target_metadata = Base.metadata

# Set SQLAlchemy URL from app settings
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
