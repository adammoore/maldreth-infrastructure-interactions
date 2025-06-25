"""
MaLDReTH Infrastructure Interactions Flask Application
Author: Adam Vials Moore
Date: 20 June 2025

A Flask web application for collecting and managing potential infrastructure
interactions for the MaLDReTH 2 Working Group meeting.

This application provides:
- Web interface for data collection
- RESTful API for programmatic access
- CSV export functionality
- PostgreSQL database integration
- Heroku deployment ready
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from api_v2 import api_v2_bp
from flask_migrate import Migrate
import csv
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
db = SQLAlchemy()
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

    # Import models after db initialization
    from models import Interaction

    # Routes
    @app.route("/")
    def index():
        """Main page with overview and navigation."""
        try:
            interaction_count = Interaction.query.count()
            recent_interactions = (
                Interaction.query.order_by(Interaction.created_at.desc()).limit(5).all()
            )

            return render_template(
                "index.html",
                interaction_count=interaction_count,
                recent_interactions=recent_interactions,
            )
        except Exception as e:
            logger.error(f"Error rendering index page: {e}")
            return render_template(
                "index.html", interaction_count=0, recent_interactions=[]
            )

    @app.route("/add")
    def add_interaction():
        """Form for adding new interactions."""
        return render_template("add_interaction.html")

    @app.route("/interactions")
    def view_interactions():
        """View all interactions."""
        try:
            page = request.args.get("page", 1, type=int)
            interactions = Interaction.query.order_by(
                Interaction.created_at.desc()
            ).paginate(page=page, per_page=20, error_out=False)
            return render_template("interactions.html", interactions=interactions)
        except Exception as e:
            logger.error(f"Error viewing interactions: {e}")
            return render_template("interactions.html", interactions=None)

    @app.route("/tools/explorer")
    def tools_explorer():
        return render_template("tools/explorer.html")

    @app.route("/dashboard/visualization")
    def visualization_dashboard():
        return render_template("dashboard/visualization.html")

    @app.route("/interactions/builder")
    def interaction_builder():
        return render_template("interactions/builder.html")

    @app.route("/export")
    def export_csv():
        """Export interactions as CSV."""
        try:
            interactions = Interaction.query.all()

            output = io.StringIO()
            writer = csv.writer(output)

            # Header row
            writer.writerow(
                [
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
                ]
            )

            # Data rows
            for interaction in interactions:
                writer.writerow(
                    [
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
                    ]
                )

            output.seek(0)

            # Create response
            response = app.response_class(
                output.getvalue(),
                mimetype="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename=maldreth_interactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                },
            )
            return response

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return jsonify({"error": "Failed to export data"}), 500

    # API Routes
    @app.route("/api/interactions", methods=["GET"])
    def api_get_interactions():
        """Get all interactions via API."""
        try:
            interactions = Interaction.query.all()
            return jsonify([interaction.to_dict() for interaction in interactions])
        except Exception as e:
            logger.error(f"Error getting interactions via API: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/interactions", methods=["POST"])
    def api_create_interaction():
        """Create new interaction via API."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({"error": "No data provided"}), 400

            # Validate required fields
            required_fields = [
                "interaction_type",
                "source_infrastructure",
                "target_infrastructure",
                "lifecycle_stage",
                "description",
            ]

            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            interaction = Interaction(
                interaction_type=data["interaction_type"],
                source_infrastructure=data["source_infrastructure"],
                target_infrastructure=data["target_infrastructure"],
                lifecycle_stage=data["lifecycle_stage"],
                description=data["description"],
                technical_details=data.get("technical_details"),
                benefits=data.get("benefits"),
                challenges=data.get("challenges"),
                examples=data.get("examples"),
                contact_person=data.get("contact_person"),
                organization=data.get("organization"),
                email=data.get("email"),
                priority=data.get("priority"),
                complexity=data.get("complexity"),
                status=data.get("status", "proposed"),
            )

            db.session.add(interaction)
            db.session.commit()

            logger.info(f"Created new interaction: {interaction.id}")
            return jsonify(interaction.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating interaction via API: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/interactions/<int:interaction_id>", methods=["GET"])
    def api_get_interaction(interaction_id):
        """Get specific interaction via API."""
        try:
            interaction = Interaction.query.get_or_404(interaction_id)
            return jsonify(interaction.to_dict())
        except Exception as e:
            logger.error(f"Error getting interaction {interaction_id} via API: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/submit", methods=["POST"])
    def submit_interaction():
        """Handle form submission for new interactions."""
        try:
            # Validate required fields
            required_fields = [
                "interaction_type",
                "source_infrastructure",
                "target_infrastructure",
                "lifecycle_stage",
                "description",
            ]

            for field in required_fields:
                if not request.form.get(field):
                    return render_template(
                        "add_interaction.html",
                        error=f"Missing required field: {field}",
                        form_data=request.form,
                    )

            interaction = Interaction(
                interaction_type=request.form["interaction_type"],
                source_infrastructure=request.form["source_infrastructure"],
                target_infrastructure=request.form["target_infrastructure"],
                lifecycle_stage=request.form["lifecycle_stage"],
                description=request.form["description"],
                technical_details=request.form.get("technical_details"),
                benefits=request.form.get("benefits"),
                challenges=request.form.get("challenges"),
                examples=request.form.get("examples"),
                contact_person=request.form.get("contact_person"),
                organization=request.form.get("organization"),
                email=request.form.get("email"),
                priority=request.form.get("priority"),
                complexity=request.form.get("complexity"),
                status=request.form.get("status", "proposed"),
            )

            db.session.add(interaction)
            db.session.commit()

            logger.info(f"Created new interaction via form: {interaction.id}")
            return redirect(url_for("view_interactions"))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error submitting interaction: {e}")
            return render_template(
                "add_interaction.html",
                error="Failed to submit interaction. Please try again.",
                form_data=request.form,
            )

    @app.route("/health")
    def health_check():
        """Health check endpoint."""
        try:
            # Test database connection
            interaction_count = Interaction.query.count()
            return jsonify(
                {
                    "status": "healthy",
                    "database": "connected",
                    "interactions_count": interaction_count,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "database": "disconnected",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                503,
            )

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize database tables."""
        try:
            db.create_all()
            logger.info("Database tables created successfully.")
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

    return app


# Create the application instance
app = create_app()

app.register_blueprint(api_v2_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"

    if os.environ.get("DYNO"):  # Running on Heroku
        logger.info("Starting application on Heroku...")
        app.run(host="0.0.0.0", port=port)
    else:
        logger.info("Starting application locally...")
        app.run(debug=debug, port=port)
