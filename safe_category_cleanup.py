#!/usr/bin/env python3
"""
Safe Category Cleanup for PRISM MaLDReTH Infrastructure

This script provides a safer approach to cleaning up category duplicates
without breaking referential integrity with tool interactions.

Strategy:
1. First cleanup duplicate categories (merge tools into canonical categories)
2. Update category descriptions to match MaLDReTH specification
3. DO NOT delete existing tools that have interactions
4. Only add missing tools that are specified in MaLDReTH data
"""

import sys
import logging
from collections import defaultdict

# Add the app directory to path
sys.path.append('.')

from streamlined_app import app, db, MaldrethStage, ToolCategory, ExemplarTool, ToolInteraction

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_duplicate_categories_safe():
    """Safely remove duplicate categories while preserving tools and interactions"""
    logger.info("Starting safe category duplication cleanup...")
    
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
                    
                    # Keep the first category (canonical) and merge tools from others
                    canonical_cat = cat_list[0]
                    
                    # Move all tools from duplicates to canonical
                    for duplicate_cat in cat_list[1:]:
                        tools = ExemplarTool.query.filter_by(category_id=duplicate_cat.id).all()
                        logger.info(f"    Moving {len(tools)} tools from duplicate category {duplicate_cat.id}")
                        
                        for tool in tools:
                            tool.category_id = canonical_cat.id
                        
                        # Only delete the duplicate category if it has no tools after moving
                        remaining_tools = ExemplarTool.query.filter_by(category_id=duplicate_cat.id).count()
                        if remaining_tools == 0:
                            db.session.delete(duplicate_cat)
                            total_removed += 1
                            logger.info(f"    Removed empty duplicate category {duplicate_cat.id}")
                        else:
                            logger.warning(f"    Category {duplicate_cat.id} still has {remaining_tools} tools, keeping it")
        
        try:
            db.session.commit()
            logger.info(f"✅ Successfully removed {total_removed} duplicate categories")
        except Exception as e:
            logger.error(f"❌ Error committing category cleanup: {e}")
            db.session.rollback()
            raise

def update_category_descriptions():
    """Update category descriptions to match MaLDReTH specification"""
    logger.info("Updating category descriptions to match MaLDReTH specification...")
    
    # Category description mappings from MaLDReTH data
    description_updates = {
        "Mind mapping, concept mapping and knowledge modelling": "Tools that define the entities of research and their relationships",
        "Diagramming and flowchart": "Tools that detail the research workflow", 
        "Wireframing and prototyping": "Tools that visualise and demonstrate the research workflow",
        "Data management planning (DMP)": "Tools focused on enabling preparation and submission of data management plans",
        "Project planning": "Tools designed to enable project planning",
        "Combined DMP/project": "Tools which combine project planning with the ability to prepare data management plans",
        "Quantitative data collection tool": "Tools that collect quantitative data",
        "Qualitative data collection (e.g. Survey tool)": "Tools that collect qualitative data",
        "Harvesting tool (e.g. WebScrapers)": "Tools that harvest data from various sources",
        "Electronic laboratory notebooks (ELNs)": "Tools that enable aggregation, management, and organization of experimental and physical sample data",
        "Scientific computing across all programming languages": "Tools that enable creation and sharing of computational documents",
        "Metadata Tool": "Tools that enable creation, application, and management of metadata, and embedding of metadata in other kinds of tools",
        "Remediation (e.g. motion capture for gait analysis)": "Tools that capture transformation of data observations",
        "Computational methods (e.g. Statistical software)": "Tools that provide computational methods for analysis",
        "Computational tools": "Tools that provide computational frameworks for processing and analysis",
        "Data Repository": "Tools that structure and provide a framework to organise information",
        "Archive": "Tools that facilitate the long-term storage of data",
        "Management tool": "Tools that facilitate the organisation of data",
        "Discipline-specific data repository": "Tools that enable storage and public sharing of data for specific disciplines",
        "Generalist data repository (e.g. Figshare, The Dataverse Project)": "Tools that enable storage and public sharing of generalist data",
        "Generalist data repository": "Tools that enable storage and public sharing of generalist data",
        "Metadata repository": "Tools that enable the storage and public sharing of metadata",
        "Data repository": "Tools that enable storage and public sharing of data",
        "Containers": "Tools that create an environment in which data can be seen in its original environment",
        "Database": "Tools that structure and provide a framework to access information",
        "Authorisation/Authentication Infrastructure": "Tools that enable scalable authorised and authenticated access to data via storage infrastructure",
        "Programming languages": "Tools and platforms infrastructure used to transform data",
        "Extract, Transform, Load (ETL) tools": "Tools that enable 'extract, transform, load'—a data integration process used to combine data from multiple sources into a single, consistent data set for loading into a data warehouse, data lake or other target system."
    }
    
    with app.app_context():
        updated_count = 0
        
        for cat_name, new_description in description_updates.items():
            categories = ToolCategory.query.filter_by(name=cat_name).all()
            
            for category in categories:
                if category.description != new_description:
                    logger.info(f"Updating description for '{cat_name}'")
                    logger.info(f"  Old: {category.description}")
                    logger.info(f"  New: {new_description}")
                    category.description = new_description
                    updated_count += 1
        
        if updated_count > 0:
            try:
                db.session.commit()
                logger.info(f"✅ Successfully updated {updated_count} category descriptions")
            except Exception as e:
                logger.error(f"❌ Error updating descriptions: {e}")
                db.session.rollback()
                raise
        else:
            logger.info("No category descriptions needed updating")

def add_missing_tools():
    """Add any missing tools specified in MaLDReTH data but not present in database"""
    logger.info("Checking for missing tools specified in MaLDReTH data...")
    
    # Tools that should exist according to MaLDReTH data
    maldreth_tools = {
        "CONCEPTUALISE": {
            "Mind mapping, concept mapping and knowledge modelling": ["Miro", "Meister Labs (MindMeister + MeisterTask)", "XMind"],
            "Diagramming and flowchart": ["Lucidchart", "Draw.io (now Diagrams.net)", "Creately"],
            "Wireframing and prototyping": ["Balsamiq", "(Figma)"]
        },
        "PLAN": {
            "Data management planning (DMP)": ["DMP Tool", "DMP Online", "RDMO"],
            "Project planning": ["Trello", "Asana", "Microsoft project"],
            "Combined DMP/project": ["Data Stewardship Wizard", "Redbox research data", "Argos"]
        },
        "COLLECT": {
            "Quantitative data collection tool": ["Open Data Kit", "GBIF", "Cedar WorkBench"],
            "Qualitative data collection (e.g. Survey tool)": ["Survey Monkey", "Online Surveys", "Zooniverse"],
            "Harvesting tool (e.g. WebScrapers)": ["Netlytic", "IRODS", "DROID"]
        },
        "PUBLISH": {
            "Discipline-specific data repository": ["NOMAD-OASIS", "Global Biodiversity Information Facility (GBIF)", "Data Station Social Sciences and Humanities"],
            "Generalist data repository (e.g. Figshare, The Dataverse Project)": ["Figshare", "Zenodo", "Dataverse", "CKAN"]
        },
        "SHARE": {
            "Data repository": ["Dataverse", "Zenodo", "Figshare"],
            "Electronic laboratory notebooks (ELNs)": ["elabftw", "RSpace", "elabnext", "lab archives"],
            "Scientific computing across all programming languages": ["Eclipse", "Jupyter", "Wolfram Alpha"]
        },
        "ACCESS": {
            "Data repository": ["CKAN", "Dataverse", "DRYAD"]
        },
        "PRESERVE": {
            "Data repository": ["Dataverse", "Invenio", "UKDS (National/Regional/Disciplinary Archive)"]
        }
    }
    
    def normalize_tool_name(name):
        """Normalize tool names for comparison"""
        if not name:
            return ""
        return name.lower().strip().replace('(', '').replace(')', '').replace('.', '').replace('-', '').replace('_', '').replace(' ', '')
    
    with app.app_context():
        added_tools = 0
        
        for stage_name, categories_data in maldreth_tools.items():
            stage = MaldrethStage.query.filter_by(name=stage_name).first()
            if not stage:
                logger.warning(f"Stage '{stage_name}' not found")
                continue
                
            for cat_name, expected_tools in categories_data.items():
                category = ToolCategory.query.filter_by(name=cat_name, stage_id=stage.id).first()
                if not category:
                    logger.warning(f"Category '{cat_name}' not found in stage '{stage_name}'")
                    continue
                
                # Get existing tools in this category
                existing_tools = ExemplarTool.query.filter_by(category_id=category.id).all()
                existing_names = {normalize_tool_name(tool.name) for tool in existing_tools}
                
                # Check for missing tools
                for expected_tool in expected_tools:
                    normalized_expected = normalize_tool_name(expected_tool)
                    
                    if normalized_expected not in existing_names:
                        logger.info(f"Adding missing tool '{expected_tool}' to category '{cat_name}' in stage '{stage_name}'")
                        
                        new_tool = ExemplarTool(
                            name=expected_tool,
                            description=f"Research tool: {expected_tool}",
                            stage_id=stage.id,
                            category_id=category.id,
                            is_active=True,
                            is_open_source=False,  # Default, can be updated later
                            auto_created=False,
                            import_source='MaLDReTH Specification'
                        )
                        db.session.add(new_tool)
                        added_tools += 1
        
        if added_tools > 0:
            try:
                db.session.commit()
                logger.info(f"✅ Successfully added {added_tools} missing tools")
            except Exception as e:
                logger.error(f"❌ Error adding missing tools: {e}")
                db.session.rollback()
                raise
        else:
            logger.info("No missing tools to add")

def verify_final_structure():
    """Verify the final structure"""
    logger.info("Verifying final structure...")
    
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
        
        logger.info(f"\n=== FINAL SUMMARY ===")
        logger.info(f"Total categories: {total_categories}")
        logger.info(f"Total tools: {total_tools}")
        logger.info(f"Stages with tools: {len([s for s in stages if ToolCategory.query.filter_by(stage_id=s.id).count() > 0])}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe cleanup and update MaLDReTH categories")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify current structure")
    parser.add_argument("--cleanup-only", action="store_true",
                       help="Only cleanup duplicates")
    parser.add_argument("--descriptions-only", action="store_true",
                       help="Only update descriptions")
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_final_structure()
    elif args.cleanup_only:
        cleanup_duplicate_categories_safe()
        verify_final_structure()
    elif args.descriptions_only:
        update_category_descriptions()
        verify_final_structure()
    else:
        # Full process
        cleanup_duplicate_categories_safe()
        update_category_descriptions()
        add_missing_tools()
        verify_final_structure()