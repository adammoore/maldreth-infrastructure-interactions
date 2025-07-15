"""
wsgi.py
WSGI entry point for production deployment.

This module provides the application instance for WSGI servers
like Gunicorn to import and run the Flask application.
"""

import os
import logging
from streamlined_app import app, init_database_with_maldreth_data as init_db

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create application instance
app = create_app()

# Initialize database on first run
with app.app_context():
    try:
        init_db()
        populate_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


if __name__ == "__main__":
    # This block is only executed when running directly
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
