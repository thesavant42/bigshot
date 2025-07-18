# Database Schema and Migration Documentation

## Overview

This document describes the database schema for the bigshot reconnaissance application and provides guidance for migrating from SQLite to PostgreSQL. The schema is designed to support hierarchical subdomain enumeration and analysis with high performance and data integrity.

## Database Schema

### Core Tables

#### 1. domains
The `domains` table is the central table for storing hierarchical subdomain information. It supports collapsible/expandable subdomain trees in the user interface.

```sql
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    root_domain TEXT NOT NULL,
    subdomain TEXT NOT NULL,
    source TEXT NOT NULL,
    tags TEXT DEFAULT '',
    cdx_indexed BOOLEAN DEFAULT FALSE,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subdomain, source)
);
```

**Columns:**
- `id`: Primary key (auto-incrementing)
- `root_domain`: The root domain (e.g., "example.com")
- `subdomain`: The full subdomain (e.g., "www.example.com", "stage.www.example.com")
- `source`: Source of discovery (e.g., "crt.sh", "virustotal", "shodan")
- `tags`: User-defined tags for categorization
- `cdx_indexed`: Whether the domain has been indexed in CDX
- `fetched_at`: When the domain was discovered
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**Hierarchical Support:**
The schema supports hierarchical subdomain display by:
- Storing the full subdomain path in the `subdomain` column
- Maintaining the `root_domain` for efficient grouping
- Using composite indexes for fast hierarchical queries

#### 2. urls
Stores discovered URLs with associated metadata.

```sql
CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    domain TEXT,
    timestamp TEXT,
    status_code INTEGER,
    mime_type TEXT,
    tags TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. jobs
Manages background enumeration and processing jobs.

```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    type TEXT,
    domain TEXT,
    status TEXT,
    progress INTEGER,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. notes
User annotations for specific URLs.

```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    url_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(url_id) REFERENCES urls(id) ON DELETE CASCADE
);
```

### Performance Indexes

The schema includes comprehensive indexes for optimal performance:

```sql
-- Domain indexes for hierarchical queries
CREATE INDEX idx_domains_root ON domains(root_domain);
CREATE INDEX idx_domains_subdomain ON domains(subdomain);
CREATE INDEX idx_domains_source ON domains(source);
CREATE INDEX idx_domains_hierarchical ON domains(root_domain, subdomain);
CREATE INDEX idx_domains_root_created ON domains(root_domain, created_at);

-- URL indexes
CREATE INDEX idx_urls_domain ON urls(domain);
CREATE INDEX idx_urls_domain_status ON urls(domain, status_code);

-- Job indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_type ON jobs(type);
CREATE INDEX idx_jobs_domain ON jobs(domain);
```

### Data Integrity Constraints

```sql
-- Ensure required fields are not empty
ALTER TABLE domains ADD CONSTRAINT chk_domains_subdomain_not_empty CHECK (subdomain != '');
ALTER TABLE domains ADD CONSTRAINT chk_domains_root_domain_not_empty CHECK (root_domain != '');
ALTER TABLE domains ADD CONSTRAINT chk_domains_source_not_empty CHECK (source != '');

-- Validate job status
ALTER TABLE jobs ADD CONSTRAINT chk_jobs_status_valid 
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));
```

## Migration Process

### SQLite to PostgreSQL Migration

The migration process involves several steps to ensure data integrity and performance:

#### 1. Prerequisites

- PostgreSQL server running and accessible
- Python 3.7+ with required packages:
  ```bash
  pip install psycopg2-binary
  ```

#### 2. Schema Setup

First, create the PostgreSQL database and apply the schema:

```bash
# Create database
createdb bigshot_recon

# Apply schema
psql -d bigshot_recon -f config/postgresql_schema.sql
```

#### 3. Data Migration

Use the provided migration script to transfer data:

```bash
python config/migrate_sqlite_to_postgresql.py \
    --sqlite-path /path/to/sqlite/database.db \
    --postgres-host localhost \
    --postgres-port 5432 \
    --postgres-db bigshot_recon \
    --postgres-user username \
    --postgres-password password
```

#### 4. Migration Verification

The migration script includes built-in verification:
- Compares row counts between source and destination
- Validates data integrity
- Reports any issues found

#### 5. Performance Optimization

After migration, optimize the PostgreSQL database:

```sql
-- Update table statistics
ANALYZE;

-- Reindex if necessary
REINDEX DATABASE bigshot_recon;
```

### Key Differences Between SQLite and PostgreSQL

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Auto-increment | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| Boolean type | `INTEGER` (0/1) | `BOOLEAN` |
| Timestamps | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | Same, but more precise |
| Constraints | Limited | Full support |
| Indexes | Basic | Advanced with partial indexes |

## Hierarchical Subdomain Support

### Data Structure

The schema supports hierarchical subdomain display through:

1. **Root Domain Grouping**: All subdomains for a domain are grouped by `root_domain`
2. **Full Subdomain Path**: The `subdomain` column contains the complete subdomain path
3. **Efficient Indexing**: Composite indexes enable fast hierarchical queries

### Example Hierarchical Structure

```
example.com
├── www.example.com
│   ├── stage.www.example.com
│   └── dev.www.example.com
├── api.example.com
│   ├── v1.api.example.com
│   └── v2.api.example.com
└── mail.example.com
```

### Query Patterns

#### Get all subdomains for a root domain:
```sql
SELECT subdomain, source, tags
FROM domains
WHERE root_domain = 'example.com'
ORDER BY subdomain;
```

#### Get hierarchical structure:
```sql
SELECT 
    root_domain,
    subdomain,
    source,
    tags,
    LENGTH(subdomain) - LENGTH(root_domain) - 1 AS depth
FROM domains
WHERE root_domain = 'example.com'
ORDER BY subdomain;
```

#### Count subdomains by source:
```sql
SELECT 
    root_domain,
    source,
    COUNT(*) as subdomain_count
FROM domains
GROUP BY root_domain, source
ORDER BY root_domain, subdomain_count DESC;
```

## Performance Considerations

### Index Strategy

1. **Primary Lookups**: Indexes on `root_domain` and `subdomain` for fast filtering
2. **Hierarchical Queries**: Composite index on `(root_domain, subdomain)` for tree operations
3. **Temporal Queries**: Indexes on timestamp columns for time-based analysis
4. **Source Analysis**: Index on `source` for enumeration source comparison

### Query Optimization

1. **Use Prepared Statements**: For repeated queries with parameters
2. **Limit Result Sets**: Use `LIMIT` and `OFFSET` for pagination
3. **Filter Early**: Apply `WHERE` clauses on indexed columns first
4. **Avoid SELECT ***: Only select needed columns

### Monitoring

Monitor these metrics for optimal performance:

```sql
-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'domains';

-- Table statistics
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE tablename = 'domains';
```

## Security Considerations

### Access Control

1. **Database User**: Create dedicated user with minimal privileges
2. **Connection Security**: Use SSL/TLS for database connections
3. **Password Security**: Use strong passwords and consider certificate authentication

### Data Protection

1. **Backup Strategy**: Regular backups with encryption
2. **Audit Logging**: Enable PostgreSQL audit logging
3. **Data Retention**: Implement data retention policies

## Troubleshooting

### Common Migration Issues

1. **Character Encoding**: Ensure UTF-8 encoding for international domains
2. **Large Datasets**: Use batch processing for large migrations
3. **Foreign Key Constraints**: Migrate tables in correct order
4. **Index Conflicts**: Drop and recreate indexes if needed

### Performance Issues

1. **Slow Queries**: Use `EXPLAIN ANALYZE` to identify bottlenecks
2. **Index Bloat**: Regular `REINDEX` operations
3. **Statistics**: Keep table statistics up to date with `ANALYZE`

### Data Integrity Issues

1. **Duplicate Data**: Use `ON CONFLICT` clauses for upsert operations
2. **Constraint Violations**: Validate data before insertion
3. **Orphaned Records**: Regular cleanup of orphaned foreign key references

## Future Enhancements

### Planned Schema Improvements

1. **Partitioning**: Table partitioning for large datasets
2. **Full-Text Search**: Add full-text search capabilities
3. **Materialized Views**: Pre-computed hierarchical views
4. **Temporal Tables**: Track historical changes

### API Integration

The schema is designed to support the planned API endpoints:

- Domain enumeration endpoints
- Hierarchical tree navigation
- Search and filtering capabilities
- Real-time updates via WebSocket

## Tools and Scripts

### Available Scripts

1. **migrate_sqlite_to_postgresql.py**: Complete migration tool
2. **analyze_hierarchical_support.py**: Schema analysis tool
3. **postgresql_schema.sql**: PostgreSQL schema definition

### Usage Examples

```bash
# Analyze existing SQLite database
python config/analyze_hierarchical_support.py \
    --db-path /path/to/database.db \
    --output-file analysis_report.json

# Migrate to PostgreSQL
python config/migrate_sqlite_to_postgresql.py \
    --sqlite-path /path/to/database.db \
    --postgres-db bigshot_recon \
    --postgres-user username \
    --postgres-password password
```

## Conclusion

The bigshot database schema provides a robust foundation for hierarchical subdomain enumeration and analysis. The migration tools and documentation ensure smooth transition from SQLite to PostgreSQL while maintaining data integrity and performance.

For questions or issues, refer to the troubleshooting section or create an issue in the project repository.