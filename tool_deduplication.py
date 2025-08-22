#!/usr/bin/env python3
"""
Tool Deduplication Script for PRISM MaLDReTH Infrastructure Interactions

This script addresses the significant tool duplication issues in the database
by creating a canonical tool registry and merging duplicate entries.

Based on analysis showing:
- 358 total tools with only ~75 unique names
- Tools duplicated up to 20 times (e.g., Dataverse)
- Pattern of 4x duplication suggesting multiple database initializations
"""

import sys
import logging
from collections import defaultdict
from datetime import datetime
from sqlalchemy import func, text

# Add the app directory to path
sys.path.append('.')

from streamlined_app import app, db, ExemplarTool, ToolInteraction, MaldrethStage, ToolCategory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_tool_name(name):
    """Normalize tool names for comparison"""
    if not name:
        return ""
    return name.lower().strip().replace('(', '').replace(')', '').replace('.', '').replace('-', '').replace('_', '').replace(' ', '')

def analyze_duplicates():
    """Analyze the current duplication situation"""
    logger.info("Analyzing tool duplication...")
    
    with app.app_context():
        total_tools = ExemplarTool.query.count()
        logger.info(f"Total tools in database: {total_tools}")
        
        # Group by normalized name
        tools = ExemplarTool.query.all()
        by_normalized_name = defaultdict(list)
        
        for tool in tools:
            normalized = normalize_tool_name(tool.name)
            by_normalized_name[normalized].append(tool)
        
        duplicates = {k: v for k, v in by_normalized_name.items() if len(v) > 1}
        unique_tools = len(by_normalized_name)
        
        logger.info(f"Unique tools (by normalized name): {unique_tools}")
        logger.info(f"Duplicate groups: {len(duplicates)}")
        
        # Show top duplicates
        top_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        logger.info("\nTop duplicates:")
        for normalized_name, tool_list in top_duplicates:
            sample_name = tool_list[0].name
            logger.info(f"  {sample_name}: {len(tool_list)} instances")
        
        return duplicates, unique_tools, total_tools

def create_canonical_tool_entry(tool_instances):
    """Create a canonical tool entry from multiple instances"""
    # Choose the "best" instance as canonical (prefer non-auto-created, most complete)
    canonical_source = sorted(tool_instances, key=lambda t: (
        t.auto_created or False,  # Prefer manually created
        -(len(t.description or "")),  # Prefer longer descriptions
        -(len(t.url or "")),  # Prefer with URLs
        t.id  # Consistent ordering
    ))[0]
    
    # Merge information from all instances
    descriptions = [t.description for t in tool_instances if t.description and t.description.strip()]
    urls = [t.url for t in tool_instances if t.url and t.url.strip()]
    providers = [t.provider for t in tool_instances if hasattr(t, 'provider') and t.provider and t.provider.strip()]
    
    # Take the longest description or combine unique ones
    if descriptions:
        description = max(descriptions, key=len)
    else:
        description = canonical_source.description
    
    # Prefer non-empty URL
    url = urls[0] if urls else canonical_source.url
    
    # Prefer non-empty provider
    provider = providers[0] if providers else (getattr(canonical_source, 'provider', None) or "")
    
    return {
        'name': canonical_source.name,
        'description': description,
        'url': url,
        'provider': provider,
        'is_open_source': canonical_source.is_open_source,
        'auto_created': False,  # Reset auto_created flag for canonical entries
        'import_source': 'Deduplication',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

def collect_stage_category_mappings(tool_instances):
    """Collect all unique stage-category combinations for a tool"""
    mappings = set()
    for tool in tool_instances:
        if tool.stage_id and tool.category_id:
            mappings.add((tool.stage_id, tool.category_id))
        elif tool.stage_id:
            # If no category, use stage's default category
            stage = MaldrethStage.query.get(tool.stage_id)
            if stage and stage.tool_categories.first():
                mappings.add((tool.stage_id, stage.tool_categories.first().id))
    return list(mappings)

def update_interactions_for_canonical_tool(old_tool_ids, canonical_tool_id):
    """Update all interactions to point to the canonical tool"""
    interactions_updated = 0
    
    # Update source tool references
    source_interactions = ToolInteraction.query.filter(ToolInteraction.source_tool_id.in_(old_tool_ids)).all()
    for interaction in source_interactions:
        interaction.source_tool_id = canonical_tool_id
        interactions_updated += 1
    
    # Update target tool references
    target_interactions = ToolInteraction.query.filter(ToolInteraction.target_tool_id.in_(old_tool_ids)).all()
    for interaction in target_interactions:
        interaction.target_tool_id = canonical_tool_id
        interactions_updated += 1
    
    return interactions_updated

def deduplicate_tools(dry_run=True):
    """Main deduplication process"""
    logger.info(f"Starting tool deduplication (dry_run={dry_run})...")
    
    with app.app_context():
        duplicates, unique_count, total_count = analyze_duplicates()
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        tools_kept = 0
        tools_removed = 0
        interactions_updated = 0
        mappings_created = 0
        
        for normalized_name, tool_instances in duplicates.items():
            if len(tool_instances) <= 1:
                continue
                
            logger.info(f"\nProcessing duplicate group: {tool_instances[0].name} ({len(tool_instances)} instances)")
            
            # Create canonical tool data
            canonical_data = create_canonical_tool_entry(tool_instances)
            
            # Collect all stage-category mappings
            stage_category_mappings = collect_stage_category_mappings(tool_instances)
            
            # Get IDs of tools to be removed
            old_tool_ids = [t.id for t in tool_instances]
            
            if not dry_run:
                # Create the canonical tool (reuse the first instance)
                canonical_tool = tool_instances[0]
                canonical_tool.name = canonical_data['name']
                canonical_tool.description = canonical_data['description']
                canonical_tool.url = canonical_data['url']
                if hasattr(canonical_tool, 'provider'):
                    canonical_tool.provider = canonical_data['provider']
                canonical_tool.is_open_source = canonical_data['is_open_source']
                canonical_tool.auto_created = canonical_data['auto_created']
                canonical_tool.import_source = canonical_data['import_source']
                canonical_tool.updated_at = canonical_data['updated_at']
                
                # Use the first stage-category mapping for the canonical tool
                if stage_category_mappings:
                    canonical_tool.stage_id = stage_category_mappings[0][0]
                    canonical_tool.category_id = stage_category_mappings[0][1]
                
                # Update interactions to point to canonical tool
                interaction_updates = update_interactions_for_canonical_tool(
                    old_tool_ids[1:], canonical_tool.id  # Exclude the canonical tool itself
                )
                interactions_updated += interaction_updates
                
                # Remove duplicate tools (keep the first one as canonical)
                for tool in tool_instances[1:]:
                    logger.debug(f"  Removing duplicate: ID {tool.id}")
                    db.session.delete(tool)
                    tools_removed += 1
                
                tools_kept += 1
                mappings_created += len(stage_category_mappings)
                
                logger.info(f"  Kept canonical tool ID {canonical_tool.id}")
                logger.info(f"  Removed {len(tool_instances) - 1} duplicates")
                logger.info(f"  Updated {interaction_updates} interactions")
                logger.info(f"  Preserved {len(stage_category_mappings)} stage-category mappings")
            else:
                logger.info(f"  Would keep: {tool_instances[0].name} (ID {tool_instances[0].id})")
                logger.info(f"  Would remove: {len(tool_instances) - 1} duplicates")
                logger.info(f"  Would preserve: {len(stage_category_mappings)} stage-category mappings")
                tools_kept += 1
                tools_removed += len(tool_instances) - 1
        
        if not dry_run:
            try:
                db.session.commit()
                logger.info("Database changes committed successfully")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error committing changes: {e}")
                raise
        
        logger.info("\n=== DEDUPLICATION SUMMARY ===")
        logger.info(f"Original tools: {total_count}")
        logger.info(f"Unique tools: {unique_count}")
        logger.info(f"Canonical tools {'created' if not dry_run else 'to create'}: {tools_kept}")
        logger.info(f"Duplicate tools {'removed' if not dry_run else 'to remove'}: {tools_removed}")
        logger.info(f"Interactions {'updated' if not dry_run else 'to update'}: {interactions_updated}")
        logger.info(f"Final tool count: {tools_kept}")
        logger.info(f"Space saved: {tools_removed} tools ({tools_removed/total_count*100:.1f}%)")

def verify_deduplication():
    """Verify the deduplication results"""
    logger.info("Verifying deduplication results...")
    
    with app.app_context():
        # Check for remaining duplicates
        tools = ExemplarTool.query.all()
        by_normalized_name = defaultdict(list)
        
        for tool in tools:
            normalized = normalize_tool_name(tool.name)
            by_normalized_name[normalized].append(tool)
        
        remaining_duplicates = {k: v for k, v in by_normalized_name.items() if len(v) > 1}
        
        logger.info(f"Total tools after deduplication: {len(tools)}")
        logger.info(f"Unique tools: {len(by_normalized_name)}")
        logger.info(f"Remaining duplicate groups: {len(remaining_duplicates)}")
        
        if remaining_duplicates:
            logger.warning("Remaining duplicates found:")
            for normalized_name, tool_list in remaining_duplicates.items():
                logger.warning(f"  {tool_list[0].name}: {len(tool_list)} instances")
        else:
            logger.info("✅ No duplicates found - deduplication successful!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deduplicate tools in PRISM database")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Run in dry-run mode (default)")
    parser.add_argument("--execute", action="store_true", 
                       help="Actually perform the deduplication")
    parser.add_argument("--verify", action="store_true",
                       help="Verify deduplication results")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_deduplication()
    else:
        # Default to dry_run=True unless --execute is specified
        dry_run = not args.execute
        deduplicate_tools(dry_run=dry_run)