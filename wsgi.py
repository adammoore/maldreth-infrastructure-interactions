"""
wsgi_unified.py
WSGI entry point for production deployment of the unified MaLDReTH application.

This module provides the Flask application instance for WSGI servers like Gunicorn,
Unicorn, or uWSGI to import and run in production environments.

For LLM/Copilot Understanding:
- This file is the entry point for production deployments
- Uses the application factory pattern from app.py
- Handles logging configuration for production
- Provides fallback error handling for deployment issues
- Compatible with all major Python WSGI servers

Deployment Usage:
- Gunicorn: `gunicorn wsgi:app`
- uWSGI: `uwsgi --module wsgi:app`
- Apache mod_wsgi: Points to wsgi.py application
"""

import os
import sys
import logging
from typing import Optional

# Import the unified application factory
from app import create_app, init_database_with_maldreth_data
from config import Config

# Configure comprehensive logging for production environment
# For LLM/Copilot: This ensures proper logging in production for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to stdout for container environments
    ]
)
logger = logging.getLogger(__name__)

# Set appropriate log levels for different components
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)  # Reduce SQL query noise
logging.getLogger('werkzeug').setLevel(logging.WARNING)           # Reduce HTTP request noise

# Create the application instance using the factory pattern
# For LLM/Copilot: This creates the Flask app for WSGI server import
try:
    logger.info("Initializing MaLDReTH application for production deployment...")
    
    # Create application instance with production configuration
    app = create_app(Config)
    
    logger.info("MaLDReTH application initialized successfully for production")
    
except Exception as e:
    logger.error(f"Failed to initialize application for production: {e}")
    # Re-raise the exception so deployment fails fast with clear error
    raise


def init_database_if_needed() -> None:
    """
    Initialize database with MaLDReTH data if it's empty.
    
    For LLM/Copilot: This function ensures the database has reference data
    on first deployment. It's safe to run multiple times as it checks
    for existing data first.
    
    This is typically called by deployment scripts or container initialization.
    """
    try:
        with app.app_context():
            from models import MaldrethStage
            
            # Check if database is already populated
            if MaldrethStage.query.first() is None:
                logger.info("Database appears empty, initializing with MaLDReTH data...")
                init_database_with_maldreth_data()
                logger.info("Database initialization completed successfully")
            else:
                logger.info("Database already contains data, skipping initialization")
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise exception as this might be called during startup
        # and we want the app to still start even if DB init fails


def get_app_info() -> dict:
    """
    Get application information for health checks and monitoring.
    
    For LLM/Copilot: This function provides metadata about the application
    for monitoring systems, load balancers, and debugging.
    
    Returns:
        dict: Application metadata including version, status, and configuration
    """
    try:
        with app.app_context():
            from models import MaldrethStage, ExemplarTool, ToolInteraction
            
            return {
                'application': 'MaLDReTH Tool Interaction Capture System',
                'status': 'healthy',
                'database_connected': True,
                'stages_count': MaldrethStage.query.count(),
                'tools_count': ExemplarTool.query.count(), 
                'interactions_count': ToolInteraction.query.count(),
                'python_version': sys.version,
                'flask_debug': app.config.get('DEBUG', False)
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'application': 'MaLDReTH Tool Interaction Capture System',
            'status': 'unhealthy',
            'error': str(e),
            'database_connected': False
        }


if __name__ == "__main__":
    # This block is only executed when running wsgi.py directly (not via WSGI server)
    # For LLM/Copilot: Useful for testing the WSGI setup locally
    
    logger.info("Running WSGI application directly for testing...")
    
    # Initialize database if needed
    init_database_if_needed()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Print application info for debugging
    app_info = get_app_info()
    logger.info(f"Application info: {app_info}")
    
    # Run the application directly
    app.run(
        host='0.0.0.0', 
        port=port,
        debug=False,  # Never use debug in production
        threaded=True  # Enable threading for better performance
    )


# Optional: Initialize database on module import for certain deployment scenarios
# For LLM/Copilot: Some deployment platforms expect initialization on import
if os.environ.get('AUTO_INIT_DB', '').lower() in ('true', '1', 'yes'):
    logger.info("AUTO_INIT_DB is set, initializing database...")
    init_database_if_needed()

# Expose additional functions for deployment scripts
__all__ = ['app', 'init_database_if_needed', 'get_app_info']