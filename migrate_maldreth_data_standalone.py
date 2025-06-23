"""
Standalone migration script to import MaLDReTH research data lifecycle data from CSV files.

This script reads data from CSV files and populates the database with:
- Lifecycle stages
- Tool categories
- Individual tools
- Stage connections

Usage:
    python migrate_maldreth_data_standalone.py
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Define minimal models needed for migration
class LifecycleStage(Base):
    __tablename__ = 'lifecycle_stages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    maldreth_description = Column(Text)
    order = Column(Integer, nullable=False, unique=True)
    color_code = Column(String(7), default='#007bff')
    icon = Column(String(50), default='bi-circle')
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ToolCategory(Base):
    __tablename__ = 'tool_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    stage_id = Column(Integer, ForeignKey('lifecycle_stages.id'), nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Tool(Base):
    __tablename__ = 'tools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    url = Column(String(500))
    provider = Column(String(200))
    tool_type = Column(String(200))
    source_type = Column(String(20), default='unknown')
    scope = Column(String(100), default='generic')
    is_interoperable = Column(Boolean, default=False)
    characteristics = Column(Text)
    stage_id = Column(Integer, ForeignKey('lifecycle_stages.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('tool_categories.id'))
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StageConnection(Base):
    __tablename__ = 'stage_connections'
    
    id = Column(Integer, primary_key=True)
    from_stage_id = Column(Integer, ForeignKey('lifecycle_stages.id'), nullable=False)
    to_stage_id = Column(Integer, ForeignKey('lifecycle_stages.id'), nullable=False)
    connection_type = Column(String(50), default='normal')
    description = Column(Text)
    weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def get_database_url():
    """Get database URL from environment or use default SQLite."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix for Heroku Postgres URL format
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        return database_url
    else:
        # Local development
        return 'sqlite:///interactions.db'


def init_maldreth_stages(session):
    """Initialize database with MaLDReTH lifecycle stages."""
    
    # Official MaLDReTH lifecycle stages
    stages_data = [
        {
            'name': 'Conceptualise',
            'description': 'Formulate research ideas and define data requirements',
            'maldreth_description': 'To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.',
            'order': 1,
            'color_code': '#e74c3c',
            'icon': 'bi-lightbulb'
        },
        {
            'name': 'Plan',
            'description': 'Create structured frameworks for research management',
            'maldreth_description': 'To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.',
            'order': 2,
            'color_code': '#3498db',
            'icon': 'bi-clipboard-data'
        },
        {
            'name': 'Fund',
            'description': 'Acquire financial resources for research',
            'maldreth_description': 'To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.',
            'order': 3,
            'color_code': '#f39c12',
            'icon': 'bi-currency-dollar'
        },
        {
            'name': 'Collect',
            'description': 'Gather reliable, high-quality data',
            'maldreth_description': 'To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.',
            'order': 4,
            'color_code': '#27ae60',
            'icon': 'bi-collection'
        },
        {
            'name': 'Process',
            'description': 'Prepare data for analysis',
            'maldreth_description': 'To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.',
            'order': 5,
            'color_code': '#9b59b6',
            'icon': 'bi-gear'
        },
        {
            'name': 'Analyse',
            'description': 'Derive insights from processed data',
            'maldreth_description': 'To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results.',
            'order': 6,
            'color_code': '#e67e22',
            'icon': 'bi-graph-up'
        },
        {
            'name': 'Store',
            'description': 'Securely record data',
            'maldreth_description': 'To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.',
            'order': 7,
            'color_code': '#34495e',
            'icon': 'bi-server'
        },
        {
            'name': 'Publish',
            'description': 'Release research data for others',
            'maldreth_description': 'To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.',
            'order': 8,
            'color_code': '#1abc9c',
            'icon': 'bi-journal-text'
        },
        {
            'name': 'Preserve',
            'description': 'Ensure long-term data accessibility',
            'maldreth_description': 'To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.',
            'order': 9,
            'color_code': '#8e44ad',
            'icon': 'bi-shield-check'
        },
        {
            'name': 'Share',
            'description': 'Make data available to humans and machines',
            'maldreth_description': 'To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community.',
            'order': 10,
            'color_code': '#2ecc71',
            'icon': 'bi-share'
        },
        {
            'name': 'Access',
            'description': 'Control and manage data access',
            'maldreth_description': 'To control and manage data access by designated users and reusers. This may be in the form of publicly available published information.',
            'order': 11,
            'color_code': '#f1c40f',
            'icon': 'bi-key'
        },
        {
            'name': 'Transform',
            'description': 'Create new data from original sources',
            'maldreth_description': 'To create new data from the original, for example: (i) by migration into a different format; (ii) by creating a subset, by selection or query, to create newly derived results.',
            'order': 12,
            'color_code': '#e74c3c',
            'icon': 'bi-arrow-repeat'
        }
    ]
    
    # Create stages
    created_stages = {}
    for stage_data in stages_data:
        existing = session.query(LifecycleStage).filter_by(name=stage_data['name']).first()
        if not existing:
            stage = LifecycleStage(**stage_data)
            session.add(stage)
            session.flush()
            created_stages[stage.name] = stage
            logger.info(f"Created stage: {stage.name}")
        else:
            created_stages[existing.name] = existing
            logger.info(f"Stage already exists: {existing.name}")
    
    session.commit()
    return created_stages


def create_stage_connections(session, stages):
    """Create standard stage connections."""
    connections_data = [
        ('Conceptualise', 'Plan', 'normal'),
        ('Plan', 'Fund', 'normal'),
        ('Fund', 'Collect', 'normal'),
        ('Collect', 'Process', 'normal'),
        ('Process', 'Analyse', 'normal'),
        ('Analyse', 'Store', 'normal'),
        ('Store', 'Publish', 'normal'),
        ('Publish', 'Preserve', 'normal'),
        ('Preserve', 'Share', 'normal'),
        ('Share', 'Access', 'normal'),
        ('Access', 'Transform', 'normal'),
        ('Transform', 'Conceptualise', 'feedback'),
    ]
    
    for from_name, to_name, conn_type in connections_data:
        if from_name in stages and to_name in stages:
            existing = session.query(StageConnection).filter_by(
                from_stage_id=stages[from_name].id,
                to_stage_id=stages[to_name].id
            ).first()
            
            if not existing:
                connection = StageConnection(
                    from_stage_id=stages[from_name].id,
                    to_stage_id=stages[to_name].id,
                    connection_type=conn_type
                )
                session.add(connection)
                logger.info(f"Created connection: {from_name} -> {to_name}")
    
    session.commit()


def clean_text(text):
    """Clean text by removing extra whitespace and handling None values."""
    if pd.isna(text) or text is None:
        return ""
    return str(text).strip()


def migrate_tools_from_csv(session, csv_file, stages):
    """Migrate tools from CSV file."""
    logger.info(f"Reading data from {csv_file}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        logger.info(f"Successfully read {len(df)} rows from CSV")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Extract stage name
                stage_name = clean_text(row.get('RESEARCH DATA LIFECYCLE STAGE', ''))
                if not stage_name:
                    logger.warning(f"Row {idx}: Missing stage name, skipping")
                    continue
                
                # Find matching stage
                stage = None
                for s_name, s_obj in stages.items():
                    if stage_name.upper() == s_name.upper():
                        stage = s_obj
                        break
                
                if not stage:
                    logger.warning(f"Row {idx}: Stage '{stage_name}' not found in MaLDReTH stages, skipping")
                    continue
                
                # Extract tool category
                category_name = clean_text(row.get('TOOL CATEGORY TYPE', ''))
                if not category_name:
                    logger.warning(f"Row {idx}: Missing category name, skipping")
                    continue
                
                # Create or get tool category
                tool_category = session.query(ToolCategory).filter_by(
                    stage_id=stage.id,
                    name=category_name
                ).first()
                
                if not tool_category:
                    description = clean_text(row.get('DESCRIPTION', '') or row.get('DESCRIPTION (1 SENTENCE)', ''))
                    tool_category = ToolCategory(
                        stage_id=stage.id,
                        name=category_name,
                        description=description
                    )
                    session.add(tool_category)
                    session.flush()
                    logger.info(f"Created category: {category_name} for stage: {stage.name}")
                
                # Extract and create tools
                tools_str = clean_text(row.get('EXAMPLES', ''))
                if tools_str:
                    # Split tools by comma and clean each one
                    tools = [clean_text(tool) for tool in tools_str.split(',')]
                    for tool_name in tools:
                        if tool_name and tool_name != '':
                            # Check if tool already exists
                            existing_tool = session.query(Tool).filter_by(
                                name=tool_name,
                                stage_id=stage.id
                            ).first()
                            
                            if not existing_tool:
                                tool = Tool(
                                    name=tool_name,
                                    description=f"Tool for {category_name}",
                                    stage_id=stage.id,
                                    category_id=tool_category.id,
                                    tool_type=category_name,
                                    source_type='unknown',
                                    scope='generic'
                                )
                                session.add(tool)
                                logger.info(f"Created tool: {tool_name}")
                
            except Exception as e:
                logger.error(f"Error processing row {idx}: {str(e)}")
                continue
        
        # Commit all changes
        session.commit()
        logger.info("Successfully committed all changes to database")
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        session.rollback()
        raise


def main():
    """Main migration function."""
    # Create database engine
    engine = create_engine(get_database_url())
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    logger.info("Database tables created/verified")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Initialize MaLDReTH stages
        logger.info("Initializing MaLDReTH lifecycle stages...")
        stages = init_maldreth_stages(session)
        
        # Create stage connections
        logger.info("Creating stage connections...")
        create_stage_connections(session, stages)
        
        # Find CSV file
        csv_file = None
        possible_names = [
            'v0.3_ Landscape Review of Research Tools   - Tool categories and descriptions (1).csv',
            'tools.csv',
            'research_data_lifecycle.csv',
            'Tool categories and descriptions.csv',
            'maldreth_tools.csv'
        ]
        
        for name in possible_names:
            if os.path.exists(name):
                csv_file = name
                break
        
        if not csv_file:
            # Look for any CSV file
            csv_files = list(Path('.').glob('*.csv'))
            if csv_files:
                csv_file = str(csv_files[0])
                logger.info(f"Using CSV file: {csv_file}")
        
        if csv_file and os.path.exists(csv_file):
            # Migrate tools from CSV
            logger.info("Migrating tools from CSV...")
            migrate_tools_from_csv(session, csv_file, stages)
        else:
            logger.warning("No CSV file found for tool migration")
        
        # Print summary
        stage_count = session.query(LifecycleStage).count()
        category_count = session.query(ToolCategory).count()
        tool_count = session.query(Tool).count()
        connection_count = session.query(StageConnection).count()
        
        logger.info(f"\nMigration Summary:")
        logger.info(f"  - Stages: {stage_count}")
        logger.info(f"  - Tool Categories: {category_count}")
        logger.info(f"  - Tools: {tool_count}")
        logger.info(f"  - Connections: {connection_count}")
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
