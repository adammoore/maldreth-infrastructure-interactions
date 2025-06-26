"""
database.py
Database initialization and utility functions.

This module handles database initialization, data population,
and provides utility functions for database operations.
"""

import logging
import json
import os
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError

# Import from extensions module
from extensions import db
from models import Stage, ToolCategory, Tool, Connection
from config import Config

# Configure logging
logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function creates all database tables defined in the models.
    """
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def populate_db():
    """
    Populate the database with initial data from JSON files.
    
    This function loads data from JSON files and populates the database
    with stages, tool categories, tools, and connections.
    """
    try:
        # Check if database is already populated
        if Stage.query.first():
            logger.info("Database already populated, skipping initialization")
            return
        
        # Get the data directory path
        base_dir = Path(__file__).parent
        data_dir = base_dir / 'static' / 'data'
        
        # Load layout data
        layout_file = data_dir / 'layout.json'
        if layout_file.exists():
            with open(layout_file, 'r') as f:
                layout_data = json.load(f)
                populate_stages(layout_data.get('stages', []))
                populate_connections(layout_data.get('connections', []))
        
        # Load tools data
        data_file = data_dir / 'data.json'
        if data_file.exists():
            with open(data_file, 'r') as f:
                tools_data = json.load(f)
                populate_tools(tools_data)
        
        db.session.commit()
        logger.info("Database populated successfully")
        
    except Exception as e:
        logger.error(f"Error populating database: {e}")
        db.session.rollback()
        raise


def populate_stages(stages_data):
    """
    Populate stages table from data.
    
    Args:
        stages_data (list): List of stage dictionaries
    """
    for idx, stage_data in enumerate(stages_data):
        stage = Stage(
            name=stage_data['name'],
            description=stage_data.get('description', ''),
            position=idx
        )
        db.session.add(stage)
        logger.info(f"Added stage: {stage.name}")


def populate_connections(connections_data):
    """
    Populate connections table from data.
    
    Args:
        connections_data (list): List of connection dictionaries
    """
    # First ensure all stages are committed
    db.session.flush()
    
    for conn_data in connections_data:
        from_stage = Stage.query.filter_by(name=conn_data['from']).first()
        to_stage = Stage.query.filter_by(name=conn_data['to']).first()
        
        if from_stage and to_stage:
            connection = Connection(
                from_stage_id=from_stage.id,
                to_stage_id=to_stage.id,
                connection_type=conn_data.get('type', 'solid')
            )
            db.session.add(connection)
            logger.info(f"Added connection: {from_stage.name} -> {to_stage.name}")


def populate_tools(tools_data):
    """
    Populate tool categories and tools from data.
    
    Args:
        tools_data (dict): Dictionary of tools organized by stage
    """
    for stage_name, stage_tools in tools_data.items():
        stage = Stage.query.filter_by(name=stage_name).first()
        if not stage:
            logger.warning(f"Stage not found: {stage_name}")
            continue
        
        for category_data in stage_tools.get('tool_category_type', []):
            # Create tool category
            category = ToolCategory(
                name=category_data['category'],
                description=category_data.get('description', ''),
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.flush()  # Ensure category has ID
            
            # Add example tools
            for example in category_data.get('examples', []):
                if example:  # Skip empty strings
                    tool = Tool(
                        name=example,
                        description='',
                        category_id=category.id,
                        stage_id=stage.id
                    )
                    db.session.add(tool)
            
            logger.info(f"Added category: {category.name} for stage: {stage_name}")


# Database query helper functions

def get_all_stages():
    """
    Get all stages ordered by position.
    
    Returns:
        list: List of Stage objects
    """
    return Stage.query.order_by(Stage.position).all()


def get_stage_by_name(name):
    """
    Get a stage by its name.
    
    Args:
        name (str): Stage name
        
    Returns:
        Stage: Stage object or None
    """
    return Stage.query.filter_by(name=name).first()


def get_tools_by_stage(stage_id):
    """
    Get all tools for a specific stage.
    
    Args:
        stage_id (int): Stage ID
        
    Returns:
        list: List of Tool objects
    """
    return Tool.query.filter_by(stage_id=stage_id).all()


def get_tool_categories_by_stage(stage_id):
    """
    Get all tool categories for a specific stage.
    
    Args:
        stage_id (int): Stage ID
        
    Returns:
        list: List of ToolCategory objects
    """
    return ToolCategory.query.filter_by(stage_id=stage_id).all()


def get_all_connections():
    """
    Get all connections between stages.
    
    Returns:
        list: List of Connection objects
    """
    return Connection.query.all()
