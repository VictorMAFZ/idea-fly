"""
Core utilities and shared infrastructure for IdeaFly.

This module provides essential shared functionality including configuration,
security utilities, database management, and common utilities.
"""

from .config import get_settings, settings
from .security import (
    # Password utilities
    hash_password,
    verify_password,
    needs_rehash,
    validate_password_strength,
    
    # JWT utilities
    create_access_token,
    create_user_token,
    decode_token,
    verify_token,
    get_token_expiry,
    is_token_expired,
    
    # Security utilities
    generate_secure_token,
    generate_state_token,
    constant_time_compare,
    
    # Token extraction utilities
    extract_token_from_header,
    get_current_user_id,
    get_token_claims,
)
from .database import (
    # Base and core objects
    Base,
    get_database_url,
    
    # Engine management
    create_database_engine,
    get_engine,
    
    # Session management  
    create_session_factory,
    get_session_factory,
    get_scoped_session,
    
    # FastAPI dependencies
    get_db_session,
    
    # Context managers
    get_db_context,
    
    # Initialization and health
    init_database,
    check_database_health,
    cleanup_database,
)

# Import test utilities only for development/testing
try:
    from .security_test_utils import (
        create_test_user_token,
        create_test_user_data,
        create_oauth_test_user_data,
        get_test_password,
        TEST_USERS,
    )
    _has_test_utils = True
except ImportError:
    _has_test_utils = False

__all__ = [
    # Configuration
    "get_settings",
    "settings",
    
    # Password utilities
    "hash_password",
    "verify_password", 
    "needs_rehash",
    "validate_password_strength",
    
    # JWT utilities
    "create_access_token",
    "create_user_token",
    "decode_token",
    "verify_token",
    "get_token_expiry",
    "is_token_expired",
    
    # Security utilities
    "generate_secure_token",
    "generate_state_token",
    "constant_time_compare",
    
    # Token extraction utilities
    "extract_token_from_header",
    "get_current_user_id",
    "get_token_claims",
    
    # Database - Base and core objects
    "Base",
    "get_database_url",
    
    # Database - Engine management
    "create_database_engine",
    "get_engine",
    
    # Database - Session management
    "create_session_factory",
    "get_session_factory",
    "get_scoped_session",
    
    # Database - FastAPI dependencies
    "get_db_session",
    
    # Database - Context managers
    "get_db_context",
    
    # Database - Initialization and health
    "init_database",
    "check_database_health",
    "cleanup_database",
]

# Import database utilities conditionally
try:
    from .db_utils import (
        # Transaction management
        atomic_transaction,
        safe_execute,
        
        # Bulk operations
        bulk_insert,
        bulk_update,
        
        # Utility functions
        get_or_create,
        exists,
        count_records,
        
        # Raw SQL and stats
        execute_raw_sql,
        get_table_stats,
        
        # Exceptions
        DatabaseTransactionError,
        DatabaseValidationError,
    )
    _has_db_utils = True
except ImportError:
    _has_db_utils = False

# Add test utilities to exports if available
if _has_test_utils:
    __all__.extend([
        "create_test_user_token",
        "create_test_user_data", 
        "create_oauth_test_user_data",
        "get_test_password",
        "TEST_USERS",
    ])

# Add database utilities to exports if available
if _has_db_utils:
    __all__.extend([
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
    ])