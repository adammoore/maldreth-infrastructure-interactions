#!/usr/bin/env python3
"""
Fix the tool_categories table schema by adding missing columns
and ensuring consistency with the model definitions.

This script fixes the database schema mismatch where the ToolCategory model
expects an 'order' column that doesn't exist in the database.
"""

import logging
import os
import sys
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import LifecycleStage, Tool, ToolCategory

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_and_add_missing_columns():
    """
    Check for missing columns in tool_categories table and add them if needed.
    """
    try:
        # Get the database engine
        engine = db.engine

        # Check existing columns in tool_categories table
        inspector = db.inspect(engine)
        existing_columns = [
            col["name"] for col in inspector.get_columns("tool_categories")
        ]
        logger.info(f"Existing tool_categories columns: {existing_columns}")

        # Define required columns
        required_columns = {
            "order": "INTEGER DEFAULT 0",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }

        # Add missing columns
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                logger.info(f"Adding missing column: {column_name}")
                sql = f'ALTER TABLE tool_categories ADD COLUMN "{column_name}" {column_def}'
                db.session.execute(db.text(sql))
                db.session.commit()
                logger.info(f"Successfully added column: {column_name}")
            else:
                logger.info(f"Column {column_name} already exists")

        # Verify the changes
        updated_columns = [
            col["name"] for col in inspector.get_columns("tool_categories")
        ]
        logger.info(f"Updated tool_categories columns: {updated_columns}")

    except Exception as e:
        logger.error(f"Error updating tool_categories schema: {e}")
        db.session.rollback()
        raise


def check_and_add_missing_tool_columns():
    """
    Check for missing columns in tools table and add them if needed.
    """
    try:
        # Get the database engine
        engine = db.engine
        inspector = db.inspect(engine)

        # Check existing columns in tools table
        existing_columns = [col["name"] for col in inspector.get_columns("tools")]
        logger.info(f"Existing tools columns: {existing_columns}")

        # Define required columns that might be missing
        required_columns = {"order": "INTEGER DEFAULT 0"}

        # Add missing columns
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                logger.info(f"Adding missing column to tools: {column_name}")
                sql = f'ALTER TABLE tools ADD COLUMN "{column_name}" {column_def}'
                db.session.execute(db.text(sql))
                db.session.commit()
                logger.info(f"Successfully added column to tools: {column_name}")
            else:
                logger.info(f"Column {column_name} already exists in tools")

    except Exception as e:
        logger.error(f"Error updating tools schema: {e}")
        db.session.rollback()
        raise


def verify_models_work():
    """
    Verify that the models can be queried without errors.
    """
    try:
        logger.info("Verifying models work correctly...")

        # Test lifecycle stages
        stage_count = LifecycleStage.query.count()
        logger.info(f"Lifecycle stages count: {stage_count}")

        # Test tool categories
        category_count = ToolCategory.query.count()
        logger.info(f"Tool categories count: {category_count}")

        # Test tools
        tool_count = Tool.query.count()
        logger.info(f"Tools count: {tool_count}")

        logger.info("All models are working correctly!")

    except Exception as e:
        logger.error(f"Error verifying models: {e}")
        raise


def initialize_tool_categories():
    """
    Initialize tool categories for each lifecycle stage if they don't exist.
    """
    try:
        logger.info("Initializing tool categories...")

        # Get all lifecycle stages
        stages = LifecycleStage.query.all()
        logger.info(f"Found {len(stages)} lifecycle stages")

        # Define default categories for each stage
        default_categories = {
            "Conceptualise": [
                {
                    "name": "Mind mapping, concept mapping and knowledge modelling",
                    "description": "Tools that define the entities of research and their relationships",
                    "order": 1,
                },
                {
                    "name": "Diagramming and flowchart",
                    "description": "Tools that detail the research workflow",
                    "order": 2,
                },
                {
                    "name": "Wireframing and prototyping",
                    "description": "Tools that visualise and demonstrate the research workflow",
                    "order": 3,
                },
            ],
            "Plan": [
                {
                    "name": "Data management planning (DMP)",
                    "description": "Tools focused on enabling preparation and submission of data management plans",
                    "order": 1,
                },
                {
                    "name": "Project planning",
                    "description": "Tools designed to enable project planning",
                    "order": 2,
                },
                {
                    "name": "Combined DMP/project",
                    "description": "Tools which combine project planning with the ability to prepare data management plans",
                    "order": 3,
                },
            ],
            "Collect": [
                {
                    "name": "Quantitative data collection tool",
                    "description": "Tools that collect quantitative data",
                    "order": 1,
                },
                {
                    "name": "Qualitative data collection (e.g. Survey tool)",
                    "description": "Tools that collect qualitative data",
                    "order": 2,
                },
                {
                    "name": "Harvesting tool (e.g. WebScrapers)",
                    "description": "Tools that harvest data from various sources",
                    "order": 3,
                },
            ],
        }

        # Add categories for each stage
        for stage in stages:
            if stage.name in default_categories:
                for cat_data in default_categories[stage.name]:
                    # Check if category already exists
                    existing_category = ToolCategory.query.filter_by(
                        name=cat_data["name"], stage_id=stage.id
                    ).first()

                    if not existing_category:
                        category = ToolCategory(
                            name=cat_data["name"],
                            description=cat_data["description"],
                            stage_id=stage.id,
                            order=cat_data["order"],
                            created_at=datetime.utcnow(),
                        )
                        db.session.add(category)
                        logger.info(
                            f"Created category: {cat_data['name']} for stage: {stage.name}"
                        )

        db.session.commit()
        logger.info("Tool categories initialization complete")

    except Exception as e:
        logger.error(f"Error initializing tool categories: {e}")
        db.session.rollback()
        raise


def main():
    """
    Main function to fix the database schema.
    """
    logger.info("Starting database schema fix...")

    try:
        # Fix tool_categories table schema
        logger.info("Fixing tool_categories table schema...")
        check_and_add_missing_columns()

        # Fix tools table schema if needed
        logger.info("Checking tools table schema...")
        check_and_add_missing_tool_columns()

        # Verify models work
        logger.info("Verifying models...")
        verify_models_work()

        # Initialize tool categories if empty
        if ToolCategory.query.count() == 0:
            initialize_tool_categories()
        else:
            logger.info("Tool categories already exist, skipping initialization")

        # Final verification
        verify_models_work()

        logger.info("Database schema fix completed successfully!")

    except Exception as e:
        logger.error(f"Error fixing database schema: {e}")
        raise


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        main()
