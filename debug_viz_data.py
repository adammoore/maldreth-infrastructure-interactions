#!/usr/bin/env python3
"""
Debug visualization data in production
"""
import sys
sys.path.append('.')

from streamlined_app import app, MaldrethStage, ExemplarTool, ToolCategory

def debug_visualization_data():
    with app.app_context():
        print("=== DEBUGGING VISUALIZATION DATA ===")
        
        # Check stages
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        print(f"Stages found: {len(stages)}")
        
        for stage in stages[:3]:  # First 3 stages
            print(f"\nStage: {stage.name}")
            print(f"  ID: {stage.id}")
            print(f"  Position: {stage.position}")
            print(f"  Description: {stage.description[:100] if stage.description else 'None'}...")
            
            # Check tools in this stage
            tools = ExemplarTool.query.filter_by(stage_id=stage.id, is_active=True).all()
            print(f"  Tools: {len(tools)}")
            
            # Check categories in this stage
            categories = ToolCategory.query.filter_by(stage_id=stage.id).all()
            print(f"  Categories: {len(categories)}")
            
            for category in categories[:2]:  # First 2 categories
                cat_tools = ExemplarTool.query.filter_by(category_id=category.id, is_active=True).all()
                print(f"    - {category.name}: {len(cat_tools)} tools")
        
        # Check total counts
        total_stages = MaldrethStage.query.count()
        total_tools = ExemplarTool.query.filter_by(is_active=True).count()
        total_categories = ToolCategory.query.count()
        
        print(f"\n=== TOTALS ===")
        print(f"Total stages: {total_stages}")
        print(f"Total active tools: {total_tools}")
        print(f"Total categories: {total_categories}")

if __name__ == "__main__":
    debug_visualization_data()