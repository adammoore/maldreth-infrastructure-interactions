#!/usr/bin/env python3
"""
Category and Tool Structure Cleanup for PRISM MaLDReTH Infrastructure

This script addresses the category duplication issues and updates the tool/category
mapping to match the official MaLDReTH data structure provided.

Issues to fix:
1. Remove duplicate categories (4x duplicates in each stage)
2. Update category descriptions to match exact MaLDReTH specification
3. Add missing tools and categories
4. Ensure proper tool-to-category mapping
"""

import sys
import logging
from collections import defaultdict

# Add the app directory to path
sys.path.append('.')

from streamlined_app import app, db, MaldrethStage, ToolCategory, ExemplarTool

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Official MaLDReTH data structure from the provided table
MALDRETH_CATEGORIES = {
    "CONCEPTUALISE": [
        {
            "name": "Mind mapping, concept mapping and knowledge modelling",
            "description": "Tools that define the entities of research and their relationships",
            "tools": ["Miro", "Meister Labs (MindMeister + MeisterTask)", "XMind"]
        },
        {
            "name": "Diagramming and flowchart",
            "description": "Tools that detail the research workflow",
            "tools": ["Lucidchart", "Draw.io (now Diagrams.net)", "Creately"]
        },
        {
            "name": "Wireframing and prototyping",
            "description": "Tools that visualise and demonstrate the research workflow",
            "tools": ["Balsamiq", "(Figma)"]
        }
    ],
    "PLAN": [
        {
            "name": "Data management planning (DMP)",
            "description": "Tools focused on enabling preparation and submission of data management plans",
            "tools": ["DMP Tool", "DMP Online", "RDMO"]
        },
        {
            "name": "Project planning",
            "description": "Tools designed to enable project planning",
            "tools": ["Trello", "Asana", "Microsoft project"]
        },
        {
            "name": "Combined DMP/project",
            "description": "Tools which combine project planning with the ability to prepare data management plans",
            "tools": ["Data Stewardship Wizard", "Redbox research data", "Argos"]
        }
    ],
    "FUND": [],  # No tools specified in the data
    "COLLECT": [
        {
            "name": "Quantitative data collection tool",
            "description": "Tools that collect quantitative data",
            "tools": ["Open Data Kit", "GBIF", "Cedar WorkBench"]
        },
        {
            "name": "Qualitative data collection (e.g. Survey tool)",
            "description": "Tools that collect qualitative data",
            "tools": ["Survey Monkey", "Online Surveys", "Zooniverse"]
        },
        {
            "name": "Harvesting tool (e.g. WebScrapers)",
            "description": "Tools that harvest data from various sources",
            "tools": ["Netlytic", "IRODS", "DROID"]
        }
    ],
    "PROCESS": [
        {
            "name": "Electronic laboratory notebooks (ELNs)",
            "description": "Tools that enable aggregation, management, and organization of experimental and physical sample data",
            "tools": ["elabnext", "E-lab FTW (Open source)", "RSpace (Open Source)", "Lab Archives"]
        },
        {
            "name": "Scientific computing across all programming languages",
            "description": "Tools that enable creation and sharing of computational documents",
            "tools": ["Jupyter", "Mathematica", "WebAssembly"]
        },
        {
            "name": "Metadata Tool",
            "description": "Tools that enable creation, application, and management of metadata, and embedding of metadata in other kinds of tools",
            "tools": ["CEDAR Workbench (biomedical data)"]
        }
    ],
    "ANALYSE": [
        {
            "name": "Remediation (e.g. motion capture for gait analysis)",
            "description": "Tools that capture transformation of data observations",
            "tools": ["Track3D"]
        },
        {
            "name": "Computational methods (e.g. Statistical software)",
            "description": "Tools that provide computational methods for analysis",
            "tools": ["SPSS", "Matlab"]
        },
        {
            "name": "Computational tools",
            "description": "Tools that provide computational frameworks for processing and analysis",
            "tools": ["Jupyter", "RStudio", "Eclipse"]
        }
    ],
    "STORE": [
        {
            "name": "Data Repository",
            "description": "Tools that structure and provide a framework to organise information",
            "tools": ["Figshare", "Zenodo", "Dataverse"]
        },
        {
            "name": "Archive",
            "description": "Tools that facilitate the long-term storage of data",
            "tools": ["Libsafe"]
        },
        {
            "name": "Management tool",
            "description": "Tools that facilitate the organisation of data",
            "tools": ["iRODS", "GLOBUS", "Mediaflux"]
        }
    ],
    "PUBLISH": [
        {
            "name": "Discipline-specific data repository",
            "description": "Tools that enable storage and public sharing of data for specific disciplines",
            "tools": ["NOMAD-OASIS", "Global Biodiversity Information Facility (GBIF)", "Data Station Social Sciences and Humanities"]
        },
        {
            "name": "Generalist data repository (e.g. Figshare, The Dataverse Project)",
            "description": "Tools that enable storage and public sharing of generalist data",
            "tools": ["Figshare", "Zenodo", "Dataverse", "CKAN"]
        },
        {
            "name": "Metadata repository",
            "description": "Tools that enable the storage and public sharing of metadata",
            "tools": ["DataCite Commons", "IBM Infosphere"]
        }
    ],
    "PRESERVE": [
        {
            "name": "Data repository",
            "description": "Tools that enable storage and public sharing of data",
            "tools": ["Dataverse", "Invenio", "UKDS (National/Regional/Disciplinary Archive)"]
        },
        {
            "name": "Archive",
            "description": "Tools that facilitate the long-term preservation of data",
            "tools": ["Archivematica"]
        },
        {
            "name": "Containers",
            "description": "Tools that create an environment in which data can be seen in its original environment",
            "tools": ["Preservica", "Docker", "Archive-it.org"]
        }
    ],
    "SHARE": [
        {
            "name": "Data repository",
            "description": "Tools that enable storage and public sharing of data",
            "tools": ["Dataverse", "Zenodo", "Figshare"]
        },
        {
            "name": "Electronic laboratory notebooks (ELNs)",
            "description": "Tools that enable aggregation, organization and management of experimental and physical sample data",
            "tools": ["elabftw", "RSpace", "elabnext", "lab archives"]
        },
        {
            "name": "Scientific computing across all programming languages",
            "description": "Tools that enable creation and sharing of computational documents",
            "tools": ["Eclipse", "Jupyter", "Wolfram Alpha"]
        }
    ],
    "ACCESS": [
        {
            "name": "Data repository",
            "description": "Tools that store data so that it can be publicly accessed",
            "tools": ["CKAN", "Dataverse", "DRYAD"]
        },
        {
            "name": "Database",
            "description": "Tools that structure and provide a framework to access information",
            "tools": ["Oracle", "MySQL / sqlLite", "Postgres"]
        },
        {
            "name": "Authorisation/Authentication Infrastructure",
            "description": "Tools that enable scalable authorised and authenticated access to data via storage infrastructure",
            "tools": ["LDAP", "SAML2", "AD"]
        }
    ],
    "TRANSFORM": [
        {
            "name": "Electronic laboratory notebooks (ELNs)",
            "description": "Tools that enable aggregation, management, and organization of experimental and physical sample data",
            "tools": ["elabftw", "RSpace", "elabnext", "Lab archive"]
        },
        {
            "name": "Programming languages",
            "description": "Tools and platforms infrastructure used to transform data",
            "tools": ["Python (Interpreted language)", "Perl (4GL)", "Fortran (Compiled language)"]
        },
        {
            "name": "Extract, Transform, Load (ETL) tools",
            "description": "Tools that enable 'extract, transform, load'—a data integration process used to combine data from multiple sources into a single, consistent data set for loading into a data warehouse, data lake or other target system.",
            "tools": ["OCI (Cloud Infrastructure Provider)", "Apache Spark", "Snowflake (Commercial)"]
        }
    ]
}

def normalize_tool_name(name):
    """Normalize tool names for comparison"""
    if not name:
        return ""
    return name.lower().strip().replace('(', '').replace(')', '').replace('.', '').replace('-', '').replace('_', '').replace(' ', '')

def cleanup_duplicate_categories():
    """Remove duplicate categories while preserving tools"""
    logger.info("Starting category duplication cleanup...")
    
    with app.app_context():
        stages = MaldrethStage.query.all()
        total_removed = 0
        
        for stage in stages:
            logger.info(f"\nProcessing stage: {stage.name}")
            
            # Group categories by name within this stage
            categories = ToolCategory.query.filter_by(stage_id=stage.id).all()
            by_name = defaultdict(list)
            
            for cat in categories:
                by_name[cat.name].append(cat)
            
            # Process duplicates
            for cat_name, cat_list in by_name.items():
                if len(cat_list) > 1:
                    logger.info(f"  Found {len(cat_list)} duplicates of '{cat_name}'")
                    
                    # Keep the first category (canonical)
                    canonical_cat = cat_list[0]
                    
                    # Move all tools from duplicates to canonical
                    for duplicate_cat in cat_list[1:]:
                        tools = ExemplarTool.query.filter_by(category_id=duplicate_cat.id).all()
                        logger.info(f"    Moving {len(tools)} tools from duplicate category {duplicate_cat.id}")
                        
                        for tool in tools:
                            tool.category_id = canonical_cat.id
                        
                        # Delete the duplicate category
                        db.session.delete(duplicate_cat)
                        total_removed += 1
                        logger.info(f"    Removed duplicate category {duplicate_cat.id}")
        
        try:
            db.session.commit()
            logger.info(f"✅ Successfully removed {total_removed} duplicate categories")
        except Exception as e:
            logger.error(f"❌ Error committing category cleanup: {e}")
            db.session.rollback()
            raise

def update_categories_and_tools():
    """Update categories and tools to match MaLDReTH specification"""
    logger.info("Updating categories and tools to match MaLDReTH specification...")
    
    with app.app_context():
        for stage_name, categories_data in MALDRETH_CATEGORIES.items():
            stage = MaldrethStage.query.filter_by(name=stage_name).first()
            if not stage:
                logger.warning(f"Stage '{stage_name}' not found in database")
                continue
                
            logger.info(f"\nUpdating stage: {stage_name}")
            
            # Remove existing categories for clean slate
            existing_categories = ToolCategory.query.filter_by(stage_id=stage.id).all()
            for cat in existing_categories:
                # Delete tools in this category first
                tools = ExemplarTool.query.filter_by(category_id=cat.id).all()
                for tool in tools:
                    db.session.delete(tool)
                db.session.delete(cat)
            
            # Create new categories and tools from specification
            for cat_data in categories_data:
                logger.info(f"  Creating category: {cat_data['name']}")
                
                category = ToolCategory(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    stage_id=stage.id
                )
                db.session.add(category)
                db.session.flush()  # Get the ID
                
                # Add tools to this category
                for tool_name in cat_data['tools']:
                    logger.info(f"    Adding tool: {tool_name}")
                    
                    tool = ExemplarTool(
                        name=tool_name,
                        description=f"Research tool: {tool_name}",
                        stage_id=stage.id,
                        category_id=category.id,
                        is_active=True,
                        is_open_source=False,  # Default, can be updated later
                        auto_created=False,
                        import_source='MaLDReTH Specification Update'
                    )
                    db.session.add(tool)
        
        try:
            db.session.commit()
            logger.info("✅ Successfully updated all categories and tools")
        except Exception as e:
            logger.error(f"❌ Error updating categories and tools: {e}")
            db.session.rollback()
            raise

def verify_structure():
    """Verify the updated structure matches expectations"""
    logger.info("Verifying updated structure...")
    
    with app.app_context():
        total_categories = 0
        total_tools = 0
        
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        for stage in stages:
            categories = ToolCategory.query.filter_by(stage_id=stage.id).all()
            stage_tool_count = 0
            
            logger.info(f"\n{stage.name} (Stage {stage.position + 1}):")
            
            if not categories:
                logger.info("  No categories")
                continue
                
            for cat in categories:
                tool_count = ExemplarTool.query.filter_by(category_id=cat.id).count()
                logger.info(f"  • {cat.name}: {tool_count} tools")
                total_categories += 1
                stage_tool_count += tool_count
            
            total_tools += stage_tool_count
            logger.info(f"  Stage total: {stage_tool_count} tools")
        
        logger.info(f"\n=== SUMMARY ===")
        logger.info(f"Total categories: {total_categories}")
        logger.info(f"Total tools: {total_tools}")
        logger.info(f"Stages with tools: {len([s for s in stages if ToolCategory.query.filter_by(stage_id=s.id).count() > 0])}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup and update MaLDReTH categories and tools")
    parser.add_argument("--cleanup-only", action="store_true", 
                       help="Only cleanup duplicates, don't update structure")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify current structure")
    parser.add_argument("--dry-run", action="store_true", default=False,
                       help="Run in dry-run mode")
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    if args.verify_only:
        verify_structure()
    elif args.cleanup_only:
        if not args.dry_run:
            cleanup_duplicate_categories()
        verify_structure()
    else:
        if not args.dry_run:
            cleanup_duplicate_categories()
            update_categories_and_tools()
        verify_structure()