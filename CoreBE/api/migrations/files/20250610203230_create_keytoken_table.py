"""
Migration: create_keytoken_table
Description: 
Created: 2025-06-10T20:32:30.040579
"""

async def upgrade(conn):
    """
    Apply migration changes
    """
    # Viết SQL để tạo/thay đổi database schema
    sql = """
        CREATE TABLE keytoken (
            id UUID NOT NULL,
            account_id UUID NOT NULL,
            refresh_token TEXT NOT NULL,
            refresh_tokens_used JSONB DEFAULT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            CONSTRAINT fk_account_id FOREIGN KEY (account_id) REFERENCES account(id)
        );

        CREATE INDEX idx_keytoken_account_id ON keytoken(account_id);

        COMMENT ON TABLE keytoken IS 'keytoken';
    """
    
    await conn.execute(sql)


async def downgrade(conn):
    """
    Rollback migration changes
    """
    # Viết SQL để rollback changes
    sql = """
    DROP TABLE IF EXISTS keytoken;
    """
    
    await conn.execute(sql)
