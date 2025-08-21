#!/usr/bin/env python3
"""
Migration script to add the color column to maldreth_stages table.
This script can be run locally or on Heroku to update the database schema.
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection from environment variables."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found")
        sys.exit(1)
    
    # Parse the DATABASE_URL
    result = urlparse(database_url)
    
    try:
        connection = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return connection
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)

def add_color_column():
    """Add color column to maldreth_stages table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if color column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='maldreth_stages' AND column_name='color'
        """)
        
        if cursor.fetchone():
            print("✅ Color column already exists in maldreth_stages table")
        else:
            # Add the color column
            cursor.execute("""
                ALTER TABLE maldreth_stages 
                ADD COLUMN color VARCHAR(7) DEFAULT '#007bff'
            """)
            conn.commit()
            print("✅ Successfully added color column to maldreth_stages table")
            
            # Update existing rows with default color
            cursor.execute("""
                UPDATE maldreth_stages 
                SET color = '#007bff' 
                WHERE color IS NULL
            """)
            conn.commit()
            print("✅ Updated existing rows with default color")
            
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting migration: Adding color column to maldreth_stages")
    add_color_column()
    print("🎉 Migration completed successfully!")