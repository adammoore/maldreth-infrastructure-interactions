#!/usr/bin/env python3
"""
Debug enhanced visualization issues
"""
import sys
sys.path.append('.')

from streamlined_app import app, ExemplarTool, MaldrethStage, ToolInteraction

def debug_enhanced_viz():
    with app.app_context():
        try:
            print("=== DEBUG ENHANCED VISUALIZATION ===")
            
            # Check basic data retrieval
            stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
            tools = ExemplarTool.query.filter_by(is_active=True).all()
            interactions = ToolInteraction.query.all()
            
            print(f"Stages: {len(stages)}")
            print(f"Tools: {len(tools)}")
            print(f"Interactions: {len(interactions)}")
            
            # Check tool attributes that might cause issues
            for tool in tools[:3]:
                print(f"\nTool: {tool.name}")
                print(f"  ID: {tool.id}")
                print(f"  Stage ID: {tool.stage_id}")
                print(f"  Active: {tool.is_active}")
                print(f"  Open source: {tool.is_open_source}")
                print(f"  Auto created: {getattr(tool, 'auto_created', 'NOT SET')}")
                print(f"  Provider: {getattr(tool, 'provider', 'NOT SET')}")
            
            # Try to replicate the stage data preparation
            for i, stage in enumerate(stages[:2]):
                stage_tools = [t for t in tools if t.stage_id == stage.id]
                print(f"\nStage: {stage.name}")
                print(f"  Tools: {len(stage_tools)}")
                
                # This might be where the error occurs
                for t in stage_tools[:2]:
                    try:
                        tool_data = {
                            'id': t.id,
                            'name': t.name,
                            'is_open_source': t.is_open_source,
                            'auto_created': getattr(t, 'auto_created', False),
                            'stage_id': t.stage_id,
                            'category_id': getattr(t, 'category_id', None)
                        }
                        print(f"    Tool data OK: {t.name}")
                    except Exception as e:
                        print(f"    ERROR with tool {t.name}: {e}")
            
            print("\n✅ Debug completed")
            
        except Exception as e:
            print(f"❌ Debug error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_enhanced_viz()