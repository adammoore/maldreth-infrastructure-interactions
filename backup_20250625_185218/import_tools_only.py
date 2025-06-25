"""
Import only tools from CSV file into existing database with lifecycle stages.
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from environment or use default SQLite."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://")
        return database_url
    else:
        return "sqlite:///interactions.db"


def clean_text(text):
    """Clean text by removing extra whitespace and handling None values."""
    if pd.isna(text) or text is None:
        return ""
    return str(text).strip()


def import_tools_from_csv(csv_file):
    """Import tools from CSV file using raw SQL."""
    engine = create_engine(get_database_url())

    logger.info(f"Reading data from {csv_file}")

    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        logger.info(f"Successfully read {len(df)} rows from CSV")

        # Clean column names
        df.columns = df.columns.str.strip()

        with engine.connect() as conn:
            # Get all stages for mapping
            result = conn.execute(text("SELECT id, name FROM lifecycle_stages"))
            stages = {row.name.upper(): row.id for row in result}
            logger.info(f"Found {len(stages)} lifecycle stages in database")

            # Process each row
            imported_categories = 0
            imported_tools = 0

            for idx, row in df.iterrows():
                try:
                    # Extract stage name
                    stage_name = clean_text(
                        row.get("RESEARCH DATA LIFECYCLE STAGE", "")
                    )
                    if not stage_name:
                        logger.warning(f"Row {idx}: Missing stage name, skipping")
                        continue

                    # Find matching stage
                    stage_id = None
                    stage_name_upper = stage_name.upper()

                    # Try exact match first
                    if stage_name_upper in stages:
                        stage_id = stages[stage_name_upper]
                    else:
                        # Try partial match
                        for db_stage_name, db_stage_id in stages.items():
                            if (
                                stage_name_upper in db_stage_name
                                or db_stage_name in stage_name_upper
                            ):
                                stage_id = db_stage_id
                                break

                    if not stage_id:
                        logger.warning(
                            f"Row {idx}: Stage '{stage_name}' not found in database, skipping"
                        )
                        continue

                    # Extract tool category
                    category_name = clean_text(row.get("TOOL CATEGORY TYPE", ""))
                    if not category_name:
                        logger.warning(f"Row {idx}: Missing category name, skipping")
                        continue

                    # Check if category exists
                    result = conn.execute(
                        text(
                            "SELECT id FROM tool_categories WHERE stage_id = :stage_id AND name = :name"
                        ),
                        {"stage_id": stage_id, "name": category_name},
                    )
                    category_row = result.first()

                    if not category_row:
                        # Create category
                        description = clean_text(
                            row.get("DESCRIPTION", "")
                            or row.get("DESCRIPTION (1 SENTENCE)", "")
                        )
                        result = conn.execute(
                            text(
                                """
                                INSERT INTO tool_categories (name, description, stage_id, "order", created_at)
                                VALUES (:name, :description, :stage_id, 0, :created_at)
                            """
                            ),
                            {
                                "name": category_name,
                                "description": description,
                                "stage_id": stage_id,
                                "created_at": datetime.utcnow(),
                            },
                        )
                        conn.commit()

                        # Get the new category ID
                        result = conn.execute(
                            text(
                                "SELECT id FROM tool_categories WHERE stage_id = :stage_id AND name = :name"
                            ),
                            {"stage_id": stage_id, "name": category_name},
                        )
                        category_row = result.first()
                        imported_categories += 1
                        logger.info(f"Created category: {category_name}")

                    category_id = category_row.id

                    # Extract and create tools
                    tools_str = clean_text(row.get("EXAMPLES", ""))
                    if tools_str:
                        # Split tools by comma and clean each one
                        tools = [clean_text(tool) for tool in tools_str.split(",")]
                        for tool_name in tools:
                            if tool_name and tool_name != "":
                                # Check if tool already exists
                                result = conn.execute(
                                    text(
                                        "SELECT id FROM tools WHERE name = :name AND stage_id = :stage_id"
                                    ),
                                    {"name": tool_name, "stage_id": stage_id},
                                )

                                if not result.first():
                                    # Create tool
                                    conn.execute(
                                        text(
                                            """
                                            INSERT INTO tools (
                                                name, description, stage_id, category_id, 
                                                tool_type, source_type, scope, is_interoperable,
                                                is_featured, usage_count, created_at
                                            )
                                            VALUES (
                                                :name, :description, :stage_id, :category_id,
                                                :tool_type, 'unknown', 'generic', 0,
                                                0, 0, :created_at
                                            )
                                        """
                                        ),
                                        {
                                            "name": tool_name,
                                            "description": f"Tool for {category_name}",
                                            "stage_id": stage_id,
                                            "category_id": category_id,
                                            "tool_type": category_name,
                                            "created_at": datetime.utcnow(),
                                        },
                                    )
                                    conn.commit()
                                    imported_tools += 1
                                    logger.info(f"Created tool: {tool_name}")

                except Exception as e:
                    logger.error(f"Error processing row {idx}: {str(e)}")
                    continue

            logger.info("\nImport Summary:")
            logger.info(f"  - New Categories: {imported_categories}")
            logger.info(f"  - New Tools: {imported_tools}")

    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        raise


def main():
    """Main function."""
    # Find CSV file
    csv_file = None
    possible_names = [
        "v0.3_ Landscape Review of Research Tools   - Tool categories and descriptions (1).csv",
        "tools.csv",
        "research_data_lifecycle.csv",
        "Tool categories and descriptions.csv",
        "maldreth_tools.csv",
    ]

    for name in possible_names:
        if os.path.exists(name):
            csv_file = name
            logger.info(f"Found CSV file: {csv_file}")
            break

    if not csv_file:
        # Look for any CSV file with relevant keywords
        csv_files = list(Path(".").glob("*.csv"))
        for f in csv_files:
            if any(
                keyword in f.name.lower()
                for keyword in [
                    "tool",
                    "lifecycle",
                    "research",
                    "maldreth",
                    "landscape",
                ]
            ):
                csv_file = str(f)
                logger.info(f"Using CSV file: {csv_file}")
                break

    if not csv_file:
        logger.error("No suitable CSV file found!")
        logger.error(
            "Please ensure you have a CSV file with tool data in the current directory"
        )
        sys.exit(1)

    # Import tools
    import_tools_from_csv(csv_file)

    # Show final counts
    engine = create_engine(get_database_url())
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM tool_categories"))
        category_count = result.scalar()

        result = conn.execute(text("SELECT COUNT(*) FROM tools"))
        tool_count = result.scalar()

        logger.info("\nFinal Database Status:")
        logger.info(f"  - Total Categories: {category_count}")
        logger.info(f"  - Total Tools: {tool_count}")


if __name__ == "__main__":
    main()
