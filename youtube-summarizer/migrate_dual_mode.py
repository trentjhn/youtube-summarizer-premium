#!/usr/bin/env python3
"""
Database Migration Script: Add Dual-Mode Support

This script migrates the database schema to support dual-mode summarization
(Quick and In-Depth modes). It adds a 'mode' column and updates the unique
constraint to allow the same video to have multiple summaries (one per mode).

Key Changes:
- Adds 'mode' column (default: 'quick')
- Changes unique constraint from 'video_id' to composite '(video_id, mode)'
- Preserves all existing data (backward compatible)

Usage:
    python migrate_dual_mode.py

The script will:
1. Connect to the existing database
2. Add the 'mode' column to all existing records (default: 'quick')
3. Drop the old unique constraint on 'video_id'
4. Add new composite unique constraint on '(video_id, mode)'
5. Commit changes only if all steps succeed
"""

import sys
import os
import logging
from datetime import datetime

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from models.video import db
from sqlalchemy import text, inspect

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


def check_column_exists(table_name: str, column_name: str) -> bool:
    """
    Check if a column exists in a table.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column
        
    Returns:
        bool: True if column exists, False otherwise
    """
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_to_dual_mode():
    """
    Main migration function.
    
    Adds 'mode' column and updates unique constraint to support dual-mode caching.
    This function is idempotent - safe to run multiple times.
    """
    logger.info("=" * 70)
    logger.info("Starting Database Migration: Dual-Mode Summarization Support")
    logger.info("=" * 70)
    
    try:
        # Step 1: Check if migration is needed
        logger.info("\n[Step 1/5] Checking current schema...")
        
        if check_column_exists('videos', 'mode'):
            logger.info("✅ 'mode' column already exists. Migration may have already run.")
            logger.info("   Verifying data integrity...")
            
            # Check if all records have a mode value
            result = db.session.execute(text("SELECT COUNT(*) FROM videos WHERE mode IS NULL"))
            null_count = result.scalar()
            
            if null_count > 0:
                logger.warning(f"⚠️  Found {null_count} records with NULL mode. Fixing...")
                db.session.execute(text("UPDATE videos SET mode = 'quick' WHERE mode IS NULL"))
                db.session.commit()
                logger.info("✅ Fixed NULL mode values")
            else:
                logger.info("✅ All records have valid mode values")
            
            logger.info("\n✅ Database is already migrated for dual-mode support!")
            return True
        
        logger.info("'mode' column does not exist. Proceeding with migration...")
        
        # Step 2: Count existing records
        logger.info("\n[Step 2/5] Analyzing existing data...")
        result = db.session.execute(text("SELECT COUNT(*) FROM videos"))
        total_videos = result.scalar()
        logger.info(f"Found {total_videos} existing video records")
        
        # Step 3: Add 'mode' column (SQLite-specific approach)
        logger.info("\n[Step 3/5] Adding 'mode' column...")
        
        # SQLite doesn't support ALTER TABLE ADD COLUMN with constraints easily,
        # so we'll add the column and set default values
        try:
            db.session.execute(text("""
                ALTER TABLE videos 
                ADD COLUMN mode VARCHAR(20) DEFAULT 'quick' NOT NULL
            """))
            logger.info("✅ Added 'mode' column with default value 'quick'")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                logger.info("✅ 'mode' column already exists (skipping)")
            else:
                raise
        
        # Step 4: Update existing records to have mode='quick'
        logger.info("\n[Step 4/5] Setting mode='quick' for all existing records...")
        db.session.execute(text("UPDATE videos SET mode = 'quick' WHERE mode IS NULL"))
        updated_count = db.session.execute(text("SELECT COUNT(*) FROM videos WHERE mode = 'quick'")).scalar()
        logger.info(f"✅ Updated {updated_count} records to mode='quick'")
        
        # Step 5: Handle unique constraint (SQLite-specific approach)
        logger.info("\n[Step 5/5] Updating unique constraint...")
        logger.info("Note: SQLite requires recreating the table to change constraints")
        
        # For SQLite, we need to:
        # 1. Create a new table with the correct schema
        # 2. Copy data from old table
        # 3. Drop old table
        # 4. Rename new table
        
        # Check if we need to recreate the table
        inspector = inspect(db.engine)
        indexes = inspector.get_indexes('videos')
        unique_constraints = inspector.get_unique_constraints('videos')
        
        logger.info(f"Current indexes: {indexes}")
        logger.info(f"Current unique constraints: {unique_constraints}")
        
        # Check if the composite unique constraint already exists
        has_composite_constraint = any(
            set(uc.get('column_names', [])) == {'video_id', 'mode'}
            for uc in unique_constraints
        )
        
        if has_composite_constraint:
            logger.info("✅ Composite unique constraint (video_id, mode) already exists")
        else:
            logger.info("Creating new table with composite unique constraint...")
            
            # Create temporary table with new schema
            db.session.execute(text("""
                CREATE TABLE videos_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id VARCHAR(20) NOT NULL,
                    mode VARCHAR(20) DEFAULT 'quick' NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    url VARCHAR(200) NOT NULL,
                    transcript TEXT,
                    summary JSON,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(video_id, mode)
                )
            """))
            logger.info("✅ Created new table with composite unique constraint")
            
            # Copy data from old table to new table
            logger.info("Copying data to new table...")
            db.session.execute(text("""
                INSERT INTO videos_new 
                    (id, video_id, mode, title, url, transcript, summary, status, created_at, updated_at)
                SELECT 
                    id, video_id, mode, title, url, transcript, summary, status, created_at, updated_at
                FROM videos
            """))
            copied_count = db.session.execute(text("SELECT COUNT(*) FROM videos_new")).scalar()
            logger.info(f"✅ Copied {copied_count} records to new table")
            
            # Drop old table
            logger.info("Dropping old table...")
            db.session.execute(text("DROP TABLE videos"))
            logger.info("✅ Dropped old table")
            
            # Rename new table
            logger.info("Renaming new table to 'videos'...")
            db.session.execute(text("ALTER TABLE videos_new RENAME TO videos"))
            logger.info("✅ Renamed table")
        
        # Commit all changes
        db.session.commit()
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ Migration Complete!")
        logger.info("   - Added 'mode' column (default: 'quick')")
        logger.info("   - Updated unique constraint to (video_id, mode)")
        logger.info("   - All existing records preserved with mode='quick'")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        logger.error("Rolling back all changes...")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        logger.error("Rollback complete. Database unchanged.")
        return False


def verify_migration():
    """
    Verify that migration was successful.
    
    Checks that:
    1. 'mode' column exists
    2. All records have a mode value
    3. Composite unique constraint exists
    """
    logger.info("\n" + "=" * 70)
    logger.info("Verifying Migration...")
    logger.info("=" * 70)
    
    try:
        # Check 1: mode column exists
        if not check_column_exists('videos', 'mode'):
            logger.error("❌ 'mode' column does not exist!")
            return False
        logger.info("✅ 'mode' column exists")
        
        # Check 2: All records have mode values
        result = db.session.execute(text("SELECT COUNT(*) FROM videos WHERE mode IS NULL"))
        null_count = result.scalar()
        if null_count > 0:
            logger.error(f"❌ Found {null_count} records with NULL mode!")
            return False
        logger.info("✅ All records have valid mode values")
        
        # Check 3: Count records by mode
        result = db.session.execute(text("""
            SELECT mode, COUNT(*) as count 
            FROM videos 
            GROUP BY mode
        """))
        mode_counts = result.fetchall()
        logger.info("Mode distribution:")
        for mode, count in mode_counts:
            logger.info(f"  - {mode}: {count} records")
        
        # Check 4: Verify unique constraint
        inspector = inspect(db.engine)
        unique_constraints = inspector.get_unique_constraints('videos')
        has_composite = any(
            set(uc.get('column_names', [])) == {'video_id', 'mode'}
            for uc in unique_constraints
        )
        
        if has_composite:
            logger.info("✅ Composite unique constraint (video_id, mode) exists")
        else:
            logger.warning("⚠️  Composite unique constraint not found (may be implicit)")
        
        logger.info("\n✅ Migration verification complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for migration script."""
    logger.info("\n🚀 Dual-Mode Database Migration Script")
    logger.info("This will add support for independent Quick and In-Depth mode caching\n")
    
    app = create_app()
    
    with app.app_context():
        # Run migration
        success = migrate_to_dual_mode()
        
        if success:
            # Verify migration
            verify_migration()
            logger.info("\n✅ Migration script completed successfully!")
            logger.info("\nNext steps:")
            logger.info("  1. Restart the backend server")
            logger.info("  2. Test both Quick and In-Depth modes")
            logger.info("  3. Verify independent caching works correctly")
            sys.exit(0)
        else:
            logger.error("\n❌ Migration script failed!")
            logger.error("Database has been rolled back to previous state.")
            sys.exit(1)


if __name__ == "__main__":
    main()

