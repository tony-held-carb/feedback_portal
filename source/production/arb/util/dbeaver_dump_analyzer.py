"""
dbeaver_dump_analyzer.py

Utility functions to analyze DBeaver SQL dump files (plain .sql files).

This module provides tools to:
  - Read and parse plain SQL dump files from DBeaver
  - Extract table schemas and data statements
  - Analyze table structures and data types
  - Provide detailed information about the dump contents
  - Help with conversion to SQLite format

Note: This module handles plain text SQL files, not gzipped files.
"""
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def read_sql_dump(file_path: str) -> str:
  """
  Read a plain SQL dump file from DBeaver.

  Args:
    file_path (str): Path to the .sql file.

  Returns:
    str: SQL content from the dump file.

  Raises:
    FileNotFoundError: If the file doesn't exist.
    OSError: If the file cannot be read.

  Examples:
    Input : "database_snapshots/dump-plumetracker-202507091443.sql"
    Output: "CREATE TABLE ... INSERT INTO ..." (SQL content)
  """
  dump_path = Path(file_path)
  if not dump_path.exists():
    raise FileNotFoundError(f"SQL dump file not found: {file_path}")
  
  try:
    with open(dump_path, 'r', encoding='utf-8') as f:
      return f.read()
  except Exception as e:
    raise OSError(f"Failed to read SQL dump {file_path}: {e}")


def extract_table_schemas_dbeaver(sql_content: str) -> Dict[str, Dict]:
  """
  Extract table creation statements from DBeaver SQL dump.

  Args:
    sql_content (str): SQL content from the DBeaver dump.

  Returns:
    Dict[str, Dict]: Mapping of table names to their schema information.
      Each table dict contains:
      - 'create_statement': Full CREATE TABLE statement
      - 'columns': List of column definitions
      - 'constraints': List of constraint definitions
      - 'indexes': List of index definitions

  Examples:
    Input : "CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);"
    Output: {
      'users': {
        'create_statement': 'CREATE TABLE users...',
        'columns': ['id SERIAL PRIMARY KEY', 'name TEXT'],
        'constraints': [],
        'indexes': []
      }
    }
  """
  # DBeaver often includes schema prefixes and additional formatting
  # Look for CREATE TABLE statements with or without schema prefixes
  create_table_pattern = r'CREATE TABLE\s+(?:[^.]*\.)?([^\s(]+)\s*\(([^)]+)\);'
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
      'constraints': constraints,
      'indexes': []
    }
  
  return schemas


def extract_data_statements_dbeaver(sql_content: str) -> Dict[str, List[str]]:
  """
  Extract INSERT statements from DBeaver SQL dump.

  Args:
    sql_content (str): SQL content from the DBeaver dump.

  Returns:
    Dict[str, List[str]]: Mapping of table names to lists of INSERT statements.

  Examples:
    Input : "INSERT INTO users VALUES (1, 'John'); INSERT INTO users VALUES (2, 'Jane');"
    Output: {'users': ['INSERT INTO users VALUES (1, \'John\');', 'INSERT INTO users VALUES (2, \'Jane\');']}
  """
  # DBeaver INSERT statements may include schema prefixes
  insert_pattern = r'INSERT INTO\s+(?:[^.]*\.)?([^\s(]+)\s*[^;]+;'
  matches = re.finditer(insert_pattern, sql_content, re.IGNORECASE | re.DOTALL)
  
  data_statements = {}
  for match in matches:
    table_name = match.group(1).strip()
    insert_statement = match.group(0).strip()
    
    if table_name not in data_statements:
      data_statements[table_name] = []
    data_statements[table_name].append(insert_statement)
  
  return data_statements


def extract_indexes_dbeaver(sql_content: str) -> Dict[str, List[str]]:
  """
  Extract CREATE INDEX statements from DBeaver SQL dump.

  Args:
    sql_content (str): SQL content from the DBeaver dump.

  Returns:
    Dict[str, List[str]]: Mapping of table names to lists of index statements.

  Examples:
    Input : "CREATE INDEX idx_users_name ON users (name);"
    Output: {'users': ['CREATE INDEX idx_users_name ON users (name);']}
  """
  # Look for CREATE INDEX statements
  index_pattern = r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+[^O]*ON\s+(?:[^.]*\.)?([^\s(]+)\s*\([^)]+\);'
  matches = re.finditer(index_pattern, sql_content, re.IGNORECASE | re.DOTALL)
  
  indexes = {}
  for match in matches:
    table_name = match.group(1).strip()
    index_statement = match.group(0).strip()
    
    if table_name not in indexes:
      indexes[table_name] = []
    indexes[table_name].append(index_statement)
  
  return indexes


def analyze_dbeaver_dump(file_path: str) -> Dict:
  """
  Comprehensive analysis of a DBeaver SQL dump file.

  Args:
    file_path (str): Path to the .sql file.

  Returns:
    Dict: Analysis results containing:
      - 'file_info': Basic file information
      - 'tables': Table schema information
      - 'data_summary': Summary of data statements
      - 'indexes': Index information
      - 'sqlite_compatibility': Notes on SQLite compatibility

  Examples:
    Input : "database_snapshots/dump-plumetracker-202507091443.sql"
    Output: {
      'file_info': {'size_mb': 5.2, 'tables_found': 8},
      'tables': {...},
      'data_summary': {...},
      'indexes': {...},
      'sqlite_compatibility': ['SERIAL types need conversion', ...]
    }
  """
  dump_path = Path(file_path)
  
  # Read and parse the SQL content
  sql_content = read_sql_dump(file_path)
  schemas = extract_table_schemas_dbeaver(sql_content)
  data_statements = extract_data_statements_dbeaver(sql_content)
  indexes = extract_indexes_dbeaver(sql_content)
  
  # Analyze SQLite compatibility
  compatibility_notes = []
  for table_name, schema in schemas.items():
    for column in schema['columns']:
      if 'SERIAL' in column.upper():
        compatibility_notes.append(f"Table '{table_name}': SERIAL type needs conversion to INTEGER")
      if 'TIMESTAMP' in column.upper() and 'WITH TIME ZONE' in column.upper():
        compatibility_notes.append(f"Table '{table_name}': TIMESTAMPTZ needs conversion to TEXT or INTEGER")
      if 'UUID' in column.upper():
        compatibility_notes.append(f"Table '{table_name}': UUID type needs conversion to TEXT")
  
  return {
    'file_info': {
      'file_path': str(dump_path),
      'size_mb': dump_path.stat().st_size / (1024 * 1024),
      'tables_found': len(schemas),
      'data_statements_found': sum(len(stmts) for stmts in data_statements.values()),
      'indexes_found': sum(len(idx) for idx in indexes.values())
    },
    'tables': schemas,
    'data_summary': {
      table: {
        'insert_count': len(statements),
        'sample_insert': statements[0] if statements else None
      }
      for table, statements in data_statements.items()
    },
    'indexes': indexes,
    'sqlite_compatibility': compatibility_notes
  }


def print_dbeaver_dump_analysis(file_path: str) -> None:
  """
  Print a formatted analysis of the DBeaver SQL dump file.

  Args:
    file_path (str): Path to the .sql file.

  Examples:
    Input : "database_snapshots/dump-plumetracker-202507091443.sql"
    Output: Prints formatted analysis to console
  """
  try:
    analysis = analyze_dbeaver_dump(file_path)
    
    print("=" * 70)
    print("DBeaver SQL DUMP ANALYSIS")
    print("=" * 70)
    
    # File info
    print(f"\nFile: {analysis['file_info']['file_path']}")
    print(f"Size: {analysis['file_info']['size_mb']:.1f} MB")
    print(f"Tables found: {analysis['file_info']['tables_found']}")
    print(f"Total INSERT statements: {analysis['file_info']['data_statements_found']}")
    print(f"Total indexes: {analysis['file_info']['indexes_found']}")
    
    # Tables
    print(f"\nTables:")
    for table_name, schema in analysis['tables'].items():
      print(f"  - {table_name} ({len(schema['columns'])} columns)")
      if table_name in analysis['data_summary']:
        print(f"    Data: {analysis['data_summary'][table_name]['insert_count']} rows")
      if table_name in analysis['indexes']:
        print(f"    Indexes: {len(analysis['indexes'][table_name])}")
    
    # Sample data
    if analysis['data_summary']:
      print(f"\nSample Data (first table with data):")
      for table_name, summary in analysis['data_summary'].items():
        if summary['insert_count'] > 0:
          print(f"  Table: {table_name}")
          print(f"  Sample INSERT: {summary['sample_insert'][:100]}...")
          break
    
    # SQLite compatibility
    if analysis['sqlite_compatibility']:
      print(f"\nSQLite Compatibility Notes:")
      for note in analysis['sqlite_compatibility']:
        print(f"  - {note}")
    else:
      print(f"\nSQLite Compatibility: No major issues detected")
    
    print("=" * 70)
    
  except Exception as e:
    print(f"Error analyzing DBeaver dump file: {e}")


def get_table_details(sql_content: str, table_name: str) -> Dict:
  """
  Get detailed information about a specific table.

  Args:
    sql_content (str): SQL content from the DBeaver dump.
    table_name (str): Name of the table to analyze.

  Returns:
    Dict: Detailed table information including schema, sample data, and indexes.

  Examples:
    Input : sql_content, "users"
    Output: {
      'schema': {...},
      'sample_data': [...],
      'indexes': [...]
    }
  """
  schemas = extract_table_schemas_dbeaver(sql_content)
  data_statements = extract_data_statements_dbeaver(sql_content)
  indexes = extract_indexes_dbeaver(sql_content)
  
  return {
        'schema': schemas.get(table_name, {}),
        'sample_data': data_statements.get(table_name, [])[:3],  # First 3 rows
        'indexes': indexes.get(table_name, [])
    } 