#!/usr/bin/env python3
"""
MaLDReTH Infrastructure Interactions Flask Application

A web application for collecting and managing potential infrastructure
interactions for the MaLDReTH 2 Working Group meeting.

This application provides:
- Web interface for data collection
- RESTful API for programmatic access
- CSV export functionality
- PostgreSQL database integration
- Heroku deployment ready

Author: Adam Vials Moore
License: Apache 2.0
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional

from flask import Flask, render_template, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration environment name (development, production, testing)
        
    Returns:
        Configured Flask application instance
        
    Raises:
        Exception: If configuration or initialization fails
    """
    try:
        app = Flask(__name__)
        
        # Load configuration
        configure_app(app, config_name)
        
        # Initialize extensions
        initialize_extensions(app)
        
        # Register blueprints
        register_blueprints(app)
        
        # Set up error handlers
        setup_error_handlers(app)
        
        # Configure context processors
        setup_context_processors(app)
        
        logger.info(f"Flask application created successfully in {app.config['ENV']} mode")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Flask application: {str(e)}")
        raise


def configure_app(app: Flask, config_name: Optional[str] = None) -> None:
    """
    Configure the Flask application with environment-specific settings.
    
    Args:
        app: Flask application instance
        config_name: Configuration environment name
    """
    # Determine configuration based on environment
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    # Base configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ITEMS_PER_PAGE'] = 20
    app.config['VERSION'] = '1.0.0'
    app.config['ENV'] = config_name
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix for Heroku PostgreSQL URL format
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maldreth_interactions.db'
    
    # Environment-specific configuration
    if config_name == 'development':
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
        logging.getLogger().setLevel(logging.DEBUG)
    elif config_name == 'testing':
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
    else:  # production
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        logging.getLogger().setLevel(logging.INFO)
    
    # Security headers for production
    if config_name == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    logger.info(f"Application configured for {config_name} environment")


def initialize_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions with the application.
    
    Args:
        app: Flask application instance
    """
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        CORS(app, resources={r"/api/*": {"origins": "*"}})
        
        logger.info("Extensions initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {str(e)}")
        raise


def register_blueprints(app: Flask) -> None:
    """
    Register application blueprints.
    
    Args:
        app: Flask application instance
    """
    try:
        # Import here to avoid circular imports
        from routes import main
        
        app.register_blueprint(main)
        
        logger.info("Blueprints registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register blueprints: {str(e)}")
        raise


def setup_error_handlers(app: Flask) -> None:
    """
    Set up global error handlers for the application.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors globally."""
        return render_template('error.html', 
                             error_code=404, 
                             error_message="The page you're looking for doesn't exist."), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors globally."""
        db.session.rollback()
        logger.error(f"Internal server error: {str(error)}")
        return render_template('error.html',
                             error_code=500,
                             error_message="An internal server error occurred."), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other exceptions globally."""
        db.session.rollback()
        logger.error(f"Unhandled exception: {str(error)}")
        return render_template('error.html',
                             error_code=500,
                             error_message="An unexpected error occurred."), 500


def setup_context_processors(app: Flask) -> None:
    """
    Set up template context processors.
    
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def inject_global_vars():
        """Inject global variables into all templates."""
        return {
            'current_year': datetime.now().year,
            'app_version': app.config.get('VERSION', '1.0.0'),
            'app_name': 'MaLDReTH Infrastructure Interactions'
        }

    @app.before_request
    def load_logged_in_user():
        """Load user information before each request if needed."""
        g.user = None  # Placeholder for future authentication


def init_database(app: Flask) -> None:
    """
    Initialize the database with required tables.
    
    Args:
        app: Flask application instance
    """
    try:
        with app.app_context():
            # Import models to ensure they're registered
            from models import Interaction
            
            # Create all tables
            db.create_all()
            
            logger.info("Database initialized successfully")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def cli_init_db():
    """CLI command to initialize the database."""
    app = create_app()
    init_database(app)
    print("Database initialized successfully!")


def cli_run_app():
    """CLI command to run the application."""
    app = create_app()
    
    # Initialize database if it doesn't exist
    try:
        init_database(app)
    except Exception as e:
        logger.warning(f"Database initialization warning: {str(e)}")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    logger.info(f"Starting application on {host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])


def help():
    """
    Display help information for the application.
    
    This function provides comprehensive information about the application,
    its features, and usage examples.
    """
    print("""
    MaLDReTH Infrastructure Interactions Application
    ===============================================
    
    A Flask web application for collecting and managing potential infrastructure
    interactions for the MaLDReTH 2 Working Group meeting.
    
    Features:
    ---------
    • Web Interface: Easy-to-use forms for data collection
    • Data Export: CSV export for analysis and sharing
    • API Access: RESTful API for programmatic access
    • Responsive Design: Works on desktop and mobile
    • PostgreSQL: Production-ready database on Heroku
    
    Usage:
    ------
    
    Initialize Database:
        python app.py init-db
    
    Run Application:
        python app.py
        # Application will be available at http://localhost:5000
    
    Environment Variables:
    ----------------------
    DATABASE_URL        - PostgreSQL connection string (required for production)
    SECRET_KEY         - Flask secret key (required for production)
    FLASK_ENV          - Environment: development, testing, production
    PORT               - Port to run on (default: 5000)
    HOST               - Host to bind to (default: 127.0.0.1)
    
    API Endpoints:
    --------------
    GET    /api/interactions       - List all interactions
    POST   /api/interactions       - Create new interaction
    GET    /api/interactions/<id>  - Get specific interaction
    PUT    /api/interactions/<id>  - Update interaction
    DELETE /api/interactions/<id>  - Delete interaction
    GET    /api/stats              - Get statistics
    
    Example API Usage:
    ------------------
    # Get all interactions
    curl https://your-app.herokuapp.com/api/interactions
    
    # Create new interaction
    curl -X POST https://your-app.herokuapp.com/api/interactions \\
         -H "Content-Type: application/json" \\
         -d '{"interaction_type": "data_flow", 
              "source_infrastructure": "Repository", 
              "target_infrastructure": "Analysis Platform",
              "lifecycle_stage": "Analyse",
              "description": "Data transfer for analysis"}'
    
    Deployment:
    -----------
    This application is configured for Heroku deployment:
    
    1. Create Heroku app: heroku create your-app-name
    2. Add PostgreSQL: heroku addons:create heroku-postgresql:mini
    3. Set secret key: heroku config:set SECRET_KEY=your-secret-key
    4. Deploy: git push heroku main
    5. Initialize DB: heroku run python app.py init-db
    
    For more information, visit:
    https://github.com/adammoore/maldreth-infrastructure-interactions
    """)


# CLI Interface
if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init-db':
            cli_init_db()
        elif command == 'help' or command == '--help' or command == '-h':
            help()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init-db, help")
            sys.exit(1)
    else:
        # Run the application
        cli_run_app()
