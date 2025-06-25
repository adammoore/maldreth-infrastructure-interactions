# init_db.py
"""
Simple database initialization script
"""
from app import app, db
from models import LifecycleStage
from initialize_db import initialize_database


def init_db():
    """Initialize database with tables and data"""
    with app.app_context():
        # Create tables
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")

        # Check if already has data
        if LifecycleStage.query.count() > 0:
            print(f"Database already contains {LifecycleStage.query.count()} stages")
            return

        # Initialize with data
        print("Initializing database with data...")
        initialize_database()
        print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
