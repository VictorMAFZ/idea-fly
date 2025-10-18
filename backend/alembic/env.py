"""
Alembic environment configuration for IdeaFly Authentication System.

This file handles database connection and migration context setup.
"""

import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our models for autogenerate support
try:
    from src.auth.models import Base
    target_metadata = Base.metadata
except ImportError:
    # Fallback if models aren't available yet
    target_metadata = None

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_database_url() -> str:
    """
    Get database URL from environment variables or config.
    Environment variables take precedence over alembic.ini.
    """
    # Try to get from environment first
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        return database_url
    
    # Fallback to alembic.ini
    return config.get_main_option("sqlalchemy.url")

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# Run migrations based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()