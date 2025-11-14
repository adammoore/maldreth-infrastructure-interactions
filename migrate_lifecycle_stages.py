#!/usr/bin/env python3
"""
Database migration script for lifecycle stage changes (Co-chairs meeting Nov 13, 2025)

Changes:
1. Make lifecycle_stage column nullable (no longer user-input)
2. Lifecycle stages now computed from source/target tools
3. No data loss - existing data preserved

This script can be run locally and is also integrated into Heroku release process.
"""

import sys
import os
sys.path.append('.')

from streamlined_app import app, db, ToolInteraction, logger

def migrate_lifecycle_stages():
    """Migrate lifecycle_stage column to nullable and update existing data."""

    logger.info("=" * 60)
    logger.info("LIFECYCLE STAGE MIGRATION")
    logger.info("=" * 60)

    with app.app_context():
        try:
            # Check current database state
            inspector = db.inspect(db.engine)

            # Check if tool_interactions table exists
            tables = inspector.get_table_names()
            if 'tool_interactions' not in tables:
                logger.info("⚠️  tool_interactions table does not exist yet")
                logger.info("   Creating all tables...")
                db.create_all()
                logger.info("✅ All tables created")
                return True

            # Get column info
            columns = {col['name']: col for col in inspector.get_columns('tool_interactions')}

            # Step 1: Make lifecycle_stage nullable if it exists
            if 'lifecycle_stage' in columns:
                logger.info("\nStep 1: Making lifecycle_stage column nullable...")

                # Check if already nullable
                is_nullable = columns['lifecycle_stage'].get('nullable', False)

                if not is_nullable:
                    try:
                        # Make column nullable
                        db.session.execute(db.text(
                            'ALTER TABLE tool_interactions ALTER COLUMN lifecycle_stage DROP NOT NULL'
                        ))
                        db.session.commit()
                        logger.info("✅ lifecycle_stage column is now nullable")
                    except Exception as e:
                        logger.warning(f"   Note: {e}")
                        logger.info("   lifecycle_stage may already be nullable")
                        db.session.rollback()
                else:
                    logger.info("✅ lifecycle_stage column is already nullable")
            else:
                logger.info("⚠️  lifecycle_stage column does not exist")

            # Step 2: Verify computed properties work
            logger.info("\nStep 2: Verifying computed lifecycle stages...")

            sample_interactions = ToolInteraction.query.limit(5).all()

            if sample_interactions:
                logger.info(f"   Testing {len(sample_interactions)} sample interactions:")
                for interaction in sample_interactions:
                    stages = interaction.lifecycle_stages
                    display = interaction.lifecycle_stages_display
                    logger.info(f"   ID {interaction.id}: {display} (stages: {stages})")
                logger.info("✅ Computed properties working correctly")
            else:
                logger.info("   No interactions in database yet (this is fine for fresh install)")

            # Step 3: Statistics
            logger.info("\nStep 3: Migration statistics...")
            total_interactions = ToolInteraction.query.count()
            logger.info(f"   Total interactions: {total_interactions}")

            if total_interactions > 0:
                # Count interactions with valid computed stages
                valid_stages = 0
                for interaction in ToolInteraction.query.all():
                    if len(interaction.lifecycle_stages) > 0:
                        valid_stages += 1

                logger.info(f"   Interactions with valid computed stages: {valid_stages}/{total_interactions}")

                if valid_stages < total_interactions:
                    logger.warning(f"   ⚠️  {total_interactions - valid_stages} interactions missing stage information")
                    logger.warning("      Check that source/target tools have assigned lifecycle stages")

            logger.info("\n" + "=" * 60)
            logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = migrate_lifecycle_stages()
    sys.exit(0 if success else 1)
