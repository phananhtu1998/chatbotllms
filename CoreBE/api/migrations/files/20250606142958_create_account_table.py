"""
Migration: create_account_table
Description: 
Created: 2025-06-06T14:29:58.676926
"""

async def upgrade(conn):
    """
    Apply migration changes
    """
    # Viết SQL để tạo/thay đổi database schema
    sql = """
    CREATE TABLE account (
    id UUID NOT NULL PRIMARY KEY,
    number INTEGER NOT NULL,
    code VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL, -- [active,inactive]
    images VARCHAR(255) NOT NULL,
    created_by UUID NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    await conn.execute(sql)


async def downgrade(conn):
    """
    Rollback migration changes
    """
    # Viết SQL để rollback changes
    sql = """
    DROP TABLE IF EXISTS account;
    """
    
    await conn.execute(sql)
