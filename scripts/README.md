# Migration Scripts

This directory contains database migration scripts for the BigShot application.

## Available Scripts

### add_error_message_column.py

**Purpose**: Adds the `error_message` column to the `jobs` table for existing databases.

**When to use**: 
- When upgrading from versions that didn't have the error_message column
- When getting `psycopg2.errors.UndefinedColumn` errors about jobs.error_message
- When setting up existing databases

**Usage**:
```bash
# PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/bigshot"
python scripts/add_error_message_column.py

# SQLite (default)
python scripts/add_error_message_column.py
```

**Safety**: 
- Safe to run multiple times
- Checks if column exists before making changes
- Provides detailed logging and verification

**Documentation**: See `docs/migration_error_message_column.md` for detailed information.

## Running Migrations

### Development (SQLite)
```bash
python scripts/add_error_message_column.py
```

### Production (PostgreSQL)
```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
python scripts/add_error_message_column.py
```

### Docker/Docker Compose
```bash
# Using docker-compose
docker-compose exec backend python scripts/add_error_message_column.py

# Using docker run
docker run --rm -e DATABASE_URL="postgresql://..." bigshot-backend python scripts/add_error_message_column.py
```

## Testing Migrations

All migration scripts include comprehensive tests:

```bash
# Test specific migration
python -m pytest tests/test_migration_script.py -v

# Test all migrations
python -m pytest tests/ -k migration -v
```

## Adding New Migrations

When adding new migration scripts:

1. Create the script in this directory
2. Follow the pattern of existing scripts (logging, error handling, verification)
3. Add comprehensive tests in `tests/test_migration_*.py`
4. Document the migration in `docs/`
5. Update this README

## Migration Best Practices

- **Always backup** your database before running migrations
- **Test migrations** on a copy of production data first
- **Run migrations** during maintenance windows for production
- **Verify results** after migration completion
- **Monitor logs** for any errors or warnings