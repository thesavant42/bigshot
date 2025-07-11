# scripts/

This directory is intended for **standalone utility scripts** that assist with development, operations, or maintenance tasks in the `bigshot` repository. These scripts are generally not part of the core application code but serve as tools to support the project's workflow.

---

## Current Scripts

### `check_backslashes.py`
**Windows Path Escaping Linter**

A linter that scans configuration files for Windows path escaping issues. It helps identify:
- Single backslashes in JSON strings that should be double-escaped
- Over-escaped paths (quadruple backslashes) that would break at runtime
- Provides guidance on proper path handling between JSON config and runtime usage

**Usage:**
```bash
python scripts/check_backslashes.py
```

**Key Features:**
- Scans `.json` and `.cfg` files recursively in the `config/` directory
- Detects both under-escaped and over-escaped Windows paths
- Provides clear guidance on fixing path escaping issues
- Integrates with the path normalization utility in `modules/utils/path_normalization.py`

### `sync_once/`
Synchronization utility for one-time data operations.

### `populate_mock_data/`
Database seeding and mock data population utilities.

---

## What types of files belong in `scripts/`?

**Files that SHOULD go in here:**
- **One-off data migration scripts**
- **Database setup, seeding, or mock data population scripts** (such as `populate_mock_data.py`)
- **Maintenance utilities** (e.g., log rotation, cache clearing, backup, or restore tools)
- **Deployment helpers** (e.g., scripts that automate cloud resource setup, or environment bootstrapping)
- **Batch data import/export scripts**
- **Diagnostics or health-check scripts**
- **Manual job runners** (e.g., scripts that trigger a background job outside of the main app)
- **Local environment setup scripts** (installing dependencies, setting up configs, etc., if not already handled by a dedicated tool like Make or npm)
- **Linters and code quality tools** (like the path escaping linter)

**Files that should NOT go in here:**
- **Core application code** (models, controllers, business logic, etc.)
- **Reusable libraries or modules** (these belong in `src/`, `lib/`, or similar)
- **Automated tests** (these should be in `tests/`, `spec/`, or similar)
- **Static assets** (images, CSS, JS, etc.)
- **Configuration files** (e.g., YAML, JSON used by the app itself—unless they're specific to a script)

---

## Directory hierarchy and organization

- **Flat or Hierarchical?**
  - For small projects, a flat structure (all scripts in `scripts/`) is fine.
  - For larger projects or when many scripts serve different domains, consider subdirectories (e.g., `scripts/db/`, `scripts/dev/`, `scripts/deploy/`).
- **Naming conventions:** Use descriptive, action-oriented names, e.g., `sync_once.py`, `export_users_to_csv.py`, `reset_local_db.sh`.

---

## How do scripts relate to core application code?

- **Loose coupling:** Scripts may import or interact with application code, but are typically not invoked by the core app itself.
- **Support role:** Scripts exist to automate tasks that are peripheral to main application workflows.
- **No import cycles:** Avoid making scripts a dependency of core code—scripts can depend on the app, but not vice versa.

---

## Filesystem hierarchy: Should scripts mirror the application structure?

- **Generally, no:** Scripts are task-oriented, not structured by feature/module like core code.
- **Exceptions:** If scripts are tightly coupled to a specific module or subsystem, a parallel subfolder (e.g., `scripts/user/cleanup_old_users.py` if `src/user/` exists) can help with organization.
- **Keep it simple:** Flat or lightly nested hierarchies are generally best for discoverability.

---

## Summary

The `scripts/` directory is for **task-specific, standalone scripts** that help manage or develop the project, not for reusable libraries or core logic. Organize by function, and keep a clear boundary between these utilities and your main application code.

If you add or update scripts, please document their purpose and usage in this README.
