"""
app.py
Main Flask application factory and configuration.

This module provides the Flask application factory function and
handles application initialization, configuration, and setup.
"""

import os
import sys
import logging
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Import extensions from separate module to avoid circular imports
from extensions import db, migrate
from config import Config
from database import init_db, populate_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def create_app(config_class=Config):
    """
    Create and configure the Flask application.
    
    Args:
        config_class: Configuration class to use (default: Config)
        
    Returns:
        Flask: Configured Flask application instance
    """
    try:
        # Create Flask instance
        app = Flask(__name__)
        
        # Load configuration
        app.config.from_object(config_class)
        logger.info(f"Application configured for {config_class.__name__} environment")
        
        # Initialize extensions with app instance
        db.init_app(app)
        migrate.init_app(app, db)
        logger.info("Extensions initialized successfully")
        
        # Initialize CORS
        CORS(app, resources={r"/api/*": {"origins": "*"}})
        
        # Register blueprints
        register_blueprints(app)
        
        # Register error handlers
        register_error_handlers(app)
        
        # Create database tables within app context
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
        
        logger.info("Flask application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Flask application: {e}")
        raise


def register_blueprints(app):
    """
    Register Flask blueprints with the application.
    
    Args:
        app: Flask application instance
    """
    try:
        from routes import main
        app.register_blueprint(main)
        logger.info("Blueprints registered successfully")
    except Exception as e:
        logger.error(f"Failed to register blueprints: {e}")
        raise


def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        logger.warning(f"404 error: {error}")
        return render_template('error.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return render_template('error.html', error="Internal server error"), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {error}")
        db.session.rollback()
        return render_template('error.html', error=str(error)), 500


# Create app instance for CLI commands
app = None

if __name__ == '__main__':
    # Handle CLI commands
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        # Create app for database initialization
        app = create_app()
        with app.app_context():
            try:
                logger.info("Initializing database...")
                init_db()
                populate_db()
                logger.info("Database initialized successfully")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                sys.exit(1)
    else:
        # Create and run the application
        app = create_app()
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
