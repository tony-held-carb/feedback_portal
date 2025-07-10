#!/usr/bin/env python3
"""
Quick SQLite diagnostics - shows detailed table information.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'source', 'production'))

from arb.util.sqlite_diagnostics import analyze_sqlite_file


def main():
    """Run quick diagnostics on the SQLite file."""
    logger = logging.getLogger(__name__)
    
    file_path = "database_snapshots/arb_snapshot_20250709_180106.sqlite"
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    logger.info("SQLite Snapshot Detailed Analysis")
    logger.info("=" * 60)
    logger.info(f"File: {file_path}")
    logger.info("")
    
    # Run analysis
    analysis = analyze_sqlite_file(file_path)
    
    if "error" in analysis:
        logger.error(f"Error: {analysis['error']}")
        return
    
    # Show file info
    file_info = analysis.get("file_info", {})
    logger.info(f"Size: {file_info.get('size_mb', 'N/A')} MB")
    logger.info(f"Created: {file_info.get('created', 'N/A')}")
    logger.info("")
    
    # Show all tables with details
    tables = analysis.get("tables", {})
    logger.info(f"Tables ({len(tables)} total):")
    logger.info("-" * 60)
    
    for table_name, table_info in sorted(tables.items()):
        if "error" in table_info:
            logger.error(f"{table_name}: ERROR - {table_info['error']}")
            continue
        
        row_count = table_info.get("row_count", 0)
        column_count = len(table_info.get("columns", []))
        
        # Show table summary
        status = "EMPTY" if row_count == 0 else f"{row_count:,} rows"
        logger.info(f"{table_name:<30} | {status:<15} | {column_count} columns")
        
        # Show column details for tables with data
        if row_count > 0:
            columns = table_info.get("columns", [])
            for col in columns[:5]:  # Show first 5 columns
                col_type = col['type']
                constraints = []
                if col['primary_key']:
                    constraints.append("PK")
                if col['not_null']:
                    constraints.append("NOT NULL")
                constraint_str = f" ({', '.join(constraints)})" if constraints else ""
                logger.info(f"    └─ {col['name']:<25} | {col_type:<10}{constraint_str}")
            
            if len(columns) > 5:
                logger.info(f"    └─ ... and {len(columns) - 5} more columns")
        
        logger.info("")
    
    # Show data integrity summary
    data_integrity = analysis.get("data_integrity", {})
    logger.info("Data Integrity Summary:")
    logger.info("-" * 60)
    logger.info(f"Tables with data: {data_integrity.get('tables_with_data', 0)}")
    logger.info(f"Empty tables: {len(data_integrity.get('empty_tables', []))}")
    logger.info(f"Large tables (>10K): {len(data_integrity.get('large_tables', []))}")
    
    # Show empty tables
    empty_tables = data_integrity.get("empty_tables", [])
    if empty_tables:
        logger.info(f"Empty Tables ({len(empty_tables)}):")
        for table in empty_tables:
            logger.info(f"   - {table}")
    
    # Show conversion issues
    conversion_issues = analysis.get("conversion_issues", [])
    if conversion_issues:
        logger.warning(f"Conversion Issues ({len(conversion_issues)}):")
        for issue in conversion_issues:
            logger.warning(f"   - {issue}")
    else:
        logger.info("No conversion issues detected!")
    
    # Show recommendations
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        logger.info("Recommendations:")
        for rec in recommendations:
            logger.info(f"   - {rec}")


if __name__ == "__main__":
    # Set up logging configuration
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"sqlite_diagnostics_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, mode='w'),
            logging.StreamHandler(sys.stdout)  # Also show in console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting SQLite diagnostics - log file: {log_filename}")
    
    main()
    
    logger.info("SQLite diagnostics completed") 