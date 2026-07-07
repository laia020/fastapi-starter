"""initial auth and documents tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-07
"""

from alembic import op


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_users_email
        ON users (email)
        """
    )
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user'
        """
    )
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        DEFAULT NOW()
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            owner_id VARCHAR(36) NOT NULL REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_documents_owner_id
        ON documents (owner_id)
        """
    )
    op.execute(
        """
        ALTER TABLE documents
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        DEFAULT NOW()
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS documents")
    op.execute("DROP TABLE IF EXISTS users")
