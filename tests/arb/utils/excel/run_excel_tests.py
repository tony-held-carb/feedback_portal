#!/usr/bin/env python3
"""
Test runner script for Excel module tests.

This script provides a convenient way to run all Excel-related tests
with proper configuration and reporting.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_excel_tests():
    """Run all Excel module tests."""
    
    # Get the directory containing this script
    test_dir = Path(__file__).parent
    
    # Change to the test directory
    os.chdir(test_dir)
    
    # Run pytest with Excel-specific configuration
    cmd = [
        sys.executable, "-m", "pytest",
        "--verbose",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings",
        "."
    ]
    
    print("Running Excel module tests...")
    print(f"Test directory: {test_dir}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_coverage():
    """Run tests with coverage reporting."""
    
    test_dir = Path(__file__).parent
    
    # Change to the test directory
    os.chdir(test_dir)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=arb.utils.excel",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "--verbose",
        "."
    ]
    
    print("Running Excel module tests with coverage...")
    print(f"Test directory: {test_dir}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"Error running coverage tests: {e}")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Excel module tests")
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run tests with coverage reporting"
    )
    
    args = parser.parse_args()
    
    if args.coverage:
        exit_code = run_coverage()
    else:
        exit_code = run_excel_tests()
    
    sys.exit(exit_code)
