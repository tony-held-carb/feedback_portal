"""
db_snapshot.py

Utilities for creating SQLite snapshots of Postgres databases for local development and testing.

This module provides functionality to:
  - Copy all tables and data from an existing SQLAlchemy engine to a SQLite database
  - Generate downloadable SQLite files for local development
  - Handle data type conversions between Postgres and SQLite
  - Gracefully handle PostgreSQL/PostGIS features that don't exist in SQLite
"""
import os
import logging
import tempfile
import shutil
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path

from sqlalchemy import create_engine, MetaData, inspect, text, Column, Table
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import CreateTable

logger = logging.getLogger(__name__)


def clean_metadata_for_sqlite(metadata: MetaData) -> Tuple[MetaData, List[str]]:
  """
  Clean PostgreSQL-specific features from metadata to make it SQLite-compatible.

  Args:
    metadata (MetaData): Original SQLAlchemy metadata from PostgreSQL.

  Returns:
    Tuple[MetaData, List[str]]: (cleaned metadata, list of warnings)

  Notes:
    - Removes PostgreSQL sequences from DEFAULT values
    - Converts PostgreSQL-specific data types to SQLite-compatible types
    - Removes PostgreSQL-specific constraints and functions
    - Handles GEOMETRY types by converting to TEXT
    - Logs all conversions as warnings for transparency
  """
  warnings = []
  
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
          
          # Check if it's a DefaultClause with TextClause
          if hasattr(default_obj, 'arg') and hasattr(default_obj.arg, 'text'):
            # Extract the actual SQL text from the TextClause
            actual_sql = default_obj.arg.text
            logger.info(f"    Actual SQL: {actual_sql}")
            
            # Check for PostgreSQL sequences
            if any(keyword in actual_sql.lower() for keyword in ['nextval(', 'currval(', '::regclass']):
              warning_msg = f"Removing PostgreSQL sequence default from column {column.name} ({default_attr}): {actual_sql}"
              logger.warning(warning_msg)
              warnings.append(warning_msg)
              setattr(column, default_attr, None)
            
            # Check for PostgreSQL now() function
            elif 'now()' in actual_sql.lower():
              warning_msg = f"Converting PostgreSQL now() to SQLite CURRENT_TIMESTAMP for column {column.name} ({default_attr})"
              logger.warning(warning_msg)
              warnings.append(warning_msg)
              # Replace now() with CURRENT_TIMESTAMP
              new_default = actual_sql.replace('now()', 'CURRENT_TIMESTAMP')
              logger.info(f"    New default: {new_default}")
              # Create a new DefaultClause with the corrected SQL
              from sqlalchemy import text as sql_text
              setattr(column, default_attr, text(new_default))
            
            # Check for other PostgreSQL timestamp functions
            elif any(func in actual_sql.lower() for func in ['current_timestamp(', 'clock_timestamp(', 'statement_timestamp(']):
              warning_msg = f"Converting PostgreSQL timestamp function to SQLite CURRENT_TIMESTAMP for column {column.name} ({default_attr})"
              logger.warning(warning_msg)
              warnings.append(warning_msg)
              new_default = 'CURRENT_TIMESTAMP'
              logger.info(f"    New default: {new_default}")
              from sqlalchemy import text as sql_text
              setattr(column, default_attr, text(new_default))
          
          elif any(keyword in default_str.lower() for keyword in ['nextval(', 'currval(', '::regclass', 'now()']):
            warning_msg = f"Removing PostgreSQL-specific default from column {column.name} ({default_attr}): {default_str}"
            logger.warning(warning_msg)
            warnings.append(warning_msg)
            setattr(column, default_attr, None)
      
      # Convert PostgreSQL-specific types to SQLite-compatible types
      if hasattr(column.type, '__class__'):
        type_name = column.type.__class__.__name__
        
        if type_name in ['GEOMETRY', 'GEOGRAPHY']:
          warning_msg = f"Converting {type_name} to TEXT for column {column.name} (PostGIS not supported in SQLite)"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          from sqlalchemy import Text
          column.type = Text()
        
        elif type_name in ['UUID']:
          warning_msg = f"Converting UUID to TEXT for column {column.name} (UUID not natively supported in SQLite)"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          from sqlalchemy import Text
          column.type = Text()
        
        elif type_name in ['JSON', 'JSONB']:
          warning_msg = f"Converting {type_name} to TEXT for column {column.name} (JSONB not natively supported in SQLite)"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          from sqlalchemy import Text
          column.type = Text()
        
        elif type_name in ['ARRAY']:
          warning_msg = f"Converting ARRAY to TEXT for column {column.name} (ARRAY not supported in SQLite)"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          from sqlalchemy import Text
          column.type = Text()
        
        elif type_name in ['DOUBLE_PRECISION']:
          warning_msg = f"Converting DOUBLE_PRECISION to REAL for column {column.name} (SQLite uses REAL for doubles)"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          from sqlalchemy import Float
          column.type = Float()
        
        elif type_name in ['NUMERIC']:
          warning_msg = f"Converting NUMERIC to REAL for column {column.name} (SQLite uses REAL for numeric)"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          from sqlalchemy import Float
          column.type = Float()
    
    # Remove PostgreSQL-specific constraints
    constraints_to_remove = []
    for constraint in table.constraints:
      try:
        if hasattr(constraint, 'sqltext'):
          constraint_sql = str(constraint.sqltext)
          if any(keyword in constraint_sql.upper() for keyword in ['REGCLASS', 'NEXTVAL', 'CURRVAL']):
            warning_msg = f"Removing PostgreSQL-specific constraint from table {table_name}: {constraint.name}"
            logger.warning(warning_msg)
            warnings.append(warning_msg)
            constraints_to_remove.append(constraint)
      except Exception:
        # Skip constraints that can't be processed
        continue
    
    for constraint in constraints_to_remove:
      table.constraints.remove(constraint)
  
  return metadata, warnings


def create_sqlite_snapshot_from_engine(
    source_engine: Engine,
    output_path: Optional[str] = None,
    include_data: bool = True
) -> Tuple[bool, str, List[str]]:
  """
  Create a SQLite snapshot from an existing SQLAlchemy engine.

  Args:
    source_engine (Engine): Source SQLAlchemy engine (Postgres).
    output_path (str, optional): Path for the output SQLite file. 
                                If None, creates a file with timestamp.
    include_data (bool): Whether to copy data (True) or just schema (False).

  Returns:
    Tuple[bool, str, List[str]]: (success, message or file path, warnings)
                     - success: True if snapshot created successfully
                     - message: Error message if failed, or file path if successful
                     - warnings: List of warnings about conversions/limitations

  Examples:
    Input: source_engine=db.engine, output_path="snapshot.sqlite"
    Output: (True, "/path/to/snapshot.sqlite", ["Converted GEOMETRY to TEXT", ...])

    Input: source_engine=db.engine, output_path=None
    Output: (True, "/tmp/arb_snapshot_20250709_143022.sqlite", ["Removed sequence defaults", ...])
  """
  warnings = []
  
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
    metadata, cleaning_warnings = clean_metadata_for_sqlite(metadata)
    warnings.extend(cleaning_warnings)
    
    # Create tables in SQLite with comprehensive error handling
    table_creation_warnings = create_tables_in_sqlite(sqlite_engine, metadata)
    warnings.extend(table_creation_warnings)
    
    logger.info(f"Created {len(metadata.tables)} tables in SQLite")
    
    if include_data:
      # Copy data from source engine to SQLite
      data_copy_warnings = copy_data_between_engines(source_engine, sqlite_engine, metadata)
      warnings.extend(data_copy_warnings)
    
    logger.info(f"SQLite snapshot created successfully: {output_path}")
    return True, output_path, warnings
    
  except SQLAlchemyError as e:
    error_msg = f"Database error creating snapshot: {e}"
    logger.error(error_msg)
    return False, error_msg, warnings
  except Exception as e:
    error_msg = f"Unexpected error creating snapshot: {e}"
    logger.error(error_msg)
    return False, error_msg, warnings


def create_tables_in_sqlite(sqlite_engine: Engine, metadata: MetaData) -> List[str]:
  """
  Create tables in SQLite with comprehensive error handling for PostgreSQL/PostGIS features.

  Args:
    sqlite_engine (Engine): SQLite engine to create tables in.
    metadata (MetaData): Cleaned metadata with SQLite-compatible types.

  Returns:
    List[str]: List of warnings about table creation issues.
  """
  warnings = []
  
  with sqlite_engine.connect() as conn:
    # Disable foreign key constraints temporarily
    conn.execute(text("PRAGMA foreign_keys=OFF"))
    
    # Create tables one by one to handle any PostgreSQL/PostGIS-specific issues
    for table_name, table in metadata.tables.items():
      try:
        logger.info(f"Creating table: {table_name}")
        logger.info(f"  Table columns: {[col.name for col in table.columns]}")
        logger.info(f"  Table constraints: {[c.name for c in table.constraints]}")
        
        # Log the CREATE TABLE SQL that will be generated
        try:
          create_sql = str(table.compile(compile_kwargs={"literal_binds": True}))
          logger.info(f"  Generated SQL: {create_sql}")
        except Exception as sql_error:
          logger.warning(f"  Could not generate SQL preview: {sql_error}")
        
        table.create(conn, checkfirst=False)
        logger.info(f"Successfully created table: {table_name}")
        
      except Exception as e:
        error_msg = str(e)
        logger.warning(f"Error creating table {table_name}: {error_msg}")
        
        # Check for specific PostgreSQL/PostGIS issues
        if any(keyword in error_msg.lower() for keyword in [
          'recovergeometrycolumn', 'addgeometrycolumn', 'postgis', 'geometry',
          'nextval', 'currval', 'regclass', 'sequence', 'serial'
        ]):
          warning_msg = f"PostgreSQL/PostGIS feature detected in table {table_name}, using simplified creation"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          
          # Try creating a simplified version of the table
          try:
            simplified_warnings = create_simplified_table(conn, table_name, table)
            warnings.extend(simplified_warnings)
          except Exception as e2:
            error_msg2 = str(e2)
            if "already exists" in error_msg2.lower():
              warning_msg2 = f"Table {table_name} already exists, skipping creation"
              logger.warning(warning_msg2)
              warnings.append(warning_msg2)
            else:
              logger.error(f"Failed to create table {table_name} even with simplified approach: {e2}")
              raise
        else:
          # Unknown error, re-raise
          raise
  
  return warnings


def create_simplified_table(conn, table_name: str, table: Table) -> List[str]:
  """
  Create a simplified table without PostgreSQL/PostGIS-specific features.

  Args:
    conn: SQLite connection.
    table_name (str): Name of the table to create.
    table (Table): SQLAlchemy table object.

  Returns:
    List[str]: List of warnings about simplifications made.
  """
  warnings = []
  
  # Create a simplified version of the table
  columns_sql = []
  column_mapping = {}  # Track original -> safe column name mappings
  
  for column in table.columns:
    # Convert column type to SQLite-compatible string
    col_type = get_sqlite_column_type(column)
    nullable = "" if column.nullable else " NOT NULL"
    
    # Handle invalid SQLite column names (containing colons, spaces, etc.)
    safe_column_name = column.name
    if ':' in column.name or ' ' in column.name or column.name.startswith('_'):
      # Replace colons with underscores and handle other invalid characters
      safe_column_name = column.name.replace(':', '_').replace(' ', '_')
      if safe_column_name.startswith('_'):
        safe_column_name = 'col_' + safe_column_name[1:]
      
      warning_msg = f"Renamed column '{column.name}' to '{safe_column_name}' (invalid SQLite column name)"
      logger.warning(warning_msg)
      warnings.append(warning_msg)
      
      # Store the mapping for data copying
      column_mapping[column.name] = safe_column_name
    
    columns_sql.append(f'"{safe_column_name}" {col_type}{nullable}')
  
  create_sql = f"CREATE TABLE {table_name} ({', '.join(columns_sql)})"
  logger.info(f"Creating simplified table {table_name}: {create_sql}")
  
  try:
    conn.execute(text(create_sql))
    warning_msg = f"Created simplified table {table_name} (PostgreSQL features removed)"
    warnings.append(warning_msg)
    
    # Store column mapping in table metadata for data copying
    if hasattr(table, '_column_mapping'):
      table._column_mapping.update(column_mapping)
    else:
      table._column_mapping = column_mapping
      
  except Exception as e:
    if "already exists" in str(e).lower():
      # Table was partially created, drop and recreate
      try:
        conn.execute(text(f"DROP TABLE {table_name}"))
        conn.execute(text(create_sql))
        warning_msg = f"Recreated simplified table {table_name} after cleanup"
        warnings.append(warning_msg)
        
        # Store column mapping in table metadata for data copying
        if hasattr(table, '_column_mapping'):
          table._column_mapping.update(column_mapping)
        else:
          table._column_mapping = column_mapping
          
      except Exception as e2:
        raise Exception(f"Failed to recreate table {table_name}: {e2}")
    else:
      raise
  
  return warnings


def get_sqlite_column_type(column: Column) -> str:
  """
  Get SQLite-compatible column type string.

  Args:
    column (Column): SQLAlchemy column object.

  Returns:
    str: SQLite-compatible type string.
  """
  type_name = column.type.__class__.__name__
  
  # Map PostgreSQL types to SQLite types
  type_mapping = {
    'INTEGER': 'INTEGER',
    'BIGINT': 'INTEGER',
    'SMALLINT': 'INTEGER',
    'SERIAL': 'INTEGER',
    'BIGSERIAL': 'INTEGER',
    'SMALLSERIAL': 'INTEGER',
    'VARCHAR': 'TEXT',
    'CHAR': 'TEXT',
    'TEXT': 'TEXT',
    'FLOAT': 'REAL',
    'DOUBLE_PRECISION': 'REAL',
    'NUMERIC': 'REAL',
    'DECIMAL': 'REAL',
    'REAL': 'REAL',
    'TIMESTAMP': 'TEXT',
    'DATE': 'TEXT',
    'TIME': 'TEXT',
    'BOOLEAN': 'INTEGER',
    'UUID': 'TEXT',
    'JSON': 'TEXT',
    'JSONB': 'TEXT',
    'ARRAY': 'TEXT',
    'GEOMETRY': 'TEXT',
    'GEOGRAPHY': 'TEXT',
  }
  
  return type_mapping.get(type_name, 'TEXT')


def copy_data_between_engines(
    source_engine: Engine,
    target_engine: Engine,
    metadata: MetaData
) -> List[str]:
  """
  Copy all data from source engine to target engine for all tables in metadata.

  Args:
    source_engine (Engine): Source SQLAlchemy engine (Postgres).
    target_engine (Engine): Target SQLAlchemy engine (SQLite).
    metadata (MetaData): SQLAlchemy metadata containing table definitions.

  Returns:
    List[str]: List of warnings about data copying issues.

  Notes:
    - Handles data type conversions between Postgres and SQLite.
    - Processes tables in dependency order to handle foreign key constraints.
    - Logs progress for large datasets.
    - Gracefully handles conversion errors with warnings.
  """
  warnings = []
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
        data_dicts = []
        for row in rows:
          try:
            # Convert row data to SQLite-compatible format
            converted_row = convert_row_for_sqlite(row, columns, table)
            data_dicts.append(converted_row)
          except Exception as e:
            warning_msg = f"Failed to convert row in table {table_name}: {e}"
            logger.warning(warning_msg)
            warnings.append(warning_msg)
            continue
        
        if not data_dicts:
          warning_msg = f"No valid data to copy for table {table_name}"
          logger.warning(warning_msg)
          warnings.append(warning_msg)
          continue
        
        # Insert in batches to handle large datasets
        batch_size = 1000
        for i in range(0, len(data_dicts), batch_size):
          batch = data_dicts[i:i + batch_size]
          try:
            target_conn.execute(table.insert(), batch)
            target_conn.commit()
          except Exception as e:
            warning_msg = f"Failed to insert batch {i//batch_size + 1} for table {table_name}: {e}"
            logger.warning(warning_msg)
            warnings.append(warning_msg)
            continue
        
        logger.info(f"  Successfully copied {len(data_dicts)} rows to {table_name}")
    
    except Exception as e:
      warning_msg = f"Error copying data for table {table_name}: {e}"
      logger.warning(warning_msg)
      warnings.append(warning_msg)
      # Continue with other tables even if one fails
      continue
  
  return warnings


def convert_row_for_sqlite(row, columns, table: Table) -> Dict:
  """
  Convert a row of data to SQLite-compatible format.

  Args:
    row: Raw row data from PostgreSQL.
    columns: Column names.
    table (Table): SQLAlchemy table object.

  Returns:
    Dict: Converted row data.
  """
  converted_row = {}
  
  for i, column_name in enumerate(columns):
    value = row[i]
    
    # Handle None values
    if value is None:
      converted_row[column_name] = None
      continue
    
    # Get column type for conversion
    column = table.columns.get(column_name)
    if column is None:
      # Column not found in table, skip
      continue
    
    type_name = column.type.__class__.__name__
    
    try:
      # Convert based on type
      if type_name in ['GEOMETRY', 'GEOGRAPHY']:
        # Convert geometry to WKT string
        converted_row[column_name] = str(value) if value else None
      elif type_name in ['UUID']:
        # Convert UUID to string
        converted_row[column_name] = str(value) if value else None
      elif type_name in ['JSON', 'JSONB']:
        # Convert JSON to string
        if isinstance(value, (dict, list)):
          import json
          converted_row[column_name] = json.dumps(value)
        else:
          converted_row[column_name] = str(value) if value else None
      elif type_name in ['ARRAY']:
        # Convert array to string
        converted_row[column_name] = str(value) if value else None
      elif type_name in ['TIMESTAMP']:
        # Convert timestamp to string
        converted_row[column_name] = str(value) if value else None
      elif type_name in ['BOOLEAN']:
        # Convert boolean to integer
        converted_row[column_name] = 1 if value else 0
      else:
        # Use value as-is for compatible types
        converted_row[column_name] = value
    except Exception as e:
      # If conversion fails, use string representation
      converted_row[column_name] = str(value) if value else None
  
  return converted_row


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

  Examples:
    Input : "snapshot.sqlite"
    Output: {
      'exists': True,
      'size_bytes': 1048576,
      'created_time': '2025-07-09 14:30:22',
      'table_count': 15,
      'total_rows': 1250
    }
  """
  try:
    path = Path(sqlite_path)
    if not path.exists():
      return {'exists': False}
    
    # Get basic file info
    stat = path.stat()
    created_time = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    
    # Get database info
    engine = create_engine(f"sqlite:///{sqlite_path}")
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    total_rows = 0
    
    for table in tables:
      try:
        with engine.connect() as conn:
          result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
          count = result.scalar()
          total_rows += count
      except Exception:
        # Skip tables that can't be counted
        continue
    
    return {
      'exists': True,
      'size_bytes': stat.st_size,
      'created_time': created_time,
      'table_count': len(tables),
      'total_rows': total_rows
    }
    
  except Exception as e:
    logger.error(f"Error getting snapshot info: {e}")
    return {'exists': False, 'error': str(e)}


def cleanup_old_snapshots(directory: str, max_age_hours: int = 24) -> int:
  """
  Clean up old SQLite snapshot files.

  Args:
    directory (str): Directory containing snapshot files.
    max_age_hours (int): Maximum age in hours before deletion.

  Returns:
    int: Number of files deleted.

  Examples:
    Input : directory="snapshots", max_age_hours=24
    Output: 3
  """
  try:
    path = Path(directory)
    if not path.exists():
      return 0
    
    cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
    deleted_count = 0
    
    for file_path in path.glob("*.sqlite"):
      if file_path.stat().st_mtime < cutoff_time:
        try:
          file_path.unlink()
          deleted_count += 1
          logger.info(f"Deleted old snapshot: {file_path}")
        except Exception as e:
          logger.error(f"Failed to delete {file_path}: {e}")
    
    return deleted_count
    
  except Exception as e:
    logger.error(f"Error cleaning up snapshots: {e}")
    return 0 