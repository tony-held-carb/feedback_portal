import os
from sqlalchemy import create_engine, inspect, text

uri = os.environ.get('DATABASE_URI')
print(f"Using DB URI: {uri}")

if not uri:
    print("DATABASE_URI environment variable is not set!")
    exit(1)

engine = create_engine(uri)

with engine.connect() as conn:
    version = conn.execute(text("SELECT version();")).scalar()
    current_db = conn.execute(text("SELECT current_database();")).scalar()
    search_path = conn.execute(text("SHOW search_path;")).scalar()
    print(f"Postgres version: {version}")
    print(f"Current database: {current_db}")
    print(f"Search path: {search_path}")

inspector = inspect(engine)
for table in ["uploaded_files", "portal_updates"]:
    print(f"\nColumns for table '{table}':")
    try:
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"  {col['name']} ({col['type']})")
    except Exception as e:
        print(f"  Could not inspect table '{table}': {e}") 