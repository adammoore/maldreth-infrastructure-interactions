"""
Reset Heroku database - drops all tables and recreates them with MaLDReTH data.

WARNING: This will DELETE ALL DATA!

Run this script on Heroku to completely reset the database:
    heroku run python reset_heroku_db.py --confirm
"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Check for confirmation
if "--confirm" not in sys.argv:
    print("WARNING: This will DELETE ALL DATA in the database!")
    print("To confirm, run: python reset_heroku_db.py --confirm")
    sys.exit(1)

# Import Flask app and models
from app import create_app, db


def reset_database():
    """Drop all tables and recreate them."""
    app = create_app()

    with app.app_context():
        logger.info("WARNING: Dropping all database tables...")

        # Drop all tables
        db.drop_all()
        logger.info("All tables dropped")

        # Create all tables fresh
        logger.info("Creating new tables...")
        db.create_all()
        logger.info("All tables created")

        # Now run the initialization
        logger.info("Running database initialization...")

        # Import models after tables are created
        # Run the init but skip the db.create_all() part
        from init_heroku_db import MALDRETH_STAGES, STAGE_CONNECTIONS
        from models_phase2 import (LifecycleStage, StageConnection, Tool,
                                   ToolCategory)

        from models import Interaction

        # Initialize MaLDReTH stages
        logger.info("Initializing MaLDReTH lifecycle stages...")
        stages = {}

        for stage_data in MALDRETH_STAGES:
            stage = LifecycleStage(**stage_data)
            db.session.add(stage)
            db.session.flush()
            stages[stage.name] = stage
            logger.info(f"Created stage: {stage.name}")

        db.session.commit()

        # Create stage connections
        logger.info("Creating stage connections...")
        for from_name, to_name, conn_type in STAGE_CONNECTIONS:
            if from_name in stages and to_name in stages:
                connection = StageConnection(
                    from_stage_id=stages[from_name].id,
                    to_stage_id=stages[to_name].id,
                    connection_type=conn_type,
                )
                db.session.add(connection)
                logger.info(f"Created connection: {from_name} -> {to_name}")

        db.session.commit()

        # Initialize tools
        logger.info("Initializing MaLDReTH tools...")
        try:
            from init_maldreth_tools import init_tools_data

            init_tools_data()
        except Exception as e:
            logger.warning(f"Could not initialize tools data: {e}")

        # Final counts
        logger.info("\nDatabase reset complete!")
        logger.info(f"Lifecycle stages: {LifecycleStage.query.count()}")
        logger.info(f"Stage connections: {StageConnection.query.count()}")
        logger.info(f"Tool categories: {ToolCategory.query.count()}")
        logger.info(f"Tools: {Tool.query.count()}")
        logger.info(f"Interactions: {Interaction.query.count()}")


if __name__ == "__main__":
    reset_database()
