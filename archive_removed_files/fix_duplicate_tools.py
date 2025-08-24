#!/usr/bin/env python3
"""
Fix duplicate tools and implement clean update mechanism
"""
import sys
sys.path.append('.')

from streamlined_app import app, MaldrethStage, ToolCategory, ExemplarTool, db

def fix_duplicate_tools():
    """Remove duplicate tools, keeping the best version of each."""
    with app.app_context():
        print("=== FIXING DUPLICATE TOOLS ===\n")
        
        # Find tools with same name
        tools = ExemplarTool.query.filter_by(is_active=True).all()
        name_groups = {}
        
        for tool in tools:
            name_key = tool.name.lower().strip()
            if name_key not in name_groups:
                name_groups[name_key] = []
            name_groups[name_key].append(tool)
        
        duplicates_fixed = 0
        tools_removed = 0
        
        for name, tool_list in name_groups.items():
            if len(tool_list) > 1:
                print(f"Processing duplicates for '{name}' ({len(tool_list)} versions)")
                
                # Sort by preference: manual entry first, then by creation date
                sorted_tools = sorted(tool_list, key=lambda t: (
                    t.auto_created,  # False (manual) comes first
                    -t.id  # Higher ID (more recent) comes first
                ))
                
                keeper = sorted_tools[0]
                to_remove = sorted_tools[1:]
                
                print(f"  Keeping: ID {keeper.id} (Stage {keeper.stage_id}, Auto: {keeper.auto_created})")
                
                for tool in to_remove:
                    print(f"  Removing: ID {tool.id} (Stage {tool.stage_id}, Auto: {tool.auto_created})")
                    
                    # Deactivate instead of delete to preserve referential integrity
                    tool.is_active = False
                    tools_removed += 1
                
                duplicates_fixed += 1
        
        # Commit changes
        try:
            db.session.commit()
            print(f"\n✅ Fixed {duplicates_fixed} sets of duplicates")
            print(f"✅ Deactivated {tools_removed} duplicate tools")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {e}")
            return False
        
        return True

def create_version_update_mechanism():
    """Create a clean update mechanism for version deployments."""
    update_script_content = '''#!/usr/bin/env python3
"""
Clean update mechanism for MaLDReTH tool deployments
Usage: python3 clean_update.py
"""
import sys
sys.path.append('.')

from streamlined_app import app, MaldrethStage, ToolCategory, ExemplarTool, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_update():
    """Perform a clean update of tool data."""
    with app.app_context():
        logger.info("Starting clean update process...")
        
        # 1. Mark all auto-created tools as inactive
        auto_tools = ExemplarTool.query.filter_by(auto_created=True, is_active=True).all()
        for tool in auto_tools:
            tool.is_active = False
        
        logger.info(f"Deactivated {len(auto_tools)} auto-created tools")
        
        # 2. Remove duplicate categories (same name in same stage)
        stages = MaldrethStage.query.all()
        for stage in stages:
            categories = ToolCategory.query.filter_by(stage_id=stage.id).all()
            name_groups = {}
            
            for cat in categories:
                name_key = cat.name.lower().strip()
                if name_key not in name_groups:
                    name_groups[name_key] = []
                name_groups[name_key].append(cat)
            
            for name, cat_list in name_groups.items():
                if len(cat_list) > 1:
                    # Keep the first one, merge tools into it
                    keeper = cat_list[0]
                    
                    for duplicate_cat in cat_list[1:]:
                        # Move tools to keeper category
                        tools_in_dup = ExemplarTool.query.filter_by(category_id=duplicate_cat.id).all()
                        for tool in tools_in_dup:
                            tool.category_id = keeper.id
                        
                        # Remove duplicate category
                        db.session.delete(duplicate_cat)
                        logger.info(f"Merged duplicate category '{name}' in stage {stage.name}")
        
        # 3. Commit all changes
        try:
            db.session.commit()
            logger.info("✅ Clean update completed successfully")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Clean update failed: {e}")
            return False

if __name__ == "__main__":
    success = clean_update()
    sys.exit(0 if success else 1)
'''
    
    with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/clean_update.py', 'w') as f:
        f.write(update_script_content)
    
    print("✅ Created clean_update.py script")

def main():
    print("MaLDReTH Data Integrity Fix")
    print("=" * 40)
    
    # Fix duplicates first
    if fix_duplicate_tools():
        print("\n✅ Duplicate tools fixed successfully")
    else:
        print("\n❌ Failed to fix duplicate tools")
        return
    
    # Create clean update mechanism
    create_version_update_mechanism()
    
    # Final verification
    with app.app_context():
        active_tools = ExemplarTool.query.filter_by(is_active=True).count()
        total_categories = ToolCategory.query.count()
        
        print(f"\n📊 Final Statistics:")
        print(f"   Active tools: {active_tools}")
        print(f"   Total categories: {total_categories}")

if __name__ == "__main__":
    main()