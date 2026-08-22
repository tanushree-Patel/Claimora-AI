import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.db.models import Base  # noqa: F401  (imported so Alembic sees the models)

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


async def run_migrations_online() -> None:
    settings = get_settings()
    connectable = create_async_engine(settings.database_url)

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn, target_metadata=target_metadata
            )
        )
        async with connection.begin():
            await connection.run_sync(lambda sync_conn: context.run_migrations())


asyncio.run(run_migrations_online())