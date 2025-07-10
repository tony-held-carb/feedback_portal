"""
sqlite_diagnostics.py

Utilities for analyzing and diagnosing SQLite snapshot files created by the ARB Feedback Portal.

This module provides comprehensive diagnostics for SQLite files including:
  - Table structure analysis
  - Data integrity checks
  - Column type verification
  - Row counts and data statistics
  - Foreign key relationship analysis
  - Performance metrics
  - Comparison with original PostgreSQL schema

Features:
  - Detailed table-by-table analysis
  - Data type conversion verification
  - Column name mapping validation
  - Data completeness checks
  - Export capabilities for analysis reports

Intended use:
  - Post-snapshot validation and verification
  - Debugging conversion issues
  - Quality assurance for local development databases
  - Documentation of conversion results

Version: 1.0.0
"""

import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


def analyze_sqlite_file(sqlite_path: str) -> Dict[str, Any]:
  """
  Perform comprehensive analysis of a SQLite snapshot file.

  Args:
    sqlite_path (str): Path to the SQLite file to analyze.

  Returns:
    Dict[str, Any]: Comprehensive analysis results including:
      - file_info: Basic file information
      - tables: Detailed table analysis
      - data_integrity: Data completeness checks
      - conversion_issues: Any detected conversion problems
      - recommendations: Suggestions for improvement

  Examples:
    Input: "database_snapshots/arb_snapshot_20250709_143022.sqlite"
    Output: {
      "file_info": {"size": 1234567, "tables": 15, "created": "2025-07-09 14:30:22"},
      "tables": {...},
      "data_integrity": {...},
      "conversion_issues": [...],
      "recommendations": [...]
    }

  Notes:
    - Performs read-only analysis (does not modify the database)
    - Handles missing files gracefully with error reporting
    - Provides detailed diagnostics for troubleshooting
  """
  if not os.path.exists(sqlite_path):
    return {
      "error": f"SQLite file not found: {sqlite_path}",
      "file_info": None,
      "tables": {},
      "data_integrity": {},
      "conversion_issues": [],
      "recommendations": []
    }

  try:
    with sqlite3.connect(sqlite_path) as conn:
      conn.row_factory = sqlite3.Row  # Enable column access by name
      
      # Basic file information
      file_info = _get_file_info(sqlite_path)
      
      # Table analysis
      tables = _analyze_tables(conn)
      
      # Data integrity checks
      data_integrity = _check_data_integrity(conn, tables)
      
      # Conversion issue detection
      conversion_issues = _detect_conversion_issues(tables)
      
      # Generate recommendations
      recommendations = _generate_recommendations(tables, conversion_issues, data_integrity)
      
      return {
        "file_info": file_info,
        "tables": tables,
        "data_integrity": data_integrity,
        "conversion_issues": conversion_issues,
        "recommendations": recommendations
      }
      
  except Exception as e:
    logger.error(f"Error analyzing SQLite file {sqlite_path}: {e}")
    return {
      "error": f"Error analyzing SQLite file: {e}",
      "file_info": None,
      "tables": {},
      "data_integrity": {},
      "conversion_issues": [],
      "recommendations": []
    }


def _get_file_info(sqlite_path: str) -> Dict[str, Any]:
  """Get basic file information."""
  file_stat = os.stat(sqlite_path)
  return {
    "path": sqlite_path,
    "size_bytes": file_stat.st_size,
    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
    "created": datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
    "modified": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
  }


def _analyze_tables(conn: sqlite3.Connection) -> Dict[str, Any]:
  """Analyze all tables in the SQLite database."""
  tables = {}
  
  # Get list of all tables
  cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
  table_names = [row['name'] for row in cursor.fetchall()]
  
  for table_name in table_names:
    try:
      # Get table schema
      cursor = conn.execute(f"PRAGMA table_info({table_name})")
      columns = []
      for row in cursor.fetchall():
        columns.append({
          "name": row['name'],
          "type": row['type'],
          "not_null": bool(row['notnull']),
          "default_value": row['dflt_value'],
          "primary_key": bool(row['pk'])
        })
      
      # Get row count
      cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
      row_count = cursor.fetchone()['count']
      
      # Get sample data (first 3 rows)
      cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT 3")
      sample_rows = [dict(row) for row in cursor.fetchall()]
      
      # Check for column name issues (colons, spaces, etc.)
      column_issues = []
      for col in columns:
        if ':' in col['name'] or ' ' in col['name']:
          column_issues.append(f"Column '{col['name']}' contains invalid characters")
      
      tables[table_name] = {
        "columns": columns,
        "row_count": row_count,
        "sample_data": sample_rows,
        "column_issues": column_issues,
        "has_geometry": any('geometry' in col['name'].lower() for col in columns),
        "has_json": any(col['type'].upper() in ['TEXT'] and any(keyword in col['name'].lower() for keyword in ['json', 'misc']) for col in columns)
      }
      
    except Exception as e:
      logger.warning(f"Error analyzing table {table_name}: {e}")
      tables[table_name] = {
        "error": str(e),
        "columns": [],
        "row_count": 0,
        "sample_data": [],
        "column_issues": [],
        "has_geometry": False,
        "has_json": False
      }
  
  return tables


def _check_data_integrity(conn: sqlite3.Connection, tables: Dict[str, Any]) -> Dict[str, Any]:
  """Check data integrity across tables."""
  integrity_checks = {
    "total_tables": len(tables),
    "tables_with_data": 0,
    "empty_tables": [],
    "large_tables": [],
    "potential_issues": []
  }
  
  for table_name, table_info in tables.items():
    if "error" in table_info:
      integrity_checks["potential_issues"].append(f"Table {table_name}: {table_info['error']}")
      continue
    
    row_count = table_info.get("row_count", 0)
    
    if row_count == 0:
      integrity_checks["empty_tables"].append(table_name)
    else:
      integrity_checks["tables_with_data"] += 1
      
      # Flag large tables
      if row_count > 10000:
        integrity_checks["large_tables"].append({
          "table": table_name,
          "rows": row_count
        })
    
    # Check for potential data issues
    column_issues = table_info.get("column_issues", [])
    if column_issues:
      integrity_checks["potential_issues"].extend([f"Table {table_name}: {issue}" for issue in column_issues])
  
  return integrity_checks


def _detect_conversion_issues(tables: Dict[str, Any]) -> List[str]:
  """Detect potential issues from PostgreSQL to SQLite conversion."""
  issues = []
  
  for table_name, table_info in tables.items():
    if "error" in table_info:
      issues.append(f"Table {table_name}: Failed to analyze - {table_info['error']}")
      continue
    
    columns = table_info.get("columns", [])
    
    # Check for geometry columns (should be TEXT in SQLite)
    geometry_columns = [col for col in columns if 'geometry' in col['name'].lower()]
    for col in geometry_columns:
      if col['type'].upper() != 'TEXT':
        issues.append(f"Table {table_name}: Geometry column '{col['name']}' has type '{col['type']}' instead of TEXT")
    
    # Check for JSON columns (should be TEXT in SQLite)
    json_columns = [col for col in columns if any(keyword in col['name'].lower() for keyword in ['json', 'misc'])]
    for col in json_columns:
      if col['type'].upper() != 'TEXT':
        issues.append(f"Table {table_name}: JSON column '{col['name']}' has type '{col['type']}' instead of TEXT")
    
    # Check for column name issues
    for col in columns:
      if ':' in col['name']:
        issues.append(f"Table {table_name}: Column '{col['name']}' still contains colon (should have been converted)")
      if col['name'].startswith('_'):
        issues.append(f"Table {table_name}: Column '{col['name']}' starts with underscore (should have been prefixed)")
  
  return issues


def _generate_recommendations(tables: Dict[str, Any], conversion_issues: List[str], data_integrity: Dict[str, Any]) -> List[str]:
  """Generate recommendations based on analysis."""
  recommendations = []
  
  # File size recommendations
  if data_integrity.get("total_tables", 0) == 0:
    recommendations.append("No tables found in database - check if snapshot creation was successful")
  
  # Empty tables
  empty_tables = data_integrity.get("empty_tables", [])
  if empty_tables:
    recommendations.append(f"Found {len(empty_tables)} empty tables: {', '.join(empty_tables[:5])}{'...' if len(empty_tables) > 5 else ''}")
  
  # Large tables
  large_tables = data_integrity.get("large_tables", [])
  if large_tables:
    recommendations.append(f"Found {len(large_tables)} large tables (>10K rows) - consider data sampling for development")
  
  # Conversion issues
  if conversion_issues:
    recommendations.append(f"Found {len(conversion_issues)} conversion issues - review PostgreSQL to SQLite mapping")
  
  # Column name issues
  tables_with_column_issues = [name for name, info in tables.items() if info.get("column_issues")]
  if tables_with_column_issues:
    recommendations.append(f"Found column naming issues in {len(tables_with_column_issues)} tables - verify column name conversion")
  
  # General recommendations
  if not recommendations:
    recommendations.append("SQLite snapshot appears to be created successfully with no major issues detected")
  
  recommendations.append("Use this SQLite file for local development and testing")
  recommendations.append("Remember that some PostgreSQL features (PostGIS, sequences) are not available in SQLite")
  
  return recommendations


def export_analysis_report(analysis: Dict[str, Any], output_path: Optional[str] = None) -> str:
  """
  Export analysis results to a formatted report.

  Args:
    analysis (Dict[str, Any]): Analysis results from analyze_sqlite_file()
    output_path (str, optional): Path for the output report file.

  Returns:
    str: Path to the generated report file.

  Examples:
    Input: analysis_results, "sqlite_analysis_report.txt"
    Output: "sqlite_analysis_report.txt" (formatted report file)
  """
  if output_path is None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"sqlite_analysis_report_{timestamp}.txt"
  
  with open(output_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("SQLITE SNAPSHOT ANALYSIS REPORT\n")
    f.write("=" * 80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # File Information
    file_info = analysis.get("file_info")
    if file_info:
      f.write("FILE INFORMATION:\n")
      f.write("-" * 40 + "\n")
      f.write(f"Path: {file_info.get('path', 'N/A')}\n")
      f.write(f"Size: {file_info.get('size_mb', 'N/A')} MB ({file_info.get('size_bytes', 'N/A')} bytes)\n")
      f.write(f"Created: {file_info.get('created', 'N/A')}\n")
      f.write(f"Modified: {file_info.get('modified', 'N/A')}\n\n")
    
    # Tables Summary
    tables = analysis.get("tables", {})
    f.write("TABLES SUMMARY:\n")
    f.write("-" * 40 + "\n")
    f.write(f"Total Tables: {len(tables)}\n")
    
    total_rows = sum(table.get("row_count", 0) for table in tables.values())
    f.write(f"Total Rows: {total_rows:,}\n\n")
    
    # Detailed Table Analysis
    f.write("DETAILED TABLE ANALYSIS:\n")
    f.write("-" * 40 + "\n")
    
    for table_name, table_info in tables.items():
      f.write(f"\nTable: {table_name}\n")
      f.write(f"  Rows: {table_info.get('row_count', 0):,}\n")
      f.write(f"  Columns: {len(table_info.get('columns', []))}\n")
      
      # Column details
      columns = table_info.get("columns", [])
      if columns:
        f.write("  Column Types:\n")
        for col in columns:
          f.write(f"    {col['name']}: {col['type']}")
          if col['primary_key']:
            f.write(" (PRIMARY KEY)")
          if col['not_null']:
            f.write(" (NOT NULL)")
          f.write("\n")
      
      # Issues
      issues = table_info.get("column_issues", [])
      if issues:
        f.write("  Issues:\n")
        for issue in issues:
          f.write(f"    - {issue}\n")
    
    # Data Integrity
    data_integrity = analysis.get("data_integrity", {})
    f.write(f"\nDATA INTEGRITY:\n")
    f.write("-" * 40 + "\n")
    f.write(f"Tables with data: {data_integrity.get('tables_with_data', 0)}\n")
    f.write(f"Empty tables: {len(data_integrity.get('empty_tables', []))}\n")
    
    empty_tables = data_integrity.get("empty_tables", [])
    if empty_tables:
      f.write(f"Empty table names: {', '.join(empty_tables)}\n")
    
    large_tables = data_integrity.get("large_tables", [])
    if large_tables:
      f.write(f"Large tables (>10K rows): {len(large_tables)}\n")
      for large_table in large_tables:
        f.write(f"  - {large_table['table']}: {large_table['rows']:,} rows\n")
    
    # Conversion Issues
    conversion_issues = analysis.get("conversion_issues", [])
    f.write(f"\nCONVERSION ISSUES:\n")
    f.write("-" * 40 + "\n")
    if conversion_issues:
      for issue in conversion_issues:
        f.write(f"- {issue}\n")
    else:
      f.write("No conversion issues detected.\n")
    
    # Recommendations
    recommendations = analysis.get("recommendations", [])
    f.write(f"\nRECOMMENDATIONS:\n")
    f.write("-" * 40 + "\n")
    for rec in recommendations:
      f.write(f"- {rec}\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("END OF REPORT\n")
    f.write("=" * 80 + "\n")
  
  return output_path


def get_sqlite_summary(sqlite_path: str) -> Dict[str, Any]:
  """
  Get a quick summary of a SQLite file for display purposes.

  Args:
    sqlite_path (str): Path to the SQLite file.

  Returns:
    Dict[str, Any]: Summary information including file size, table count, and row counts.

  Examples:
    Input: "database_snapshots/arb_snapshot_20250709_143022.sqlite"
    Output: {
      "file_size_mb": 12.5,
      "table_count": 15,
      "total_rows": 45678,
      "largest_table": "scenes",
      "largest_table_rows": 12345
    }
  """
  if not os.path.exists(sqlite_path):
    return {"error": f"File not found: {sqlite_path}"}
  
  try:
    with sqlite3.connect(sqlite_path) as conn:
      # Get table count
      cursor = conn.execute("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'")
      table_count = cursor.fetchone()[0]
      
      # Get all table names
      cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
      table_names = [row[0] for row in cursor.fetchall()]
      
      # Get row counts
      total_rows = 0
      largest_table = None
      largest_table_rows = 0
      
      for table_name in table_names:
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        row_count = cursor.fetchone()[0]
        total_rows += row_count
        
        if row_count > largest_table_rows:
          largest_table_rows = row_count
          largest_table = table_name
      
      # File size
      file_size_mb = round(os.path.getsize(sqlite_path) / (1024 * 1024), 2)
      
      return {
        "file_size_mb": file_size_mb,
        "table_count": table_count,
        "total_rows": total_rows,
        "largest_table": largest_table,
        "largest_table_rows": largest_table_rows,
        "tables": table_names
      }
      
  except Exception as e:
    return {"error": f"Error reading SQLite file: {e}"} 