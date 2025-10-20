"""
Database configuration and session management for IdeaFly Authentication System.

This module provides SQLAlchemy engine configuration, session management,
and dependency injection utilities for FastAPI applications.
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional, Any, Dict

from sqlalchemy import (
    create_engine, 
    Engine, 
    event,
    pool,
    exc
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    sessionmaker, 
    Session, 
    scoped_session
)
from sqlalchemy.pool import QueuePool, StaticPool

from .config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Create base class for all models
Base = declarative_base()

# Global variables for engine and session factory
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None
_scoped_session_factory: Optional[scoped_session] = None


def get_database_url() -> str:
    """
    Get database URL from settings with validation.
    
    Returns:
        str: Complete database URL for SQLAlchemy
        
    Raises:
        ValueError: If DATABASE_URL is not configured
        
    Example:
        >>> url = get_database_url()
        >>> # Returns: "postgresql://user:pass@localhost/dbname"
    """
    settings = get_settings()
    
    if not settings.DATABASE_URL:
        raise ValueError(
            "DATABASE_URL must be configured. "
            "Set it in .env file or environment variables."
        )
    
    return settings.DATABASE_URL


def create_database_engine(
    database_url: Optional[str] = None,
    echo: bool = False,
    **engine_kwargs: Any
) -> Engine:
    """
    Create SQLAlchemy engine with optimized configuration.
    
    Args:
        database_url: Database URL (defaults to settings.DATABASE_URL)
        echo: Whether to log SQL queries (default: False)
        **engine_kwargs: Additional engine configuration options
        
    Returns:
        Engine: Configured SQLAlchemy engine
        
    Example:
        >>> engine = create_database_engine(echo=True)
        >>> # Creates engine with SQL logging enabled
    """
    if database_url is None:
        database_url = get_database_url()
    
    # Default engine configuration for production
    default_config = {
        "poolclass": QueuePool,
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # 1 hour
        "echo": echo,
        "future": True,  # Use SQLAlchemy 2.0 style
    }
    
    # Handle SQLite for testing
    if database_url.startswith("sqlite"):
        default_config.update({
            "poolclass": StaticPool,
            "connect_args": {
                "check_same_thread": False,
                "timeout": 20
            },
            # Remove pool settings not applicable to SQLite
            "pool_size": None,
            "max_overflow": None,
            "pool_recycle": None,
        })
        # Clean up None values
        default_config = {k: v for k, v in default_config.items() if v is not None}
    
    # Override defaults with provided kwargs
    config = {**default_config, **engine_kwargs}
    
    try:
        engine = create_engine(database_url, **config)
        logger.info(f"Database engine created successfully: {database_url.split('@')[-1] if '@' in database_url else 'SQLite'}")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def get_engine() -> Engine:
    """
    Get or create the global database engine.
    
    Returns:
        Engine: Global SQLAlchemy engine instance
        
    Example:
        >>> engine = get_engine()
        >>> # Returns singleton engine instance
    """
    global _engine
    
    if _engine is None:
        settings = get_settings()
        _engine = create_database_engine(
            echo=settings.environment == "development"
        )
    
    return _engine


def create_session_factory(engine: Optional[Engine] = None) -> sessionmaker:
    """
    Create sessionmaker factory with proper configuration.
    
    Args:
        engine: SQLAlchemy engine (defaults to global engine)
        
    Returns:
        sessionmaker: Configured session factory
        
    Example:
        >>> factory = create_session_factory()
        >>> session = factory()
    """
    if engine is None:
        engine = get_engine()
    
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )


def get_session_factory() -> sessionmaker:
    """
    Get or create the global session factory.
    
    Returns:
        sessionmaker: Global session factory instance
        
    Example:
        >>> factory = get_session_factory()
        >>> session = factory()
    """
    global _session_factory
    
    if _session_factory is None:
        _session_factory = create_session_factory()
    
    return _session_factory


def get_scoped_session() -> scoped_session:
    """
    Get thread-safe scoped session factory.
    
    Returns:
        scoped_session: Thread-safe session factory
        
    Example:
        >>> scoped_sess = get_scoped_session()
        >>> session = scoped_sess()
        >>> # Automatically thread-local
    """
    global _scoped_session_factory
    
    if _scoped_session_factory is None:
        session_factory = get_session_factory()
        _scoped_session_factory = scoped_session(session_factory)
    
    return _scoped_session_factory


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    This is the primary dependency to use in FastAPI route handlers.
    Automatically handles session lifecycle and cleanup.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        >>> # In FastAPI route:
        >>> @app.post("/users/")
        >>> def create_user(
        ...     user_data: UserCreate,
        ...     db: Session = Depends(get_db_session)
        >>> ):
        ...     # Use db session here
        ...     pass
    """
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        yield session
        # Commit transaction if no exceptions occurred
        session.commit()
    except Exception as e:
        # Rollback on any exception
        session.rollback()
        logger.error(f"Database session error, rolling back: {e}")
        raise
    finally:
        # Always close the session
        session.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        >>> # Outside FastAPI context:
        >>> with get_db_context() as db:
        ...     user = db.query(User).first()
        ...     # Session automatically committed/rolled back
    """
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database context error, rolling back: {e}")
        raise
    finally:
        session.close()


def init_database_original(create_tables: bool = False) -> None:
    """
    Initialize database connection and optionally create tables.
    
    Args:
        create_tables: Whether to create all tables defined in Base metadata
        
    Example:
        >>> init_database(create_tables=True)
        >>> # Initializes DB and creates all tables
    """
    try:
        engine = get_engine()
        
        # Test connection
        with engine.connect() as conn:
            logger.info("Database connection test successful")
        
        if create_tables:
            # Import all models to ensure they're registered
            from ..auth.models import User, OAuthProfile
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def check_database_health() -> Dict[str, Any]:
    """
    Check database connection health and return status info.
    
    Returns:
        dict: Database health status and connection info
        
    Example:
        >>> health = check_database_health()
        >>> print(health["status"])  # "healthy" or "unhealthy"
    """
    try:
        engine = get_engine()
        
        with engine.connect() as conn:
            # Test query
            result = conn.execute("SELECT 1")
            result.fetchone()
            
        # Get connection pool status
        pool_status = {
            "size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "invalidated": engine.pool.invalidated(),
        }
        
        return {
            "status": "healthy",
            "database_url_masked": _mask_database_url(str(engine.url)),
            "pool_status": pool_status,
            "engine_echo": engine.echo
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url_masked": "unavailable"
        }


def _mask_database_url(url: str) -> str:
    """
    Mask sensitive information in database URL for logging.
    
    Args:
        url: Database URL with potential credentials
        
    Returns:
        str: Masked URL safe for logging
    """
    if "@" in url:
        # Split protocol://user:pass@host/db format
        parts = url.split("@")
        if len(parts) >= 2:
            protocol_and_creds = parts[0]
            host_and_db = "@".join(parts[1:])
            
            if "://" in protocol_and_creds:
                protocol = protocol_and_creds.split("://")[0]
                return f"{protocol}://***:***@{host_and_db}"
    
    return url


# Event listeners for connection monitoring
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log database connections."""
    logger.debug("Database connection established")


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout from pool."""
    logger.debug("Database connection checked out from pool")


@event.listens_for(Engine, "checkin")  
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin to pool."""
    logger.debug("Database connection checked in to pool")


def cleanup_database() -> None:
    """
    Clean up database connections and resources.
    Call this on application shutdown.
    
    Example:
        >>> # In FastAPI shutdown event:
        >>> @app.on_event("shutdown")
        >>> def shutdown():
        ...     cleanup_database()
    """
    global _engine, _session_factory, _scoped_session_factory
    
    try:
        if _scoped_session_factory:
            _scoped_session_factory.remove()
            _scoped_session_factory = None
            
        if _engine:
            _engine.dispose()
            _engine = None
            
        _session_factory = None
        logger.info("Database cleanup completed")
        
    except Exception as e:
        logger.error(f"Database cleanup error: {e}")


# ============================================================================
# ASYNC DATABASE LIFECYCLE (FOR FASTAPI LIFESPAN)
# ============================================================================

async def init_database() -> None:
    """
    Async version of database initialization for FastAPI lifespan.
    
    This function initializes the database connection asynchronously
    for use with FastAPI's lifespan context manager.
    """
    import asyncio
    
    # Run synchronous init_database in thread pool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, init_database_original)


async def close_database() -> None:
    """
    Async version of database cleanup for FastAPI lifespan.
    
    This function cleans up database connections asynchronously
    for use with FastAPI's lifespan context manager.
    """
    import asyncio
    
    # Run synchronous cleanup_database in thread pool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, cleanup_database)


__all__ = [
    # Base and core objects
    "Base",
    "get_database_url",
    
    # Engine management
    "create_database_engine", 
    "get_engine",
    
    # Session management
    "create_session_factory",
    "get_session_factory",
    "get_scoped_session",
    
    # FastAPI dependencies
    "get_db_session",
    
    # Context managers
    "get_db_context",
    
    # Initialization and health
    "init_database",
    "init_database_original", 
    "check_database_health",
    "cleanup_database",
    "close_database",
]