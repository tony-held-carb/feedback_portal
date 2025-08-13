#!/usr/bin/env python3
"""
Script to run all Excel module tests with coverage reporting.

This script provides a convenient way to run the complete Excel testing suite
and generate coverage reports.
"""

import sys
import subprocess
from pathlib import Path

# Import our new path utility
from arb.utils.path_utils import find_repo_root


def main():
    """Run all Excel tests with coverage."""
    try:
        # Find the repository root
        repo_root = find_repo_root(Path(__file__))
        print(f"Repository root: {repo_root}")
        
        # Find the Excel tests directory
        excel_tests_dir = repo_root / "tests" / "arb" / "utils" / "excel"
        print(f"Excel tests directory: {excel_tests_dir}")
        
        if not excel_tests_dir.exists():
            print(f"❌ Excel tests directory not found: {excel_tests_dir}")
            return 1
        
        # Change to the Excel tests directory
        excel_tests_dir = excel_tests_dir.resolve()
        print(f"Changing to directory: {excel_tests_dir}")
        
        # Run pytest with coverage
        cmd = [
            sys.executable, "-m", "pytest",
            "--tb=short",  # Short traceback format
            "--cov=arb.utils.excel",  # Coverage for Excel module
            "--cov-report=term-missing",  # Show missing lines
            "--cov-report=html:htmlcov",  # Generate HTML report
            "--cov-report=xml",  # Generate XML report for CI
            "-v",  # Verbose output
            "."
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        print(f"Working directory: {excel_tests_dir}")
        
        # Run the tests
        result = subprocess.run(
            cmd,
            cwd=excel_tests_dir,
            capture_output=False,  # Let output go to terminal
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ All Excel tests passed!")
            print(f"Coverage report generated in: {excel_tests_dir}/htmlcov/")
            print(f"XML coverage report: {excel_tests_dir}/.coverage")
        else:
            print(f"\n❌ Some Excel tests failed (exit code: {result.returncode})")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running Excel tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
