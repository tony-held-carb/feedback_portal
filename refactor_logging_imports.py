#!/usr/bin/env python3
"""
Script to refactor logging imports across the codebase.

This script replaces the old pattern:
    from arb.__get_logger import get_logger
    logger, pp_log = get_logger()

With the new pattern:
    import logging
    logger = logging.getLogger(__name__)

And ensures proper import ordering (standard library imports first).
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

def find_files_to_refactor() -> List[Path]:
    """Find all Python files that use the old logging pattern."""
    files_to_update = []
    
    # Search in the source/production directory
    source_dir = Path("source/production")
    if not source_dir.exists():
        print("Error: source/production directory not found")
        return []
    
    for py_file in source_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            if "from arb.__get_logger import get_logger" in content:
                files_to_update.append(py_file)
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}")
    
    return files_to_update

def analyze_file(file_path: Path) -> Tuple[bool, List[str], Optional[str]]:
    """
    Analyze a file to determine if it needs refactoring.
    
    Returns:
        (needs_refactor, issues, pp_log_usage)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Could not read file: {e}"], None
    
    issues = []
    pp_log_usage = None
    
    # Check if file uses the old pattern
    if "from arb.__get_logger import get_logger" not in content:
        return False, ["Does not use old logging pattern"], None
    
    # Check if pp_log is used (either assigned or called)
    if "pp_log(" in content:
        pp_log_usage = "pp_log is called in this file"
        # We'll handle this by adding get_pretty_printer import
    elif "pp_log" in content:
        pp_log_usage = "pp_log is assigned but not called"
        # We'll handle this by adding get_pretty_printer import for consistency
    
    # Check if logger, pp_log = get_logger() pattern exists
    if "logger, pp_log = get_logger" not in content:
        issues.append("Unexpected get_logger usage pattern")
    
    return True, issues, pp_log_usage

def refactor_file(file_path: Path, dry_run: bool = True) -> Tuple[bool, List[str]]:
    """
    Refactor a single file to use the new logging pattern.
    
    Args:
        file_path: Path to the file to refactor
        dry_run: If True, only show what would be changed
    
    Returns:
        (success, messages)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Could not read file: {e}"]
    
    original_content = content
    messages = []
    
    # Step 1: Remove the old import
    old_import_pattern = r'from arb\.__get_logger import get_logger\n'
    if re.search(old_import_pattern, content):
        content = re.sub(old_import_pattern, '', content)
        messages.append("Removed: from arb.__get_logger import get_logger")
    else:
        return False, ["Could not find old import pattern"]
    
    # Step 2: Replace logger, pp_log = get_logger() with logger and pp_log setup
    old_logger_pattern = r'logger, pp_log = get_logger\(\)'
    new_logger_pattern = 'logger = logging.getLogger(__name__)\n_, pp_log = get_pretty_printer()'
    
    if re.search(old_logger_pattern, content):
        content = re.sub(old_logger_pattern, new_logger_pattern, content)
        messages.append(f"Replaced: {old_logger_pattern} -> {new_logger_pattern}")
    else:
        # Try with parameters
        old_logger_pattern_with_params = r'logger, pp_log = get_logger\([^)]*\)'
        if re.search(old_logger_pattern_with_params, content):
            content = re.sub(old_logger_pattern_with_params, new_logger_pattern, content)
            messages.append(f"Replaced: {old_logger_pattern_with_params} -> {new_logger_pattern}")
        else:
            return False, ["Could not find logger assignment pattern"]
    
    # Step 3: Add import logging and get_pretty_printer at the top with other standard library imports
    # Find the first import section
    lines = content.split('\n')
    import_section_start = -1
    import_section_end = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            if import_section_start == -1:
                import_section_start = i
            import_section_end = i
        elif import_section_start != -1 and line.strip() == '':
            import_section_end = i
            break
    
    if import_section_start == -1:
        return False, ["Could not find import section"]
    
    # Find where to insert logging import
    insert_pos = import_section_start
    
    # Look for existing standard library imports
    for i in range(import_section_start, import_section_end + 1):
        line = lines[i].strip()
        if line.startswith('import ') and not line.startswith('import arb'):
            insert_pos = i + 1
        elif line.startswith('from ') and not line.startswith('from arb'):
            # This is likely a third-party import, insert before it
            insert_pos = i
            break
    
    # Insert logging import
    if 'import logging' not in content:
        lines.insert(insert_pos, 'import logging')
        messages.append("Added: import logging")
    
    # Step 4: Add get_pretty_printer import (always add it for consistency)
    # Find where to insert get_pretty_printer import (with other arb imports)
    arb_import_pos = -1
    for i in range(import_section_start, len(lines)):
        line = lines[i].strip()
        if line.startswith('from arb.') and 'get_pretty_printer' not in line:
            arb_import_pos = i + 1
        elif line.startswith('from arb.') and 'get_pretty_printer' in line:
            # Already imported
            break
    
    if arb_import_pos != -1 and 'from arb_logging import get_pretty_printer' not in content:
        lines.insert(arb_import_pos, 'from arb_logging import get_pretty_printer')
        messages.append("Added: from arb_logging import get_pretty_printer")
    
    content = '\n'.join(lines)
    
    # Step 4: Write the file if not dry run
    if not dry_run:
        try:
            file_path.write_text(content, encoding='utf-8')
            messages.append(f"Updated file: {file_path}")
        except Exception as e:
            return False, [f"Could not write file: {e}"]
    else:
        messages.append(f"Would update file: {file_path}")
    
    return True, messages

def main():
    """Main function to run the refactoring."""
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    print(f"Logging Import Refactor {'(DRY RUN)' if dry_run else ''}")
    print("=" * 50)
    
    # Find files to refactor
    files_to_update = find_files_to_refactor()
    print(f"Found {len(files_to_update)} files to analyze")
    
    # Analyze each file
    files_to_refactor = []
    files_with_issues = []
    
    for file_path in files_to_update:
        needs_refactor, issues, pp_log_usage = analyze_file(file_path)
        
        if needs_refactor:
            if issues:
                files_with_issues.append((file_path, issues, pp_log_usage))
            else:
                files_to_refactor.append(file_path)
    
    print(f"\nFiles ready for refactoring: {len(files_to_refactor)}")
    print(f"Files with issues: {len(files_with_issues)}")
    
    # Show files with issues
    if files_with_issues:
        print("\nFiles with issues (need manual review):")
        for file_path, issues, pp_log_usage in files_with_issues:
            print(f"  {file_path}")
            for issue in issues:
                print(f"    - {issue}")
            if pp_log_usage:
                print(f"    - {pp_log_usage}")
        print()
    
    # Refactor files
    if files_to_refactor:
        print(f"Refactoring {len(files_to_refactor)} files...")
        
        success_count = 0
        for file_path in files_to_refactor:
            success, messages = refactor_file(file_path, dry_run=dry_run)
            if success:
                success_count += 1
                print(f"✅ {file_path}")
                for message in messages:
                    print(f"   {message}")
            else:
                print(f"❌ {file_path}")
                for message in messages:
                    print(f"   {message}")
            print()
        
        print(f"Successfully processed {success_count}/{len(files_to_refactor)} files")
    
    if dry_run:
        print("\nThis was a dry run. Use --apply to actually make changes.")
    else:
        print("\nRefactoring complete!")

if __name__ == "__main__":
    main() 