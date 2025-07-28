#!/bin/bash
# -----------------------------------------------------------------------------
# clone_schema.sh
#
# Copies a PostgreSQL schema (structure + data) to a new schema within
# the same database by dumping, renaming, and restoring the schema.
#
# This script:
#   1. Dumps the original schema using pg_dump
#   2. Replaces all schema references with the new schema name
#   3. Creates the new schema in the database
#   4. Loads the modified SQL into the new schema
#
# Requires:
#   - PostgreSQL CLI tools (pg_dump, psql)
#   - sed
#
# Usage:
#   ./clone_schema.sh
# -----------------------------------------------------------------------------

# 🛠️ CONFIGURATION VARIABLES — update these as needed
SRC_SCHEMA="satellite_tracker_new"
DEST_SCHEMA="satellite_tracker_demo1"
DB_NAME="tony_home_tracker"
DB_USER="postgres"
OUTPUT_SQL="schema_clone.sql"

# 🚨 Abort on any error
set -e

echo "🔄 Dumping schema: $SRC_SCHEMA from database: $DB_NAME..."

# Step 1: Dump the source schema (structure + data)
pg_dump -U "$DB_USER" -d "$DB_NAME" -n "$SRC_SCHEMA" > "$OUTPUT_SQL"

echo "✅ Dump complete: $OUTPUT_SQL"

# Step 2: Replace schema name in the SQL file
MODIFIED_SQL="${OUTPUT_SQL%.sql}_${DEST_SCHEMA}.sql"

echo "🛠️ Replacing schema name '$SRC_SCHEMA' with '$DEST_SCHEMA' in SQL file..."

# Use word-boundary match to avoid over-replacing similar names
sed "s/\\b$SRC_SCHEMA\\b/$DEST_SCHEMA/g" "$OUTPUT_SQL" > "$MODIFIED_SQL"

echo "✅ Schema name replaced: $MODIFIED_SQL"

# Step 3: Create the new schema in the database
echo "📦 Creating new schema '$DEST_SCHEMA' in database '$DB_NAME'..."
psql -U "$DB_USER" -d "$DB_NAME" -c "CREATE SCHEMA IF NOT EXISTS $DEST_SCHEMA;"

# Step 4: Restore the modified SQL into the new schema
echo "📥 Importing modified SQL into schema '$DEST_SCHEMA'..."
psql -U "$DB_USER" -d "$DB_NAME" -f "$MODIFIED_SQL"

echo "✅ Clone complete: '$SRC_SCHEMA' → '$DEST_SCHEMA'"

# Optional cleanup
# rm "$OUTPUT_SQL" "$MODIFIED_SQL"
