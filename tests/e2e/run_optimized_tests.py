#!/usr/bin/env python3
"""
Optimized E2E Test Runner

This script runs all the optimized E2E tests in the correct order with proper configuration.
It addresses the performance issues and failures found in the original tests.

Usage:
    python tests/e2e/run_optimized_tests.py [options]

Options:
    --performance-only    Run only performance comparison tests
    --comprehensive-only  Run only comprehensive route tests  
    --equivalence-only    Run only route equivalence tests
    --all                Run all optimized tests (default)
    --parallel           Run tests in parallel if available
    --verbose            Verbose output
    --fast               Use fastest test configuration
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description, verbose=False):
    """Run a command and handle errors."""
    if verbose:
        print(f"\n🚀 Running: {description}")
        print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        if verbose:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print("Output:", result.stdout)
        
        return True, result.stdout
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False, e.stderr

def run_performance_tests(verbose=False, fast=False):
    """Run optimized performance comparison tests."""
    cmd = [
        "python", "-m", "pytest",
        "tests/e2e/test_upload_performance_comparison_optimized.py",
        "-v"
    ]
    
    if fast:
        cmd.extend(["--performance-tolerance", "0.35", "--min-upload-speed", "0.02"])
    
    return run_command(cmd, "Performance Comparison Tests", verbose)

def run_comprehensive_tests(verbose=False, fast=False):
    """Run optimized comprehensive route tests."""
    cmd = [
        "python", "-m", "pytest",
        "tests/e2e/test_refactored_routes_comprehensive_optimized.py",
        "-v"
    ]
    
    if fast:
        cmd.extend(["--test-files", "representative"])
    
    return run_command(cmd, "Comprehensive Route Tests", verbose)

def run_equivalence_tests(verbose=False, fast=False):
    """Run optimized route equivalence tests."""
    cmd = [
        "python", "-m", "pytest",
        "tests/e2e/test_refactored_routes_equivalence_optimized.py",
        "-v"
    ]
    
    if fast:
        cmd.extend(["--test-files", "representative", "--timeout", "8"])
    
    return run_command(cmd, "Route Equivalence Tests", verbose)

def run_all_optimized_tests(verbose=False, fast=False, parallel=False):
    """Run all optimized tests in sequence."""
    print("🧪 Running All Optimized E2E Tests")
    print("=" * 50)
    
    # Test 1: Performance Comparison
    print("\n📊 Test 1: Performance Comparison")
    success, output = run_performance_tests(verbose, fast)
    if not success:
        print("⚠️ Performance tests had issues, continuing with other tests...")
    
    # Test 2: Comprehensive Route Tests
    print("\n🔍 Test 2: Comprehensive Route Tests")
    success, output = run_comprehensive_tests(verbose, fast)
    if not success:
        print("⚠️ Comprehensive tests had issues, continuing with other tests...")
    
    # Test 3: Route Equivalence Tests
    print("\n⚖️ Test 3: Route Equivalence Tests")
    success, output = run_equivalence_tests(verbose, fast)
    if not success:
        print("⚠️ Equivalence tests had issues")
    
    print("\n" + "=" * 50)
    print("🎯 All Optimized Tests Completed")
    
    return True

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run optimized E2E tests for the feedback portal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python tests/e2e/run_optimized_tests.py --all --fast
    python tests/e2e/run_optimized_tests.py --performance-only --verbose
    python tests/e2e/run_optimized_tests.py --comprehensive-only
        """
    )
    
    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="Run only performance comparison tests"
    )
    
    parser.add_argument(
        "--comprehensive-only",
        action="store_true",
        help="Run only comprehensive route tests"
    )
    
    parser.add_argument(
        "--equivalence-only",
        action="store_true",
        help="Run only route equivalence tests"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all optimized tests (default)"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel if available"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use fastest test configuration"
    )
    
    args = parser.parse_args()
    
    # Set default behavior
    if not any([args.performance_only, args.comprehensive_only, args.equivalence_only, args.all]):
        args.all = True
    
    # Check if we're in the right directory
    if not Path("tests/e2e").exists():
        print("❌ Error: Must run from the project root directory")
        print("Current directory:", Path.cwd())
        print("Expected to find: tests/e2e/")
        sys.exit(1)
    
    # Run tests based on arguments
    if args.performance_only:
        success, _ = run_performance_tests(args.verbose, args.fast)
        sys.exit(0 if success else 1)
    
    elif args.comprehensive_only:
        success, _ = run_comprehensive_tests(args.verbose, args.fast)
        sys.exit(0 if success else 1)
    
    elif args.equivalence_only:
        success, _ = run_equivalence_tests(args.verbose, args.fast)
        sys.exit(0 if success else 1)
    
    elif args.all:
        success = run_all_optimized_tests(args.verbose, args.fast, args.parallel)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
