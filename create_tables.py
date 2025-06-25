"""
Script to create database tables on Heroku
"""
from app import create_app, db
from models import LifecycleStage

def create_tables():
    """Create all database tables"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if we need to add initial data
        if LifecycleStage.query.count() == 0:
            print("No stages found. Run initialize_db.py to add initial data.")
        else:
            print(f"Found {LifecycleStage.query.count()} stages in database.")

if __name__ == '__main__':
    create_tables()
