import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

from alembic import context

from models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    Generates SQL scripts without needing a live DB connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    # Configure the migration context with our DB connection and models
    context.configure(connection=connection, target_metadata=target_metadata)
    # Open a transaction and run any pending migrations
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    Creates an async engine and runs migrations against a live DB connection.
    """
    # Create an async engine using the URL from alembic.ini
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    # Connect to the DB and run migrations synchronously within the async context
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    # Clean up the engine after migrations are done
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Entry point — runs the async migration function
    asyncio.run(run_migrations_online())