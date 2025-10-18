"""
Advanced database utilities for IdeaFly Authentication System.

This module provides transaction management, batch operations,
and database utilities for complex operations.
"""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import (
    Generator, 
    List, 
    Dict, 
    Any, 
    Optional, 
    Callable,
    Type,
    TypeVar
)

from sqlalchemy import text, inspect
from sqlalchemy.exc import (
    IntegrityError, 
    SQLAlchemyError,
    DatabaseError,
    DisconnectionError
)
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .database import get_db_context, get_session_factory, Base

# Type variable for generic model operations
T = TypeVar('T')

logger = logging.getLogger(__name__)


class DatabaseTransactionError(Exception):
    """Custom exception for transaction-related errors."""
    pass


class DatabaseValidationError(Exception):
    """Custom exception for database validation errors."""
    pass


@contextmanager
def atomic_transaction(
    session: Optional[Session] = None
) -> Generator[Session, None, None]:
    """
    Context manager for atomic database transactions.
    
    Args:
        session: Existing session to use, or None to create new one
        
    Yields:
        Session: Database session with transaction management
        
    Raises:
        DatabaseTransactionError: If transaction fails
        
    Example:
        >>> with atomic_transaction() as db:
        ...     user = User(email="test@example.com")
        ...     db.add(user)
        ...     # Automatically commits on success, rolls back on error
    """
    if session is not None:
        # Use existing session (nested transaction)
        savepoint = session.begin_nested()
        try:
            yield session
            savepoint.commit()
        except Exception as e:
            savepoint.rollback()
            logger.error(f"Nested transaction rolled back: {e}")
            raise DatabaseTransactionError(f"Transaction failed: {e}") from e
    else:
        # Create new session
        with get_db_context() as db:
            try:
                yield db
            except Exception as e:
                logger.error(f"Transaction rolled back: {e}")
                raise DatabaseTransactionError(f"Transaction failed: {e}") from e


def safe_execute(
    operation: Callable[[Session], T], 
    session: Optional[Session] = None,
    max_retries: int = 3
) -> T:
    """
    Safely execute database operation with retry logic.
    
    Args:
        operation: Function that takes a session and returns result
        session: Optional existing session to use
        max_retries: Maximum number of retry attempts
        
    Returns:
        T: Result of the operation
        
    Raises:
        DatabaseTransactionError: If operation fails after retries
        
    Example:
        >>> def create_user(db: Session) -> User:
        ...     user = User(email="test@example.com")
        ...     db.add(user)
        ...     return user
        >>> 
        >>> user = safe_execute(create_user)
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if session is not None:
                return operation(session)
            else:
                with atomic_transaction() as db:
                    return operation(db)
                    
        except (DisconnectionError, DatabaseError) as e:
            last_exception = e
            logger.warning(
                f"Database operation attempt {attempt + 1} failed: {e}. "
                f"Retrying... ({max_retries - attempt} attempts left)"
            )
            
            if attempt == max_retries:
                break
                
        except IntegrityError as e:
            # Don't retry integrity errors
            logger.error(f"Database integrity error: {e}")
            raise DatabaseValidationError(f"Data validation failed: {e}") from e
            
        except Exception as e:
            # Don't retry other exceptions
            logger.error(f"Database operation error: {e}")
            raise DatabaseTransactionError(f"Operation failed: {e}") from e
    
    raise DatabaseTransactionError(
        f"Operation failed after {max_retries + 1} attempts: {last_exception}"
    )


def bulk_insert(
    model_class: Type[T],
    data: List[Dict[str, Any]], 
    session: Optional[Session] = None,
    batch_size: int = 1000
) -> List[T]:
    """
    Efficiently insert multiple records in batches.
    
    Args:
        model_class: SQLAlchemy model class
        data: List of dictionaries with model data
        session: Optional existing session
        batch_size: Number of records to insert per batch
        
    Returns:
        List[T]: List of created model instances
        
    Example:
        >>> users_data = [
        ...     {"email": "user1@example.com", "name": "User 1"},
        ...     {"email": "user2@example.com", "name": "User 2"}
        ... ]
        >>> users = bulk_insert(User, users_data)
    """
    if not data:
        return []
    
    def _bulk_insert_operation(db: Session) -> List[T]:
        created_objects = []
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_objects = [model_class(**item_data) for item_data in batch]
            
            db.add_all(batch_objects)
            db.flush()  # Flush to get IDs without committing
            
            created_objects.extend(batch_objects)
            
            logger.debug(f"Inserted batch {i // batch_size + 1}: {len(batch)} records")
        
        return created_objects
    
    return safe_execute(_bulk_insert_operation, session)


def bulk_update(
    model_class: Type[T],
    updates: List[Dict[str, Any]], 
    id_field: str = "id",
    session: Optional[Session] = None,
    batch_size: int = 1000
) -> int:
    """
    Efficiently update multiple records in batches.
    
    Args:
        model_class: SQLAlchemy model class
        updates: List of dictionaries with ID and update data
        id_field: Name of the ID field (default: "id")
        session: Optional existing session
        batch_size: Number of records to update per batch
        
    Returns:
        int: Number of updated records
        
    Example:
        >>> updates = [
        ...     {"id": "uuid1", "name": "New Name 1"},
        ...     {"id": "uuid2", "name": "New Name 2"}
        ... ]
        >>> count = bulk_update(User, updates)
    """
    if not updates:
        return 0
    
    def _bulk_update_operation(db: Session) -> int:
        total_updated = 0
        
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            
            # Use bulk update for efficiency
            for update_data in batch:
                id_value = update_data.pop(id_field)
                result = db.query(model_class).filter(
                    getattr(model_class, id_field) == id_value
                ).update(update_data)
                total_updated += result
            
            db.flush()
            logger.debug(f"Updated batch {i // batch_size + 1}: {len(batch)} records")
        
        return total_updated
    
    return safe_execute(_bulk_update_operation, session)


def get_or_create(
    model_class: Type[T],
    defaults: Optional[Dict[str, Any]] = None,
    session: Optional[Session] = None,
    **kwargs: Any
) -> tuple[T, bool]:
    """
    Get existing record or create new one atomically.
    
    Args:
        model_class: SQLAlchemy model class
        defaults: Default values for creation if record doesn't exist
        session: Optional existing session
        **kwargs: Filter criteria for lookup
        
    Returns:
        tuple: (instance, created) where created is True if new record
        
    Example:
        >>> user, created = get_or_create(
        ...     User, 
        ...     defaults={"name": "New User"},
        ...     email="test@example.com"
        ... )
        >>> print(f"User {'created' if created else 'exists'}: {user.email}")
    """
    def _get_or_create_operation(db: Session) -> tuple[T, bool]:
        try:
            # Try to get existing record
            instance = db.query(model_class).filter_by(**kwargs).one()
            return instance, False
            
        except NoResultFound:
            # Create new record
            create_data = {**kwargs}
            if defaults:
                create_data.update(defaults)
            
            instance = model_class(**create_data)
            db.add(instance)
            db.flush()  # Get ID without committing
            
            return instance, True
            
        except MultipleResultsFound as e:
            raise DatabaseValidationError(
                f"Multiple records found for {model_class.__name__} with {kwargs}"
            ) from e
    
    return safe_execute(_get_or_create_operation, session)


def exists(
    model_class: Type[T], 
    session: Optional[Session] = None,
    **kwargs: Any
) -> bool:
    """
    Check if record exists with given criteria.
    
    Args:
        model_class: SQLAlchemy model class
        session: Optional existing session
        **kwargs: Filter criteria
        
    Returns:
        bool: True if record exists
        
    Example:
        >>> user_exists = exists(User, email="test@example.com")
    """
    def _exists_operation(db: Session) -> bool:
        return db.query(model_class).filter_by(**kwargs).first() is not None
    
    if session is not None:
        return _exists_operation(session)
    else:
        with get_db_context() as db:
            return _exists_operation(db)


def count_records(
    model_class: Type[T],
    session: Optional[Session] = None,
    **filters: Any
) -> int:
    """
    Count records matching given criteria.
    
    Args:
        model_class: SQLAlchemy model class
        session: Optional existing session
        **filters: Filter criteria
        
    Returns:
        int: Number of matching records
        
    Example:
        >>> active_users = count_records(User, is_active=True)
    """
    def _count_operation(db: Session) -> int:
        query = db.query(model_class)
        if filters:
            query = query.filter_by(**filters)
        return query.count()
    
    if session is not None:
        return _count_operation(session)
    else:
        with get_db_context() as db:
            return _count_operation(db)


def execute_raw_sql(
    sql: str, 
    params: Optional[Dict[str, Any]] = None,
    session: Optional[Session] = None
) -> Any:
    """
    Execute raw SQL query safely.
    
    Args:
        sql: SQL query string
        params: Query parameters (default: None)
        session: Optional existing session
        
    Returns:
        Any: Query result
        
    Example:
        >>> result = execute_raw_sql(
        ...     "SELECT COUNT(*) FROM users WHERE is_active = :active",
        ...     {"active": True}
        ... )
    """
    def _execute_operation(db: Session) -> Any:
        return db.execute(text(sql), params or {}).fetchall()
    
    return safe_execute(_execute_operation, session)


def get_table_stats(table_name: str, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Get statistics for a database table.
    
    Args:
        table_name: Name of the table
        session: Optional existing session
        
    Returns:
        dict: Table statistics
        
    Example:
        >>> stats = get_table_stats("users")
        >>> print(f"Total users: {stats['row_count']}")
    """
    def _stats_operation(db: Session) -> Dict[str, Any]:
        # Basic row count
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        
        stats = {
            "table_name": table_name,
            "row_count": result,
            "timestamp": datetime.now()
        }
        
        # Try to get table size (PostgreSQL specific)
        try:
            size_result = db.execute(
                text("SELECT pg_size_pretty(pg_total_relation_size(:table_name))"),
                {"table_name": table_name}
            ).scalar()
            stats["table_size"] = size_result
        except Exception:
            # Not PostgreSQL or table doesn't exist
            stats["table_size"] = "unknown"
        
        return stats
    
    return safe_execute(_stats_operation, session)


__all__ = [
    # Transaction management
    "atomic_transaction",
    "safe_execute",
    
    # Bulk operations
    "bulk_insert",
    "bulk_update", 
    
    # Utility functions
    "get_or_create",
    "exists",
    "count_records",
    
    # Raw SQL and stats
    "execute_raw_sql",
    "get_table_stats",
    
    # Exceptions
    "DatabaseTransactionError",
    "DatabaseValidationError",
]