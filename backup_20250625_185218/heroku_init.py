import os

os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", "").replace(
    "postgres://", "postgresql://"
)

from app import app, db
from models import LifecycleStage, ToolCategory, Tool
from initialize_db import initialize_database

print("Starting database initialization...")

with app.app_context():
    # Create all tables
    print("Creating tables...")
    db.create_all()

    # Check current state
    stage_count = LifecycleStage.query.count()
    print(f"Current stages: {stage_count}")

    if stage_count == 0:
        print("Initializing data...")
        initialize_database()
        print(f"Stages after init: {LifecycleStage.query.count()}")
        print(f"Categories: {ToolCategory.query.count()}")
        print(f"Tools: {Tool.query.count()}")
    else:
        print("Database already has data")

print("Done!")
