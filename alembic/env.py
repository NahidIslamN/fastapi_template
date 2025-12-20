from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context
from core.db import Base
from core import models  # IMPORTANT: load all models
from sqlalchemy.ext.asyncio import async_engine_from_config
import asyncio
from decouple import config as decouple_config

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    # Helper to overwrite sqlalchemy.url with value from environment/config
    # This ensures we use the real DB url, not the dummy one in alembic.ini
    
    # We can fetch DATABASE_URL from environment using decouple like in core/db.py
    # or just rely on alembic.ini if user filled it.
    # Given the user instruction was "Configure Database URL ... in alembic.ini",
    # but practically we want to support env vars.
    # Let's try to load it from env if possible, to match core/db.py behavior.
    
    try:
        db_url = decouple_config('DATABASE_URL')
        if db_url:
             config.set_main_option('sqlalchemy.url', db_url)
    except:
        pass # Fallback to alembic.ini value

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online_wrapper():
    asyncio.run(run_migrations_online())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online_wrapper()
