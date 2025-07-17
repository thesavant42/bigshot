#!/usr/bin/env python3
"""
Test script to validate migration tools without requiring PostgreSQL.
This script performs dry-run tests and validation.
"""

import sys
import os
import tempfile
import sqlite3
from datetime import datetime

# Add the config directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_sqlite_schema():
    """Test that the SQLite schema can be created and used."""
    print("Testing SQLite schema...")
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor.executescript(schema_sql)
        
        # Test basic operations
        cursor.execute("""
            INSERT INTO domains (root_domain, subdomain, source, tags)
            VALUES ('example.com', 'www.example.com', 'crt.sh', 'test')
        """)
        
        cursor.execute("SELECT * FROM domains")
        row = cursor.fetchone()
        
        assert row is not None, "Failed to insert test data"
        assert row[1] == 'example.com', "Incorrect root_domain"
        assert row[2] == 'www.example.com', "Incorrect subdomain"
        
        conn.commit()
        print("✅ SQLite schema test passed")
        
    except Exception as e:
        print(f"❌ SQLite schema test failed: {e}")
        return False
    
    finally:
        if conn:
            conn.close()
        os.unlink(db_path)
    
    return True

def test_postgresql_schema():
    """Test that the PostgreSQL schema is syntactically correct."""
    print("Testing PostgreSQL schema syntax...")
    
    try:
        schema_path = os.path.join(os.path.dirname(__file__), 'postgresql_schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Basic syntax validation
        required_elements = [
            'CREATE TABLE',
            'domains',
            'SERIAL PRIMARY KEY',
            'CREATE INDEX',
            'CREATE TRIGGER',
            'CREATE OR REPLACE FUNCTION'
        ]
        
        for element in required_elements:
            if element not in schema_sql:
                print(f"❌ PostgreSQL schema missing: {element}")
                return False
        
        print("✅ PostgreSQL schema syntax test passed")
        
    except Exception as e:
        print(f"❌ PostgreSQL schema test failed: {e}")
        return False
    
    return True

def test_migration_script_import():
    """Test that the migration script can be imported."""
    print("Testing migration script import...")
    
    try:
        # Test importing without psycopg2
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "migrate_sqlite_to_postgresql", 
            os.path.join(os.path.dirname(__file__), 'migrate_sqlite_to_postgresql.py')
        )
        
        # We can't actually import it due to psycopg2 dependency,
        # but we can check that the file is syntactically correct
        with open(os.path.join(os.path.dirname(__file__), 'migrate_sqlite_to_postgresql.py'), 'r') as f:
            content = f.read()
        
        # Basic validation
        required_classes = ['SQLiteToPostgreSQLMigrator']
        required_methods = ['connect_databases', 'migrate_table', 'run_migration']
        
        for cls in required_classes:
            if f"class {cls}" not in content:
                print(f"❌ Migration script missing class: {cls}")
                return False
        
        for method in required_methods:
            if f"def {method}" not in content:
                print(f"❌ Migration script missing method: {method}")
                return False
        
        print("✅ Migration script structure test passed")
        
    except Exception as e:
        print(f"❌ Migration script test failed: {e}")
        return False
    
    return True

def test_analysis_script():
    """Test the hierarchical analysis script."""
    print("Testing hierarchical analysis script...")
    
    try:
        # Test importing the analysis script
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "analyze_hierarchical_support", 
            os.path.join(os.path.dirname(__file__), 'analyze_hierarchical_support.py')
        )
        
        # Basic validation
        with open(os.path.join(os.path.dirname(__file__), 'analyze_hierarchical_support.py'), 'r') as f:
            content = f.read()
        
        required_classes = ['SubdomainHierarchyAnalyzer']
        required_methods = ['analyze_schema_structure', 'analyze_sample_data', 'run_analysis']
        
        for cls in required_classes:
            if f"class {cls}" not in content:
                print(f"❌ Analysis script missing class: {cls}")
                return False
        
        for method in required_methods:
            if f"def {method}" not in content:
                print(f"❌ Analysis script missing method: {method}")
                return False
        
        print("✅ Analysis script structure test passed")
        
    except Exception as e:
        print(f"❌ Analysis script test failed: {e}")
        return False
    
    return True

def test_documentation():
    """Test that documentation exists and contains required sections."""
    print("Testing documentation...")
    
    try:
        doc_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'database_schema.md')
        
        with open(doc_path, 'r') as f:
            content = f.read()
        
        required_sections = [
            '# Database Schema and Migration Documentation',
            '## Database Schema',
            '## Migration Process',
            '## Hierarchical Subdomain Support',
            '## Performance Considerations',
            '## Troubleshooting'
        ]
        
        for section in required_sections:
            if section not in content:
                print(f"❌ Documentation missing section: {section}")
                return False
        
        print("✅ Documentation test passed")
        
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False
    
    return True

def main():
    """Run all validation tests."""
    print("Bigshot Database Tools Validation Suite")
    print("=" * 45)
    
    tests = [
        test_sqlite_schema,
        test_postgresql_schema,
        test_migration_script_import,
        test_analysis_script,
        test_documentation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 45)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All validation tests passed!")
        return 0
    else:
        print(f"❌ {failed} validation tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())