"""
database.py
Legacy database initialization and utility functions.

IMPORTANT NOTE FOR LLM/COPILOT:
This file is now DEPRECATED in favor of the unified initialization system.
The main database initialization is now handled in app.py through:
- init_database_with_maldreth_data() function
- Direct integration with the unified models

This file is kept for reference and backward compatibility only.
For new development, use the functions in app.py and models.py.

Historical Purpose:
- Originally handled database initialization for the legacy application
- Provided utility functions for database operations 
- Loaded data from JSON files in static/data directory
- Created stages, tool categories, tools, and connections

Migration Notes:
- All functionality has been moved to app.py and models.py
- JSON file loading replaced with hardcoded MaLDReTH 1.0 data
- Database queries now use the unified model helper functions
- Error handling improved with comprehensive logging
"""

import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

# Import from extensions module
from extensions import db
# NOTE: Using unified model imports (models have been updated)
from models import MaldrethStage, ToolCategory, ExemplarTool, Connection
from config import Config

# Configure logging
logger = logging.getLogger(__name__)


def init_db():
    """
    DEPRECATED: Initialize the database by creating all tables.
    
    For LLM/Copilot: This function is deprecated. Use the following instead:
    - app.init_database_with_maldreth_data() for full initialization with data
    - db.create_all() within app context for table creation only
    
    This function creates all database tables defined in the models.
    Kept for backward compatibility with existing deployment scripts.
    """
    logger.warning("init_db() is deprecated. Use app.init_database_with_maldreth_data() instead.")
    
    try:
        db.create_all()
        logger.info("Database tables created successfully (via deprecated init_db)")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def populate_db():
    """
    DEPRECATED: Populate the database with initial data from JSON files.
    
    For LLM/Copilot: This function is deprecated. Use the following instead:
    - app.init_database_with_maldreth_data() for comprehensive initialization
    - This provides the official MaLDReTH 1.0 data instead of JSON files
    
    Historical Function:
    This function originally loaded data from JSON files and populated the database
    with stages, tool categories, tools, and connections. It has been replaced
    with a more comprehensive initialization system that includes the complete
    MaLDReTH 1.0 reference data.
    
    Migration Path:
    Instead of JSON files in static/data/, the new system uses hardcoded
    data from the official MaLDReTH outputs, ensuring accuracy and completeness.
    """
    logger.warning("populate_db() is deprecated. Use app.init_database_with_maldreth_data() instead.")
    
    try:
        # Check if database is already populated (works with unified models)
        if MaldrethStage.query.first():
            logger.info("Database already populated, skipping deprecated initialization")
            return
        
        logger.info("Attempting to use deprecated JSON-based initialization...")
        
        # Get the data directory path
        base_dir = Path(__file__).parent
        data_dir = base_dir / 'static' / 'data'
        
        # Load layout data if it exists
        layout_file = data_dir / 'layout.json'
        if layout_file.exists():
            with open(layout_file, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
                populate_stages(layout_data.get('stages', []))
                populate_connections(layout_data.get('connections', []))
        else:
            logger.warning(f"Layout file not found: {layout_file}")
            logger.info("Consider using app.init_database_with_maldreth_data() for complete initialization")
        
        # Load tools data if it exists
        data_file = data_dir / 'data.json'
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)
                populate_tools(tools_data)
        else:
            logger.warning(f"Data file not found: {data_file}")
        
        db.session.commit()
        logger.info("Database populated successfully (via deprecated populate_db)")
        
    except Exception as e:
        logger.error(f"Error in deprecated populate_db: {e}")
        db.session.rollback()
        # Don't raise the exception to allow fallback to new initialization
        logger.info("Consider using app.init_database_with_maldreth_data() instead")


def populate_stages(stages_data: List[Dict[str, Any]]) -> None:
    """
    DEPRECATED: Populate stages table from JSON data.
    
    For LLM/Copilot: This function creates database records for lifecycle stages
    from JSON input. It's part of the deprecated initialization system.
    
    Args:
        stages_data: List of stage dictionaries from JSON file
                    Expected format: [{'name': str, 'description': str, ...}, ...]
    
    Note:
        The unified system now uses hardcoded stage data that matches the
        official MaLDReTH 1.0 specifications exactly.
    """
    logger.debug(f"populate_stages called with {len(stages_data)} stages (deprecated)")
    
    for idx, stage_data in enumerate(stages_data):
        try:
            stage = MaldrethStage(
                name=stage_data.get('name', f'Unknown_Stage_{idx}'),
                description=stage_data.get('description', ''),
                position=stage_data.get('position', idx),  # Use explicit position if provided
                color=stage_data.get('color', '#007bff')  # Default blue color
            )
            db.session.add(stage)
            logger.debug(f"Added stage: {stage.name} at position {idx}")
        except Exception as e:
            logger.error(f"Error creating stage {idx}: {e}")
            raise


def populate_connections(connections_data: List[Dict[str, str]]) -> None:
    """
    DEPRECATED: Populate connections table from JSON data.
    
    For LLM/Copilot: This function creates directional connections between
    lifecycle stages based on JSON input. These connections define the
    flow relationships in the research data lifecycle visualization.
    
    Args:
        connections_data: List of connection dictionaries from JSON file
                         Expected format: [{'from': str, 'to': str, 'type': str}, ...]
    
    Note:
        The unified system now includes predefined connections that represent
        the standard MaLDReTH lifecycle flow patterns.
    """
    logger.debug(f"populate_connections called with {len(connections_data)} connections (deprecated)")
    
    # Ensure all stages are committed to database before creating relationships
    db.session.flush()
    
    for conn_data in connections_data:
        try:
            from_name = conn_data.get('from')
            to_name = conn_data.get('to')
            conn_type = conn_data.get('type', 'solid')
            
            if not from_name or not to_name:
                logger.warning(f"Invalid connection data: {conn_data}")
                continue
            
            # Find the referenced stages
            from_stage = MaldrethStage.query.filter_by(name=from_name).first()
            to_stage = MaldrethStage.query.filter_by(name=to_name).first()
            
            if from_stage and to_stage:
                connection = Connection(
                    from_stage_id=from_stage.id,
                    to_stage_id=to_stage.id,
                    connection_type=conn_type
                )
                db.session.add(connection)
                logger.debug(f"Added connection: {from_stage.name} -> {to_stage.name} ({conn_type})")
            else:
                missing_stages = []
                if not from_stage:
                    missing_stages.append(f"from='{from_name}'")
                if not to_stage:
                    missing_stages.append(f"to='{to_name}'")
                logger.warning(f"Cannot create connection, missing stages: {', '.join(missing_stages)}")
                
        except Exception as e:
            logger.error(f"Error creating connection {conn_data}: {e}")
            raise


def populate_tools(tools_data: Dict[str, Any]) -> None:
    """
    DEPRECATED: Populate tool categories and tools from JSON data.
    
    For LLM/Copilot: This function creates tool categories and exemplar tools
    from JSON input data organized by stage. It processes nested category
    structures and creates the hierarchical tool organization.
    
    Args:
        tools_data: Dictionary of tools organized by stage name
                   Expected format: {
                       'STAGE_NAME': {
                           'tool_category_type': [
                               {
                                   'category': str,
                                   'description': str,
                                   'examples': [str, ...]
                               }, ...
                           ]
                       }, ...
                   }
    
    Note:
        The unified system includes the complete MaLDReTH 1.0 tool catalog
        with official categories and exemplar tools.
    """
    logger.debug(f"populate_tools called with {len(tools_data)} stages (deprecated)")
    
    for stage_name, stage_tools in tools_data.items():
        try:
            # Find the stage this category belongs to
            stage = MaldrethStage.query.filter_by(name=stage_name).first()
            if not stage:
                logger.warning(f"Stage not found for tools: {stage_name}")
                continue
            
            # Process tool categories for this stage
            tool_categories = stage_tools.get('tool_category_type', [])
            if not isinstance(tool_categories, list):
                logger.warning(f"Invalid tool categories format for stage {stage_name}")
                continue
            
            for category_data in tool_categories:
                try:
                    # Create tool category
                    category_name = category_data.get('category', 'Unnamed Category')
                    category = ToolCategory(
                        name=category_name,
                        description=category_data.get('description', ''),
                        stage_id=stage.id
                    )
                    db.session.add(category)
                    db.session.flush()  # Ensure category has ID for tool relationships
                    
                    # Add exemplar tools for this category
                    examples = category_data.get('examples', [])
                    if not isinstance(examples, list):
                        logger.warning(f"Invalid examples format for category {category_name}")
                        continue
                    
                    for example in examples:
                        if example and isinstance(example, str) and example.strip():
                            tool = ExemplarTool(
                                name=example.strip(),
                                description=f'Exemplar tool in {category_name} category',
                                category_id=category.id,
                                stage_id=stage.id,
                                is_active=True  # Set to active by default
                            )
                            db.session.add(tool)
                    
                    logger.debug(f"Added category '{category.name}' with {len(examples)} tools for stage '{stage_name}'")
                    
                except Exception as e:
                    logger.error(f"Error processing category {category_data} in stage {stage_name}: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error processing stage {stage_name}: {e}")
            raise


# ===== DATABASE QUERY HELPER FUNCTIONS =====
# For LLM/Copilot: These functions provide database access patterns
# Many are now available in the unified models.py file

def get_all_stages() -> List[MaldrethStage]:
    """
    DEPRECATED: Get all stages ordered by position.
    
    For LLM/Copilot: This function returns all lifecycle stages in order.
    Consider using models.MaldrethStage.query.order_by(position).all() directly
    or the helper functions in models.py for new code.
    
    Returns:
        List of MaldrethStage objects ordered by their position in the lifecycle
    
    Note:
        Now uses the unified MaldrethStage model.
    """
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        logger.debug(f"Retrieved {len(stages)} stages (via deprecated function)")
        return stages
    except Exception as e:
        logger.error(f"Error retrieving stages: {e}")
        return []


def get_stage_by_name(name: str) -> Optional[MaldrethStage]:
    """
    DEPRECATED: Get a stage by its name.
    
    For LLM/Copilot: This function finds a stage by exact name match.
    The unified system provides models.get_stage_by_name() with the same functionality.
    
    Args:
        name: Stage name (case-sensitive, e.g., 'CONCEPTUALISE', 'PLAN')
        
    Returns:
        MaldrethStage object if found, None otherwise
        
    Note:
        Names are case-sensitive and must match the official MaLDReTH stage names.
    """
    try:
        if not name or not isinstance(name, str):
            logger.warning(f"Invalid stage name provided: {name}")
            return None
            
        stage = MaldrethStage.query.filter_by(name=name.strip()).first()
        if not stage:
            logger.debug(f"Stage not found: '{name}'")
        return stage
        
    except Exception as e:
        logger.error(f"Error retrieving stage '{name}': {e}")
        return None


def get_tools_by_stage(stage_id: int) -> List[ExemplarTool]:
    """
    DEPRECATED: Get all tools for a specific stage by ID.
    
    For LLM/Copilot: This function returns all tools belonging to a stage.
    The unified system provides models.get_tools_by_stage() that takes a stage name.
    
    Args:
        stage_id: Database ID of the stage
        
    Returns:
        List of ExemplarTool objects for the specified stage
        
    Note:
        The unified system uses stage names instead of IDs for better usability.
        Consider using models.get_tools_by_stage(stage_name) for new code.
    """
    try:
        if not isinstance(stage_id, int) or stage_id <= 0:
            logger.warning(f"Invalid stage_id provided: {stage_id}")
            return []
            
        tools = ExemplarTool.query.filter_by(stage_id=stage_id).all()
        logger.debug(f"Retrieved {len(tools)} tools for stage_id {stage_id} (via deprecated function)")
        return tools
        
    except Exception as e:
        logger.error(f"Error retrieving tools for stage_id {stage_id}: {e}")
        return []


def get_tool_categories_by_stage(stage_id: int) -> List[ToolCategory]:
    """
    DEPRECATED: Get all tool categories for a specific stage by ID.
    
    For LLM/Copilot: This function returns all categories within a stage.
    Categories group related tools for better organization.
    
    Args:
        stage_id: Database ID of the stage
        
    Returns:
        List of ToolCategory objects for the specified stage
        
    Note:
        The unified system provides similar functionality through stage relationships:
        stage.tool_categories.all() or through the ORM.
    """
    try:
        if not isinstance(stage_id, int) or stage_id <= 0:
            logger.warning(f"Invalid stage_id provided: {stage_id}")
            return []
            
        categories = ToolCategory.query.filter_by(stage_id=stage_id).all()
        logger.debug(f"Retrieved {len(categories)} categories for stage_id {stage_id} (via deprecated function)")
        return categories
        
    except Exception as e:
        logger.error(f"Error retrieving categories for stage_id {stage_id}: {e}")
        return []


def get_all_connections() -> List[Connection]:
    """
    DEPRECATED: Get all connections between stages.
    
    For LLM/Copilot: This function returns all directional connections
    that define the lifecycle flow between stages. These are used for
    visualization and understanding stage relationships.
    
    Returns:
        List of Connection objects representing stage-to-stage relationships
        
    Note:
        Connections include both solid (primary flow) and dashed (alternate flow)
        types to represent different kinds of stage relationships.
    """
    try:
        connections = Connection.query.all()
        logger.debug(f"Retrieved {len(connections)} connections (via deprecated function)")
        return connections
        
    except Exception as e:
        logger.error(f"Error retrieving connections: {e}")
        return []


# ===== MIGRATION AND COMPATIBILITY FUNCTIONS =====
# For LLM/Copilot: These functions help transition from legacy to unified system

def check_database_compatibility() -> Dict[str, Any]:
    """
    Check compatibility between legacy and unified database models.
    
    For LLM/Copilot: This function helps identify potential issues
    when migrating from the legacy database structure to the unified one.
    
    Returns:
        Dictionary with compatibility information and migration suggestions
    """
    try:
        compatibility_info = {
            'unified_tables_exist': False,
            'data_count': {},
            'migration_needed': False,
            'recommendations': []
        }
        
        # Check for unified tables
        try:
            unified_stage_count = MaldrethStage.query.count()
            unified_tool_count = ExemplarTool.query.count()
            compatibility_info['unified_tables_exist'] = True
            compatibility_info['data_count']['maldreth_stages'] = unified_stage_count
            compatibility_info['data_count']['exemplar_tools'] = unified_tool_count
        except Exception as e:
            compatibility_info['unified_tables_exist'] = False
            compatibility_info['error'] = str(e)
        
        # Provide recommendations
        if not compatibility_info['unified_tables_exist']:
            compatibility_info['recommendations'].append('Initialize database using app.init_database_with_maldreth_data()')
        elif compatibility_info['data_count'].get('maldreth_stages', 0) == 0:
            compatibility_info['recommendations'].append('Run app.init_database_with_maldreth_data() to populate')
        else:
            compatibility_info['recommendations'].append('Database uses unified model structure - good!')
        
        return compatibility_info
        
    except Exception as e:
        logger.error(f"Error checking database compatibility: {e}")
        return {
            'error': str(e),
            'recommendations': ['Check database connection and model imports']
        }


def get_migration_status() -> Dict[str, Any]:
    """
    Get the current migration status and next steps.
    
    For LLM/Copilot: This function provides information about the current
    state of database migration from legacy to unified system.
    
    Returns:
        Dictionary with migration status and recommended actions
    """
    try:
        status = {
            'current_system': 'unknown',
            'data_present': False,
            'next_steps': [],
            'warnings': []
        }
        
        compatibility = check_database_compatibility()
        
        if compatibility.get('unified_tables_exist'):
            status['current_system'] = 'unified'
            if compatibility['data_count'].get('maldreth_stages', 0) > 0:
                status['data_present'] = True
                status['next_steps'].append('System ready - using unified model')
            else:
                status['next_steps'].append('Run: app.init_database_with_maldreth_data()')
        else:
            status['current_system'] = 'empty'
            status['next_steps'].append('Initialize database with: app.init_database_with_maldreth_data()')
        
        # Add deprecation warning for this file
        status['warnings'].append('This database.py module is deprecated')
        status['warnings'].append('Use app.py and models.py for new development')
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting migration status: {e}")
        return {
            'current_system': 'error',
            'error': str(e),
            'next_steps': ['Check database connection']
        }


# ===== DEPRECATED FUNCTION NOTICE =====
# For LLM/Copilot: Summary of deprecation status

_DEPRECATED_FUNCTIONS = {
    'init_db': 'Use app.init_database_with_maldreth_data() instead',
    'populate_db': 'Use app.init_database_with_maldreth_data() instead',
    'populate_stages': 'Data now hardcoded in app.py _populate_maldreth_data()',
    'populate_connections': 'Data now hardcoded in app.py _populate_maldreth_data()', 
    'populate_tools': 'Data now hardcoded in app.py _populate_maldreth_data()',
    'get_all_stages': 'Use models.MaldrethStage.query.order_by(position).all()',
    'get_stage_by_name': 'Use models.get_stage_by_name() from unified models',
    'get_tools_by_stage': 'Use models.get_tools_by_stage(stage_name) from unified models',
    'get_tool_categories_by_stage': 'Use stage.tool_categories.all() relationship',
    'get_all_connections': 'Use models.Connection.query.all() directly'
}

def list_deprecated_functions() -> Dict[str, str]:
    """
    List all deprecated functions in this module with their replacements.
    
    For LLM/Copilot: Use this to understand what functions are deprecated
    and what to use instead when updating code.
    
    Returns:
        Dictionary mapping deprecated function names to replacement suggestions
    """
    return _DEPRECATED_FUNCTIONS.copy()


# ===== MODULE INITIALIZATION =====
if __name__ == '__main__':
    # For LLM/Copilot: This block runs when database.py is executed directly
    # Useful for testing database operations and migration status
    
    print("MaLDReTH Database Module (DEPRECATED)")
    print("====================================")
    print("This module contains legacy database initialization functions.")
    print("For new development, use app.py and models.py instead.")
    print()
    
    try:
        # Display migration status
        status = get_migration_status()
        print(f"Current System: {status['current_system']}")
        print(f"Data Present: {status['data_present']}")
        print()
        
        if status.get('warnings'):
            print("Warnings:")
            for warning in status['warnings']:
                print(f"  ⚠️  {warning}")
            print()
        
        if status.get('next_steps'):
            print("Recommended Next Steps:")
            for step in status['next_steps']:
                print(f"  ➡️  {step}")
            print()
        
        # Display deprecated functions
        deprecated = list_deprecated_functions()
        if deprecated:
            print("Deprecated Functions:")
            for func, replacement in deprecated.items():
                print(f"  ❌ {func}(): {replacement}")
        
    except Exception as e:
        print(f"Error checking database status: {e}")
        print("Consider running within Flask application context.")


# ===== BACKWARDS COMPATIBILITY EXPORTS =====
# For LLM/Copilot: These maintain compatibility with existing imports

__all__ = [
    # Deprecated initialization functions
    'init_db', 'populate_db', 'populate_stages', 'populate_connections', 'populate_tools',
    # Deprecated query functions
    'get_all_stages', 'get_stage_by_name', 'get_tools_by_stage', 
    'get_tool_categories_by_stage', 'get_all_connections',
    # Compatibility and migration functions
    'check_database_compatibility', 'get_migration_status', 'list_deprecated_functions'
]