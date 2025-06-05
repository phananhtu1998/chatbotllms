"""
Migration: create_users_table
Description: Create users table with basic fields
Created: 2024-03-20T00:00:00
"""

async def upgrade(conn):
    """
    Apply migration changes
    """
    # SQL để tạo bảng users
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    await conn.execute(sql)


async def downgrade(conn):
    """
    Rollback migration changes
    """
    # SQL để xóa bảng users
    sql = """
    DROP TABLE IF EXISTS users;
    """
    
    await conn.execute(sql) 