"""
Test for the error_message column migration script
"""

import pytest
import tempfile
import sqlite3
import os
import subprocess
from pathlib import Path


class TestErrorMessageColumnMigration:
    """Test that the migration script works correctly"""

    def test_migration_script_adds_missing_column(self):
        """Test that the migration script adds error_message column when missing"""
        # Create a temporary database without error_message column
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            # Create database with old schema (no error_message column)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create jobs table without error_message column
            cursor.execute(
                """
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    type VARCHAR(100),
                    domain VARCHAR(255),
                    status VARCHAR(50),
                    progress INTEGER,
                    result TEXT,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """
            )
            conn.commit()

            # Verify error_message column doesn't exist initially
            cursor.execute("PRAGMA table_info(jobs)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            assert (
                "error_message" not in column_names
            ), "error_message should not exist initially"
            conn.close()

            # Run the migration script
            script_path = (
                Path(__file__).parent.parent / "scripts" / "add_error_message_column.py"
            )
            env = os.environ.copy()
            env["DATABASE_URL"] = f"sqlite:///{db_path}"

            result = subprocess.run(
                ["python", str(script_path)], env=env, capture_output=True, text=True
            )

            assert result.returncode == 0, f"Migration script failed: {result.stderr}"
            output = result.stdout + result.stderr
            assert "Migration completed successfully" in output

            # Verify error_message column was added
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(jobs)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            assert (
                "error_message" in column_names
            ), f"error_message column should exist after migration. Found: {column_names}"
            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_migration_script_handles_existing_column(self):
        """Test that the migration script handles databases that already have the column"""
        # Create a temporary database with error_message column
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            # Create database with current schema (includes error_message column)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    type VARCHAR(100),
                    domain VARCHAR(255),
                    status VARCHAR(50),
                    progress INTEGER,
                    result TEXT,
                    error_message TEXT,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """
            )
            conn.commit()

            # Verify error_message column exists initially
            cursor.execute("PRAGMA table_info(jobs)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            assert (
                "error_message" in column_names
            ), "error_message should exist initially"
            conn.close()

            # Run the migration script
            script_path = (
                Path(__file__).parent.parent / "scripts" / "add_error_message_column.py"
            )
            env = os.environ.copy()
            env["DATABASE_URL"] = f"sqlite:///{db_path}"

            result = subprocess.run(
                ["python", str(script_path)], env=env, capture_output=True, text=True
            )

            assert result.returncode == 0, f"Migration script failed: {result.stderr}"
            output = result.stdout + result.stderr
            assert "already exists" in output
            assert "Migration completed successfully" in output

            # Verify error_message column still exists
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(jobs)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            assert (
                "error_message" in column_names
            ), f"error_message column should still exist. Found: {column_names}"
            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_migration_script_file_exists(self):
        """Test that the migration script file exists and is executable"""
        script_path = (
            Path(__file__).parent.parent / "scripts" / "add_error_message_column.py"
        )

        assert script_path.exists(), f"Migration script not found at {script_path}"
        assert script_path.is_file(), f"Migration script is not a file: {script_path}"

        # Check if file is executable (on Unix-like systems)
        if os.name != "nt":  # Not Windows
            assert os.access(
                script_path, os.X_OK
            ), f"Migration script is not executable: {script_path}"

    def test_migration_script_database_connection_error_handling(self):
        """Test that the migration script handles database connection errors gracefully"""
        # Run the migration script with an invalid database URL
        script_path = (
            Path(__file__).parent.parent / "scripts" / "add_error_message_column.py"
        )
        env = os.environ.copy()
        env["DATABASE_URL"] = "postgresql://invalid:invalid@nonexistent:5432/invalid"

        result = subprocess.run(
            ["python", str(script_path)], env=env, capture_output=True, text=True
        )

        # Script should handle the error gracefully and return non-zero exit code
        assert (
            result.returncode != 0
        ), "Migration script should fail with invalid database URL"
        output = result.stdout + result.stderr
        assert "Migration failed" in output or "error" in output.lower()
