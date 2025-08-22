#!/usr/bin/env python3
"""
Check tool duplication status in production database
"""
import sys
import os
from collections import defaultdict

# Set up app context
sys.path.append('.')
from streamlined_app import app, db, ExemplarTool

def normalize_tool_name(name):
    """Normalize tool names for comparison"""
    if not name:
        return ""
    return name.lower().strip().replace('(', '').replace(')', '').replace('.', '').replace('-', '').replace('_', '').replace(' ', '')

def check_tool_duplication():
    """Check current tool duplication status"""
    with app.app_context():
        # Get all tools
        all_tools = ExemplarTool.query.all()
        total_tools = len(all_tools)
        
        # Group by normalized names
        by_normalized_name = defaultdict(list)
        for tool in all_tools:
            normalized_name = normalize_tool_name(tool.name)
            by_normalized_name[normalized_name].append(tool)
        
        # Count unique tools and duplicates
        unique_tools = len(by_normalized_name)
        duplicate_groups = sum(1 for group in by_normalized_name.values() if len(group) > 1)
        total_duplicates = sum(len(group) - 1 for group in by_normalized_name.values() if len(group) > 1)
        
        print(f"=== TOOL DUPLICATION ANALYSIS ===")
        print(f"Total tools in database: {total_tools}")
        print(f"Unique tools (normalized): {unique_tools}")
        print(f"Duplicate groups: {duplicate_groups}")
        print(f"Total duplicate tools: {total_duplicates}")
        print(f"Duplication rate: {total_duplicates/total_tools*100:.1f}%")
        print()
        
        # Show examples of duplicated tools
        if duplicate_groups > 0:
            print("=== EXAMPLES OF DUPLICATED TOOLS ===")
            count = 0
            for normalized_name, group in by_normalized_name.items():
                if len(group) > 1 and count < 10:  # Show first 10 examples
                    print(f"Normalized: '{normalized_name}' ({len(group)} copies)")
                    for tool in group:
                        print(f"  - ID: {tool.id}, Name: '{tool.name}', Stage: {tool.stage_id}, Category: {tool.category_id}")
                    print()
                    count += 1
        else:
            print("✅ No duplicates found!")

if __name__ == "__main__":
    check_tool_duplication()