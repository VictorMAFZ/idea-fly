"""Create oauth_profiles table

Revision ID: 002_create_oauth_profiles_table
Revises: 001_create_users_table
Create Date: 2025-10-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_create_oauth_profiles_table'
down_revision: Union[str, None] = '001_create_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create oauth_profiles table for social authentication integration."""
    
    # Create oauth_profiles table
    op.create_table(
        'oauth_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), 
                  primary_key=True, 
                  server_default=sa.text('gen_random_uuid()'),
                  comment='Unique OAuth profile identifier'),
        
        sa.Column('user_id', postgresql.UUID(as_uuid=True), 
                  nullable=False,
                  comment='Reference to users table'),
        
        sa.Column('provider', sa.String(50), 
                  nullable=False,
                  comment='OAuth provider name (google, facebook, etc.)'),
        
        sa.Column('provider_user_id', sa.String(255), 
                  nullable=False,
                  comment='User ID from OAuth provider'),
        
        sa.Column('provider_email', sa.String(254), 
                  nullable=True,
                  comment='Email from OAuth provider (may differ from user email)'),
        
        sa.Column('access_token_hash', sa.String(255), 
                  nullable=True,
                  comment='Hashed access token for revocation support'),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                  nullable=False,
                  server_default=sa.func.current_timestamp(),
                  comment='Record creation timestamp'),
        
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), 
                  nullable=False,
                  server_default=sa.func.current_timestamp(),
                  comment='Record last modification timestamp'),
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_oauth_profiles_user_id',
        'oauth_profiles', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Create unique constraint on provider + provider_user_id
    op.create_unique_constraint(
        'uq_oauth_provider_user',
        'oauth_profiles',
        ['provider', 'provider_user_id']
    )
    
    # Create performance indexes
    op.create_index('idx_oauth_user_id', 'oauth_profiles', ['user_id'])
    op.create_index('idx_oauth_provider', 'oauth_profiles', ['provider', 'provider_user_id'])
    op.create_index('idx_oauth_provider_email', 'oauth_profiles', ['provider_email'])
    
    # Add check constraints for data validation
    op.create_check_constraint(
        'ck_oauth_provider_valid',
        'oauth_profiles',
        sa.text("provider IN ('google', 'facebook', 'github', 'linkedin')")
    )
    
    op.create_check_constraint(
        'ck_oauth_provider_user_id_not_empty',
        'oauth_profiles',
        sa.text("length(trim(provider_user_id)) > 0")
    )
    
    # Email format validation if provided
    op.create_check_constraint(
        'ck_oauth_email_format',
        'oauth_profiles',
        sa.text("provider_email IS NULL OR "
               "provider_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'")
    )


def downgrade() -> None:
    """Drop oauth_profiles table and all associated constraints."""
    
    # Drop indexes
    op.drop_index('idx_oauth_provider_email', table_name='oauth_profiles')
    op.drop_index('idx_oauth_provider', table_name='oauth_profiles')
    op.drop_index('idx_oauth_user_id', table_name='oauth_profiles')
    
    # Drop check constraints
    op.drop_constraint('ck_oauth_email_format', 'oauth_profiles', type_='check')
    op.drop_constraint('ck_oauth_provider_user_id_not_empty', 'oauth_profiles', type_='check')
    op.drop_constraint('ck_oauth_provider_valid', 'oauth_profiles', type_='check')
    
    # Drop unique constraint
    op.drop_constraint('uq_oauth_provider_user', 'oauth_profiles', type_='unique')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_oauth_profiles_user_id', 'oauth_profiles', type_='foreignkey')
    
    # Drop table
    op.drop_table('oauth_profiles')