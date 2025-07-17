#!/usr/bin/env python3
"""
Test script to verify hierarchical subdomain support in the database schema.
This script creates test data and validates the hierarchical structure.
"""

import sqlite3
import os
import tempfile
from datetime import datetime

def create_test_database():
    """Create a test database with sample hierarchical subdomain data."""
    
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute the schema
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    
    # Insert test data with hierarchical structure
    test_domains = [
        # example.com hierarchy
        ('example.com', 'example.com', 'crt.sh', 'production'),
        ('example.com', 'www.example.com', 'crt.sh', 'production'),
        ('example.com', 'api.example.com', 'crt.sh', 'production'),
        ('example.com', 'mail.example.com', 'crt.sh', 'production'),
        ('example.com', 'stage.www.example.com', 'crt.sh', 'staging'),
        ('example.com', 'dev.www.example.com', 'crt.sh', 'development'),
        ('example.com', 'v1.api.example.com', 'crt.sh', 'api'),
        ('example.com', 'v2.api.example.com', 'crt.sh', 'api'),
        ('example.com', 'admin.stage.www.example.com', 'crt.sh', 'admin,staging'),
        ('example.com', 'test.dev.www.example.com', 'crt.sh', 'test,development'),
        
        # target.org hierarchy
        ('target.org', 'target.org', 'virustotal', 'target'),
        ('target.org', 'blog.target.org', 'virustotal', 'target'),
        ('target.org', 'shop.target.org', 'virustotal', 'target'),
        ('target.org', 'secure.shop.target.org', 'virustotal', 'target,secure'),
        ('target.org', 'payment.secure.shop.target.org', 'virustotal', 'target,secure,payment'),
        
        # test.com hierarchy with multiple sources
        ('test.com', 'test.com', 'crt.sh', 'testing'),
        ('test.com', 'test.com', 'shodan', 'testing'),
        ('test.com', 'www.test.com', 'crt.sh', 'testing'),
        ('test.com', 'www.test.com', 'virustotal', 'testing'),
        ('test.com', 'app.test.com', 'crt.sh', 'testing'),
    ]
    
    for root_domain, subdomain, source, tags in test_domains:
        cursor.execute("""
            INSERT INTO domains (root_domain, subdomain, source, tags, cdx_indexed, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (root_domain, subdomain, source, tags, 0, datetime.now().isoformat()))
    
    conn.commit()
    print(f"Created test database: {db_path}")
    print(f"Inserted {len(test_domains)} test domain records")
    
    return db_path, conn

def test_hierarchical_queries(conn):
    """Test various hierarchical queries to verify schema support."""
    
    cursor = conn.cursor()
    
    print("\n=== Testing Hierarchical Queries ===")
    
    # Test 1: Get all root domains
    print("\n1. Root domains:")
    cursor.execute("SELECT DISTINCT root_domain FROM domains ORDER BY root_domain")
    for row in cursor.fetchall():
        print(f"   - {row[0]}")
    
    # Test 2: Get hierarchical structure for example.com
    print("\n2. Hierarchical structure for example.com:")
    cursor.execute("""
        SELECT subdomain, source, tags
        FROM domains
        WHERE root_domain = 'example.com'
        ORDER BY subdomain
    """)
    
    for row in cursor.fetchall():
        subdomain, source, tags = row
        # Calculate depth by counting additional parts
        depth = len(subdomain.split('.')) - 2  # -2 for root domain parts
        indent = "  " * depth
        print(f"   {indent}- {subdomain} (source: {source}, tags: {tags})")
    
    # Test 3: Count subdomains by root domain
    print("\n3. Subdomain counts by root domain:")
    cursor.execute("""
        SELECT root_domain, COUNT(*) as count
        FROM domains
        GROUP BY root_domain
        ORDER BY count DESC
    """)
    
    for row in cursor.fetchall():
        root_domain, count = row
        print(f"   - {root_domain}: {count} subdomains")
    
    # Test 4: Test unique constraint (subdomain, source)
    print("\n4. Testing unique constraint (subdomain, source):")
    cursor.execute("""
        SELECT subdomain, COUNT(*) as count
        FROM domains
        GROUP BY subdomain, source
        HAVING COUNT(*) > 1
    """)
    
    duplicates = cursor.fetchall()
    if duplicates:
        print("   ⚠️  Found duplicate (subdomain, source) pairs:")
        for row in duplicates:
            print(f"     - {row[0]}: {row[1]} duplicates")
    else:
        print("   ✅ No duplicate (subdomain, source) pairs found")
    
    # Test 5: Test indexes performance (simulate with EXPLAIN QUERY PLAN)
    print("\n5. Testing index usage for hierarchical queries:")
    
    test_queries = [
        ("Root domain lookup", "SELECT * FROM domains WHERE root_domain = 'example.com'"),
        ("Subdomain lookup", "SELECT * FROM domains WHERE subdomain = 'www.example.com'"),
        ("Hierarchical query", "SELECT * FROM domains WHERE root_domain = 'example.com' ORDER BY subdomain"),
    ]
    
    for query_name, query in test_queries:
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchone()
        uses_index = "USING INDEX" in plan[3] if plan else False
        status = "✅" if uses_index else "⚠️"
        print(f"   {status} {query_name}: {'Uses index' if uses_index else 'No index usage detected'}")
    
    # Test 6: Test hierarchical filtering
    print("\n6. Testing hierarchical filtering:")
    
    # Find all subdomains under www.example.com
    cursor.execute("""
        SELECT subdomain
        FROM domains
        WHERE root_domain = 'example.com'
        AND subdomain LIKE '%.www.example.com'
        ORDER BY subdomain
    """)
    
    www_subdomains = cursor.fetchall()
    print(f"   Found {len(www_subdomains)} subdomains under www.example.com:")
    for row in www_subdomains:
        print(f"     - {row[0]}")
    
    # Test 7: Test source analysis
    print("\n7. Source analysis:")
    cursor.execute("""
        SELECT source, COUNT(DISTINCT root_domain) as domains, COUNT(*) as total_subdomains
        FROM domains
        GROUP BY source
        ORDER BY total_subdomains DESC
    """)
    
    for row in cursor.fetchall():
        source, domains, total_subdomains = row
        print(f"   - {source}: {domains} domains, {total_subdomains} subdomains")

def test_data_integrity(conn):
    """Test data integrity constraints."""
    
    cursor = conn.cursor()
    
    print("\n=== Testing Data Integrity ===")
    
    # Test 1: Try to insert invalid data
    print("\n1. Testing constraint violations:")
    
    invalid_tests = [
        ("Empty root_domain", "INSERT INTO domains (root_domain, subdomain, source) VALUES ('', 'test.com', 'test')"),
        ("Empty subdomain", "INSERT INTO domains (root_domain, subdomain, source) VALUES ('test.com', '', 'test')"),
        ("Empty source", "INSERT INTO domains (root_domain, subdomain, source) VALUES ('test.com', 'test.com', '')"),
        ("Duplicate (subdomain, source)", "INSERT INTO domains (root_domain, subdomain, source) VALUES ('test.com', 'test.com', 'crt.sh')"),
    ]
    
    for test_name, invalid_query in invalid_tests:
        try:
            cursor.execute(invalid_query)
            conn.commit()
            print(f"   ⚠️  {test_name}: Should have failed but succeeded")
        except sqlite3.IntegrityError as e:
            print(f"   ✅ {test_name}: Correctly rejected ({e})")
        except Exception as e:
            print(f"   ⚠️  {test_name}: Unexpected error ({e})")

def generate_analysis_report(conn):
    """Generate a comprehensive analysis report."""
    
    cursor = conn.cursor()
    
    print("\n=== Analysis Report ===")
    
    # Basic statistics
    cursor.execute("SELECT COUNT(*) FROM domains")
    total_domains = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT root_domain) FROM domains")
    unique_roots = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT subdomain) FROM domains")
    unique_subdomains = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT source) FROM domains")
    unique_sources = cursor.fetchone()[0]
    
    print(f"\nStatistics:")
    print(f"  - Total domain records: {total_domains}")
    print(f"  - Unique root domains: {unique_roots}")
    print(f"  - Unique subdomains: {unique_subdomains}")
    print(f"  - Unique sources: {unique_sources}")
    
    # Hierarchical complexity analysis
    cursor.execute("""
        SELECT 
            root_domain,
            COUNT(*) as subdomain_count,
            MAX(LENGTH(subdomain) - LENGTH(root_domain)) as max_depth
        FROM domains
        GROUP BY root_domain
        ORDER BY subdomain_count DESC
    """)
    
    print(f"\nHierarchical complexity:")
    for row in cursor.fetchall():
        root_domain, subdomain_count, max_depth = row
        print(f"  - {root_domain}: {subdomain_count} subdomains, max depth: {max_depth}")
    
    # Schema validation
    cursor.execute("PRAGMA table_info(domains)")
    columns = cursor.fetchall()
    
    required_columns = ['root_domain', 'subdomain', 'source', 'tags', 'cdx_indexed', 'fetched_at']
    found_columns = [col[1] for col in columns]
    
    print(f"\nSchema validation:")
    for col in required_columns:
        status = "✅" if col in found_columns else "❌"
        print(f"  {status} {col}")
    
    # Index analysis
    cursor.execute("PRAGMA index_list(domains)")
    indexes = cursor.fetchall()
    
    print(f"\nIndexes found: {len(indexes)}")
    for index in indexes:
        print(f"  - {index[1]} ({'unique' if index[2] else 'non-unique'})")

def main():
    """Main function to run all tests."""
    
    print("Bigshot Database Schema Test Suite")
    print("=" * 40)
    
    # Create test database
    db_path, conn = create_test_database()
    
    try:
        # Run tests
        test_hierarchical_queries(conn)
        test_data_integrity(conn)
        generate_analysis_report(conn)
        
        print("\n" + "=" * 40)
        print("✅ All tests completed successfully!")
        print(f"Test database preserved at: {db_path}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()