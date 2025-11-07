#!/usr/bin/env python3
"""
Automated Alembic Migration Script

This script automates the Alembic migration process for the Medical Report Analysis system.
It generates a new revision based on model changes and applies it to the database.

Usage:
    python scripts/migrate.py [--message "Migration message"]

Requirements:
    - Alembic must be installed
    - Database must be accessible
    - Models must be importable (ensure app is in PYTHONPATH)
"""

import subprocess
import sys
import argparse
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, check=True)
        print(f"✓ {cmd}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {cmd}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Automate Alembic migrations")
    parser.add_argument('--message', '-m', default="Auto-generated migration",
                       help="Migration message")
    parser.add_argument('--dry-run', action='store_true',
                       help="Generate migration but don't apply it")
    args = parser.parse_args()

    # Ensure we're in the project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🚀 Starting automated Alembic migration process...")

    # Step 1: Generate revision
    print("\n📝 Generating migration revision...")
    revision_cmd = f'alembic revision --autogenerate -m "{args.message}"'
    if not run_command(revision_cmd):
        print("❌ Failed to generate revision")
        sys.exit(1)

    # Step 2: Apply migration (unless dry-run)
    if not args.dry_run:
        print("\n⬆️  Applying migration to database...")
        upgrade_cmd = 'alembic upgrade head'
        if not run_command(upgrade_cmd):
            print("❌ Failed to apply migration")
            sys.exit(1)

    print("\n✅ Migration process completed successfully!")

if __name__ == "__main__":
    main()
