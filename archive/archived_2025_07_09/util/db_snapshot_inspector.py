"""
db_snapshot_inspector.py

Utility functions to inspect and work with gzipped PostgreSQL dump files.

This module provides tools to:
  - Extract and read gzipped SQL dumps
  - Parse SQL to understand schema and data structure
  - Analyze table structures and data types
  - Help with conversion to SQLite format

Note: This module focuses on inspection and analysis, not direct conversion.
"""
import gzip
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def read_gzipped_sql_dump(file_path: str) -> str:
  """
  Read and decompress a gzipped SQL dump file.

  Args:
    file_path (str): Path to the .sql.gz file.

  Returns:
    str: Decompressed SQL content.

  Raises:
    FileNotFoundError: If the file doesn't exist.
    OSError: If the file is not a valid gzip file.

  Examples:
    Input : "database_snapshots/current_satellite_tracker2507092101.sql.gz"
    Output: "CREATE TABLE ... INSERT INTO ..." (decompressed SQL)
  """
  dump_path = Path(file_path)
  if not dump_path.exists():
    raise FileNotFoundError(f"SQL dump file not found: {file_path}")
  
  try:
    with gzip.open(dump_path, 'rt', encoding='utf-8') as f:
      return f.read()
  except Exception as e:
    raise OSError(f"Failed to read gzipped SQL dump {file_path}: {e}")


def extract_table_schemas(sql_content: str) -> Dict[str, Dict]:
  """
  Extract table creation statements and parse schema information.

  Args:
    sql_content (str): Decompressed SQL content from the dump.

  Returns:
    Dict[str, Dict]: Mapping of table names to their schema information.
      Each table dict contains:
      - 'create_statement': Full CREATE TABLE statement
      - 'columns': List of column definitions
      - 'constraints': List of constraint definitions

  Examples:
    Input : "CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);"
    Output: {
      'users': {
        'create_statement': 'CREATE TABLE users...',
        'columns': ['id SERIAL PRIMARY KEY', 'name TEXT'],
        'constraints': []
      }
    }
  """
  # Find all CREATE TABLE statements
  create_table_pattern = r'CREATE TABLE\s+([^\s(]+)\s*\(([^)]+)\);'
  matches = re.finditer(create_table_pattern, sql_content, re.IGNORECASE | re.DOTALL)
  
  schemas = {}
  for match in matches:
    table_name = match.group(1).strip()
    table_body = match.group(2).strip()
    
    # Split columns and constraints
    lines = [line.strip() for line in table_body.split('\n') if line.strip()]
    columns = []
    constraints = []
    
    for line in lines:
      line = line.strip().rstrip(',')
      if line.upper().startswith(('CONSTRAINT', 'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK')):
        constraints.append(line)
      elif line and not line.startswith('--'):
        columns.append(line)
    
    schemas[table_name] = {
      'create_statement': match.group(0),
      'columns': columns,
      'constraints': constraints
    }
  
  return schemas


def extract_data_statements(sql_content: str) -> Dict[str, List[str]]:
  """
  Extract INSERT statements grouped by table name.

  Args:
    sql_content (str): Decompressed SQL content from the dump.

  Returns:
    Dict[str, List[str]]: Mapping of table names to lists of INSERT statements.

  Examples:
    Input : "INSERT INTO users VALUES (1, 'John'); INSERT INTO users VALUES (2, 'Jane');"
    Output: {'users': ['INSERT INTO users VALUES (1, \'John\');', 'INSERT INTO users VALUES (2, \'Jane\');']}
  """
  # Find all INSERT statements
  insert_pattern = r'INSERT INTO\s+([^\s(]+)\s*[^;]+;'
  matches = re.finditer(insert_pattern, sql_content, re.IGNORECASE | re.DOTALL)
  
  data_statements = {}
  for match in matches:
    table_name = match.group(1).strip()
    insert_statement = match.group(0).strip()
    
    if table_name not in data_statements:
      data_statements[table_name] = []
    data_statements[table_name].append(insert_statement)
  
  return data_statements


def analyze_dump_file(file_path: str) -> Dict:
  """
  Comprehensive analysis of a gzipped SQL dump file.

  Args:
    file_path (str): Path to the .sql.gz file.

  Returns:
    Dict: Analysis results containing:
      - 'file_info': Basic file information
      - 'tables': Table schema information
      - 'data_summary': Summary of data statements
      - 'sqlite_compatibility': Notes on SQLite compatibility

  Examples:
    Input : "database_snapshots/current_satellite_tracker2507092101.sql.gz"
    Output: {
      'file_info': {'size_mb': 17.0, 'tables_found': 5},
      'tables': {...},
      'data_summary': {...},
      'sqlite_compatibility': ['SERIAL types need conversion', ...]
    }
  """
  dump_path = Path(file_path)
  
  # Read and parse the SQL content
  sql_content = read_gzipped_sql_dump(file_path)
  schemas = extract_table_schemas(sql_content)
  data_statements = extract_data_statements(sql_content)
  
  # Analyze SQLite compatibility
  compatibility_notes = []
  for table_name, schema in schemas.items():
    for column in schema['columns']:
      if 'SERIAL' in column.upper():
        compatibility_notes.append(f"Table '{table_name}': SERIAL type needs conversion to INTEGER")
      if 'TIMESTAMP' in column.upper() and 'WITH TIME ZONE' in column.upper():
        compatibility_notes.append(f"Table '{table_name}': TIMESTAMPTZ needs conversion to TEXT or INTEGER")
  
  return {
    'file_info': {
      'file_path': str(dump_path),
      'size_mb': dump_path.stat().st_size / (1024 * 1024),
      'tables_found': len(schemas),
      'data_statements_found': sum(len(stmts) for stmts in data_statements.values())
    },
    'tables': schemas,
    'data_summary': {
      table: {
        'insert_count': len(statements),
        'sample_insert': statements[0] if statements else None
      }
      for table, statements in data_statements.items()
    },
    'sqlite_compatibility': compatibility_notes
  }


def print_dump_analysis(file_path: str) -> None:
  """
  Print a formatted analysis of the SQL dump file.

  Args:
    file_path (str): Path to the .sql.gz file.

  Examples:
    Input : "database_snapshots/current_satellite_tracker2507092101.sql.gz"
    Output: Prints formatted analysis to console
  """
  try:
    analysis = analyze_dump_file(file_path)
    
    print("=" * 60)
    print("POSTGRESQL DUMP ANALYSIS")
    print("=" * 60)
    
    # File info
    print(f"\nFile: {analysis['file_info']['file_path']}")
    print(f"Size: {analysis['file_info']['size_mb']:.1f} MB")
    print(f"Tables found: {analysis['file_info']['tables_found']}")
    print(f"Total INSERT statements: {analysis['file_info']['data_statements_found']}")
    
    # Tables
    print(f"\nTables:")
    for table_name, schema in analysis['tables'].items():
      print(f"  - {table_name} ({len(schema['columns'])} columns)")
      if table_name in analysis['data_summary']:
        print(f"    Data: {analysis['data_summary'][table_name]['insert_count']} rows")
    
    # SQLite compatibility
    if analysis['sqlite_compatibility']:
      print(f"\nSQLite Compatibility Notes:")
      for note in analysis['sqlite_compatibility']:
        print(f"  - {note}")
    else:
      print(f"\nSQLite Compatibility: No major issues detected")
    
    print("=" * 60)
    
  except Exception as e:
    print(f"Error analyzing dump file: {e}")


def get_sample_data(sql_content: str, table_name: str, limit: int = 5) -> List[str]:
  """
  Extract sample INSERT statements for a specific table.

  Args:
    sql_content (str): Decompressed SQL content.
    table_name (str): Name of the table to sample.
    limit (int): Maximum number of sample statements to return.

  Returns:
    List[str]: Sample INSERT statements for the table.

  Examples:
    Input : sql_content, "users", 3
    Output: ["INSERT INTO users VALUES (1, 'John');", "INSERT INTO users VALUES (2, 'Jane');", ...]
  """
  data_statements = extract_data_statements(sql_content)
  if table_name in data_statements:
    return data_statements[table_name][:limit]
  return [] 