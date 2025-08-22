#!/usr/bin/env python3
"""
Investigate data model and duplication issues
"""
import sys
sys.path.append('.')

from streamlined_app import app, MaldrethStage, ToolCategory, ExemplarTool

def investigate_data_issues():
    with app.app_context():
        print("=== DATA MODEL INVESTIGATION ===\n")
        
        # 1. Check stage-category relationship integrity
        print("1. STAGE-CATEGORY RELATIONSHIP ISSUES:")
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        
        for stage in stages:
            stage_categories = ToolCategory.query.filter_by(stage_id=stage.id).all()
            stage_tools_direct = ExemplarTool.query.filter_by(stage_id=stage.id, is_active=True).all()
            stage_tools_via_category = []
            
            for category in stage_categories:
                cat_tools = ExemplarTool.query.filter_by(category_id=category.id, is_active=True).all()
                stage_tools_via_category.extend(cat_tools)
            
            print(f"Stage {stage.position + 1} - {stage.name}:")
            print(f"  Categories: {len(stage_categories)}")
            print(f"  Tools (direct stage_id): {len(stage_tools_direct)}")
            print(f"  Tools (via categories): {len(stage_tools_via_category)}")
            
            # Check for tools with wrong stage_id vs category.stage_id
            mismatched_tools = []
            for tool in stage_tools_direct:
                if tool.category and tool.category.stage_id != tool.stage_id:
                    mismatched_tools.append(tool)
            
            if mismatched_tools:
                print(f"  ⚠️  MISMATCH: {len(mismatched_tools)} tools have stage_id != category.stage_id")
                for tool in mismatched_tools[:3]:  # Show first 3
                    print(f"    - {tool.name}: stage_id={tool.stage_id}, category.stage_id={tool.category.stage_id}")
            
            print()
        
        # 2. Check for duplicate tools
        print("2. DUPLICATE TOOL DETECTION:")
        
        # Find tools with same name
        tools = ExemplarTool.query.filter_by(is_active=True).all()
        name_counts = {}
        
        for tool in tools:
            name_key = tool.name.lower().strip()
            if name_key not in name_counts:
                name_counts[name_key] = []
            name_counts[name_key].append(tool)
        
        duplicates_by_name = {name: tools_list for name, tools_list in name_counts.items() if len(tools_list) > 1}
        
        print(f"Tools with duplicate names: {len(duplicates_by_name)}")
        for name, duplicate_tools in list(duplicates_by_name.items())[:5]:  # Show first 5
            print(f"  '{name}' appears {len(duplicate_tools)} times:")
            for tool in duplicate_tools:
                print(f"    - ID {tool.id}: Stage {tool.stage_id}, Category {tool.category_id}, Auto: {tool.auto_created}")
        
        # 3. Check category distribution across stages
        print("\n3. CATEGORY DISTRIBUTION ISSUES:")
        all_categories = ToolCategory.query.all()
        category_names = {}
        
        for category in all_categories:
            name_key = category.name.lower().strip()
            if name_key not in category_names:
                category_names[name_key] = []
            category_names[name_key].append(category)
        
        duplicate_category_names = {name: cats for name, cats in category_names.items() if len(cats) > 1}
        
        print(f"Category names appearing in multiple stages: {len(duplicate_category_names)}")
        for name, categories in list(duplicate_category_names.items())[:5]:  # Show first 5
            print(f"  '{name}' appears in {len(categories)} stages:")
            for cat in categories:
                stage = MaldrethStage.query.get(cat.stage_id)
                tool_count = ExemplarTool.query.filter_by(category_id=cat.id, is_active=True).count()
                print(f"    - Stage {stage.position + 1} ({stage.name}): {tool_count} tools")
        
        # 4. Summary statistics
        print("\n4. SUMMARY STATISTICS:")
        total_stages = MaldrethStage.query.count()
        total_categories = ToolCategory.query.count()
        total_tools = ExemplarTool.query.filter_by(is_active=True).count()
        auto_created_tools = ExemplarTool.query.filter_by(is_active=True, auto_created=True).count()
        
        print(f"  Total stages: {total_stages}")
        print(f"  Total categories: {total_categories}")
        print(f"  Total active tools: {total_tools}")
        print(f"  Auto-created tools: {auto_created_tools} ({auto_created_tools/total_tools*100:.1f}%)")
        
        # Check for orphaned tools
        orphaned_tools = ExemplarTool.query.filter(
            ExemplarTool.is_active == True,
            ExemplarTool.category_id == None
        ).count()
        print(f"  Orphaned tools (no category): {orphaned_tools}")

if __name__ == "__main__":
    investigate_data_issues()