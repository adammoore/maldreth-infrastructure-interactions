#!/usr/bin/env python3
"""
init_database.py

Initialize the MaLDReTH database with lifecycle stages, categories, tools, and connections.

This script populates the database with the complete MaLDReTH research data lifecycle
structure including all stages, tool categories, example tools, and stage connections.

Usage:
    python init_database.py
"""

import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Import models
from models import db, Stage, ToolCategory, Tool, Connection


def create_app():
    """Create a Flask app for database initialization."""
    app = Flask(__name__)
    
    # Configure database
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///maldreth.db')
    
    # Fix for Heroku Postgres
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'init-secret-key'
    
    # Initialize database
    db.init_app(app)
    
    return app


def init_database():
    """Initialize the database with MaLDReTH data."""
    
    print("=" * 60)
    print("MaLDReTH Database Initialization")
    print("=" * 60)
    
    # Create all tables
    try:
        db.create_all()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False
    
    # Check if data already exists
    existing_stages = Stage.query.count()
    if existing_stages > 0:
        print(f"ℹ Database already contains {existing_stages} stages.")
        response = input("Do you want to clear and reinitialize? (y/N): ")
        if response.lower() != 'y':
            print("Initialization cancelled.")
            return True
        else:
            # Clear existing data
            print("Clearing existing data...")
            try:
                Tool.query.delete()
                ToolCategory.query.delete()
                Connection.query.delete()
                Stage.query.delete()
                db.session.commit()
                print("✓ Existing data cleared")
            except Exception as e:
                print(f"✗ Error clearing data: {e}")
                db.session.rollback()
                return False
    
    # Define lifecycle stages
    print("\nCreating lifecycle stages...")
    stages_data = [
        {
            "name": "CONCEPTUALISE",
            "description": "To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project."
        },
        {
            "name": "PLAN",
            "description": "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis."
        },
        {
            "name": "FUND",
            "description": "To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation."
        },
        {
            "name": "COLLECT",
            "description": "To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis."
        },
        {
            "name": "PROCESS",
            "description": "To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data."
        },
        {
            "name": "ANALYSE",
            "description": "To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results."
        },
        {
            "name": "STORE",
            "description": "To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security."
        },
        {
            "name": "PUBLISH",
            "description": "To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles."
        },
        {
            "name": "PRESERVE",
            "description": "To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible."
        },
        {
            "name": "SHARE",
            "description": "To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community."
        },
        {
            "name": "ACCESS",
            "description": "To control and manage data access by designated users and reusers. This may be in the form of publicly available published information."
        },
        {
            "name": "TRANSFORM",
            "description": "To create new data from the original, for example by migration into a different format or by creating a subset to create newly derived results."
        }
    ]
    
    # Create stages
    stages = {}
    for idx, stage_data in enumerate(stages_data):
        try:
            stage = Stage(
                name=stage_data["name"],
                description=stage_data["description"]
            )
            db.session.add(stage)
            stages[stage_data["name"]] = stage
        except Exception as e:
            print(f"✗ Error creating stage {stage_data['name']}: {e}")
            db.session.rollback()
            return False
    
    try:
        db.session.commit()
        print(f"✓ Created {len(stages)} lifecycle stages")
    except Exception as e:
        print(f"✗ Error committing stages: {e}")
        db.session.rollback()
        return False
    
    # Define tool categories and tools
    print("\nCreating tool categories and tools...")
    tools_data = {
        "CONCEPTUALISE": [
            {
                "category": "Mind mapping, concept mapping and knowledge modelling",
                "description": "Tools that define the entities of research and their relationships",
                "tools": ["Miro", "MindMeister", "XMind"]
            },
            {
                "category": "Diagramming and flowchart",
                "description": "Tools that detail the research workflow",
                "tools": ["Lucidchart", "Draw.io (Diagrams.net)", "Creately"]
            },
            {
                "category": "Wireframing and prototyping",
                "description": "Tools that visualise and demonstrate the research workflow",
                "tools": ["Balsamiq", "Figma"]
            }
        ],
        "PLAN": [
            {
                "category": "Data management planning (DMP)",
                "description": "Tools focused on enabling preparation and submission of data management plans",
                "tools": ["DMP Tool", "DMP Online", "RDMO"]
            },
            {
                "category": "Project planning",
                "description": "Tools designed to enable project planning",
                "tools": ["Trello", "Asana", "Microsoft Project"]
            },
            {
                "category": "Combined DMP/project",
                "description": "Tools which combine project planning with the ability to prepare data management plans",
                "tools": ["Data Stewardship Wizard", "Redbox Research Data", "Argos"]
            }
        ],
        "FUND": [
            {
                "category": "Funding databases",
                "description": "Tools to search and identify funding opportunities",
                "tools": ["Grants.gov", "Research Professional", "Pivot-RP"]
            }
        ],
        "COLLECT": [
            {
                "category": "Quantitative data collection tools",
                "description": "Tools that collect quantitative data",
                "tools": ["Open Data Kit", "GBIF", "Cedar WorkBench"]
            },
            {
                "category": "Qualitative data collection tools",
                "description": "Tools that collect qualitative data",
                "tools": ["SurveyMonkey", "Online Surveys", "Zooniverse"]
            },
            {
                "category": "Harvesting tools",
                "description": "Tools that harvest data from various sources",
                "tools": ["Netlytic", "IRODS", "DROID"]
            }
        ],
        "PROCESS": [
            {
                "category": "Electronic laboratory notebooks (ELNs)",
                "description": "Tools that enable aggregation, management, and organization of experimental and physical sample data",
                "tools": ["eLabNext", "Lab Archives", "RSpace"]
            },
            {
                "category": "Scientific computing",
                "description": "Tools that enable creation and sharing of computational documents",
                "tools": ["Jupyter", "Mathematica", "WebAssembly"]
            },
            {
                "category": "Metadata tools",
                "description": "Tools that enable creation, application, and management of metadata",
                "tools": ["CEDAR Workbench"]
            }
        ],
        "ANALYSE": [
            {
                "category": "Statistical software",
                "description": "Tools that provide computational methods for analysis",
                "tools": ["SPSS", "Matlab", "R"]
            },
            {
                "category": "Computational tools",
                "description": "Tools that provide computational frameworks for processing and analysis",
                "tools": ["Jupyter", "RStudio", "Eclipse"]
            },
            {
                "category": "Remediation tools",
                "description": "Tools that capture transformation of data observations",
                "tools": ["Track3D"]
            }
        ],
        "STORE": [
            {
                "category": "Data repository",
                "description": "Tools that structure and provide a framework to organise information",
                "tools": ["Figshare", "Zenodo", "Dataverse"]
            },
            {
                "category": "Archive",
                "description": "Tools that facilitate the long-term storage of data",
                "tools": ["Libsafe"]
            },
            {
                "category": "Management tools",
                "description": "Tools that facilitate the organisation of data",
                "tools": ["iRODS", "GLOBUS", "Mediaflux"]
            }
        ],
        "PUBLISH": [
            {
                "category": "Discipline-specific data repository",
                "description": "Tools that enable storage and public sharing of data for specific disciplines",
                "tools": ["NOMAD-OASIS", "Global Biodiversity Information Facility (GBIF)", "Data Station Social Sciences and Humanities"]
            },
            {
                "category": "Generalist data repository",
                "description": "Tools that enable storage and public sharing of generalist data",
                "tools": ["Figshare", "Zenodo", "Dataverse", "CKAN"]
            },
            {
                "category": "Metadata repository",
                "description": "Tools that enable the storage and public sharing of metadata",
                "tools": ["DataCite Commons", "IBM Infosphere"]
            }
        ],
        "PRESERVE": [
            {
                "category": "Data repository",
                "description": "Tools that enable storage and public sharing of data",
                "tools": ["Dataverse", "Invenio", "UKDS Archive"]
            },
            {
                "category": "Archive",
                "description": "Tools that facilitate the long-term preservation of data",
                "tools": ["Archivematica"]
            },
            {
                "category": "Containers",
                "description": "Tools that create an environment in which data can be seen in its original environment",
                "tools": ["Preservica", "Docker", "Archive-it.org"]
            }
        ],
        "SHARE": [
            {
                "category": "Data repository",
                "description": "Tools that enable storage and public sharing of data",
                "tools": ["Dataverse", "Zenodo", "Figshare"]
            },
            {
                "category": "Electronic laboratory notebooks",
                "description": "Tools that enable aggregation, organization and management of experimental and physical sample data",
                "tools": ["elabftw", "RSpace", "eLabNext", "Lab Archives"]
            },
            {
                "category": "Scientific computing",
                "description": "Tools that enable creation and sharing of computational documents",
                "tools": ["Eclipse", "Jupyter", "Wolfram Alpha"]
            }
        ],
        "ACCESS": [
            {
                "category": "Data repository",
                "description": "Tools that store data so that it can be publicly accessed",
                "tools": ["CKAN", "Dataverse", "DRYAD"]
            },
            {
                "category": "Database",
                "description": "Tools that structure and provide a framework to access information",
                "tools": ["Oracle", "MySQL", "PostgreSQL"]
            },
            {
                "category": "Authentication infrastructure",
                "description": "Tools that enable scalable authorised and authenticated access to data",
                "tools": ["LDAP", "SAML2", "Active Directory"]
            }
        ],
        "TRANSFORM": [
            {
                "category": "Electronic laboratory notebooks",
                "description": "Tools that enable aggregation, management, and organization of experimental and physical sample data",
                "tools": ["elabftw", "RSpace", "eLabNext", "Lab Archive"]
            },
            {
                "category": "Programming languages",
                "description": "Tools and platforms infrastructure used to transform data",
                "tools": ["Python", "R", "Julia", "Fortran"]
            },
            {
                "category": "ETL tools",
                "description": "Tools that enable extract, transform, load—a data integration process",
                "tools": ["Apache Spark", "Talend", "Pentaho", "Snowflake"]
            }
        ]
    }
    
    # Create categories and tools
    category_count = 0
    tool_count = 0
    
    for stage_name, categories_data in tools_data.items():
        stage = stages.get(stage_name)
        if not stage:
            print(f"✗ Stage not found: {stage_name}")
            continue
        
        for cat_data in categories_data:
            try:
                # Create category
                category = ToolCategory(
                    category=cat_data["category"],
                    description=cat_data["description"],
                    stage_id=stage.id
                )
                db.session.add(category)
                db.session.flush()  # Get the ID
                category_count += 1
                
                # Create tools
                for tool_name in cat_data["tools"]:
                    tool = Tool(
                        name=tool_name,
                        category_id=category.id,
                        stage_id=stage.id
                    )
                    db.session.add(tool)
                    tool_count += 1
                    
            except Exception as e:
                print(f"✗ Error creating category/tools for {stage_name}: {e}")
                db.session.rollback()
                return False
    
    try:
        db.session.commit()
        print(f"✓ Created {category_count} categories")
        print(f"✓ Created {tool_count} tools")
    except Exception as e:
        print(f"✗ Error committing categories/tools: {e}")
        db.session.rollback()
        return False
    
    # Create connections
    print("\nCreating stage connections...")
    connections_data = [
        # Main lifecycle flow
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
    
    connection_count = 0
    for from_name, to_name, conn_type in connections_data:
        try:
            from_stage = stages.get(from_name)
            to_stage = stages.get(to_name)
            
            if from_stage and to_stage:
                connection = Connection(
                    from_stage_id=from_stage.id,
                    to_stage_id=to_stage.id,
                    type=conn_type
                )
                db.session.add(connection)
                connection_count += 1
            else:
                print(f"✗ Could not create connection: {from_name} -> {to_name}")
                
        except Exception as e:
            print(f"✗ Error creating connection {from_name} -> {to_name}: {e}")
    
    try:
        db.session.commit()
        print(f"✓ Created {connection_count} connections")
    except Exception as e:
        print(f"✗ Error committing connections: {e}")
        db.session.rollback()
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("Database Initialization Complete!")
    print("=" * 60)
    print(f"✓ Stages: {len(stages)}")
    print(f"✓ Categories: {category_count}")
    print(f"✓ Tools: {tool_count}")
    print(f"✓ Connections: {connection_count}")
    print("=" * 60)
    
    return True


def main():
    """Main entry point."""
    app = create_app()
    
    with app.app_context():
        try:
            success = init_database()
            if not success:
                print("\n✗ Database initialization failed!")
                sys.exit(1)
            else:
                print("\n✓ Database initialization successful!")
                sys.exit(0)
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
