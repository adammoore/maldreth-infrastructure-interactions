#!/usr/bin/env python3
"""
Database Management Utility for PRISM
Provides tools for cleaning test data and managing database state
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from streamlined_app import app, db, ToolInteraction, ExemplarTool, MaldrethStage, ToolCategory
    print("✅ Successfully imported application models")
except ImportError as e:
    print(f"❌ Error importing application: {e}")
    sys.exit(1)

def get_database_stats():
    """Get current database statistics"""
    with app.app_context():
        stats = {
            'interactions': ToolInteraction.query.count(),
            'tools': ExemplarTool.query.count(),
            'stages': MaldrethStage.query.count(),
            'categories': ToolCategory.query.count()
        }
    return stats

def identify_test_entries():
    """Identify entries that appear to be test data"""
    test_indicators = [
        'test', 'testing', 'demo', 'example', 'sample', 'temp', 'temporary',
        'debug', 'placeholder', 'lorem', 'ipsum', 'xxx', 'yyy', 'zzz',
        'asdf', 'qwerty', 'foo', 'bar', 'baz'
    ]
    
    with app.app_context():
        # Check tool interactions
        test_interactions = []
        interactions = ToolInteraction.query.all()
        
        for interaction in interactions:
            fields_to_check = [
                interaction.description or '',
                interaction.technical_details or '',
                interaction.benefits or '',
                interaction.challenges or '',
                interaction.examples or '',
                interaction.contact_person or '',
                interaction.organization or '',
                interaction.submitted_by or ''
            ]
            
            is_test = False
            for field in fields_to_check:
                field_lower = field.lower()
                if any(indicator in field_lower for indicator in test_indicators):
                    is_test = True
                    break
            
            if is_test:
                test_interactions.append({
                    'id': interaction.id,
                    'source_tool': interaction.source_tool.name if interaction.source_tool else 'N/A',
                    'target_tool': interaction.target_tool.name if interaction.target_tool else 'N/A',
                    'description': interaction.description[:50] + '...' if interaction.description else 'N/A',
                    'submitted_by': interaction.submitted_by or 'N/A'
                })
        
        return test_interactions

def bulk_edit_interactions():
    """Provide bulk editing options for interactions"""
    with app.app_context():
        print("\n🔍 BULK EDIT OPTIONS")
        print("=" * 50)
        
        # Show stats first
        stats = get_database_stats()
        print(f"Current Database Stats:")
        print(f"  - Interactions: {stats['interactions']}")
        print(f"  - Tools: {stats['tools']}")
        print(f"  - Stages: {stats['stages']}")
        print(f"  - Categories: {stats['categories']}")
        
        # Show test entries
        test_entries = identify_test_entries()
        if test_entries:
            print(f"\n⚠️  Found {len(test_entries)} potential test entries:")
            for entry in test_entries[:10]:  # Show first 10
                print(f"  ID {entry['id']}: {entry['source_tool']} → {entry['target_tool']}")
                print(f"    Description: {entry['description']}")
                print(f"    Submitted by: {entry['submitted_by']}")
                print()
        else:
            print("\n✅ No obvious test entries found")
        
        print("\nBULK EDIT OPTIONS:")
        print("1. Remove test entries (based on keywords)")
        print("2. Update all 'Submitted By' fields to 'MaLDReTH II Working Group'")
        print("3. Set all empty organizations to 'Research Data Alliance'")
        print("4. Update priority field for entries without priority")
        print("5. Show detailed interaction report")
        print("6. Exit without changes")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            remove_test_entries()
        elif choice == '2':
            update_submitted_by_fields()
        elif choice == '3':
            update_empty_organizations()
        elif choice == '4':
            update_priority_fields()
        elif choice == '5':
            show_detailed_report()
        elif choice == '6':
            print("Exiting without changes")
        else:
            print("Invalid choice")

def remove_test_entries():
    """Remove entries that appear to be test data"""
    test_entries = identify_test_entries()
    
    if not test_entries:
        print("✅ No test entries found to remove")
        return
    
    print(f"\n⚠️  This will remove {len(test_entries)} interactions")
    print("Test entries to be removed:")
    for entry in test_entries:
        print(f"  ID {entry['id']}: {entry['source_tool']} → {entry['target_tool']}")
    
    confirm = input(f"\nConfirm removal of {len(test_entries)} entries? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        with app.app_context():
            removed_count = 0
            for entry in test_entries:
                interaction = ToolInteraction.query.get(entry['id'])
                if interaction:
                    db.session.delete(interaction)
                    removed_count += 1
            
            try:
                db.session.commit()
                print(f"✅ Successfully removed {removed_count} test entries")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error removing entries: {e}")
    else:
        print("Operation cancelled")

def update_submitted_by_fields():
    """Update all submitted_by fields to standardize attribution"""
    with app.app_context():
        interactions = ToolInteraction.query.filter(
            (ToolInteraction.submitted_by == None) | 
            (ToolInteraction.submitted_by == '') |
            (ToolInteraction.submitted_by.like('%test%'))
        ).all()
        
        print(f"Found {len(interactions)} interactions with empty/test submitted_by fields")
        
        if interactions:
            confirm = input(f"Update {len(interactions)} 'Submitted By' fields to 'MaLDReTH II Working Group'? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                updated = 0
                for interaction in interactions:
                    interaction.submitted_by = 'MaLDReTH II Working Group'
                    updated += 1
                
                try:
                    db.session.commit()
                    print(f"✅ Updated {updated} interactions")
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ Error updating: {e}")
            else:
                print("Operation cancelled")

def update_empty_organizations():
    """Update empty organization fields"""
    with app.app_context():
        interactions = ToolInteraction.query.filter(
            (ToolInteraction.organization == None) | 
            (ToolInteraction.organization == '')
        ).all()
        
        print(f"Found {len(interactions)} interactions with empty organization fields")
        
        if interactions:
            confirm = input(f"Update {len(interactions)} organization fields to 'Research Data Alliance'? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                updated = 0
                for interaction in interactions:
                    interaction.organization = 'Research Data Alliance'
                    updated += 1
                
                try:
                    db.session.commit()
                    print(f"✅ Updated {updated} interactions")
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ Error updating: {e}")
            else:
                print("Operation cancelled")

def update_priority_fields():
    """Update priority fields for entries without priority"""
    with app.app_context():
        interactions = ToolInteraction.query.filter(
            (ToolInteraction.priority == None) | 
            (ToolInteraction.priority == '')
        ).all()
        
        print(f"Found {len(interactions)} interactions without priority")
        
        if interactions:
            print("Priority options: High, Medium, Low")
            priority = input("Set priority for all entries (High/Medium/Low): ").strip()
            
            if priority in ['High', 'Medium', 'Low']:
                confirm = input(f"Set priority to '{priority}' for {len(interactions)} interactions? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    updated = 0
                    for interaction in interactions:
                        interaction.priority = priority
                        updated += 1
                    
                    try:
                        db.session.commit()
                        print(f"✅ Updated {updated} interactions")
                    except Exception as e:
                        db.session.rollback()
                        print(f"❌ Error updating: {e}")
                else:
                    print("Operation cancelled")
            else:
                print("Invalid priority option")

def show_detailed_report():
    """Show detailed database report"""
    with app.app_context():
        print("\n📊 DETAILED DATABASE REPORT")
        print("=" * 50)
        
        # Basic stats
        stats = get_database_stats()
        print("BASIC STATISTICS:")
        for key, value in stats.items():
            print(f"  {key.title()}: {value}")
        
        # Interaction types distribution
        print("\nINTERACTION TYPES:")
        interaction_types = db.session.query(
            ToolInteraction.interaction_type, 
            db.func.count(ToolInteraction.id)
        ).group_by(ToolInteraction.interaction_type).all()
        
        for itype, count in interaction_types:
            print(f"  {itype}: {count}")
        
        # Lifecycle stages distribution
        print("\nLIFECYCLE STAGES:")
        stage_counts = db.session.query(
            ToolInteraction.lifecycle_stage, 
            db.func.count(ToolInteraction.id)
        ).group_by(ToolInteraction.lifecycle_stage).all()
        
        for stage, count in stage_counts:
            print(f"  {stage}: {count}")
        
        # Submission sources
        print("\nSUBMISSION SOURCES:")
        submitters = db.session.query(
            ToolInteraction.submitted_by, 
            db.func.count(ToolInteraction.id)
        ).group_by(ToolInteraction.submitted_by).all()
        
        for submitter, count in submitters:
            submitter_name = submitter if submitter else 'Unknown'
            print(f"  {submitter_name}: {count}")

def reset_database():
    """Complete database reset (DANGEROUS - DEVELOPMENT ONLY)"""
    print("\n🚨 DATABASE RESET WARNING 🚨")
    print("=" * 50)
    print("This will completely reset the database and reload initial data.")
    print("ALL CURRENT DATA WILL BE LOST!")
    print()
    
    # Check if this is production
    database_url = os.environ.get('DATABASE_URL', '')
    if 'heroku' in database_url.lower() or 'amazonaws' in database_url.lower():
        print("❌ SAFETY LOCK: Cannot reset production database!")
        print("This operation is only allowed for local development databases.")
        return
    
    confirm1 = input("Type 'RESET' to continue: ").strip()
    if confirm1 != 'RESET':
        print("Operation cancelled")
        return
    
    confirm2 = input("Are you absolutely sure? Type 'YES DELETE ALL DATA': ").strip()
    if confirm2 != 'YES DELETE ALL DATA':
        print("Operation cancelled")
        return
    
    print("Proceeding with database reset...")
    
    try:
        with app.app_context():
            # Drop all tables
            db.drop_all()
            print("✅ Dropped all tables")
            
            # Recreate tables
            db.create_all()
            print("✅ Created new tables")
            
            # Reload initial data (you might need to implement this)
            # reload_initial_data()
            print("✅ Database reset complete")
            
    except Exception as e:
        print(f"❌ Error during reset: {e}")

def main():
    """Main menu for database management"""
    print("🗄️  PRISM Database Management Utility")
    print("=" * 50)
    
    # Show current stats
    stats = get_database_stats()
    print("Current Database State:")
    for key, value in stats.items():
        print(f"  {key.title()}: {value}")
    
    print("\nMANAGEMENT OPTIONS:")
    print("1. Bulk edit interactions")
    print("2. Identify and manage test entries")
    print("3. Show detailed database report")
    print("4. Reset database (DEVELOPMENT ONLY)")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        bulk_edit_interactions()
    elif choice == '2':
        test_entries = identify_test_entries()
        print(f"Found {len(test_entries)} potential test entries")
        if test_entries:
            print("Use option 1 (Bulk edit) to manage them")
    elif choice == '3':
        show_detailed_report()
    elif choice == '4':
        reset_database()
    elif choice == '5':
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == '__main__':
    main()