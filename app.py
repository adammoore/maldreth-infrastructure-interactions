"""
MaLDReTH Infrastructure Interactions Flask Application
Author: Adam Vials Moore
Date: 26 June 2025

A Flask web application for collecting and managing potential infrastructure
interactions for the MaLDReTH 2 Working Group meeting.

This application provides:
- Web interface for data collection
- RESTful API for programmatic access
- CSV export functionality
- PostgreSQL database integration
- Heroku deployment ready
"""

import csv
import io
import logging
import os
from datetime import datetime

from flask import Flask, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, Interaction, init_database
from routes import main_bp
from api_v2 import api_v2_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
migrate = Migrate()


def create_app():
    """
    Application factory pattern for creating Flask app instances.

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-key-change-in-production"
    )

    # Database configuration
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Fix for Heroku Postgres URL format
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://")
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Local development
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///interactions.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_v2_bp)

    # API Routes
    @app.route("/api/interactions", methods=["GET"])
    def api_get_interactions():
        """Get all interactions via API."""
        try:
            interactions = Interaction.query.all()
            return jsonify({
                "status": "success",
                "data": [interaction.to_dict() for interaction in interactions],
                "count": len(interactions)
            })
        except Exception as e:
            logger.error(f"Error getting interactions via API: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/interactions", methods=["POST"])
    def api_create_interaction():
        """Create new interaction via API."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({"status": "error", "message": "No data provided"}), 400

            # Create interaction from data
            interaction = Interaction.from_dict(data)
            
            # Validate
            is_valid, errors = interaction.validate()
            if not is_valid:
                return jsonify({
                    "status": "error", 
                    "message": "Validation failed",
                    "errors": errors
                }), 400

            db.session.add(interaction)
            db.session.commit()

            logger.info(f"Created new interaction: {interaction.id}")
            return jsonify({
                "status": "success",
                "data": interaction.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating interaction via API: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/interactions/<int:interaction_id>", methods=["GET"])
    def api_get_interaction(interaction_id):
        """Get specific interaction via API."""
        try:
            interaction = Interaction.query.get_or_404(interaction_id)
            return jsonify({
                "status": "success",
                "data": interaction.to_dict()
            })
        except Exception as e:
            logger.error(f"Error getting interaction {interaction_id} via API: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/interactions/<int:interaction_id>", methods=["PUT"])
    def api_update_interaction(interaction_id):
        """Update interaction via API."""
        try:
            interaction = Interaction.query.get_or_404(interaction_id)
            data = request.get_json()

            if not data:
                return jsonify({"status": "error", "message": "No data provided"}), 400

            # Update interaction
            interaction.update_from_dict(data)
            
            # Validate
            is_valid, errors = interaction.validate()
            if not is_valid:
                return jsonify({
                    "status": "error", 
                    "message": "Validation failed",
                    "errors": errors
                }), 400

            db.session.commit()

            logger.info(f"Updated interaction: {interaction.id}")
            return jsonify({
                "status": "success",
                "data": interaction.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating interaction {interaction_id} via API: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/interactions/<int:interaction_id>", methods=["DELETE"])
    def api_delete_interaction(interaction_id):
        """Delete interaction via API."""
        try:
            interaction = Interaction.query.get_or_404(interaction_id)
            db.session.delete(interaction)
            db.session.commit()

            logger.info(f"Deleted interaction: {interaction_id}")
            return jsonify({
                "status": "success",
                "message": "Interaction deleted successfully"
            })

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting interaction {interaction_id} via API: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/export")
    def export_csv():
        """Export interactions as CSV."""
        try:
            interactions = Interaction.query.all()

            output = io.StringIO()
            writer = csv.writer(output)

            # Header row
            writer.writerow([
                "ID",
                "Interaction Type",
                "Source Infrastructure",
                "Target Infrastructure",
                "Lifecycle Stage",
                "Description",
                "Technical Details",
                "Benefits",
                "Challenges",
                "Examples",
                "Contact Person",
                "Organization",
                "Email",
                "Priority",
                "Complexity",
                "Status",
                "Created At",
            ])

            # Data rows
            for interaction in interactions:
                writer.writerow([
                    interaction.id,
                    interaction.interaction_type,
                    interaction.source_infrastructure,
                    interaction.target_infrastructure,
                    interaction.lifecycle_stage,
                    interaction.description,
                    interaction.technical_details or "",
                    interaction.benefits or "",
                    interaction.challenges or "",
                    interaction.examples or "",
                    interaction.contact_person or "",
                    interaction.organization or "",
                    interaction.email or "",
                    interaction.priority or "",
                    interaction.complexity or "",
                    interaction.status or "",
                    (
                        interaction.created_at.isoformat()
                        if interaction.created_at
                        else ""
                    ),
                ])

            output.seek(0)

            # Create response
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = (
                f'attachment; filename=maldreth_interactions_'
                f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
            response.headers["Content-Type"] = "text/csv"
            return response

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return jsonify({"error": "Failed to export data"}), 500

    @app.route("/health")
    def health_check():
        """Health check endpoint."""
        try:
            # Test database connection
            interaction_count = Interaction.query.count()
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "interactions_count": interaction_count,
                "timestamp": datetime.utcnow().isoformat(),
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return (
                jsonify({
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                503,
            )

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize database tables."""
        try:
            init_database(app)
            print("Database initialized!")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            print(f"Error initializing database: {e}")

    @app.cli.command("reset-db")
    def reset_db_command():
        """Reset database (drop and recreate all tables)."""
        try:
            db.drop_all()
            db.create_all()
            logger.info("Database reset successfully.")
            print("Database reset!")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            print(f"Error resetting database: {e}")

    # Create database tables on first run
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")

    return app


# Create the application instance for Heroku
app = create_app()

# For Heroku compatibility - expose server variable
server = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"

    if os.environ.get("DYNO"):  # Running on Heroku
        logger.info("Starting application on Heroku...")
        app.run(host="0.0.0.0", port=port)
    else:
        logger.info("Starting application locally...")
        app.run(debug=debug, port=port)
