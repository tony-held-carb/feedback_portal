#!/usr/bin/env python3
"""
Command-line script to run SQLite diagnostics on snapshot files.

Usage:
    python run_sqlite_diagnostics.py [filename]
    
If no filename is provided, it will analyze the most recent snapshot file.
"""

import os
import sys
import glob
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'source', 'production'))

from arb.util.sqlite_diagnostics import analyze_sqlite_file, get_sqlite_summary, export_analysis_report


def find_latest_snapshot():
    """Find the most recent SQLite snapshot file."""
    snapshots_dir = "database_snapshots"
    if not os.path.exists(snapshots_dir):
        print(f"❌ Snapshots directory '{snapshots_dir}' not found!")
        return None
    
    # Find all .sqlite files
    sqlite_files = glob.glob(os.path.join(snapshots_dir, "arb_snapshot_*.sqlite"))
    
    if not sqlite_files:
        print(f"❌ No SQLite snapshot files found in '{snapshots_dir}'!")
        return None
    
    # Get the most recent file
    latest_file = max(sqlite_files, key=os.path.getctime)
    return latest_file


def main():
    """Main function to run diagnostics."""
    print("🔍 SQLite Snapshot Diagnostics Tool")
    print("=" * 50)
    
    # Determine which file to analyze
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"❌ File '{filename}' not found!")
            return
        file_path = filename
    else:
        file_path = find_latest_snapshot()
        if not file_path:
            return
        print(f"📁 Analyzing latest snapshot: {os.path.basename(file_path)}")
    
    print(f"🔍 Analyzing: {file_path}")
    print()
    
    # Get quick summary first
    print("📊 Quick Summary:")
    print("-" * 30)
    summary = get_sqlite_summary(file_path)
    
    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        return
    
    print(f"📁 File Size: {summary['file_size_mb']} MB")
    print(f"📋 Tables: {summary['table_count']}")
    print(f"📊 Total Rows: {summary['total_rows']:,}")
    if summary['largest_table']:
        print(f"🐘 Largest Table: {summary['largest_table']} ({summary['largest_table_rows']:,} rows)")
    print()
    
    # Run comprehensive analysis
    print("🔍 Running comprehensive analysis...")
    analysis = analyze_sqlite_file(file_path)
    
    if "error" in analysis:
        print(f"❌ Analysis Error: {analysis['error']}")
        return
    
    # Display key findings
    print("\n📋 Key Findings:")
    print("-" * 30)
    
    # File info
    file_info = analysis.get("file_info", {})
    print(f"📁 File: {file_info.get('path', 'N/A')}")
    print(f"📏 Size: {file_info.get('size_mb', 'N/A')} MB")
    print(f"📅 Created: {file_info.get('created', 'N/A')}")
    
    # Tables info
    tables = analysis.get("tables", {})
    print(f"📊 Total Tables: {len(tables)}")
    
    # Data integrity
    data_integrity = analysis.get("data_integrity", {})
    print(f"📈 Tables with Data: {data_integrity.get('tables_with_data', 0)}")
    print(f"📭 Empty Tables: {len(data_integrity.get('empty_tables', []))}")
    print(f"🐘 Large Tables (>10K): {len(data_integrity.get('large_tables', []))}")
    
    # Conversion issues
    conversion_issues = analysis.get("conversion_issues", [])
    print(f"⚠️  Conversion Issues: {len(conversion_issues)}")
    
    # Show empty tables if any
    empty_tables = data_integrity.get("empty_tables", [])
    if empty_tables:
        print(f"\n📭 Empty Tables ({len(empty_tables)}):")
        for table in empty_tables[:10]:  # Show first 10
            print(f"   - {table}")
        if len(empty_tables) > 10:
            print(f"   ... and {len(empty_tables) - 10} more")
    
    # Show large tables if any
    large_tables = data_integrity.get("large_tables", [])
    if large_tables:
        print(f"\n🐘 Large Tables (>10K rows):")
        for large_table in large_tables:
            print(f"   - {large_table['table']}: {large_table['rows']:,} rows")
    
    # Show conversion issues if any
    if conversion_issues:
        print(f"\n⚠️  Conversion Issues:")
        for issue in conversion_issues[:5]:  # Show first 5
            print(f"   - {issue}")
        if len(conversion_issues) > 5:
            print(f"   ... and {len(conversion_issues) - 5} more")
    else:
        print(f"\n✅ No conversion issues detected!")
    
    # Show recommendations
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   - {rec}")
    
    # Offer to export report
    print(f"\n📄 Export Options:")
    print("-" * 30)
    print("To export a detailed report, run:")
    print(f"   python run_sqlite_diagnostics.py --export {os.path.basename(file_path)}")
    
    # Handle export if requested
    if len(sys.argv) > 2 and sys.argv[1] == "--export":
        export_filename = sys.argv[2]
        if not export_filename.startswith("arb_snapshot_") or not export_filename.endswith(".sqlite"):
            print("❌ Invalid filename for export. Must be arb_snapshot_*.sqlite")
            return
        
        export_path = os.path.join("database_snapshots", export_filename)
        if not os.path.exists(export_path):
            print(f"❌ File not found: {export_path}")
            return
        
        print(f"\n📄 Exporting detailed report...")
        report_path = export_analysis_report(analysis, f"sqlite_analysis_{export_filename.replace('.sqlite', '')}.txt")
        print(f"✅ Report exported to: {report_path}")


if __name__ == "__main__":
    main() 