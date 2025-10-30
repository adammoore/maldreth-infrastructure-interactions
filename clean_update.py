#!/usr/bin/env python3
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

        # Check if tables exist first
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            if 'exemplar_tools' not in tables:
                logger.info("Tables not initialized yet, skipping clean update")
                return True
        except Exception as e:
            logger.warning(f"Could not check table existence: {e}")
            return True

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
