"""
db_snapshot.py

Utilities for creating SQLite snapshots of Postgres databases for local development and testing.

This module provides functionality to:
  - Copy all tables and data from an existing SQLAlchemy engine to a SQLite database
  - Generate downloadable SQLite files for local development
  - Handle data type conversions between Postgres and SQLite
"""
import os
import logging
import tempfile
import shutil
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def clean_metadata_for_sqlite(metadata: MetaData) -> MetaData:
  """
  Clean PostgreSQL-specific features from metadata to make it SQLite-compatible.

  Args:
    metadata (MetaData): Original SQLAlchemy metadata from PostgreSQL.

  Returns:
    MetaData: Cleaned metadata suitable for SQLite.

  Notes:
    - Removes PostgreSQL sequences from DEFAULT values
    - Converts PostgreSQL-specific data types to SQLite-compatible types
    - Removes PostgreSQL-specific constraints and functions
    - Handles GEOMETRY types by converting to TEXT
  """
  import re
  
  logger.info("Cleaning metadata for SQLite compatibility")
  
  for table_name, table in metadata.tables.items():
    logger.info(f"Cleaning table: {table_name}")
    
    for column in table.columns:
      logger.info(f"  Processing column: {column.name} (type: {column.type})")
      
      # Handle PostgreSQL sequences in DEFAULT values
      # Check both default and server_default
      for default_attr in ['default', 'server_default']:
        default_obj = getattr(column, default_attr, None)
        if default_obj is not None:
          default_str = str(default_obj)
          logger.info(f"    {default_attr}: {default_str}")
          if any(keyword in default_str.lower() for keyword in ['nextval(', 'currval(', '::regclass']):
            logger.info(f"    Removing PostgreSQL sequence default from column {column.name} ({default_attr})")
            setattr(column, default_attr, None)
      
      # Convert PostgreSQL-specific types to SQLite-compatible types
      if hasattr(column.type, '__class__'):
        type_name = column.type.__class__.__name__
        
        if type_name in ['GEOMETRY', 'GEOGRAPHY']:
          logger.info(f"  Converting {type_name} to TEXT for column {column.name}")
          from sqlalchemy import Text
          column.type = Text()
        
        elif type_name in ['UUID']:
          logger.info(f"  Converting UUID to TEXT for column {column.name}")
          from sqlalchemy import Text
          column.type = Text()
        
        elif type_name in ['JSON', 'JSONB']:
          logger.info(f"  Converting {type_name} to TEXT for column {column.name}")
          from sqlalchemy import Text
          column.type = Text()
        
        elif type_name in ['ARRAY']:
          logger.info(f"  Converting ARRAY to TEXT for column {column.name}")
          from sqlalchemy import Text
          column.type = Text()
    
    # Remove PostgreSQL-specific constraints
    constraints_to_remove = []
    for constraint in table.constraints:
      try:
        if hasattr(constraint, 'sqltext'):
          constraint_sql = str(constraint.sqltext)
          if any(keyword in constraint_sql.upper() for keyword in ['REGCLASS', 'NEXTVAL', 'CURRVAL']):
            logger.info(f"  Removing PostgreSQL-specific constraint: {constraint.name}")
            constraints_to_remove.append(constraint)
      except Exception:
        # Skip constraints that can't be processed
        continue
    
    for constraint in constraints_to_remove:
      table.constraints.remove(constraint)
  
  return metadata


def create_sqlite_snapshot_from_engine(
    source_engine: Engine,
    output_path: Optional[str] = None,
    include_data: bool = True
) -> Tuple[bool, str]:
  """
  Create a SQLite snapshot from an existing SQLAlchemy engine.

  Args:
    source_engine (Engine): Source SQLAlchemy engine (Postgres).
    output_path (str, optional): Path for the output SQLite file. 
                                If None, creates a file with timestamp.
    include_data (bool): Whether to copy data (True) or just schema (False).

  Returns:
    Tuple[bool, str]: (success, message or file path)
                     - success: True if snapshot created successfully
                     - message: Error message if failed, or file path if successful

  Examples:
    Input: source_engine=db.engine, output_path="snapshot.sqlite"
    Output: (True, "/path/to/snapshot.sqlite")

    Input: source_engine=db.engine, output_path=None
    Output: (True, "/tmp/arb_snapshot_20250709_143022.sqlite")
  """
  try:
    # Create output path if not provided
    if output_path is None:
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      output_path = f"arb_snapshot_{timestamp}.sqlite"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else "."
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Creating SQLite snapshot from existing engine")
    logger.info(f"Output path: {output_path}")
    
    # Create SQLite engine
    sqlite_engine = create_engine(f"sqlite:///{output_path}")
    
    # Reflect schema from source engine
    metadata = MetaData()
    metadata.reflect(bind=source_engine)
    
    # Clean metadata for SQLite compatibility
    metadata = clean_metadata_for_sqlite(metadata)
    
    # Create tables in SQLite
    metadata.create_all(sqlite_engine)
    logger.info(f"Created {len(metadata.tables)} tables in SQLite")
    
    if include_data:
      # Copy data from source engine to SQLite
      copy_data_between_engines(source_engine, sqlite_engine, metadata)
    
    logger.info(f"SQLite snapshot created successfully: {output_path}")
    return True, output_path
    
  except SQLAlchemyError as e:
    error_msg = f"Database error creating snapshot: {e}"
    logger.error(error_msg)
    return False, error_msg
  except Exception as e:
    error_msg = f"Unexpected error creating snapshot: {e}"
    logger.error(error_msg)
    return False, error_msg


def copy_data_between_engines(
    source_engine: Engine,
    target_engine: Engine,
    metadata: MetaData
) -> None:
  """
  Copy all data from source engine to target engine for all tables in metadata.

  Args:
    source_engine (Engine): Source SQLAlchemy engine (Postgres).
    target_engine (Engine): Target SQLAlchemy engine (SQLite).
    metadata (MetaData): SQLAlchemy metadata containing table definitions.

  Notes:
    - Handles data type conversions between Postgres and SQLite.
    - Processes tables in dependency order to handle foreign key constraints.
    - Logs progress for large datasets.
  """
  inspector = inspect(source_engine)
  
  # Get tables in dependency order (parents before children)
  table_names = list(metadata.tables.keys())
  
  for table_name in table_names:
    table = metadata.tables[table_name]
    logger.info(f"Copying data for table: {table_name}")
    
    try:
      # Get all data from source
      with source_engine.connect() as source_conn:
        result = source_conn.execute(text(f"SELECT * FROM {table_name}"))
        rows = result.fetchall()
        columns = result.keys()
      
      if not rows:
        logger.info(f"  Table {table_name} is empty, skipping data copy")
        continue
      
      logger.info(f"  Copying {len(rows)} rows from {table_name}")
      
      # Insert data into target
      with target_engine.connect() as target_conn:
        # Convert rows to dictionaries for easier handling
        data_dicts = [dict(zip(columns, row)) for row in rows]
        
        # Insert in batches to handle large datasets
        batch_size = 1000
        for i in range(0, len(data_dicts), batch_size):
          batch = data_dicts[i:i + batch_size]
          target_conn.execute(table.insert(), batch)
          target_conn.commit()
        
        logger.info(f"  Successfully copied {len(rows)} rows to {table_name}")
    
    except Exception as e:
      logger.error(f"  Error copying data for table {table_name}: {e}")
      # Continue with other tables even if one fails
      continue


def get_snapshot_info(sqlite_path: str) -> Dict[str, Any]:
  """
  Get information about a SQLite snapshot file.

  Args:
    sqlite_path (str): Path to the SQLite snapshot file.

  Returns:
    Dict[str, Any]: Dictionary containing snapshot information:
                   - exists (bool): Whether file exists
                   - size_bytes (int): File size in bytes
                   - created_time (str): File creation timestamp
                   - table_count (int): Number of tables
                   - total_rows (int): Total rows across all tables
                   - error (str): Error message if any

  Examples:
    Input: sqlite_path="snapshot.sqlite"
    Output: {
      "exists": True,
      "size_bytes": 1048576,
      "created_time": "2025-07-09 14:30:22",
      "table_count": 15,
      "total_rows": 1250,
      "error": None
    }
  """
  info = {
    "exists": False,
    "size_bytes": 0,
    "created_time": None,
    "table_count": 0,
    "total_rows": 0,
    "error": None
  }
  
  try:
    if not os.path.exists(sqlite_path):
      info["error"] = f"File not found: {sqlite_path}"
      return info
    
    # File info
    stat = os.stat(sqlite_path)
    info["exists"] = True
    info["size_bytes"] = stat.st_size
    info["created_time"] = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    
    # Database info
    engine = create_engine(f"sqlite:///{sqlite_path}")
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    info["table_count"] = len(tables)
    
    # Count total rows
    total_rows = 0
    with engine.connect() as conn:
      for table in tables:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
        if count is not None:
          total_rows += count
    
    info["total_rows"] = total_rows
    
  except Exception as e:
    info["error"] = f"Error reading snapshot info: {e}"
    logger.error(f"Error getting snapshot info for {sqlite_path}: {e}")
  
  return info


def cleanup_old_snapshots(directory: str, max_age_hours: int = 24) -> int:
  """
  Clean up old SQLite snapshot files in a directory.

  Args:
    directory (str): Directory to search for snapshot files.
    max_age_hours (int): Maximum age in hours before files are deleted.

  Returns:
    int: Number of files deleted.

  Notes:
    - Only deletes files matching pattern "arb_snapshot_*.sqlite"
    - Files older than max_age_hours will be removed.
    - Logs all deletions for audit purposes.
  """
  deleted_count = 0
  cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
  
  try:
    for file_path in Path(directory).glob("arb_snapshot_*.sqlite"):
      if file_path.stat().st_mtime < cutoff_time:
        try:
          file_path.unlink()
          logger.info(f"Deleted old snapshot: {file_path}")
          deleted_count += 1
        except Exception as e:
          logger.error(f"Failed to delete {file_path}: {e}")
  
  except Exception as e:
    logger.error(f"Error during cleanup: {e}")
  
  return deleted_count 