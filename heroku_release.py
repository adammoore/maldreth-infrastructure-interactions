#!/usr/bin/env python3
"""
Heroku release command - runs before each deployment
Ensures clean database state and prevents duplicates
"""
import sys
import os
sys.path.append('.')

# Set environment for Heroku
os.environ.setdefault('FLASK_APP', 'wsgi.py')

from streamlined_app import app, db, logger, ExemplarTool, migrate_database_schema, init_database_with_maldreth_data

def heroku_release():
    """Run database initialization and cleanup for Heroku releases."""
    logger.info("=== HEROKU RELEASE PROCESS ===")

    with app.app_context():
        try:
            # Step 1: Ensure database tables exist and schema is up to date
            logger.info("Step 1: Running database schema migration...")
            migrate_database_schema()

            # Step 2: Initialize database with MaLDReTH data if needed
            logger.info("Step 2: Initializing database with MaLDReTH data...")
            init_database_with_maldreth_data()

            # Step 3: Clean up any duplicates or invalid data
            logger.info("Step 3: Running clean update process...")
            try:
                from clean_update import clean_update
                clean_update()
            except Exception as e:
                logger.warning(f"Clean update skipped or failed: {e}")
                # Don't fail the release if clean_update has issues

            logger.info("✅ Heroku release process completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Heroku release error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

if __name__ == "__main__":
    success = heroku_release()
    sys.exit(0 if success else 1)