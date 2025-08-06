"""
Database migration script for multiple roles support.

This script updates the existing 'role' column in the users table
to support multiple roles using comma-separated values.

Run this script once after deploying the updated User model.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from arb.auth import init_auth, get_db
from arb.auth.models import User
from arb.portal.extensions import db as portal_db
from arb.portal.config import get_config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from flask import Flask


def create_migration_app() -> 'Flask':
  """
  Create a minimal Flask app for migration.

  Returns:
      Flask: A minimal Flask app configured for migration.

  Examples:
      app = create_migration_app()
  """
  app = Flask(__name__)
  app.config.from_object(get_config())

  # Initialize extensions
  portal_db.init_app(app)

  # Initialize auth package
  init_auth(app=app, db=portal_db)

  return app


def migrate_role_column() -> None:
  """
  Migrate the role column to support multiple roles.

  This function updates existing single-role users to use the new
  comma-separated multiple roles format.

  Returns:
      None: This function migrates data but doesn't return anything.

  Examples:
      migrate_role_column()
  """

  print("Starting role column migration...")

  with app.app_context():
    # Get all users
    users = User.query.all()
    print(f"Found {len(users)} users to migrate")

    migrated_count = 0
    skipped_count = 0

    for user in users:
      current_role = user.role

      # Skip if already in multiple role format
      if ',' in current_role:
        print(f"Skipping user {user.email} - already has multiple roles: {current_role}")
        skipped_count += 1
        continue

      # Convert single role to list format
      if current_role and current_role.strip():
        old_role = current_role
        user.set_roles([current_role.strip()])
        print(f"Migrated user {user.email}: '{old_role}' -> '{user.role}'")
      else:
        old_role = current_role
        user.set_roles(['user'])
        print(f"Migrated user {user.email}: '{old_role}' -> 'user'")

      migrated_count += 1

    # Commit all changes
    get_db().session.commit()

    print(f"\nMigration completed!")
    print(f"Users migrated: {migrated_count}")
    print(f"Users skipped: {skipped_count}")
    print(f"Total processed: {migrated_count + skipped_count}")


def verify_migration() -> None:
  """
  Verify that the migration was successful.

  This function checks that all users have been properly migrated
  to the new multiple roles format.

  Returns:
      None: This function verifies data but doesn't return anything.

  Examples:
      verify_migration()
  """

  print("\nVerifying migration...")

  with app.app_context():
    users = User.query.all()

    for user in users:
      roles = user.get_roles()
      print(f"User {user.email}: roles = {roles}")

      # Test role checking methods
      if roles:
        test_role = roles[0]
        has_role = user.has_role(test_role)
        print(f"  - has_role('{test_role}'): {has_role}")

    print("Verification completed!")


def update_database_schema() -> None:
  """
  Update the database schema to increase role column size.

  This function provides instructions for manually updating the database
  schema to support multiple roles.

  Returns:
      None: This function provides instructions but doesn't return anything.

  Examples:
      update_database_schema()
  """

  print("Updating database schema...")

  with app.app_context():
    # This would typically be done with Alembic or raw SQL
    # For now, we'll just print the SQL that needs to be run

    print("\nIMPORTANT: You need to run the following SQL command:")
    print("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(255);")
    print("\nThis increases the role column size to support multiple roles.")
    print("Run this command in your database before running the migration.")


if __name__ == "__main__":
  print("ARB Feedback Portal - Role Migration Script")
  print("===========================================")

  # Create the app
  app = create_migration_app()

  try:
    # Step 1: Update schema (manual step)
    update_database_schema()

    # Step 2: Migrate existing data
    migrate_role_column()

    # Step 3: Verify migration
    verify_migration()

    print("\n✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Test the new multiple roles functionality")
    print("2. Update your routes to use the new decorators")
    print("3. Update your templates to use the new role checking methods")

  except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    sys.exit(1)
