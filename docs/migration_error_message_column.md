# Database Migration: Adding error_message Column

This document describes the migration process for adding the `error_message` column to the `jobs` table.

## Background

The BigShot application initially had a jobs table without an `error_message` column. When the Job model was updated to include this column, existing databases were left with the old schema, causing `psycopg2.errors.UndefinedColumn` errors when trying to query jobs.

## Solution

A migration script has been created to safely add the missing column to existing databases.

### Script Location

```
scripts/add_error_message_column.py
```

### Usage

#### Basic Usage (SQLite)
If no database URL is specified, the script will use the default SQLite database:

```bash
python scripts/add_error_message_column.py
```

#### PostgreSQL Usage
For PostgreSQL databases, set the DATABASE_URL environment variable:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/bigshot"
python scripts/add_error_message_column.py
```

#### Alternative Environment Variable
You can also use SQLALCHEMY_DATABASE_URI:

```bash
export SQLALCHEMY_DATABASE_URI="postgresql://username:password@localhost:5432/bigshot"
python scripts/add_error_message_column.py
```

### What the Script Does

1. **Checks for existing column**: The script first verifies if the `error_message` column already exists in the `jobs` table
2. **Adds column if missing**: If the column doesn't exist, it executes `ALTER TABLE jobs ADD COLUMN error_message TEXT`
3. **Verifies success**: After the migration, it confirms the column was added successfully
4. **Safe operation**: If the column already exists, the script exits successfully without making any changes

### Output

#### Successful Migration (column added)
```
2025-07-19 08:47:22,933 - INFO - Starting jobs table migration: adding error_message column
2025-07-19 08:47:22,933 - INFO - Using database: sqlite:////path/to/database.db
2025-07-19 08:47:22,941 - INFO - Database connection successful
2025-07-19 08:47:22,942 - INFO - Adding error_message column to jobs table...
2025-07-19 08:47:22,942 - INFO - Executing SQL: ALTER TABLE jobs ADD COLUMN error_message TEXT
2025-07-19 08:47:22,943 - INFO - Successfully added error_message column to jobs table
2025-07-19 08:47:22,943 - INFO - ✓ Verification successful: error_message column exists
2025-07-19 08:47:22,944 - INFO - ✓ Migration completed successfully
```

#### Column Already Exists
```
2025-07-19 08:47:01,745 - INFO - Starting jobs table migration: adding error_message column
2025-07-19 08:47:01,745 - INFO - Using database: sqlite:///instance/bigshot.db
2025-07-19 08:47:01,754 - INFO - Database connection successful
2025-07-19 08:47:01,755 - INFO - Column error_message already exists in jobs table
2025-07-19 08:47:01,755 - INFO - ✓ Verification successful: error_message column exists
2025-07-19 08:47:01,755 - INFO - ✓ Migration completed successfully
```

### Database Support

The script supports:
- **PostgreSQL** (primary production database)
- **SQLite** (development database)  
- **MySQL** (basic support)

### Error Handling

- **Database connection errors**: Script exits with code 1 and logs the error
- **Column already exists**: Script detects this and skips the migration
- **SQL errors**: Script catches and logs SQL execution errors
- **Verification failure**: Script reports if the column addition cannot be verified

### Integration with CI/CD

This migration can be run as part of deployment scripts:

```bash
# In your deployment script
echo "Running database migrations..."
python scripts/add_error_message_column.py
if [ $? -eq 0 ]; then
    echo "Migration completed successfully"
else
    echo "Migration failed!"
    exit 1
fi
```

### Testing

The migration script includes comprehensive tests in `tests/test_migration_script.py`:

- Tests adding column to database without it
- Tests handling database that already has the column  
- Tests error handling for invalid database connections
- Tests script file existence and permissions

Run the tests with:
```bash
python -m pytest tests/test_migration_script.py -v
```

## When to Run This Migration

Run this migration when:

1. **Upgrading from older versions** that didn't have the error_message column
2. **Setting up existing databases** that were created before this column was added
3. **Getting psycopg2.errors.UndefinedColumn errors** mentioning jobs.error_message

## Manual Verification

After running the migration, you can verify the column exists:

### PostgreSQL
```sql
\d jobs
-- or
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'jobs' AND column_name = 'error_message';
```

### SQLite  
```sql
PRAGMA table_info(jobs);
```

You should see `error_message` listed as a TEXT column in the jobs table.