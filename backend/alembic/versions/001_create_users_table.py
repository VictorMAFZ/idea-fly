"""Create users table

Revision ID: 001_create_users_table
Revises: 
Create Date: 2025-10-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_create_users_table'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users table with all required fields and constraints."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), 
                  primary_key=True, 
                  server_default=sa.text('gen_random_uuid()'),
                  comment='Unique user identifier'),
        
        sa.Column('email', sa.String(254), 
                  nullable=False, 
                  unique=True,
                  comment='User email address - unique login identifier'),
        
        sa.Column('name', sa.String(100), 
                  nullable=False,
                  comment='User full name for personalization'),
        
        sa.Column('hashed_password', sa.String(255), 
                  nullable=True,
                  comment='Bcrypt hashed password - NULL for OAuth-only users'),
        
        sa.Column('is_active', sa.Boolean, 
                  nullable=False, 
                  server_default=sa.text('true'),
                  comment='Active status flag for soft delete/suspension'),
        
        sa.Column('auth_provider', sa.String(20), 
                  nullable=False, 
                  server_default=sa.text("'email'"),
                  comment='Primary authentication method'),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                  nullable=False,
                  server_default=sa.func.current_timestamp(),
                  comment='Record creation timestamp'),
        
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), 
                  nullable=False,
                  server_default=sa.func.current_timestamp(),
                  comment='Record last modification timestamp'),
    )
    
    # Create performance indexes
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_active', 'users', ['is_active'], 
                    postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_users_auth_provider', 'users', ['auth_provider'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Add check constraints for data validation
    op.create_check_constraint(
        'ck_users_auth_provider_valid',
        'users',
        sa.text("auth_provider IN ('email', 'google', 'mixed')")
    )
    
    op.create_check_constraint(
        'ck_users_name_length',
        'users', 
        sa.text("length(name) >= 2 AND length(name) <= 100")
    )
    
    op.create_check_constraint(
        'ck_users_email_format',
        'users',
        sa.text("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'")
    )
    
    # Password required for email and mixed auth providers
    op.create_check_constraint(
        'ck_users_password_required',
        'users',
        sa.text("(auth_provider = 'google' AND hashed_password IS NULL) OR "
               "(auth_provider IN ('email', 'mixed') AND hashed_password IS NOT NULL)")
    )


def downgrade() -> None:
    """Drop users table and all associated indexes and constraints."""
    
    # Drop indexes first
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_auth_provider', table_name='users')
    op.drop_index('idx_users_active', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    
    # Drop check constraints
    op.drop_constraint('ck_users_password_required', 'users', type_='check')
    op.drop_constraint('ck_users_email_format', 'users', type_='check')
    op.drop_constraint('ck_users_name_length', 'users', type_='check')
    op.drop_constraint('ck_users_auth_provider_valid', 'users', type_='check')
    
    # Drop table
    op.drop_table('users')