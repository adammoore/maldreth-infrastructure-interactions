"""
Migration script to import MaLDReTH research data lifecycle data from CSV files.

This script reads data from CSV files and populates the database with:
- Lifecycle stages
- Tool categories
- Individual tools
- Stage connections

Usage:
    python migrate_maldreth_data.py
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import app components after path is set
from app import create_app, db
from models_phase2 import LifecycleStage, ToolCategory, Tool, StageConnection, init_maldreth_data


def clean_text(text):
    """
    Clean text by removing extra whitespace and handling None values.
    
    Args:
        text: Text to clean (can be str or None)
    
    Returns:
        str: Cleaned text or empty string if None
    """
    if pd.isna(text) or text is None:
        return ""
    return str(text).strip()


def migrate_stages_and_tools(csv_file):
    """
    Migrate stages and tools from the CSV file.
    
    Args:
        csv_file (str): Path to the CSV file containing stage and tool data
    """
    logger.info(f"Reading data from {csv_file}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        logger.info(f"Successfully read {len(df)} rows from CSV")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # First, ensure all MaLDReTH stages exist
        logger.info("Initializing MaLDReTH lifecycle stages...")
        init_maldreth_data()
        
        # Get all stages for mapping
        stages = {stage.name.upper(): stage for stage in LifecycleStage.query.all()}
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Extract stage name
                stage_name = clean_text(row.get('RESEARCH DATA LIFECYCLE STAGE', ''))
                if not stage_name:
                    logger.warning(f"Row {idx}: Missing stage name, skipping")
                    continue
                
                # Normalize stage name for matching
                stage_name_upper = stage_name.upper()
                
                # Find the corresponding stage
                stage = stages.get(stage_name_upper)
                if not stage:
                    # Try to match by partial name
                    for stage_key, stage_obj in stages.items():
                        if stage_name_upper in stage_key or stage_key in stage_name_upper:
                            stage = stage_obj
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
                tool_category = ToolCategory.query.filter_by(
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
                    db.session.add(tool_category)
                    db.session.flush()  # Ensure category has an ID
                    logger.info(f"Created category: {category_name} for stage: {stage.name}")
                
                # Extract and create tools
                tools_str = clean_text(row.get('EXAMPLES', ''))
                if tools_str:
                    # Split tools by comma and clean each one
                    tools = [clean_text(tool) for tool in tools_str.split(',')]
                    for tool_name in tools:
                        if tool_name and tool_name != '':  # Skip empty tool names
                            # Check if tool already exists
                            existing_tool = Tool.query.filter_by(
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
                                db.session.add(tool)
                                logger.info(f"Created tool: {tool_name}")
                
            except Exception as e:
                logger.error(f"Error processing row {idx}: {str(e)}")
                continue
        
        # Commit all changes
        db.session.commit()
        logger.info("Successfully committed all changes to database")
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        db.session.rollback()
        raise


def main():
    """Main migration function."""
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        logger.info("Database tables created/verified")
        
        # Define CSV file path
        csv_file = 'v0.3_ Landscape Review of Research Tools   - Tool categories and descriptions (1).csv'
        
        # Alternative file names to try
        alternative_files = [
            'tools.csv',
            'research_data_lifecycle.csv',
            'Tool categories and descriptions.csv',
            'research_data_lifecycle.csv',
            'maldreth_tools.csv'
        ]
        
        # Check if file exists
        if not os.path.exists(csv_file):
            logger.warning(f"Primary CSV file not found: {csv_file}")
            
            # Try alternative file names
            for alt_file in alternative_files:
                if os.path.exists(alt_file):
                    csv_file = alt_file
                    logger.info(f"Found alternative CSV file: {csv_file}")
                    break
            else:
                # Look for CSV files in the current directory
                csv_files = list(Path('.').glob('*.csv'))
                if csv_files:
                    logger.info(f"Found CSV files: {[f.name for f in csv_files]}")
                    # Use the first CSV file that contains relevant keywords
                    for f in csv_files:
                        if any(keyword in f.name.lower() for keyword in ['tool', 'lifecycle', 'research', 'maldreth']):
                            csv_file = str(f)
                            logger.info(f"Using CSV file: {csv_file}")
                            break
                else:
                    logger.error("No CSV file found. Please ensure one of the following files exists:")
                    logger.error(f"  - {csv_file}")
                    for alt_file in alternative_files:
                        logger.error(f"  - {alt_file}")
                    return
        
        # Run migration
        try:
            migrate_stages_and_tools(csv_file)
            logger.info("Migration completed successfully!")
            
            # Print summary
            stage_count = LifecycleStage.query.count()
            category_count = ToolCategory.query.count()
            tool_count = Tool.query.count()
            connection_count = StageConnection.query.count()
            
            logger.info(f"\nMigration Summary:")
            logger.info(f"  - Stages: {stage_count}")
            logger.info(f"  - Tool Categories: {category_count}")
            logger.info(f"  - Tools: {tool_count}")
            logger.info(f"  - Connections: {connection_count}")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
