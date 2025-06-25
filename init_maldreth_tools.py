# Check if tool already exists
                existing_tool = Tool.query.filter_by(
                    name=tool_name, category_id=category.id
                ).first()
                
                if existing_tool:
                    logger.debug(f"Tool already exists: {tool_name}")
                    continue
                    
                # Create new tool
                tool = Tool(
                    name=tool_name,
                    category_id=category.id,
                    stage_id=stage.id
                )
                
                # Add optional fields
                if desc_col and not pd.isna(row[desc_col]):
                    tool.description = str(row[desc_col]).strip()
                    
                if link_col and not pd.isna(row[link_col]):
                    tool.link = str(row[link_col]).strip()
                    
                if provider_col and not pd.isna(row[provider_col]):
                    tool.provider = str(row[provider_col]).strip()
                    
                db.session.add(tool)
                logger.debug(f"Added tool: {tool_name}")
                
            except Exception as e:
                logger.error(f"Error processing tool at row {idx}: {e}")
                continue
                
        db.session.commit()
        
    def initialize_connections(self) -> bool:
        """
        Initialize default connections between stages.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Define the standard lifecycle connections
            connections = [
                ("Conceptualise", "Plan", "solid"),
                ("Plan", "Fund", "solid"),
                ("Fund", "Collect", "solid"),
                ("Collect", "Process", "solid"),
                ("Process", "Analyse", "solid"),
                ("Analyse", "Store", "solid"),
                ("Store", "Publish", "solid"),
                ("Publish", "Preserve", "solid"),
                ("Preserve", "Share", "solid"),
                ("Share", "Access", "solid"),
                ("Access", "Transform", "solid"),
                ("Transform", "Conceptualise", "solid"),
                # Alternative paths
                ("Collect", "Analyse", "dashed"),
                ("Store", "Process", "dashed"),
                ("Analyse", "Collect", "dashed")
            ]
            
            for from_name, to_name, conn_type in connections:
                # Check if connection already exists
                existing = Connection.query.join(
                    Stage, Connection.from_stage_id == Stage.id
                ).filter(
                    Stage.name == from_name
                ).first()
                
                if existing:
                    continue
                    
                # Find stages
                from_stage = self.stages_map.get(from_name)
                to_stage = self.stages_map.get(to_name)
                
                if from_stage and to_stage:
                    connection = Connection(
                        from_stage_id=from_stage.id,
                        to_stage_id=to_stage.id,
                        type=conn_type
                    )
                    db.session.add(connection)
                    logger.info(f"Created connection: {from_name} -> {to_name}")
                else:
                    logger.warning(f"Stages not found for connection: {from_name} -> {to_name}")
                    
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error initializing connections: {e}")
            return False
            
    def run(self) -> bool:
        """
        Run the complete initialization process.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting MaLDReTH tools initialization...")
        
        # Validate Excel file
        if not self.validate_excel_file():
            return False
            
        # Load stages and categories
        logger.info("Loading stages and categories...")
        if not self.load_stages_and_categories():
            return False
            
        # Load detailed tools
        logger.info("Loading tools from individual sheets...")
        if not self.load_tools_from_sheets():
            return False
            
        # Initialize connections
        logger.info("Initializing stage connections...")
        if not self.initialize_connections():
            return False
            
        logger.info("MaLDReTH tools initialization completed successfully!")
        return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Initialize MaLDReTH tools data from Excel file"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="data/research_data_lifecycle.xlsx",
        help="Path to the Excel file containing tools data"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before initialization"
    )
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing data if requested
            if args.clear:
                logger.info("Clearing existing data...")
                Tool.query.delete()
                ToolCategory.query.delete()
                Connection.query.delete()
                Stage.query.delete()
                db.session.commit()
                logger.info("Existing data cleared")
                
            # Run initialization
            initializer = MaLDReTHToolsInitializer(args.file)
            success = initializer.run()
            
            if success:
                # Print summary
                stage_count = Stage.query.count()
                category_count = ToolCategory.query.count()
                tool_count = Tool.query.count()
                connection_count = Connection.query.count()
                
                print("\nInitialization Summary:")
                print(f"  Stages: {stage_count}")
                print(f"  Categories: {category_count}")
                print(f"  Tools: {tool_count}")
                print(f"  Connections: {connection_count}")
                
                sys.exit(0)
            else:
                logger.error("Initialization failed")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()        link_col = self._find_column(df.columns, ['LINK TO TOOL', 'URL', 'LINK'])
        provider_col = self._find_column(df.columns, ['TOOL PROVIDER', 'PROVIDER'])
        
        if not name_col:
            logger.warning(f"Tool name column not found in sheet for stage: {stage.name}")
            return
            
        # Process each tool
        for idx, row in df.iterrows():
            try:
                tool_name = str(row[name_col]).strip() if not pd.isna(row[name_col]) else None
                
                if not tool_name or tool_name == 'nan':
                    continue
                    
                # Get or create category
                category_name = str(row[category_col]).strip() if category_col and not pd.isna(row[category_col]) else "Uncategorized"
                category = self._get_or_create_category(category_name, "", stage)
                
                # Check if tool already exists
                existing_tool = Tool.query.filter_by(
                    name=tool    def _find_column(self, columns: List[str], possible_names: List[str]) -> Optional[str]:
        """
        Find a column name from a list of possibilities.
        
        Args:
            columns: List of column names in the DataFrame
            possible_names: List of possible column names to search for
            
        Returns:
            The matching column name or None if not found
        """
        for col in columns:
            for possible in possible_names:
                if possible.upper() in col.upper():
                    return col
        return None
        
    def _get_or_create_stage(self, name: str, description: str) -> Stage:
        """
        Get existing stage or create a new one.
        
        Args:
            name: Stage name
            description: Stage description
            
        Returns:
            Stage object
        """
        if name in self.stages_map:
            return self.stages_map[name]
            
        stage = Stage.query.filter_by(name=name).first()
        if not stage:
            stage = Stage(name=name, description=description)
            db.session.add(stage)
            db.session.commit()
            logger.info(f"Created stage: {name}")
        else:
            logger.info(f"Found existing stage: {name}")
            
        self.stages_map[name] = stage
        return stage
        
    def _get_or_create_category(self, name: str, description: str, stage: Stage) -> ToolCategory:
        """
        Get existing category or create a new one.
        
        Args:
            name: Category name
            description: Category description
            stage: Parent stage
            
        Returns:
            ToolCategory object
        """
        key = (stage.name, name)
        if key in self.categories_map:
            return self.categories_map[key]
            
        category = ToolCategory.query.filter_by(
            category=name, stage_id=stage.id
        ).first()
        
        if not category:
            category = ToolCategory(
                category=name,
                description=description,
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.commit()
            logger.info(f"Created category: {name} for stage: {stage.name}")
        else:
            logger.info(f"Found existing category: {name}")
            
        self.categories_map[key] = category
        return category
        
    def _add_example_tools(self, examples_str: str, category: ToolCategory) -> None:
        """
        Add example tools from a comma-separated string.
        
        Args:
            examples_str: Comma-separated string of tool names
            category: Parent category
        """
        tool_names = [name.strip() for name in examples_str.split(',') if name.strip()]
        
        for tool_name in tool_names:
            # Check if tool already exists
            existing_tool = Tool.query.filter_by(
                name=tool_name, category_id=category.id
            ).first()
            
            if not existing_tool:
                tool = Tool(
                    name=tool_name,
                    category_id=category.id,
                    stage_id=category.stage_id
                )
                db.session.add(tool)
                logger.debug(f"Added example tool: {tool_name}")
                
        db.session.commit()
        
    def _process_tools_dataframe(self, df: pd.DataFrame, stage: Stage) -> None:
        """
        Process tools from a DataFrame.
        
        Args:
            df: DataFrame containing tools data
            stage: Stage to associate tools with
        """
        # Find relevant columns
        name_col = self._find_column(df.columns, ['TOOL NAME', 'NAME'])
        category_col = self._find_column(df.columns, ['TOOL TYPE', 'TOOL CATEGORY TYPE', 'TYPE'])
        desc_col = self._find_column(df.columns, ['TOOL CHARACTERISTICS', 'DESCRIPTION'])
        link_col = self._find_column(df.columns, ['LINK TO#!/usr/bin/env python3
"""
init_maldreth_tools.py

Initialize MaLDReTH tools data from Excel file.

This script loads research data lifecycle stages, tool categories, and tools
from an Excel file and populates the database with this information.

Usage:
    python init_maldreth_tools.py [--file path/to/excel/file.xlsx]

Author: MaLDReTH Development Team
Date: 2024
"""

import os
import sys
import argparse
import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models import Stage, ToolCategory, Tool, Connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MaLDReTHToolsInitializer:
    """Handler for initializing MaLDReTH tools data from Excel files."""
    
    def __init__(self, excel_path: str):
        """
        Initialize the tools initializer.
        
        Args:
            excel_path: Path to the Excel file containing tools data
        """
        self.excel_path = excel_path
        self.stages_map: Dict[str, Stage] = {}
        self.categories_map: Dict[Tuple[str, str], ToolCategory] = {}
        
    def validate_excel_file(self) -> bool:
        """
        Validate that the Excel file exists and is readable.
        
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not os.path.exists(self.excel_path):
            logger.error(f"Excel file not found: {self.excel_path}")
            return False
            
        if not os.path.isfile(self.excel_path):
            logger.error(f"Path is not a file: {self.excel_path}")
            return False
            
        try:
            # Try to read the file to ensure it's a valid Excel file
            pd.ExcelFile(self.excel_path)
            return True
        except Exception as e:
            logger.error(f"Invalid Excel file: {e}")
            return False
            
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean column names by removing extra spaces and newlines.
        
        Args:
            df: DataFrame with potentially messy column names
            
        Returns:
            DataFrame with cleaned column names
        """
        df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')
        return df
        
    def load_stages_and_categories(self) -> bool:
        """
        Load lifecycle stages and tool categories from the first sheet.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read the first sheet
            df = pd.read_excel(self.excel_path, sheet_name=0)
            df = self.clean_column_names(df)
            
            logger.info(f"Loading stages from sheet with columns: {list(df.columns)}")
            
            # Expected column names (with variations)
            stage_col = self._find_column(df.columns, ['RESEARCH DATA LIFECYCLE STAGE', 'LIFECYCLE STAGE'])
            category_col = self._find_column(df.columns, ['TOOL CATEGORY TYPE', 'CATEGORY TYPE'])
            desc_col = self._find_column(df.columns, ['DESCRIPTION', 'DESCRIPTION (1 SENTENCE)'])
            examples_col = self._find_column(df.columns, ['EXAMPLES', 'EXAMPLE TOOLS'])
            
            if not all([stage_col, category_col, desc_col]):
                logger.error("Required columns not found in Excel file")
                return False
                
            # Process each row
            for idx, row in df.iterrows():
                try:
                    stage_name = str(row[stage_col]).strip()
                    category_name = str(row[category_col]).strip()
                    description = str(row[desc_col]).strip()
                    
                    # Skip empty rows
                    if pd.isna(stage_name) or stage_name == 'nan':
                        continue
                        
                    # Create or get stage
                    stage = self._get_or_create_stage(stage_name, description)
                    
                    # Create or get category
                    if not pd.isna(category_name) and category_name != 'nan':
                        category = self._get_or_create_category(
                            category_name, description, stage
                        )
                        
                        # Add example tools if present
                        if examples_col and not pd.isna(row[examples_col]):
                            self._add_example_tools(str(row[examples_col]), category)
                            
                except Exception as e:
                    logger.error(f"Error processing row {idx}: {e}")
                    continue
                    
            return True
            
        except Exception as e:
            logger.error(f"Error loading stages and categories: {e}")
            return False
            
    def load_tools_from_sheets(self) -> bool:
        """
        Load detailed tools information from individual stage sheets.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            
            # Skip the first sheet (already processed)
            for sheet_name in excel_file.sheet_names[1:]:
                # Skip sheets that don't match stage names
                if sheet_name.upper() not in [s.upper() for s in self.stages_map.keys()]:
                    logger.info(f"Skipping sheet '{sheet_name}' - not a recognized stage")
                    continue
                    
                logger.info(f"Processing tools sheet: {sheet_name}")
                
                try:
                    # Read sheet with header at row 6 (0-indexed)
                    df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=6)
                    df = self.clean_column_names(df)
                    
                    # Find the stage
                    stage = None
                    for stage_name, stage_obj in self.stages_map.items():
                        if stage_name.upper() == sheet_name.upper():
                            stage = stage_obj
                            break
                            
                    if not stage:
                        logger.warning(f"Stage not found for sheet: {sheet_name}")
                        continue
                        
                    # Process tools
                    self._process_tools_dataframe(df, stage)
                    
                except Exception as e:
                    logger.error(f"Error processing sheet '{sheet_name}': {e}")
                    continue
                    
            return True
            
        except Exception as e:
            logger.error(f"Error loading tools from sheets: {e}")
            return False
            
    def _find_column(self, columns: List[str], possible_names: List[str]) -> Optional[str]:
        """
        Find a
