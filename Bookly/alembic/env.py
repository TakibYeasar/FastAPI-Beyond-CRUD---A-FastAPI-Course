import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from sqlmodel import SQLModel
from alembic import context

from src.reviews.models import Review
from src.books.models import BookTag, Book, Tag
from src.auth.models import User
from src.conf.config import settings


# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import settings and models

# Load the database URL and convert it to a synchronous URL
async_database_url = settings.DATABASE_URL
sync_database_url = async_database_url.replace("asyncpg", "psycopg2")

# Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", sync_database_url)

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(sync_database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
