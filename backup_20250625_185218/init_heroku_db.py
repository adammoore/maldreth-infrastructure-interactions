"""
Initialize Heroku database with all required tables and MaLDReTH data.

Run this script on Heroku to set up the database:
    heroku run python init_heroku_db.py
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from models_phase2 import LifecycleStage, StageConnection, Tool, ToolCategory

# Import Flask app and models
from app import create_app, db
from models import Interaction

# MaLDReTH stages data
MALDRETH_STAGES = [
    {
        "name": "Conceptualise",
        "description": "Formulate research ideas and define data requirements",
        "maldreth_description": "To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.",
        "order": 1,
        "color_code": "#e74c3c",
        "icon": "bi-lightbulb",
    },
    {
        "name": "Plan",
        "description": "Create structured frameworks for research management",
        "maldreth_description": "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.",
        "order": 2,
        "color_code": "#3498db",
        "icon": "bi-clipboard-data",
    },
    {
        "name": "Fund",
        "description": "Acquire financial resources for research",
        "maldreth_description": "To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.",
        "order": 3,
        "color_code": "#f39c12",
        "icon": "bi-currency-dollar",
    },
    {
        "name": "Collect",
        "description": "Gather reliable, high-quality data",
        "maldreth_description": "To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.",
        "order": 4,
        "color_code": "#27ae60",
        "icon": "bi-collection",
    },
    {
        "name": "Process",
        "description": "Prepare data for analysis",
        "maldreth_description": "To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.",
        "order": 5,
        "color_code": "#9b59b6",
        "icon": "bi-gear",
    },
    {
        "name": "Analyse",
        "description": "Derive insights from processed data",
        "maldreth_description": "To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results.",
        "order": 6,
        "color_code": "#e67e22",
        "icon": "bi-graph-up",
    },
    {
        "name": "Store",
        "description": "Securely record data",
        "maldreth_description": "To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.",
        "order": 7,
        "color_code": "#34495e",
        "icon": "bi-server",
    },
    {
        "name": "Publish",
        "description": "Release research data for others",
        "maldreth_description": "To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.",
        "order": 8,
        "color_code": "#1abc9c",
        "icon": "bi-journal-text",
    },
    {
        "name": "Preserve",
        "description": "Ensure long-term data accessibility",
        "maldreth_description": "To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.",
        "order": 9,
        "color_code": "#8e44ad",
        "icon": "bi-shield-check",
    },
    {
        "name": "Share",
        "description": "Make data available to humans and machines",
        "maldreth_description": "To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community.",
        "order": 10,
        "color_code": "#2ecc71",
        "icon": "bi-share",
    },
    {
        "name": "Access",
        "description": "Control and manage data access",
        "maldreth_description": "To control and manage data access by designated users and reusers. This may be in the form of publicly available published information.",
        "order": 11,
        "color_code": "#f1c40f",
        "icon": "bi-key",
    },
    {
        "name": "Transform",
        "description": "Create new data from original sources",
        "maldreth_description": "To create new data from the original, for example: (i) by migration into a different format; (ii) by creating a subset, by selection or query, to create newly derived results.",
        "order": 12,
        "color_code": "#e74c3c",
        "icon": "bi-arrow-repeat",
    },
]

# Stage connections
STAGE_CONNECTIONS = [
    ("Conceptualise", "Plan", "normal"),
    ("Plan", "Fund", "normal"),
    ("Fund", "Collect", "normal"),
    ("Collect", "Process", "normal"),
    ("Process", "Analyse", "normal"),
    ("Analyse", "Store", "normal"),
    ("Store", "Publish", "normal"),
    ("Publish", "Preserve", "normal"),
    ("Preserve", "Share", "normal"),
    ("Share", "Access", "normal"),
    ("Access", "Transform", "normal"),
    ("Transform", "Conceptualise", "feedback"),
]


def init_database():
    """Initialize the database with all required tables and data."""
    app = create_app()

    with app.app_context():
        logger.info("Creating database tables...")

        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")

        # Initialize MaLDReTH stages
        logger.info("Initializing MaLDReTH lifecycle stages...")
        stages = {}

        for stage_data in MALDRETH_STAGES:
            existing = LifecycleStage.query.filter_by(name=stage_data["name"]).first()
            if not existing:
                stage = LifecycleStage(**stage_data)
                db.session.add(stage)
                db.session.flush()
                stages[stage.name] = stage
                logger.info(f"Created stage: {stage.name}")
            else:
                stages[existing.name] = existing
                logger.info(f"Stage already exists: {existing.name}")

        db.session.commit()

        # Create stage connections
        logger.info("Creating stage connections...")
        for from_name, to_name, conn_type in STAGE_CONNECTIONS:
            if from_name in stages and to_name in stages:
                existing = StageConnection.query.filter_by(
                    from_stage_id=stages[from_name].id, to_stage_id=stages[to_name].id
                ).first()

                if not existing:
                    connection = StageConnection(
                        from_stage_id=stages[from_name].id,
                        to_stage_id=stages[to_name].id,
                        connection_type=conn_type,
                    )
                    db.session.add(connection)
                    logger.info(f"Created connection: {from_name} -> {to_name}")

        db.session.commit()

        # Check table counts
        logger.info("\nDatabase initialization complete!")
        logger.info(f"Lifecycle stages: {LifecycleStage.query.count()}")
        logger.info(f"Stage connections: {StageConnection.query.count()}")
        logger.info(f"Tool categories: {ToolCategory.query.count()}")
        logger.info(f"Tools: {Tool.query.count()}")
        logger.info(f"Interactions: {Interaction.query.count()}")

        # Run the MaLDReTH tools initialization
        logger.info("\nRunning MaLDReTH tools initialization...")
        try:
            from init_maldreth_tools import init_tools_data

            init_tools_data()
        except Exception as e:
            logger.warning(f"Could not initialize tools data: {e}")
            logger.info(
                "You can run init_maldreth_tools.py separately to populate tools"
            )


if __name__ == "__main__":
    init_database()
