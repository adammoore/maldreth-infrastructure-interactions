#!/usr/bin/env python3
"""
Migration script to add missing columns to exemplar_tools table.
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

def add_missing_columns():
    """Add missing columns to exemplar_tools table if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check and add description column
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='exemplar_tools' AND column_name='description'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE exemplar_tools 
                ADD COLUMN description TEXT
            """)
            print("✅ Added description column to exemplar_tools table")
        else:
            print("✅ Description column already exists in exemplar_tools table")
            
        # Check and add url column
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='exemplar_tools' AND column_name='url'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE exemplar_tools 
                ADD COLUMN url VARCHAR(500)
            """)
            print("✅ Added url column to exemplar_tools table")
        else:
            print("✅ URL column already exists in exemplar_tools table")
            
        # Check and add is_active column
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='exemplar_tools' AND column_name='is_active'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE exemplar_tools 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """)
            print("✅ Added is_active column to exemplar_tools table")
            
            # Update existing rows to have is_active = true
            cursor.execute("""
                UPDATE exemplar_tools 
                SET is_active = TRUE 
                WHERE is_active IS NULL
            """)
            print("✅ Updated existing rows with default is_active value")
        else:
            print("✅ is_active column already exists in exemplar_tools table")
            
        conn.commit()
            
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting migration: Adding missing columns to exemplar_tools")
    add_missing_columns()
    print("🎉 Migration completed successfully!")