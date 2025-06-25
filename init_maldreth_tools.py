#!/usr/bin/env python3
"""
init_maldreth_tools.py

Initialize MaLDReTH tools data from Excel file or CSV file.

This script loads research data lifecycle stages, tool categories, and tools
from an Excel/CSV file and populates the database with this information.

Usage:
    python init_maldreth_tools.py [--file path/to/file] [--type excel|csv]

Author: MaLDReTH Development Team
Date: 2024
"""

import os
import sys
import argparse
import logging
import pandas as pd
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
from app import create_app, db
from app.models import Stage, ToolCategory, Tool, Connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maldreth_init.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MaLDReTHDataInitializer:
    """
    Initialize MaLDReTH database from Excel or CSV files.
    
    This class handles the complete initialization process including:
    - Reading and validating input files
    - Creating stages, categories, and tools
    - Establishing connections between stages
    - Error handling and recovery
    """
    
    # Define the expected lifecycle stages in order
    LIFECYCLE_STAGES = [
        "CONCEPTUALISE", "PLAN", "FUND", "COLLECT", "PROCESS", 
        "ANALYSE", "STORE", "PUBLISH", "PRESERVE", "SHARE", 
        "ACCESS", "TRANSFORM"
    ]
    
    # Define standard connections between stages
    STANDARD_CONNECTIONS = [
        ("CONCEPTUALISE", "PLAN", "solid"),
        ("PLAN", "FUND", "solid"),
        ("FUND", "COLLECT", "solid"),
        ("COLLECT", "PROCESS", "solid"),
        ("PROCESS", "ANALYSE", "solid"),
        ("ANALYSE", "STORE", "solid"),
        ("STORE", "PUBLISH", "solid"),
        ("PUBLISH", "PRESERVE", "solid"),
        ("PRESERVE", "SHARE", "solid"),
        ("SHARE", "ACCESS", "solid"),
        ("ACCESS", "TRANSFORM", "solid"),
        ("TRANSFORM", "CONCEPTUALISE", "solid"),
        # Alternative paths
        ("COLLECT", "ANALYSE", "dashed"),
        ("STORE", "PROCESS", "dashed"),
        ("ANALYSE", "COLLECT", "dashed")
    ]
    
    def __init__(self, file_path: str, file_type: str = "excel"):
        """
        Initialize the data initializer.
        
        Args:
            file_path: Path to the input file
            file_type: Type of file ('excel' or 'csv')
        """
        self.file_path = file_path
        self.file_type = file_type.lower()
        self.stages_map: Dict[str, Stage] = {}
        self.categories_map: Dict[Tuple[str, str], ToolCategory] = {}
        self.stats = {
            'stages_created': 0,
            'categories_created': 0,
            'tools_created': 0,
            'connections_created': 0,
            'errors': 0,
            'warnings': 0
        }
        
    def run(self) -> bool:
        """
        Run the complete initialization process.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Starting MaLDReTH initialization from {self.file_type} file: {self.file_path}")
            
            # Validate input file
            if not self._validate_file():
                return False
            
            # Process based on file type
            if self.file_type == "excel":
                success = self._process_excel_file()
            else:
                success = self._process_csv_file()
            
            if not success:
                logger.error("Failed to process input file")
                return False
            
            # Create connections
            self._create_connections()
            
            # Print summary
            self._print_summary()
            
            return self.stats['errors'] == 0
            
        except Exception as e:
            logger.error(f"Fatal error during initialization: {e}", exc_info=True)
            return False
    
    def _validate_file(self) -> bool:
        """Validate that the input file exists and is readable."""
        if not os.path.exists(self.file_path):
            logger.error(f"File not found: {self.file_path}")
            return False
            
        if not os.path.isfile(self.file_path):
            logger.error(f"Path is not a file: {self.file_path}")
            return False
            
        # Check file extension
        ext = os.path.splitext(self.file_path)[1].lower()
        if self.file_type == "excel" and ext not in ['.xlsx', '.xls']:
            logger.error(f"Invalid Excel file extension: {ext}")
            return False
        elif self.file_type == "csv" and ext != '.csv':
            logger.error(f"Invalid CSV file extension: {ext}")
            return False
            
        return True
    
    def _process_excel_file(self) -> bool:
        """Process an Excel file containing MaLDReTH data."""
        try:
            # First, try to read the summary sheet (first sheet)
            logger.info("Reading Excel file...")
            excel_file = pd.ExcelFile(self.file_path)
            
            # Process the first sheet for overview data
            if not self._process_overview_sheet(excel_file):
                return False
            
            # Process individual stage sheets
            if not self._process_stage_sheets(excel_file):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            self.stats['errors'] += 1
            return False
    
    def _process_csv_file(self) -> bool:
        """Process a CSV file containing MaLDReTH data."""
        try:
            logger.info("Reading CSV file...")
            
            # Read CSV with multiple encoding attempts
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(self.file_path, encoding=encoding)
                    logger.info(f"Successfully read CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
                    
            if df is None:
                logger.error("Failed to read CSV file with any encoding")
                return False
            
            # Clean column names
            df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')
            
            # Process the data
            return self._process_dataframe(df)
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            self.stats['errors'] += 1
            return False
    
    def _process_overview_sheet(self, excel_file: pd.ExcelFile) -> bool:
        """Process the overview sheet containing stages and categories."""
        try:
            # Read first sheet
            df = pd.read_excel(excel_file, sheet_name=0)
            df = self._clean_dataframe(df)
            
            logger.info(f"Processing overview sheet with {len(df)} rows")
            logger.debug(f"Columns found: {list(df.columns)}")
            
            return self._process_dataframe(df)
            
        except Exception as e:
            logger.error(f"Error processing overview sheet: {e}")
            self.stats['errors'] += 1
            return False
    
    def _process_stage_sheets(self, excel_file: pd.ExcelFile) -> bool:
        """Process individual stage sheets containing detailed tool information."""
        try:
            # Get all sheet names
            sheet_names = excel_file.sheet_names[1:]  # Skip first sheet
            
            for sheet_name in sheet_names:
                # Normalize sheet name
                normalized_name = sheet_name.strip().upper()
                
                # Check if it's a valid stage
                if normalized_name not in self.LIFECYCLE_STAGES:
                    logger.debug(f"Skipping non-stage sheet: {sheet_name}")
                    continue
                
                logger.info(f"Processing stage sheet: {sheet_name}")
                
                # Find the corresponding stage
                stage = self._find_stage(normalized_name)
                if not stage:
                    logger.warning(f"Stage not found for sheet: {sheet_name}")
                    continue
                
                # Process the sheet
                try:
                    # Try different header rows (some sheets have headers at row 6)
                    for header_row in [0, 5, 6]:
                        try:
                            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row)
                            if len(df.columns) > 3:  # Valid data should have multiple columns
                                break
                        except:
                            continue
                    
                    df = self._clean_dataframe(df)
                    
                    # Skip empty dataframes
                    if df.empty or len(df.columns) < 2:
                        logger.warning(f"Empty or invalid data in sheet: {sheet_name}")
                        continue
                    
                    # Process tools in this sheet
                    self._process_stage_tools(df, stage)
                    
                except Exception as e:
                    logger.error(f"Error processing sheet {sheet_name}: {e}")
                    self.stats['warnings'] += 1
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing stage sheets: {e}")
            self.stats['errors'] += 1
            return False
    
    def _process_dataframe(self, df: pd.DataFrame) -> bool:
        """Process a dataframe containing stages, categories, and tools."""
        try:
            # Identify columns
            columns = self._identify_columns(df.columns)
            
            if not columns.get('stage'):
                logger.error("Stage column not found in data")
                return False
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    # Get stage name
                    stage_name = self._clean_value(row[columns['stage']])
                    if not stage_name:
                        continue
                    
                    # Normalize stage name
                    stage_name = stage_name.upper()
                    
                    # Create or get stage
                    stage = self._get_or_create_stage(stage_name)
                    
                    # Process category if present
                    if columns.get('category'):
                        category_name = self._clean_value(row[columns['category']])
                        if category_name:
                            description = ""
                            if columns.get('description'):
                                description = self._clean_value(row[columns['description']])
                            
                            category = self._get_or_create_category(
                                category_name, description, stage
                            )
                            
                            # Process examples/tools if present
                            if columns.get('examples'):
                                examples = self._clean_value(row[columns['examples']])
                                if examples:
                                    self._process_examples(examples, category, stage)
                    
                except Exception as e:
                    logger.error(f"Error processing row {idx}: {e}")
                    self.stats['warnings'] += 1
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing dataframe: {e}")
            self.stats['errors'] += 1
            return False
    
    def _process_stage_tools(self, df: pd.DataFrame, stage: Stage) -> None:
        """Process tools from a stage-specific sheet."""
        try:
            # Identify columns
            columns = self._identify_tool_columns(df.columns)
            
            if not columns.get('name'):
                logger.warning(f"Tool name column not found for stage: {stage.name}")
                return
            
            # Process each tool
            for idx, row in df.iterrows():
                try:
                    tool_name = self._clean_value(row[columns['name']])
                    if not tool_name:
                        continue
                    
                    # Get or create category
                    category_name = "General"  # Default category
                    if columns.get('category'):
                        cat_value = self._clean_value(row[columns['category']])
                        if cat_value:
                            category_name = cat_value
                    
                    category = self._get_or_create_category(category_name, "", stage)
                    
                    # Check if tool already exists
                    existing_tool = Tool.query.filter_by(
                        name=tool_name,
                        category_id=category.id
                    ).first()
                    
                    if existing_tool:
                        logger.debug(f"Tool already exists: {tool_name}")
                        continue
                    
                    # Create tool
                    tool = Tool(
                        name=tool_name,
                        category_id=category.id,
                        stage_id=stage.id
                    )
                    
                    # Add optional fields
                    if columns.get('description'):
                        tool.description = self._clean_value(row[columns['description']])
                    
                    if columns.get('link'):
                        tool.link = self._clean_value(row[columns['link']])
                    
                    if columns.get('provider'):
                        tool.provider = self._clean_value(row[columns['provider']])
                    
                    db.session.add(tool)
                    self.stats['tools_created'] += 1
                    logger.debug(f"Created tool: {tool_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing tool at row {idx}: {e}")
                    self.stats['warnings'] += 1
                    continue
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error processing stage tools: {e}")
            self.stats['errors'] += 1
    
    def _identify_columns(self, columns: pd.Index) -> Dict[str, str]:
        """Identify relevant columns in the dataframe."""
        column_mapping = {
            'stage': ['RESEARCH DATA LIFECYCLE STAGE', 'LIFECYCLE STAGE', 'STAGE'],
            'category': ['TOOL CATEGORY TYPE', 'CATEGORY TYPE', 'CATEGORY'],
            'description': ['DESCRIPTION', 'DESCRIPTION (1 SENTENCE)'],
            'examples': ['EXAMPLES', 'EXAMPLE TOOLS', 'TOOLS']
        }
        
        found_columns = {}
        
        for key, possible_names in column_mapping.items():
            for col in columns:
                col_upper = col.upper()
                for possible in possible_names:
                    if possible in col_upper:
                        found_columns[key] = col
                        break
                if key in found_columns:
                    break
        
        return found_columns
    
    def _identify_tool_columns(self, columns: pd.Index) -> Dict[str, str]:
        """Identify tool-specific columns in a dataframe."""
        column_mapping = {
            'name': ['TOOL NAME', 'NAME', 'TOOL'],
            'category': ['TOOL TYPE', 'TOOL CATEGORY TYPE', 'TYPE', 'CATEGORY'],
            'description': ['TOOL CHARACTERISTICS', 'CHARACTERISTICS', 'DESCRIPTION'],
            'link': ['LINK TO TOOL', 'URL', 'LINK', 'TOOL LINK'],
            'provider': ['TOOL PROVIDER', 'PROVIDER', 'VENDOR']
        }
        
        found_columns = {}
        
        for key, possible_names in column_mapping.items():
            for col in columns:
                col_upper = col.upper()
                for possible in possible_names:
                    if possible in col_upper:
                        found_columns[key] = col
                        break
                if key in found_columns:
                    break
        
        return found_columns
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean a dataframe by removing empty rows and fixing column names."""
        # Clean column names
        df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove rows where all values are empty strings
        df = df[~(df == '').all(axis=1)]
        
        return df
    
    def _clean_value(self, value: Any) -> str:
        """Clean a cell value from the dataframe."""
        if pd.isna(value):
            return ""
        
        # Convert to string and strip
        value = str(value).strip()
        
        # Remove 'nan' strings
        if value.lower() == 'nan':
            return ""
        
        # Remove BOM and other special characters
        value = value.replace('\ufeff', '').replace('\u200b', '')
        
        return value
    
    def _get_or_create_stage(self, name: str) -> Optional[Stage]:
        """Get existing stage or create a new one."""
        # Check cache first
        if name in self.stages_map:
            return self.stages_map[name]
        
        # Check database
        stage = Stage.query.filter_by(name=name).first()
        
        if not stage:
            # Create new stage
            stage = Stage(
                name=name,
                description=self._get_stage_description(name)
            )
            db.session.add(stage)
            db.session.commit()
            self.stats['stages_created'] += 1
            logger.info(f"Created stage: {name}")
        
        self.stages_map[name] = stage
        return stage
    
    def _get_or_create_category(self, name: str, description: str, stage: Stage) -> Optional[ToolCategory]:
        """Get existing category or create a new one."""
        # Check cache first
        cache_key = (stage.name, name)
        if cache_key in self.categories_map:
            return self.categories_map[cache_key]
        
        # Check database
        category = ToolCategory.query.filter_by(
            category=name,
            stage_id=stage.id
        ).first()
        
        if not category:
            # Create new category
            category = ToolCategory(
                category=name,
                description=description or f"Tools for {name.lower()}",
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.commit()
            self.stats['categories_created'] += 1
            logger.debug(f"Created category: {name} for stage: {stage.name}")
        
        self.categories_map[cache_key] = category
        return category
    
    def _process_examples(self, examples: str, category: ToolCategory, stage: Stage) -> None:
        """Process example tools from a comma-separated string."""
        # Split by comma and clean each tool name
        tool_names = [name.strip() for name in examples.split(',') if name.strip()]
        
        for tool_name in tool_names:
            # Skip empty or invalid names
            if not tool_name or tool_name.lower() in ['nan', 'none', 'n/a']:
                continue
            
            # Check if tool already exists
            existing_tool = Tool.query.filter_by(
                name=tool_name,
                category_id=category.id
            ).first()
            
            if not existing_tool:
                tool = Tool(
                    name=tool_name,
                    category_id=category.id,
                    stage_id=stage.id
                )
                db.session.add(tool)
                self.stats['tools_created'] += 1
                logger.debug(f"Created tool: {tool_name}")
        
        db.session.commit()
    
    def _find_stage(self, name: str) -> Optional[Stage]:
        """Find a stage by name (case-insensitive)."""
        name_upper = name.upper()
        
        # Check cache
        for stage_name, stage in self.stages_map.items():
            if stage_name.upper() == name_upper:
                return stage
        
        # Check database
        all_stages = Stage.query.all()
        for stage in all_stages:
            if stage.name.upper() == name_upper:
                self.stages_map[stage.name] = stage
                return stage
        
        return None
    
    def _create_connections(self) -> None:
        """Create standard connections between stages."""
        logger.info("Creating stage connections...")
        
        for from_name, to_name, conn_type in self.STANDARD_CONNECTIONS:
            try:
                # Find stages
                from_stage = self._find_stage(from_name)
                to_stage = self._find_stage(to_name)
                
                if not from_stage or not to_stage:
                    logger.warning(f"Stages not found for connection: {from_name} -> {to_name}")
                    continue
                
                # Check if connection exists
                existing = Connection.query.filter_by(
                    from_stage_id=from_stage.id,
                    to_stage_id=to_stage.id
                ).first()
                
                if existing:
                    logger.debug(f"Connection already exists: {from_name} -> {to_name}")
                    continue
                
                # Create connection
                connection = Connection(
                    from_stage_id=from_stage.id,
                    to_stage_id=to_stage.id,
                    type=conn_type
                )
                db.session.add(connection)
                self.stats['connections_created'] += 1
                logger.debug(f"Created connection: {from_name} -> {to_name}")
                
            except Exception as e:
                logger.error(f"Error creating connection {from_name} -> {to_name}: {e}")
                self.stats['warnings'] += 1
                continue
        
        db.session.commit()
    
    def _get_stage_description(self, stage_name: str) -> str:
        """Get the standard description for a stage."""
        descriptions = {
            "CONCEPTUALISE": "To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.",
            "PLAN": "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.",
            "FUND": "To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.",
            "COLLECT": "To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.",
            "PROCESS": "To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.",
            "ANALYSE": "To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results.",
            "STORE": "To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.",
            "PUBLISH": "To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.",
            "PRESERVE": "To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.",
            "SHARE": "To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community.",
            "ACCESS": "To control and manage data access by designated users and reusers. This may be in the form of publicly available published information.",
            "TRANSFORM": "To create new data from the original, for example by migration into a different format or by creating a subset."
        }
        
        return descriptions.get(stage_name.upper(), f"Stage for {stage_name.lower()} in the research data lifecycle")
    
    def _print_summary(self) -> None:
        """Print a summary of the initialization process."""
        print("\n" + "=" * 60)
        print("MaLDReTH Initialization Summary")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Input File: {self.file_path}")
        print(f"File Type: {self.file_type}")
        print("\nResults:")
        print(f"  Stages Created: {self.stats['stages_created']}")
        print(f"  Categories Created: {self.stats['categories_created']}")
        print(f"  Tools Created: {self.stats['tools_created']}")
        print(f"  Connections Created: {self.stats['connections_created']}")
        print(f"  Warnings: {self.stats['warnings']}")
        print(f"  Errors: {self.stats['errors']}")
        print("\nDatabase Totals:")
        print(f"  Total Stages: {Stage.query.count()}")
        print(f"  Total Categories: {ToolCategory.query.count()}")
        print(f"  Total Tools: {Tool.query.count()}")
        print(f"  Total Connections: {Connection.query.count()}")
        print("=" * 60)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Initialize MaLDReTH database from Excel or CSV file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize from Excel file
  python init_maldreth_tools.py --file data/research_data_lifecycle.xlsx
  
  # Initialize from CSV file
  python init_maldreth_tools.py --file data/tools.csv --type csv
  
  # Clear existing data before initialization
  python init_maldreth_tools.py --file data/tools.xlsx --clear
        """
    )
    
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the Excel or CSV file containing MaLDReTH data"
    )
    
    parser.add_argument(
        "--type",
        type=str,
        choices=["excel", "csv"],
        default="excel",
        help="Type of input file (default: excel)"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before initialization"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing data if requested
            if args.clear:
                logger.info("Clearing existing data...")
                
                # Delete in correct order to avoid foreign key constraints
                Tool.query.delete()
                ToolCategory.query.delete()
                Connection.query.delete()
                Stage.query.delete()
                db.session.commit()
                
                logger.info("Existing data cleared successfully")
            
            # Initialize data
            initializer = MaLDReTHDataInitializer(args.file, args.type)
            success = initializer.run()
            
            if success:
                logger.info("Initialization completed successfully!")
                sys.exit(0)
            else:
                logger.error("Initialization failed!")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
