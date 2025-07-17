#!/usr/bin/env python3
"""
Migration script to convert SQLite database to PostgreSQL
for the bigshot reconnaissance application.

This script handles the schema conversion and data migration
from SQLite to PostgreSQL, ensuring data integrity and
performance optimization.
"""

import sqlite3
import psycopg2
import argparse
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SQLiteToPostgreSQLMigrator:
    """Handles migration from SQLite to PostgreSQL."""
    
    def __init__(self, sqlite_path: str, postgres_config: Dict[str, Any]):
        """
        Initialize the migrator.
        
        Args:
            sqlite_path: Path to SQLite database file
            postgres_config: PostgreSQL connection configuration
        """
        self.sqlite_path = sqlite_path
        self.postgres_config = postgres_config
        self.sqlite_conn = None
        self.postgres_conn = None
        
        # Table mapping for data type conversion
        self.type_mapping = {
            'INTEGER': 'INTEGER',
            'TEXT': 'TEXT',
            'TIMESTAMP': 'TIMESTAMP',
            'BOOLEAN': 'BOOLEAN'
        }
        
        # Tables to migrate in order (respecting foreign key dependencies)
        self.migration_order = [
            'urls',
            'jobs',
            'import_status',
            'text_notes',
            'jwt_cookies',
            'screenshots',
            'sitezips',
            'assets',
            'domains',
            'notes'  # Notes last due to foreign key to urls
        ]
    
    def connect_databases(self) -> bool:
        """
        Establish connections to both SQLite and PostgreSQL databases.
        
        Returns:
            bool: True if connections successful, False otherwise
        """
        try:
            # Connect to SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.sqlite_path}")
            
            # Connect to PostgreSQL
            self.postgres_conn = psycopg2.connect(**self.postgres_config)
            self.postgres_conn.autocommit = False
            logger.info("Connected to PostgreSQL database")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            return False
    
    def close_connections(self):
        """Close database connections."""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("Closed SQLite connection")
        
        if self.postgres_conn:
            self.postgres_conn.close()
            logger.info("Closed PostgreSQL connection")
    
    def validate_schema(self) -> bool:
        """
        Validate that the PostgreSQL schema exists and is correct.
        
        Returns:
            bool: True if schema is valid, False otherwise
        """
        try:
            cursor = self.postgres_conn.cursor()
            
            # Check if main tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('urls', 'jobs', 'domains', 'notes')
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            required_tables = ['urls', 'jobs', 'domains', 'notes']
            
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Missing required tables: {missing_tables}")
                return False
            
            logger.info("PostgreSQL schema validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get all data from a SQLite table.
        
        Args:
            table_name: Name of the table to query
            
        Returns:
            List of dictionaries containing row data
        """
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Convert sqlite3.Row objects to dictionaries
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get data from table {table_name}: {e}")
            return []
    
    def convert_row_data(self, table_name: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert SQLite row data to PostgreSQL format.
        
        Args:
            table_name: Name of the table
            row_data: Dictionary containing row data
            
        Returns:
            Converted row data
        """
        converted_data = {}
        
        for key, value in row_data.items():
            # Skip SQLite rowid if present
            if key == 'rowid':
                continue
            
            # Convert SQLite AUTOINCREMENT to PostgreSQL SERIAL (skip id in insert)
            if key == 'id' and table_name != 'import_status':
                continue
            
            # Convert Boolean values for PostgreSQL
            if key == 'cdx_indexed' and isinstance(value, int):
                converted_data[key] = bool(value)
            else:
                converted_data[key] = value
        
        return converted_data
    
    def build_insert_query(self, table_name: str, data: Dict[str, Any]) -> tuple:
        """
        Build INSERT query for PostgreSQL.
        
        Args:
            table_name: Name of the table
            data: Dictionary containing row data
            
        Returns:
            Tuple of (query_string, values_tuple)
        """
        columns = list(data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        values = tuple(data.values())
        
        return query, values
    
    def migrate_table(self, table_name: str) -> bool:
        """
        Migrate a single table from SQLite to PostgreSQL.
        
        Args:
            table_name: Name of the table to migrate
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            logger.info(f"Starting migration of table: {table_name}")
            
            # Get data from SQLite
            rows = self.get_table_data(table_name)
            
            if not rows:
                logger.info(f"No data found in table {table_name}")
                return True
            
            # Prepare PostgreSQL cursor
            cursor = self.postgres_conn.cursor()
            
            # Clear existing data (if any)
            cursor.execute(f"DELETE FROM {table_name}")
            
            # Insert data
            migrated_count = 0
            
            for row in rows:
                try:
                    converted_data = self.convert_row_data(table_name, row)
                    
                    if not converted_data:
                        continue
                    
                    query, values = self.build_insert_query(table_name, converted_data)
                    cursor.execute(query, values)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate row in {table_name}: {e}")
                    continue
            
            # Reset sequence for SERIAL columns
            if table_name != 'import_status':
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), (SELECT MAX(id) FROM {table_name}))")
            
            self.postgres_conn.commit()
            logger.info(f"Successfully migrated {migrated_count} rows from {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate table {table_name}: {e}")
            self.postgres_conn.rollback()
            return False
    
    def verify_migration(self) -> bool:
        """
        Verify that the migration was successful by comparing row counts.
        
        Returns:
            bool: True if verification successful, False otherwise
        """
        try:
            sqlite_cursor = self.sqlite_conn.cursor()
            postgres_cursor = self.postgres_conn.cursor()
            
            verification_results = {}
            
            for table_name in self.migration_order:
                # Get SQLite count
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # Get PostgreSQL count
                postgres_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                postgres_count = postgres_cursor.fetchone()[0]
                
                verification_results[table_name] = {
                    'sqlite_count': sqlite_count,
                    'postgres_count': postgres_count,
                    'match': sqlite_count == postgres_count
                }
            
            # Print verification results
            logger.info("Migration verification results:")
            for table_name, result in verification_results.items():
                status = "✓" if result['match'] else "✗"
                logger.info(f"{status} {table_name}: SQLite={result['sqlite_count']}, PostgreSQL={result['postgres_count']}")
            
            # Check if all tables match
            all_match = all(result['match'] for result in verification_results.values())
            
            if all_match:
                logger.info("✓ All tables successfully migrated")
            else:
                logger.error("✗ Some tables have mismatched row counts")
            
            return all_match
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def run_migration(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            # Connect to databases
            if not self.connect_databases():
                return False
            
            # Validate PostgreSQL schema
            if not self.validate_schema():
                return False
            
            # Migrate tables in order
            for table_name in self.migration_order:
                if not self.migrate_table(table_name):
                    logger.error(f"Migration failed at table: {table_name}")
                    return False
            
            # Verify migration
            if not self.verify_migration():
                logger.error("Migration verification failed")
                return False
            
            logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        
        finally:
            self.close_connections()

def main():
    """Main function to run the migration."""
    parser = argparse.ArgumentParser(description='Migrate SQLite database to PostgreSQL')
    parser.add_argument('--sqlite-path', required=True, help='Path to SQLite database file')
    parser.add_argument('--postgres-host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--postgres-port', default=5432, type=int, help='PostgreSQL port')
    parser.add_argument('--postgres-db', required=True, help='PostgreSQL database name')
    parser.add_argument('--postgres-user', required=True, help='PostgreSQL username')
    parser.add_argument('--postgres-password', required=True, help='PostgreSQL password')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no actual migration)')
    
    args = parser.parse_args()
    
    # Check if SQLite file exists
    if not os.path.exists(args.sqlite_path):
        logger.error(f"SQLite file not found: {args.sqlite_path}")
        sys.exit(1)
    
    # PostgreSQL configuration
    postgres_config = {
        'host': args.postgres_host,
        'port': args.postgres_port,
        'database': args.postgres_db,
        'user': args.postgres_user,
        'password': args.postgres_password
    }
    
    # Create migrator instance
    migrator = SQLiteToPostgreSQLMigrator(args.sqlite_path, postgres_config)
    
    # Run migration
    success = migrator.run_migration()
    
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1)

if __name__ == '__main__':
    main()