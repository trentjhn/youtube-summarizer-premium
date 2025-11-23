#!/usr/bin/env python3
"""
Database Migration Script: Text Summaries to JSON Format

This script migrates existing text-based summaries in the database to the new
JSON-structured format required by the premium UI upgrade.

Key Features:
- Idempotent: Safe to run multiple times without causing issues
- Backward Compatible: Preserves existing data while converting format
- Error Handling: Comprehensive logging and rollback on failure
- Validation: Checks data integrity before and after migration

Usage:
    python migrate_db.py

The script will:
1. Connect to the existing database
2. Find all videos with text-based summaries
3. Convert them to JSON format
4. Commit changes only if all conversions succeed
"""

import sys
import os
import json
import logging
from datetime import datetime, timezone

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from models.video import db, Video

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Create Flask app with database configuration."""
    app = Flask(__name__)
    
    # Database configuration - use the existing database
    db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    logger.info(f"Connected to database: {db_path}")
    return app


def is_text_summary(summary) -> bool:
    """
    Check if a summary is in old text format (not JSON).
    
    Args:
        summary: The summary field from database
        
    Returns:
        bool: True if summary is text format, False if already JSON or None
    """
    if summary is None:
        return False
    
    # If it's already a dict/list, it's JSON format
    if isinstance(summary, (dict, list)):
        return False
    
    # If it's a string, it's old text format
    if isinstance(summary, str):
        return True
    
    return False


def convert_text_to_json(text_summary: str, title: str) -> dict:
    """
    Convert old text-based summary to new JSON structure.
    
    Args:
        text_summary: The old text summary
        title: Video title
        
    Returns:
        dict: JSON-structured summary
    """
    # Create a basic JSON structure from the text summary
    json_summary = {
        "quick_takeaway": f"Summary of: {title}",
        "key_points": [
            "This summary was migrated from the previous text format.",
            "For best results, consider regenerating the summary."
        ],
        "topics": [
            {"topic_name": "Video Content", "summary_section_id": 1}
        ],
        "timestamps": [],
        "full_summary": [
            {
                "id": 1,
                "content": text_summary
            }
        ]
    }
    
    return json_summary


def migrate_summaries():
    """
    Main migration function.
    
    Finds all videos with text summaries and converts them to JSON format.
    This function is idempotent - safe to run multiple times.
    """
    logger.info("=" * 60)
    logger.info("Starting Database Migration: Text to JSON Summaries")
    logger.info("=" * 60)
    
    try:
        # Query all videos
        # NOTE: We need to query the raw database because SQLAlchemy's JSON column
        # will fail to deserialize old text summaries
        logger.info("Querying all videos from database...")

        # Use raw SQL to get videos without JSON deserialization
        from sqlalchemy import text
        result = db.session.execute(text("SELECT id, video_id, title, summary FROM videos"))
        rows = result.fetchall()

        total_videos = len(rows)
        logger.info(f"Found {total_videos} total videos in database")
        
        # Find videos that need migration
        videos_to_migrate = []
        already_migrated = 0
        no_summary = 0

        for row in rows:
            try:
                video_id = row[1]
                title = row[2]
                summary_raw = row[3]

                logger.info(f"  Checking video {video_id}...")

                if summary_raw is None:
                    no_summary += 1
                    logger.info(f"    → No summary")
                else:
                    # Try to parse as JSON
                    try:
                        summary_obj = json.loads(summary_raw)
                        # Check if it has the new JSON structure
                        if isinstance(summary_obj, dict) and 'quick_takeaway' in summary_obj:
                            already_migrated += 1
                            logger.info(f"    → Already migrated (valid JSON structure)")
                        else:
                            # It's JSON but not the right structure - needs migration
                            videos_to_migrate.append((row[0], video_id, title, summary_raw))
                            logger.info(f"    → Needs migration (JSON but wrong structure)")
                    except (json.JSONDecodeError, TypeError):
                        # It's plain text - needs migration
                        videos_to_migrate.append((row[0], video_id, title, summary_raw))
                        logger.info(f"    → Needs migration (plain text)")
            except Exception as e:
                logger.error(f"    ERROR checking video {video_id}: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        logger.info(f"Migration Status:")
        logger.info(f"  - Already in JSON format: {already_migrated}")
        logger.info(f"  - Need migration: {len(videos_to_migrate)}")
        logger.info(f"  - No summary: {no_summary}")
        
        # If nothing to migrate, exit early
        if len(videos_to_migrate) == 0:
            logger.info("✅ No summaries need migration. Database is up to date!")
            return True
        
        # Migrate each video
        logger.info(f"\nMigrating {len(videos_to_migrate)} summaries...")
        migrated_count = 0

        for i, (video_db_id, video_id, title, summary_raw) in enumerate(videos_to_migrate, 1):
            try:
                logger.info(f"  [{i}/{len(videos_to_migrate)}] Migrating video: {video_id} - {title[:50]}...")

                # Convert text summary to JSON
                json_summary = convert_text_to_json(summary_raw, title)
                json_str = json.dumps(json_summary)

                # Update the video record using raw SQL
                update_sql = text("""
                    UPDATE videos
                    SET summary = :summary, updated_at = :updated_at
                    WHERE id = :id
                """)
                db.session.execute(update_sql, {
                    'summary': json_str,
                    'updated_at': datetime.now(timezone.utc),
                    'id': video_db_id
                })

                migrated_count += 1
                logger.info(f"      ✓ Successfully converted to JSON format")

            except Exception as e:
                logger.error(f"      ✗ Failed to migrate video {video_id}: {e}")
                raise  # Re-raise to trigger rollback
        
        # Commit all changes
        db.session.commit()
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ Migration Complete!")
        logger.info(f"   Successfully migrated {migrated_count} summaries")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        logger.error("Rolling back all changes...")
        db.session.rollback()
        logger.error("Rollback complete. Database unchanged.")
        return False


def verify_migration():
    """
    Verify that migration was successful.
    
    Checks that all summaries are now in JSON format.
    """
    logger.info("\nVerifying migration...")
    
    all_videos = Video.query.filter(Video.summary.isnot(None)).all()
    text_summaries = sum(1 for v in all_videos if is_text_summary(v.summary))
    json_summaries = sum(1 for v in all_videos if not is_text_summary(v.summary))
    
    logger.info(f"Verification Results:")
    logger.info(f"  - JSON summaries: {json_summaries}")
    logger.info(f"  - Text summaries: {text_summaries}")
    
    if text_summaries == 0:
        logger.info("✅ All summaries are in JSON format!")
        return True
    else:
        logger.warning(f"⚠️  {text_summaries} summaries are still in text format")
        return False


def main():
    """Main entry point for migration script."""
    app = create_app()
    
    with app.app_context():
        # Run migration
        success = migrate_summaries()
        
        if success:
            # Verify migration
            verify_migration()
            logger.info("\n✅ Migration script completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n❌ Migration script failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()

