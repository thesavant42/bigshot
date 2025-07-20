# Fix for Missing error_message Column in Jobs Table

## Issue Description

If you encounter an error like this when fetching jobs:

```
(psycopg2.errors.UndefinedColumn) column jobs.error_message does not exist
LINE 1: ...ess AS jobs_progress, jobs.result AS jobs_result, jobs.error...
```

This means your database was created before the `error_message` column was added to the Job model, or a migration was not applied.

## Quick Fix

Run the migration script to add the missing column:

```bash
# For PostgreSQL
export DATABASE_URL="postgresql://user:password@host:port/database"
python scripts/add_error_message_column.py

# For SQLite
export DATABASE_URL="sqlite:///path/to/your/database.db"
python scripts/add_error_message_column.py
```

## What the Script Does

The migration script (`scripts/add_error_message_column.py`) will:

1. ✅ Check if the `error_message` column already exists
2. ✅ Add the column safely if it's missing
3. ✅ Verify the column was added successfully
4. ✅ Handle both SQLite and PostgreSQL databases
5. ✅ Provide detailed logging of the process

## Verification

After running the migration, you can verify it worked by:

1. **Check the database directly:**
   ```sql
   -- PostgreSQL
   \d jobs
   
   -- SQLite
   PRAGMA table_info(jobs);
   ```

2. **Test the API:**
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:5000/api/v1/jobs
   ```

3. **Run the tests:**
   ```bash
   python -m pytest tests/test_jobs_error_message_fix.py -v
   ```

## Root Cause

This issue occurs when:
- The database was created from an older schema before the `error_message` column was added
- A database migration was interrupted or not applied
- The database was manually created without using the full schema

## Prevention

To prevent this issue in the future:
- Always use the latest schema files when creating new databases
- Run all migrations when updating an existing installation
- Use the provided migration scripts rather than manual schema changes

## Related Files

- **Migration Script**: `scripts/add_error_message_column.py`
- **Job Model**: `app/models/models.py` (line 59)
- **PostgreSQL Schema**: `config/postgresql_schema.sql` (line 38)
- **SQLite Schema**: `config/schema.sql` (line 18)
- **Tests**: `tests/test_jobs_error_message_fix.py`

## Support

If you continue to experience issues after running the migration:

1. Check the migration script output for any error messages
2. Verify database permissions allow schema modifications
3. Ensure you're using the correct DATABASE_URL format
4. Check the application logs for additional details