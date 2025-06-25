"""
Fix Heroku database schema issues by updating existing tables.

Run this script on Heroku to fix database schema:
    heroku run python fix_heroku_db.py
"""

import logging
from sqlalchemy import text, inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Flask app and models
from app import create_app, db
from models import Interaction
from models_phase2 import LifecycleStage, ToolCategory, Tool, StageConnection, LifecycleSubstage


def check_and_update_schema():
    """Check existing schema and add missing columns."""
    engine = db.engine
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Check if lifecycle_stages table exists
        if 'lifecycle_stages' in inspector.get_table_names():
            logger.info("Found existing lifecycle_stages table")
            
            # Get existing columns
            columns = [col['name'] for col in inspector.get_columns('lifecycle_stages')]
            logger.info(f"Existing columns: {columns}")
            
            # Add missing columns
            if 'maldreth_description' not in columns:
                logger.info("Adding maldreth_description column...")
                conn.execute(text("ALTER TABLE lifecycle_stages ADD COLUMN maldreth_description TEXT"))
                conn.commit()
            
            if 'color_code' not in columns:
                logger.info("Adding color_code column...")
                conn.execute(text("ALTER TABLE lifecycle_stages ADD COLUMN color_code VARCHAR(7) DEFAULT '#007bff'"))
                conn.commit()
            
            if 'icon' not in columns:
                logger.info("Adding icon column...")
                conn.execute(text("ALTER TABLE lifecycle_stages ADD COLUMN icon VARCHAR(50) DEFAULT 'bi-circle'"))
                conn.commit()
            
            if 'is_active' not in columns:
                logger.info("Adding is_active column...")
                conn.execute(text("ALTER TABLE lifecycle_stages ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                conn.commit()
            
            if 'created_at' not in columns:
                logger.info("Adding created_at column...")
                conn.execute(text("ALTER TABLE lifecycle_stages ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column...")
                conn.execute(text("ALTER TABLE lifecycle_stages ADD COLUMN updated_at TIMESTAMP"))
                conn.commit()
        
        # Check other tables
        if 'interactions' not in inspector.get_table_names():
            logger.info("Creating interactions table...")
            Interaction.__table__.create(engine)
        
        if 'lifecycle_substages' not in inspector.get_table_names():
            logger.info("Creating lifecycle_substages table...")
            LifecycleSubstage.__table__.create(engine)
        
        if 'interaction_tools' not in inspector.get_table_names():
            # Skip this table as it's not used in the basic setup
            pass


def update_maldreth_data():
    """Update MaLDReTH data in existing tables."""
    maldreth_data = {
        'Conceptualise': 'To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.',
        'Plan': 'To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.',
        'Fund': 'To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.',
        'Collect': 'To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.',
        'Process': 'To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.',
        'Analyse': 'To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results.',
        'Store': 'To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.',
        'Publish': 'To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.',
        'Preserve': 'To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.',
        'Share': 'To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community.',
        'Access': 'To control and manage data access by designated users and reusers. This may be in the form of publicly available published information.',
        'Transform': 'To create new data from the original, for example: (i) by migration into a different format; (ii) by creating a subset, by selection or query, to create newly derived results.'
    }
    
    colors = ['#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6', '#e67e22', 
              '#34495e', '#1abc9c', '#8e44ad', '#2ecc71', '#f1c40f', '#e74c3c']
    icons = ['bi-lightbulb', 'bi-clipboard-data', 'bi-currency-dollar', 'bi-collection',
             'bi-gear', 'bi-graph-up', 'bi-server', 'bi-journal-text', 'bi-shield-check',
             'bi-share', 'bi-key', 'bi-arrow-repeat']
    
    stages = LifecycleStage.query.all()
    for i, stage in enumerate(stages):
        if stage.name in maldreth_data:
            stage.maldreth_description = maldreth_data[stage.name]
            stage.color_code = colors[i % len(colors)]
            stage.icon = icons[i % len(icons)]
            logger.info(f"Updated stage: {stage.name}")
    
    db.session.commit()


def main():
    """Main function to fix database."""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("Checking and updating database schema...")
            check_and_update_schema()
            
            logger.info("Database schema updated successfully")
            
            # Update MaLDReTH descriptions
            logger.info("Updating MaLDReTH data...")
            update_maldreth_data()
            
            # Verify counts
            logger.info("\nDatabase status:")
            logger.info(f"Lifecycle stages: {LifecycleStage.query.count()}")
            logger.info(f"Stage connections: {StageConnection.query.count()}")
            logger.info(f"Tool categories: {ToolCategory.query.count()}")
            logger.info(f"Tools: {Tool.query.count()}")
            logger.info(f"Interactions: {Interaction.query.count()}")
            
            logger.info("\nDatabase fix complete!")
            
            # Now run tools initialization if needed
            if Tool.query.count() == 0:
                logger.info("\nInitializing MaLDReTH tools...")
                try:
                    from init_maldreth_tools import init_tools_data
                    init_tools_data()
                except Exception as e:
                    logger.warning(f"Could not initialize tools data: {e}")
                    logger.info("You can run init_maldreth_tools.py separately")
            
        except Exception as e:
            logger.error(f"Error fixing database: {e}")
            raise


if __name__ == "__main__":
    main()
