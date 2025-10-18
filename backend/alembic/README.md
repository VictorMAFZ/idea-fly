# Database Migrations - IdeaFly Authentication System

This directory contains Alembic database migrations for the authentication system.

## Overview

The database schema is designed for a robust authentication system supporting:
- Email/password authentication
- Google OAuth authentication  
- Mixed authentication (users can have both)
- User management and soft deletion
- OAuth profile management

## Migration Files

### 001_create_users_table.py
Creates the main `users` table with:
- UUID primary key with auto-generation
- Email (unique, required for login)
- Name (required, 2-100 characters)
- Hashed password (optional for OAuth-only users)
- Active status flag for soft deletion
- Authentication provider tracking
- Created/updated timestamps
- Comprehensive validation constraints
- Performance indexes

### 002_create_oauth_profiles_table.py
Creates the `oauth_profiles` table for social authentication:
- Links to users table with CASCADE delete
- Provider-specific user IDs
- Provider email tracking
- Access token hash for revocation
- Unique constraints per provider
- Validation for supported providers

## Database Schema

```sql
-- Core users table
users (
    id UUID PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL, 
    hashed_password VARCHAR(255), -- NULL for OAuth-only
    is_active BOOLEAN DEFAULT true,
    auth_provider VARCHAR(20) DEFAULT 'email',
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- OAuth integration table
oauth_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(254),
    access_token_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(provider, provider_user_id)
);
```

## Running Migrations

### Prerequisites
1. PostgreSQL database running
2. Database configured in .env file
3. Python dependencies installed

### Commands

```bash
# Navigate to backend directory
cd backend

# Run all pending migrations
alembic upgrade head

# Check current migration status
alembic current

# View migration history
alembic history

# Downgrade to previous migration
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 001_create_users_table

# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"
```

### Environment Variables

Alembic will use these environment variables (from `.env`):
- `DATABASE_URL`: Complete PostgreSQL connection string
- Alternative: Individual DB variables (`DB_HOST`, `DB_PORT`, etc.)

### Migration Validation

Each migration includes:
- ✅ Proper UUID handling with `gen_random_uuid()`
- ✅ Timezone-aware timestamps
- ✅ Data validation constraints
- ✅ Performance indexes
- ✅ Proper foreign key relationships
- ✅ Complete downgrade procedures

## Data Validation

### Users Table Constraints:
- Email format validation (RFC 5322 compliant)
- Name length (2-100 characters)
- Auth provider values: 'email', 'google', 'mixed'
- Password required for email/mixed auth
- Unique email addresses

### OAuth Profiles Constraints:
- Supported providers: 'google', 'facebook', 'github', 'linkedin'
- Unique provider + provider_user_id combinations
- Non-empty provider user IDs
- Optional email format validation

## Indexing Strategy

### Performance Indexes:
- `users.email` (unique, primary lookup)
- `users.is_active` (filtered index for active users)
- `users.auth_provider` (authentication flow optimization)
- `users.created_at` (chronological queries)
- `oauth_profiles.user_id` (foreign key optimization)
- `oauth_profiles.provider + provider_user_id` (OAuth lookups)

### Query Optimization:
- Active user lookups: `WHERE is_active = true`
- Email login: `WHERE email = ? AND is_active = true`
- OAuth login: `WHERE provider = ? AND provider_user_id = ?`
- User profile: `JOIN oauth_profiles ON users.id = user_id`

## Backup and Recovery

Before running migrations in production:
1. Create database backup: `pg_dump ideafly > backup.sql`
2. Test migrations on staging environment
3. Run migrations during maintenance window
4. Verify data integrity post-migration

## Troubleshooting

### Common Issues:
- **Connection failed**: Check DATABASE_URL and PostgreSQL service
- **Migration conflict**: Use `alembic merge` to resolve branches  
- **Constraint violation**: Review existing data before migration
- **Permission denied**: Ensure database user has DDL privileges

### Emergency Rollback:
```bash
# Immediate rollback to previous migration
alembic downgrade -1

# Restore from backup if needed
psql ideafly < backup.sql
```