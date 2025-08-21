#!/usr/bin/env python3
"""
add_dmptool_entry.py

Add the DMPTool entry provided by Maria Praetzellis to the database.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from streamlined_app import app, db, MaldrethStage, ExemplarTool, ToolInteraction


def add_dmptool_entry():
    """Add the DMPTool interaction entry to the database."""
    
    print("=" * 60)
    print("Adding DMPTool Entry")
    print("=" * 60)
    
    # First, ensure DMPTool exists as an exemplar tool
    dmptool = ExemplarTool.query.filter_by(name="DMPTool").first()
    if not dmptool:
        # Find the PLAN stage
        plan_stage = MaldrethStage.query.filter_by(name="PLAN").first()
        if not plan_stage:
            print("✗ PLAN stage not found!")
            return False
        
        # Create DMPTool as an exemplar tool in PLAN stage
        # Find DMP category or create it
        from streamlined_app import ToolCategory
        dmp_category = ToolCategory.query.filter_by(
            name="Data management planning (DMP)", 
            stage_id=plan_stage.id
        ).first()
        
        if not dmp_category:
            print("✗ DMP category not found!")
            return False
        
        dmptool = ExemplarTool(
            name="DMPTool",
            stage_id=plan_stage.id,
            category_id=dmp_category.id
        )
        db.session.add(dmptool)
        db.session.flush()
        print("✓ Created DMPTool as exemplar tool")
    else:
        print("✓ DMPTool already exists")
    
    # Create a generic "RSpace" tool if it doesn't exist (as target tool)
    rspace_tool = ExemplarTool.query.filter_by(name="RSpace").first()
    if not rspace_tool:
        # Find PROCESS stage for RSpace (ELN tool)
        process_stage = MaldrethStage.query.filter_by(name="PROCESS").first()
        if not process_stage:
            print("✗ PROCESS stage not found!")
            return False
        
        # Find ELN category
        from streamlined_app import ToolCategory
        eln_category = ToolCategory.query.filter_by(
            name="Electronic laboratory notebooks (ELNs)",
            stage_id=process_stage.id
        ).first()
        
        if not eln_category:
            print("✗ ELN category not found!")
            return False
        
        rspace_tool = ExemplarTool(
            name="RSpace",
            stage_id=process_stage.id,
            category_id=eln_category.id
        )
        db.session.add(rspace_tool)
        db.session.flush()
        print("✓ Created RSpace as exemplar tool")
    else:
        print("✓ RSpace already exists")
    
    # Check if this interaction already exists
    existing_interaction = ToolInteraction.query.filter_by(
        source_tool_id=dmptool.id,
        target_tool_id=rspace_tool.id,
        interaction_type="API based"
    ).first()
    
    if existing_interaction:
        print("ℹ DMPTool interaction already exists, updating...")
        interaction = existing_interaction
    else:
        interaction = ToolInteraction()
        print("✓ Creating new DMPTool interaction")
    
    # Set the interaction data based on the provided entry
    interaction.source_tool_id = dmptool.id
    interaction.target_tool_id = rspace_tool.id
    interaction.interaction_type = "API based"
    interaction.lifecycle_stage = "ALL"  # As specified in the entry
    interaction.description = "Integration between DMPTool and internal security systems in universities, user support systems, RSpace"
    interaction.technical_details = "Rest API with JSON. Different for each of the integrations. Based on the information in DMPs, it can assign resources to researchers for HPC use"
    interaction.benefits = "Efficiency in planning for upcoming potential resourcing needs; identifying security/privacy issues early"
    interaction.challenges = "Resourcing issues, QA, access to actual plans"
    interaction.examples = "Recent pilot program. RDA Common Standard for DMPs"
    interaction.contact_person = "Maria Praetzellis"
    interaction.organization = "CDL"
    interaction.email = "maria.praetzellis@ucop.edu"
    interaction.priority = "Medium"
    interaction.complexity = "Medium"
    interaction.status = "pilot"
    interaction.submitted_by = "Maria Praetzellis (DMPTool owner)"
    interaction.submitted_at = datetime.utcnow()
    
    if not existing_interaction:
        db.session.add(interaction)
    
    try:
        db.session.commit()
        print("✓ DMPTool interaction added successfully")
        print(f"  - Source: {dmptool.name}")
        print(f"  - Target: {rspace_tool.name}")
        print(f"  - Type: {interaction.interaction_type}")
        print(f"  - Contact: {interaction.contact_person}")
        print(f"  - Organization: {interaction.organization}")
        return True
    except Exception as e:
        print(f"✗ Error adding interaction: {e}")
        db.session.rollback()
        return False


def main():
    """Main entry point."""
    with app.app_context():
        try:
            success = add_dmptool_entry()
            if not success:
                print("\n✗ Failed to add DMPTool entry!")
                sys.exit(1)
            else:
                print("\n✓ DMPTool entry added successfully!")
                sys.exit(0)
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()