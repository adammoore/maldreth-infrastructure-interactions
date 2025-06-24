"""
Initialize MaLDReTH tools database with tool categories and examples.

This script populates the database with the tool categories and example tools
from the MaLDReTH Deliverable 2 categorization schema.
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from environment or use default SQLite."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        return database_url
    else:
        return 'sqlite:///interactions.db'


# MaLDReTH tool data from Deliverable 2
MALDRETH_TOOLS_DATA = {
    'CONCEPTUALISE': [
        {
            'category': 'Mind mapping, concept mapping and knowledge modelling',
            'description': 'Tools that define the entities of research and their relationships',
            'tools': ['Miro', 'Meister Labs (MindMeister + MeisterTask)', 'XMind']
        },
        {
            'category': 'Diagramming and flowchart',
            'description': 'Tools that detail the research workflow',
            'tools': ['Lucidchart', 'Draw.io (now Diagrams.net)', 'Creately']
        },
        {
            'category': 'Wireframing and prototyping',
            'description': 'Tools that visualise and demonstrate the research workflow',
            'tools': ['Balsamiq', 'Figma']
        }
    ],
    'PLAN': [
        {
            'category': 'Data management planning (DMP)',
            'description': 'Tools focused on enabling preparation and submission of data management plans',
            'tools': ['DMP Tool', 'DMP Online', 'RDMO']
        },
        {
            'category': 'Project planning',
            'description': 'Tools designed to enable project planning',
            'tools': ['Trello', 'Asana', 'Microsoft Project']
        },
        {
            'category': 'Combined DMP/project',
            'description': 'Tools which combine project planning with the ability to prepare data management plans',
            'tools': ['Data Stewardship Wizard', 'Redbox research data', 'Argos']
        }
    ],
    'COLLECT': [
        {
            'category': 'Quantitative data collection tool',
            'description': 'Tools that collect quantitative data',
            'tools': ['Open Data Kit', 'GBIF', 'Cedar WorkBench']
        },
        {
            'category': 'Qualitative data collection (e.g. Survey tool)',
            'description': 'Tools that collect qualitative data',
            'tools': ['Survey Monkey', 'Online Surveys', 'Zooniverse']
        },
        {
            'category': 'Harvesting tool (e.g. WebScrapers)',
            'description': 'Tools that harvest data from various sources',
            'tools': ['Netlytic', 'IRODS', 'DROID']
        }
    ],
    'PROCESS': [
        {
            'category': 'Electronic laboratory notebooks (ELNs)',
            'description': 'Tools that enable aggregation, management, and organization of experimental and physical sample data',
            'tools': ['elabnext', 'E-lab FTW (Open source)', 'RSpace (Open Source)', 'Lab Archives']
        },
        {
            'category': 'Scientific computing across all programming languages',
            'description': 'Tools that enable creation and sharing of computational documents',
            'tools': ['Jupyter', 'Mathematica', 'WebAssembly']
        },
        {
            'category': 'Metadata Tool',
            'description': 'Tools that enable creation, application, and management of metadata, and embedding of metadata in other kinds of tools',
            'tools': ['CEDAR Workbench (biomedical data)']
        }
    ],
    'ANALYSE': [
        {
            'category': 'Remediation (e.g. motion capture for gait analysis)',
            'description': 'Tools that capture transformation of data observations',
            'tools': ['Track3D']
        },
        {
            'category': 'Computational methods (e.g. Statistical software)',
            'description': 'Tools that provide computational methods for analysis',
            'tools': ['SPSS', 'Matlab']
        },
        {
            'category': 'Computational tools',
            'description': 'Tools that provide computational frameworks for processing and analysis',
            'tools': ['Jupyter', 'RStudio', 'Eclipse']
        }
    ],
    'STORE': [
        {
            'category': 'Data Repository',
            'description': 'Tools that structure and provide a framework to organise information',
            'tools': ['Figshare', 'Zenodo', 'Dataverse']
        },
        {
            'category': 'Archive',
            'description': 'Tools that facilitate the long-term storage of data',
            'tools': ['Libsafe']
        },
        {
            'category': 'Management tool',
            'description': 'Tools that facilitate the organisation of data',
            'tools': ['iRODS', 'GLOBUS', 'Mediaflux']
        }
    ],
    'PUBLISH': [
        {
            'category': 'Discipline-specific data repository',
            'description': 'Tools that enable storage and public sharing of data for specific disciplines',
            'tools': ['NOMAD-OASIS', 'Global Biodiversity Information Facility (GBIF)', 'Data Station Social Sciences and Humanities']
        },
        {
            'category': 'Generalist data repository',
            'description': 'Tools that enable storage and public sharing of generalist data',
            'tools': ['Figshare', 'Zenodo', 'Dataverse', 'CKAN']
        },
        {
            'category': 'Metadata repository',
            'description': 'Tools that enable the storage and public sharing of metadata',
            'tools': ['DataCite Commons', 'IBM Infosphere']
        }
    ],
    'PRESERVE': [
        {
            'category': 'Data repository',
            'description': 'Tools that enable storage and public sharing of data',
            'tools': ['Dataverse', 'Invenio', 'UKDS (National/Regional/Disciplinary Archive)']
        },
        {
            'category': 'Archive',
            'description': 'Tools that facilitate the long-term preservation of data',
            'tools': ['Archivematica']
        },
        {
            'category': 'Containers',
            'description': 'Tools that create an environment in which data can be seen in its original environment',
            'tools': ['Preservica', 'Docker', 'Archive-it.org']
        }
    ],
    'SHARE': [
        {
            'category': 'Data repository',
            'description': 'Tools that enable storage and public sharing of data',
            'tools': ['Dataverse', 'Zenodo', 'Figshare']
        },
        {
            'category': 'Electronic laboratory notebooks (ELNs)',
            'description': 'Tools that enable aggregation, organization and management of experimental and physical sample data',
            'tools': ['elabftw', 'RSpace', 'elabnext', 'lab archives']
        },
        {
            'category': 'Scientific computing across all programming languages',
            'description': 'Tools that enable creation and sharing of computational documents',
            'tools': ['Eclipse', 'Jupyter', 'Wolfram Alpha']
        }
    ],
    'ACCESS': [
        {
            'category': 'Data repository',
            'description': 'Tools that store data so that it can be publicly accessed',
            'tools': ['CKAN', 'Dataverse', 'DRYAD']
        },
        {
            'category': 'Database',
            'description': 'Tools that structure and provide a framework to access information',
            'tools': ['Oracle', 'MySQL / sqlLite', 'Postgres']
        },
        {
            'category': 'Authorisation/Authentication Infrastructure',
            'description': 'Tools that enable scalable authorised and authenticated access to data via storage infrastructure',
            'tools': ['LDAP', 'SAML2', 'AD']
        }
    ],
    'TRANSFORM': [
        {
            'category': 'Electronic laboratory notebooks (ELNs)',
            'description': 'Tools that enable aggregation, management, and organization of experimental and physical sample data',
            'tools': ['elabftw', 'RSpace', 'elabnext', 'Lab archive']
        },
        {
            'category': 'Programming languages',
            'description': 'Tools and platforms infrastructure used to transform data',
            'tools': ['Python (Interpreted language)', 'Perl (4GL)', 'Fortran (Compiled language)']
        },
        {
            'category': 'Extract, Transform, Load (ETL) tools',
            'description': 'Tools that enable extract, transform, load—a data integration process used to combine data from multiple sources',
            'tools': ['OCI (Cloud Infrastructure Provider)', 'Apache Spark', 'Snowflake (Commercial)']
        }
    ]
}


def init_tools_data():
    """Initialize the database with MaLDReTH tool categories and examples."""
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        # Get all stages for mapping
        result = conn.execute(text("SELECT id, name FROM lifecycle_stages"))
        stages = {row.name.upper(): row.id for row in result}
        logger.info(f"Found {len(stages)} lifecycle stages in database")
        
        # Counter for tracking imports
        imported_categories = 0
        imported_tools = 0
        
        # Process each stage's tools
        for stage_name, categories_data in MALDRETH_TOOLS_DATA.items():
            stage_id = stages.get(stage_name.upper())
            
            if not stage_id:
                logger.warning(f"Stage '{stage_name}' not found in database, skipping")
                continue
            
            logger.info(f"\nProcessing stage: {stage_name}")
            
            for category_data in categories_data:
                category_name = category_data['category']
                category_desc = category_data['description']
                
                # Check if category exists
                result = conn.execute(
                    text("SELECT id FROM tool_categories WHERE stage_id = :stage_id AND name = :name"),
                    {"stage_id": stage_id, "name": category_name}
                )
                category_row = result.first()
                
                if not category_row:
                    # Create category
                    conn.execute(
                        text("""
                            INSERT INTO tool_categories (name, description, stage_id, "order", created_at)
                            VALUES (:name, :description, :stage_id, :order, :created_at)
                        """),
                        {
                            "name": category_name,
                            "description": category_desc,
                            "stage_id": stage_id,
                            "order": imported_categories,
                            "created_at": datetime.utcnow()
                        }
                    )
                    conn.commit()
                    
                    # Get the new category ID
                    result = conn.execute(
                        text("SELECT id FROM tool_categories WHERE stage_id = :stage_id AND name = :name"),
                        {"stage_id": stage_id, "name": category_name}
                    )
                    category_row = result.first()
                    imported_categories += 1
                    logger.info(f"  Created category: {category_name}")
                
                category_id = category_row.id
                
                # Import tools
                for tool_name in category_data['tools']:
                    if tool_name:  # Skip empty tools
                        # Check if tool already exists
                        result = conn.execute(
                            text("SELECT id FROM tools WHERE name = :name AND stage_id = :stage_id"),
                            {"name": tool_name, "stage_id": stage_id}
                        )
                        
                        if not result.first():
                            # Create tool
                            conn.execute(
                                text("""
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
                                """),
                                {
                                    "name": tool_name,
                                    "description": f"{category_desc} - Example tool",
                                    "stage_id": stage_id,
                                    "category_id": category_id,
                                    "tool_type": category_name,
                                    "created_at": datetime.utcnow()
                                }
                            )
                            conn.commit()
                            imported_tools += 1
                            logger.info(f"    Added tool: {tool_name}")
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Import Summary:")
        logger.info(f"  - New Categories: {imported_categories}")
        logger.info(f"  - New Tools: {imported_tools}")
        
        # Show final counts
        result = conn.execute(text("SELECT COUNT(*) FROM tool_categories"))
        total_categories = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM tools"))
        total_tools = result.scalar()
        
        logger.info(f"\nTotal Database Contents:")
        logger.info(f"  - Total Categories: {total_categories}")
        logger.info(f"  - Total Tools: {total_tools}")


def main():
    """Main function."""
    logger.info("Initializing MaLDReTH tools data...")
    init_tools_data()
    logger.info("\nMaLDReTH tools initialization complete!")


if __name__ == "__main__":
    main()
