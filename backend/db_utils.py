#!/usr/bin/env python3
"""
Database Migration Utilities for IdeaFly Authentication System

Provides convenience functions for common database operations including
migration management, database setup, and validation.
"""

import os
import sys
from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional

# Add backend directory to Python path for imports
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

def check_database_connection() -> bool:
    """
    Test database connectivity before running migrations.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import create_engine
        from .config import get_database_url
        
        engine = create_engine(get_database_url())
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_alembic_command(command: str, args: Optional[str] = None) -> bool:
    """
    Execute Alembic command with error handling.
    
    Args:
        command: Alembic command (upgrade, downgrade, etc.)
        args: Optional command arguments
        
    Returns:
        bool: True if command successful, False otherwise
    """
    try:
        cmd = ["alembic", command]
        if args:
            cmd.extend(args.split())
            
        result = run(cmd, cwd=BACKEND_DIR, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Alembic {command} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Alembic {command} failed:")
            print(result.stderr)
            return False
            
    except CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Install with: pip install alembic")
        return False

def setup_database():
    """Initialize database with all migrations."""
    print("🔧 Setting up IdeaFly authentication database...")
    
    # Check connection first
    if not check_database_connection():
        return False
    
    # Check current revision
    print("📋 Checking current migration status...")
    if not run_alembic_command("current"):
        return False
    
    # Run all migrations
    print("🚀 Running database migrations...")
    if not run_alembic_command("upgrade", "head"):
        return False
    
    print("✅ Database setup completed successfully!")
    return True

def reset_database():
    """Reset database by downgrading all migrations."""
    print("🔄 Resetting database (removing all tables)...")
    
    # Confirm destructive action
    confirm = input("⚠️  This will delete all data. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return False
    
    # Downgrade to base
    if not run_alembic_command("downgrade", "base"):
        return False
    
    print("✅ Database reset completed")
    return True

def create_migration(description: str):
    """Create a new migration file."""
    if not description:
        description = input("📝 Enter migration description: ")
    
    print(f"📄 Creating new migration: {description}")
    return run_alembic_command("revision", f"--autogenerate -m \"{description}\"")

def migration_status():
    """Show current migration status and history."""
    print("📊 Current Migration Status:")
    print("=" * 50)
    
    print("\n🔄 Current Revision:")
    run_alembic_command("current")
    
    print("\n📋 Migration History:")
    run_alembic_command("history", "--verbose")

def validate_schema():
    """Validate database schema against models."""
    print("✅ Validating database schema...")
    
    try:
        from sqlalchemy import create_engine, inspect
        from .config import get_database_url
        
        engine = create_engine(get_database_url())
        inspector = inspect(engine)
        
        # Check required tables
        tables = inspector.get_table_names()
        required_tables = ['users', 'oauth_profiles']
        
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Check users table structure
        users_columns = {col['name']: col['type'] for col in inspector.get_columns('users')}
        required_users_cols = ['id', 'email', 'name', 'hashed_password', 'is_active', 'auth_provider', 'created_at', 'updated_at']
        
        missing_cols = [col for col in required_users_cols if col not in users_columns]
        if missing_cols:
            print(f"❌ Missing columns in users table: {missing_cols}")
            return False
        
        # Check indexes
        users_indexes = inspector.get_indexes('users')
        index_names = [idx['name'] for idx in users_indexes]
        
        print("✅ Schema validation passed!")
        print(f"📊 Tables: {tables}")
        print(f"📊 Users indexes: {index_names}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def main():
    """Main CLI interface for database utilities."""
    if len(sys.argv) < 2:
        print("""
🗃️  IdeaFly Database Migration Utilities

Usage:
    python db_utils.py <command> [args]

Commands:
    setup           - Initialize database with all migrations
    reset           - Reset database (remove all tables)  
    status          - Show current migration status
    validate        - Validate database schema
    upgrade [rev]   - Upgrade to revision (default: head)
    downgrade [rev] - Downgrade to revision (default: -1)
    create <desc>   - Create new migration
    history         - Show migration history
    current         - Show current revision

Examples:
    python db_utils.py setup
    python db_utils.py create "Add user preferences table"  
    python db_utils.py upgrade head
    python db_utils.py downgrade -1
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        setup_database()
    elif command == "reset":
        reset_database()
    elif command == "status":
        migration_status()
    elif command == "validate":
        validate_schema()
    elif command == "upgrade":
        rev = sys.argv[2] if len(sys.argv) > 2 else "head"
        run_alembic_command("upgrade", rev)
    elif command == "downgrade":
        rev = sys.argv[2] if len(sys.argv) > 2 else "-1"
        run_alembic_command("downgrade", rev)
    elif command == "create":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        create_migration(desc)
    elif command == "history":
        run_alembic_command("history", "--verbose")
    elif command == "current":
        run_alembic_command("current")
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python db_utils.py' for help")

if __name__ == "__main__":
    main()