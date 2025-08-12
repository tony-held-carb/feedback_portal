#!/usr/bin/env python3
"""
Test Infrastructure Validation Script

This script validates that the test infrastructure is working correctly and that
all test files in the standard testing directory are accessible.

Run this script to verify:
1. Test directories can be resolved
2. Test files are accessible
3. Path formats are correct (Linux/WSL, not Windows)
4. No silent failures due to path issues

Usage:
    python test_infrastructure_validation.py
"""

import os
import sys
from pathlib import Path

def find_repo_root() -> Path:
    """Find the repository root directory by looking for .git directory."""
    current_path = Path(__file__).resolve()
    while current_path.parent != current_path:
        if (current_path / ".git").exists():
            return current_path
        current_path = current_path.parent
    
    return Path.cwd()

def validate_test_infrastructure():
    """Validate that all required test infrastructure exists."""
    print("🔍 Validating test infrastructure...")
    
    # Find repository root
    repo_root = find_repo_root()
    print(f"📁 Repository root: {repo_root}")
    
    # Check if .git directory exists
    if not (repo_root / ".git").exists():
        print("❌ .git directory not found in repository root")
        return False
    
    # Define test directories
    test_files_dir = repo_root / "feedback_forms" / "testing_versions"
    standard_test_files_dir = test_files_dir / "standard"
    
    print(f"📁 Test files directory: {test_files_dir}")
    print(f"📁 Standard test files directory: {standard_test_files_dir}")
    
    # Check if directories exist
    if not test_files_dir.exists():
        print("❌ Test files directory not found")
        return False
    
    if not standard_test_files_dir.exists():
        print("❌ Standard test files directory not found")
        return False
    
    # Check if there are actual test files
    test_files = list(standard_test_files_dir.glob("*.xlsx"))
    if not test_files:
        print("❌ No Excel test files found in standard directory")
        return False
    
    print(f"✅ Found {len(test_files)} test files in standard directory")
    
    # Validate each test file
    accessible_files = []
    inaccessible_files = []
    windows_path_files = []
    
    for file_path in test_files:
        file_str = str(file_path)
        
        # Check if file is accessible
        if file_path.exists():
            accessible_files.append(file_str)
        else:
            inaccessible_files.append(file_str)
        
        # Check for Windows-style paths
        if '\\' in file_str:
            windows_path_files.append(file_str)
    
    print(f"\n📊 File validation results:")
    print(f"   Total files: {len(test_files)}")
    print(f"   Accessible: {len(accessible_files)}")
    print(f"   Inaccessible: {len(inaccessible_files)}")
    print(f"   Windows paths: {len(windows_path_files)}")
    
    # Report issues
    if inaccessible_files:
        print(f"\n⚠️  Inaccessible files (first 5):")
        for file_path in inaccessible_files[:5]:
            print(f"   {file_path}")
    
    if windows_path_files:
        print(f"\n⚠️  Files with Windows-style paths (first 5):")
        for file_path in windows_path_files[:5]:
            print(f"   {file_path}")
    
    # Check path format consistency
    print(f"\n🔍 Path format analysis:")
    for file_path in accessible_files[:3]:
        print(f"   {file_path}")
        if '\\' in file_path:
            print(f"     ⚠️  Contains Windows backslashes")
        if '/' in file_path:
            print(f"     ✅ Contains forward slashes")
    
    # Final validation
    if not accessible_files:
        print("\n❌ CRITICAL: No accessible test files found!")
        return False
    
    if windows_path_files:
        print("\n⚠️  WARNING: Some files have Windows-style paths")
        print("   This may cause issues when running tests on Linux/WSL")
    
    print(f"\n✅ Test infrastructure validation completed successfully")
    print(f"   {len(accessible_files)} test files are ready for testing")
    
    return True

def main():
    """Main function to run the validation."""
    print("=" * 60)
    print("TEST INFRASTRUCTURE VALIDATION")
    print("=" * 60)
    
    success = validate_test_infrastructure()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ VALIDATION PASSED - Test infrastructure is ready")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED - Test infrastructure has issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
