"""
Inspect the current database to see what tables and data exist.
"""

import os

from sqlalchemy import create_engine, inspect, text


def get_database_url():
    """Get database URL from environment or use default SQLite."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://")
        return database_url
    else:
        return "sqlite:///interactions.db"


def inspect_database():
    """Inspect database tables and content."""
    engine = create_engine(get_database_url())
    inspector = inspect(engine)

    print("=== DATABASE INSPECTION ===\n")

    # List all tables
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}\n")

    # For each table, show structure and row count
    with engine.connect() as conn:
        for table in tables:
            print(f"Table: {table}")
            print("-" * 50)

            # Get columns
            columns = inspector.get_columns(table)
            print("Columns:")
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")

            # Get row count
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"\nRow count: {count}")

            # Show sample data for important tables
            if table in [
                "lifecycle_stages",
                "tool_categories",
                "tools",
                "interactions",
            ]:
                print(f"\nSample data from {table}:")
                if table == "lifecycle_stages":
                    result = conn.execute(
                        text(
                            f'SELECT id, name, "order" FROM {table} ORDER BY "order" LIMIT 5'
                        )
                    )
                elif table == "interactions":
                    result = conn.execute(
                        text(
                            f"SELECT id, interaction_type, source_infrastructure, target_infrastructure FROM {table} LIMIT 5"
                        )
                    )
                else:
                    result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5"))

                rows = result.fetchall()
                for row in rows:
                    print(f"  {dict(row._mapping)}")

            print("\n")


if __name__ == "__main__":
    inspect_database()
