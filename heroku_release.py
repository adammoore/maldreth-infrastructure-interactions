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

from streamlined_app import app, db, logger, ExemplarTool
from clean_update import clean_update

def heroku_release():
    """Run clean update process for Heroku releases."""
    logger.info("=== HEROKU RELEASE PROCESS ===")
    
    with app.app_context():
        try:
            # Run clean update to prevent duplicates
            success = clean_update()
            
            if success:
                logger.info("✅ Heroku release process completed successfully")
                return True
            else:
                logger.error("❌ Heroku release process failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Heroku release error: {e}")
            return False

if __name__ == "__main__":
    success = heroku_release()
    sys.exit(0 if success else 1)