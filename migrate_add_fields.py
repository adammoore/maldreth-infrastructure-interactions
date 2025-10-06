#!/usr/bin/env python3
"""
Database migration script to add new fields to ExemplarTool and ToolInteraction models.

This script adds:
- ExemplarTool: license, github_url, notes, created_via, is_archived
- ToolInteraction: auto_created, is_archived

Run this before starting the Flask app with the updated models.
"""

import sqlite3
import sys

DATABASE_PATH = 'instance/streamlined_maldreth.db'

def migrate_database():
    """Add new columns to existing tables."""

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        print("Starting database migration...")

        # Add columns to exemplar_tools table
        print("\n1. Adding columns to exemplar_tools table...")

        migrations = [
            ("license", "ALTER TABLE exemplar_tools ADD COLUMN license VARCHAR(100)"),
            ("github_url", "ALTER TABLE exemplar_tools ADD COLUMN github_url VARCHAR(500)"),
            ("notes", "ALTER TABLE exemplar_tools ADD COLUMN notes TEXT"),
            ("created_via", "ALTER TABLE exemplar_tools ADD COLUMN created_via VARCHAR(100) DEFAULT 'UI'"),
            ("is_archived", "ALTER TABLE exemplar_tools ADD COLUMN is_archived BOOLEAN DEFAULT 0"),
        ]

        for col_name, sql in migrations:
            try:
                cursor.execute(sql)
                print(f"   ✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ⊗ Column {col_name} already exists, skipping")
                else:
                    raise

        # Add columns to tool_interactions table
        print("\n2. Adding columns to tool_interactions table...")

        interaction_migrations = [
            ("auto_created", "ALTER TABLE tool_interactions ADD COLUMN auto_created BOOLEAN DEFAULT 0"),
            ("is_archived", "ALTER TABLE tool_interactions ADD COLUMN is_archived BOOLEAN DEFAULT 0"),
        ]

        for col_name, sql in interaction_migrations:
            try:
                cursor.execute(sql)
                print(f"   ✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ⊗ Column {col_name} already exists, skipping")
                else:
                    raise

        # Update existing auto_created tools to set created_via
        print("\n3. Updating existing auto_created tools...")
        cursor.execute("""
            UPDATE exemplar_tools
            SET created_via = 'CSV Import'
            WHERE auto_created = 1 AND (created_via IS NULL OR created_via = 'UI')
        """)
        updated_count = cursor.rowcount
        print(f"   ✓ Updated {updated_count} tools with created_via = 'CSV Import'")

        # Make stage_id and category_id nullable (can't directly modify in SQLite, need to recreate)
        print("\n4. Making stage_id and category_id nullable...")

        # Step 1: Create new table with nullable constraints
        cursor.execute("""
            CREATE TABLE exemplar_tools_new (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                url VARCHAR(500),
                stage_id INTEGER,
                category_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                is_open_source BOOLEAN DEFAULT 0,
                provider VARCHAR(200),
                license VARCHAR(100),
                github_url VARCHAR(500),
                notes TEXT,
                created_via VARCHAR(100) DEFAULT 'UI',
                is_archived BOOLEAN DEFAULT 0,
                auto_created BOOLEAN DEFAULT 0,
                import_source VARCHAR(100),
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (stage_id) REFERENCES maldreth_stages (id),
                FOREIGN KEY (category_id) REFERENCES tool_categories (id)
            )
        """)
        print("   ✓ Created new table with nullable foreign keys")

        # Step 2: Copy all data from old table to new table
        cursor.execute("""
            INSERT INTO exemplar_tools_new
            SELECT id, name, description, url, stage_id, category_id, is_active,
                   is_open_source, provider, license, github_url, notes, created_via,
                   is_archived, auto_created, import_source, created_at, updated_at
            FROM exemplar_tools
        """)
        print(f"   ✓ Copied {cursor.rowcount} rows to new table")

        # Step 3: Drop old table
        cursor.execute("DROP TABLE exemplar_tools")
        print("   ✓ Dropped old table")

        # Step 4: Rename new table to original name
        cursor.execute("ALTER TABLE exemplar_tools_new RENAME TO exemplar_tools")
        print("   ✓ Renamed new table to exemplar_tools")

        conn.commit()
        print("\n✅ Migration completed successfully!")

        # Show summary
        print("\n" + "="*60)
        print("Migration Summary:")
        print("="*60)
        cursor.execute("SELECT COUNT(*) FROM exemplar_tools")
        tool_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tool_interactions")
        interaction_count = cursor.fetchone()[0]

        print(f"Total tools: {tool_count}")
        print(f"Total interactions: {interaction_count}")

        cursor.execute("SELECT COUNT(*) FROM exemplar_tools WHERE auto_created = 1")
        auto_created_count = cursor.fetchone()[0]
        print(f"Auto-created tools: {auto_created_count}")

        print("\nNew fields added:")
        print("  ExemplarTool: license, github_url, notes, created_via, is_archived")
        print("  ToolInteraction: auto_created, is_archived")
        print("\n✅ Database is ready for the updated application!")

        conn.close()

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("PRISM Database Migration")
    print("="*60)
    print(f"Database: {DATABASE_PATH}")
    print("="*60)

    # Check if database exists
    import os
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database file not found: {DATABASE_PATH}")
        print("Please ensure the database exists before running migration.")
        sys.exit(1)

    # Confirm migration
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        sys.exit(0)

    migrate_database()
