#!/usr/bin/env python3
"""
Migration script to add error_message column to existing jobs table.

This script handles the case where a database was created before the error_message
column was added to the Job model. It safely adds the column if it doesn't exist.

Usage:
    python scripts/add_error_message_column.py

Environment variables:
    DATABASE_URL or SQLALCHEMY_DATABASE_URI - Database connection string

Example:
    export DATABASE_URL="postgresql://user:pass@localhost/bigshot"
    python scripts/add_error_message_column.py
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from environment variables"""
    # Try different environment variable names
    for env_var in ["DATABASE_URL", "SQLALCHEMY_DATABASE_URI"]:
        url = os.getenv(env_var)
        if url:
            return url

    # Default to SQLite for development
    default_url = "sqlite:///instance/bigshot.db"
    logger.warning(f"No DATABASE_URL found, using default: {default_url}")
    return default_url


def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)

    try:
        columns = inspector.get_columns(table_name)
        column_names = [col["name"] for col in columns]
        return column_name in column_names
    except Exception as e:
        logger.error(f"Error checking if column exists: {e}")
        return False


def add_error_message_column(engine):
    """Add error_message column to jobs table if it doesn't exist"""
    table_name = "jobs"
    column_name = "error_message"

    # Check if column already exists
    if check_column_exists(engine, table_name, column_name):
        logger.info(f"Column {column_name} already exists in {table_name} table")
        return True

    logger.info(f"Adding {column_name} column to {table_name} table...")

    try:
        # Determine database dialect
        dialect = engine.dialect.name

        if dialect == "postgresql":
            # PostgreSQL syntax
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"
        elif dialect == "sqlite":
            # SQLite syntax
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"
        elif dialect == "mysql":
            # MySQL syntax
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"
        else:
            # Generic SQL
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"

        logger.info(f"Executing SQL: {sql}")

        with engine.connect() as conn:
            # Use a transaction for safety
            with conn.begin():
                conn.execute(text(sql))
                logger.info(
                    f"Successfully added {column_name} column to {table_name} table"
                )

        return True

    except ProgrammingError as e:
        if "already exists" in str(e).lower():
            logger.info(f"Column {column_name} already exists (caught exception)")
            return True
        else:
            logger.error(f"Database error adding column: {e}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error adding column: {e}")
        return False


def verify_column_added(engine):
    """Verify that the error_message column was successfully added"""
    if check_column_exists(engine, "jobs", "error_message"):
        logger.info("✓ Verification successful: error_message column exists")
        return True
    else:
        logger.error("✗ Verification failed: error_message column not found")
        return False


def main():
    """Main migration function"""
    logger.info("Starting jobs table migration: adding error_message column")

    # Get database URL
    database_url = get_database_url()
    logger.info(
        f"Using database: {database_url.split('@')[-1] if '@' in database_url else database_url}"
    )

    try:
        # Create engine
        engine = create_engine(database_url)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")

        # Add the column
        success = add_error_message_column(engine)

        if success:
            # Verify the change
            if verify_column_added(engine):
                logger.info("✓ Migration completed successfully")
                return 0
            else:
                logger.error("✗ Migration verification failed")
                return 1
        else:
            logger.error("✗ Migration failed")
            return 1

    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
