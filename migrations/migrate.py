#!/usr/bin/env python3
"""Database migration script for upgrading to v2 schema."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask

from src.autogen_research.database import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///research.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def run_migration():
    """Run the migration."""
    with app.app_context():
        print("Starting database migration to v2...")

        # Read SQL migration file
        sql_file = Path(__file__).parent / "upgrade_v2.sql"
        if not sql_file.exists():
            print(f"Error: Migration file not found: {sql_file}")
            sys.exit(1)

        with open(sql_file) as f:
            sql = f.read()

        # Split by statements (handle multi-line)
        statements = [
            s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")
        ]

        # Execute each statement
        for statement in statements:
            try:
                print(f"Executing: {statement[:60]}...")
                db.session.execute(db.text(statement))
                db.session.commit()
                print("  ✓ Success")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                # Continue with other statements even if one fails

        print("\nMigration completed!")
        print("\nNote: If using PostgreSQL, you may need to manually adjust data types.")
        print("See upgrade_v2.sql for details.")


if __name__ == "__main__":
    run_migration()
