# Map possible column names
                column_mappings = {
                    'stage': ['RESEARCH DATA LIFECYCLE STAGE', 'stage', 'Stage'],
                    'category': ['TOOL CATEGORY TYPE', 'category', 'Category'],
                    'description': ['DESCRIPTION', 'description', 'Description'],
                    'examples': ['EXAMPLES', 'examples', 'Tools']
                }
                
                # Get actual column names
                headers = reader.fieldnames or []
                actual_columns = {}
                for key, possible_names in column_mappings.items():
                    for header in headers:
                        if any(name in header for name in possible_names):
                            actual_columns[key] = header
                            break
                
                if not all(k in actual_columns for k in ['stage', 'category']):
                    logger.error(f"Required columns not found. Headers: {headers}")
                    return False
                
                for row in reader:
                    try:
                        stage_name = self.clean_value(row.get(actual_columns['stage'], ''))
                        category_name = self.clean_value(row.get(actual_columns['category'], ''))
                        
                        if not stage_name:
                            continue
                            
                        # Find or create stage
                        stage = self.stages_map.get(stage_name)
                        if not stage:
                            stage = Stage.query.filter_by(name=stage_name).first()
                            if not stage:
                                # Create stage if it doesn't exist
                                stage = Stage(name=stage_name, description="")
                                db.session.add(stage)
                                db.session.flush()
                                self.stages_map[stage_name] = stage
                                self.migration_stats['stages_created'] += 1
                        
                        # Find or create category
                        category_key = (stage_name, category_name)
                        category = self.categories_map.get(category_key)
                        if not category:
                            category = ToolCategory.query.filter_by(
                                category=category_name, stage_id=stage.id
                            ).first()
                            if not category:
                                desc = self.clean_value(row.get(actual_columns.get('description', ''), ''))
                                category = ToolCategory(
                                    category=category_name,
                                    description=desc,
                                    stage_id=stage.id
                                )
                                db.session.add(category)
                                db.session.flush()
                                self.categories_map[category_key] = category
                                self.migration_stats['categories_created'] += 1
                        
                        # Process tools/examples
                        if 'examples' in actual_columns:
                            examples = self.clean_value(row.get(actual_columns['examples'], ''))
                            if examples:
                                tool_names = [name.strip() for name in examples.split(',') if name.strip()]
                                for tool_name in tool_names:
                                    # Check if tool exists
                                    existing_tool = Tool.query.filter_by(
                                        name=tool_name, category_id=category.id
                                    ).first()
                                    
                                    if not existing_tool:
                                        tool = Tool(
                                            name=tool_name,
                                            category_id=category.id,
                                            stage_id=stage.id
                                        )
                                        db.session.add(tool)
                                        self.migration_stats['tools_created'] += 1
                                        
                    except Exception as e:
                        logger.error(f"Error processing tool row: {e}")
                        self.migration_stats['errors'] += 1
                        continue
                        
                db.session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error migrating tools: {e}")
            self.migration_stats['errors'] += 1
            return False
            
    def migrate_connections(self, filename: str = "connections.csv") -> bool:
        """
        Migrate stage connections from CSV file.
        
        Args:
            filename: Name of the connections CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        # First try to load from CSV file
        filepath = os.path.join(self.csv_directory, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        try:
                            from_stage = self.clean_value(row.get('from', ''))
                            to_stage = self.clean_value(row.get('to', ''))
                            conn_type = self.clean_value(row.get('type', 'solid'))
                            
                            if not from_stage or not to_stage:
                                continue
                                
                            self._create_connection(from_stage, to_stage, conn_type)
                            
                        except Exception as e:
                            logger.error(f"Error processing connection row: {e}")
                            self.migration_stats['errors'] += 1
                            continue
                            
                db.session.commit()
                return True
                
            except Exception as e:
                logger.error(f"Error reading connections file: {e}")
                
        # If no file or error, create default connections
        logger.info("Creating default stage connections...")
        return self._create_default_connections()
        
    def _create_connection(self, from_name: str, to_name: str, conn_type: str = "solid") -> bool:
        """
        Create a connection between two stages.
        
        Args:
            from_name: Name of the source stage
            to_name: Name of the target stage
            conn_type: Type of connection (solid or dashed)
            
        Returns:
            bool: True if created, False if already exists or error
        """
        try:
            # Find stages
            from_stage = Stage.query.filter_by(name=from_name).first()
            to_stage = Stage.query.filter_by(name=to_name).first()
            
            if not from_stage or not to_stage:
                logger.warning(f"Stages not found for connection: {from_name} -> {to_name}")
                return False
                
            # Check if connection exists
            existing = Connection.query.filter_by(
                from_stage_id=from_stage.id,
                to_stage_id=to_stage.id
            ).first()
            
            if existing:
                return False
                
            # Create connection
            connection = Connection(
                from_stage_id=from_stage.id,
                to_stage_id=to_stage.id,
                type=conn_type
            )
            db.session.add(connection)
            self.migration_stats['connections_created'] += 1
            logger.info(f"Created connection: {from_name} -> {to_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating connection: {e}")
            return False
            
    def _create_default_connections(self) -> bool:
        """
        Create default connections between stages.
        
        Returns:
            bool: True if successful, False otherwise
        """
        default_connections = [
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
        
        for from_name, to_name, conn_type in default_connections:
            self._create_connection(from_name, to_name, conn_type)
            
        db.session.commit()
        return True
        
    def generate_migration_report(self) -> str:
        """
        Generate a summary report of the migration.
        
        Returns:
            str: Migration report
        """
        report = [
            "\n" + "=" * 50,
            "Migration Summary Report",
            "=" * 50,
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"CSV Directory: {self.csv_directory}",
            "",
            "Results:",
            f"  Stages Created: {self.migration_stats['stages_created']}",
            f"  Stages Updated: {self.migration_stats['stages_updated']}",
            f"  Categories Created: {self.migration_stats['categories_created']}",
            f"  Tools Created: {self.migration_stats['tools_created']}",
            f"  Tools Updated: {self.migration_stats['tools_updated']}",
            f"  Connections Created: {self.migration_stats['connections_created']}",
            f"  Errors: {self.migration_stats['errors']}",
            "",
            "Database Totals:",
            f"  Total Stages: {Stage.query.count()}",
            f"  Total Categories: {ToolCategory.query.count()}",
            f"  Total Tools: {Tool.query.count()}",
            f"  Total Connections: {Connection.query.count()}",
            "=" * 50
        ]
        
        return "\n".join(report)
        
    def run(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting CSV data migration...")
        
        # Validate CSV directory
        if not self.validate_csv_directory():
            return False
            
        # Migrate data in order
        steps = [
            ("stages", self.migrate_stages),
            ("categories", self.migrate_categories),
            ("tools", self.migrate_tools),
            ("connections", self.migrate_connections)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Migrating {step_name}...")
            if not step_func():
                logger.error(f"Failed to migrate {step_name}")
                # Continue with other steps even if one fails
                
        # Generate and display report
        report = self.generate_migration_report()
        print(report)
        
        # Save report to file
        report_file = os.path.join(self.csv_directory, f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        try:
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"Migration report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            
        return self.migration_stats['errors'] == 0


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Migrate MaLDReTH data from CSV files"
    )
    parser.add_argument(
        "--csv-dir",
        type=str,
        default="data/csv",
        help="Directory containing CSV files"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before migration"
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
                
            # Run migration
            migrator = CSVDataMigrator(args.csv_dir)
            success = migrator.run()
            
            sys.exit(0 if success else 1)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()            # Try alternative filename
            alt_filename = "research_data_lifecycle.csv"
            filepath = os.path.join(self.csv_directory, alt_filename)
            if not os.path.exists(filepath):
                logger.warning(f"Tools file not found: {filename} or {alt_filename}")
                return True
                
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # Map possible column names
                column_mappings = {
                    'stage        except Exception as e:
            logger.error(f"Error migrating categories: {e}")
            self.migration_stats['errors'] += 1
            return False
            
    def migrate_tools(self, filename: str = "tools.csv") -> bool:
        """
        Migrate tools data from CSV file.
        
        Args:
            filename: Name of the tools CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        filepath = os.path.join(self.csv_directory, filename)
        if not os.path.exists(filepath):
            ##!/usr/bin/env python3
"""
migrate_maldreth_data_standalone.py

Migrate MaLDReTH data from CSV files to the database.

This script handles migration of research data lifecycle information from
CSV files, with robust error handling and data validation.

Usage:
    python migrate_maldreth_data_standalone.py [--csv-dir path/to/csv/files]

Author: MaLDReTH Development Team
Date: 2024
"""

import os
import sys
import csv
import argparse
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app import create_app, db
from app.models import Stage, ToolCategory, Tool, Connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CSVDataMigrator:
    """Handler for migrating MaLDReTH data from CSV files."""
    
    def __init__(self, csv_directory: str):
        """
        Initialize the CSV data migrator.
        
        Args:
            csv_directory: Directory containing CSV files
        """
        self.csv_directory = csv_directory
        self.stages_map: Dict[str, Stage] = {}
        self.categories_map: Dict[Tuple[str, str], ToolCategory] = {}
        self.migration_stats = {
            'stages_created': 0,
            'stages_updated': 0,
            'categories_created': 0,
            'tools_created': 0,
            'tools_updated': 0,
            'connections_created': 0,
            'errors': 0
        }
        
    def validate_csv_directory(self) -> bool:
        """
        Validate that the CSV directory exists and contains CSV files.
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not os.path.exists(self.csv_directory):
            logger.error(f"CSV directory not found: {self.csv_directory}")
            return False
            
        if not os.path.isdir(self.csv_directory):
            logger.error(f"Path is not a directory: {self.csv_directory}")
            return False
            
        csv_files = [f for f in os.listdir(self.csv_directory) if f.endswith('.csv')]
        if not csv_files:
            logger.error(f"No CSV files found in directory: {self.csv_directory}")
            return False
            
        logger.info(f"Found {len(csv_files)} CSV files to process")
        return True
        
    def clean_value(self, value: str) -> str:
        """
        Clean a CSV value by stripping whitespace and handling encoding.
        
        Args:
            value: Raw value from CSV
            
        Returns:
            Cleaned string value
        """
        if not value:
            return ""
        return value.strip().replace('\ufeff', '')  # Remove BOM if present
        
    def migrate_stages(self, filename: str = "stages.csv") -> bool:
        """
        Migrate stages data from CSV file.
        
        Args:
            filename: Name of the stages CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        filepath = os.path.join(self.csv_directory, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Stages file not found: {filepath}")
            return True  # Not critical if missing
            
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        stage_name = self.clean_value(row.get('stage', ''))
                        description = self.clean_value(row.get('description', ''))
                        
                        if not stage_name:
                            logger.warning("Skipping row with empty stage name")
                            continue
                            
                        # Check if stage exists
                        stage = Stage.query.filter_by(name=stage_name).first()
                        
                        if stage:
                            # Update existing stage
                            stage.description = description
                            self.migration_stats['stages_updated'] += 1
                            logger.info(f"Updated stage: {stage_name}")
                        else:
                            # Create new stage
                            stage = Stage(name=stage_name, description=description)
                            db.session.add(stage)
                            self.migration_stats['stages_created'] += 1
                            logger.info(f"Created stage: {stage_name}")
                            
                        self.stages_map[stage_name] = stage
                        
                    except Exception as e:
                        logger.error(f"Error processing stage row: {e}")
                        self.migration_stats['errors'] += 1
                        continue
                        
                db.session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error migrating stages: {e}")
            self.migration_stats['errors'] += 1
            return False
            
    def migrate_categories(self, filename: str = "categories.csv") -> bool:
        """
        Migrate tool categories from CSV file.
        
        Args:
            filename: Name of the categories CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        filepath = os.path.join(self.csv_directory, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Categories file not found: {filepath}")
            return True  # Not critical if missing
            
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        stage_name = self.clean_value(row.get('stage', ''))
                        category_name = self.clean_value(row.get('category', ''))
                        description = self.clean_value(row.get('description', ''))
                        
                        if not stage_name or not category_name:
                            logger.warning("Skipping row with empty stage or category")
                            continue
                            
                        # Find stage
                        stage = self.stages_map.get(stage_name) or Stage.query.filter_by(name=stage_name).first()
                        if not stage:
                            logger.warning(f"Stage not found: {stage_name}")
                            continue
                            
                        # Check if category exists
                        category = ToolCategory.query.filter_by(
                            category=category_name, stage_id=stage.id
                        ).first()
                        
                        if not category:
                            # Create new category
                            category = ToolCategory(
                                category=category_name,
                                description=description,
                                stage_id=stage.id
                            )
                            db.session.add(category)
                            self.migration_stats['categories_created'] += 1
                            logger.info(f"Created category: {category_name} for stage: {stage_name}")
                            
                        self.categories_map[(stage_name, category_name)] = category
                        
                    except Exception as e:
                        logger.error(f"Error processing category row: {e}")
                        self.migration_stats['errors'] += 1
                        continue
                        
                db.session.commit()
                return True
                
        except Exception as e:
            logger.error(f
