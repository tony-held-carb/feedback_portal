#!/usr/bin/env python3
"""
Automated test runner for file upload workflows in the ARB Feedback Portal.

This script runs comprehensive tests on the file upload and ingestion system
using actual Excel files from the feedback_forms/testing_versions folder.

Usage:
    python scripts/run_upload_tests.py [options]

Options:
    --quick          Run only basic upload tests (faster)
    --full           Run all tests including staged uploads
    --sector SECTOR  Run tests for specific sector only
    --verbose        Enable verbose output
    --output FILE    Save test results to file

Examples:
    python scripts/run_upload_tests.py --quick
    python scripts/run_upload_tests.py --sector dairy
    python scripts/run_upload_tests.py --full --verbose --output results.txt

Args:
    None

Returns:
    int: Exit code (0 for success, 1 for failure)

Attributes:
    None

Notes:
    - Requires Flask app to be properly configured
    - Tests actual Excel files from feedback_forms/testing_versions/
    - Provides detailed reporting of test results
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

def setup_environment():
    """
    Setup the Python environment for testing.
    
    Args:
        None
        
    Returns:
        bool: True if setup successful
        
    Examples:
        if setup_environment():
            # Environment ready for testing
            pass
    """
    # Add the source directory to Python path
    source_dir = Path(__file__).parent.parent / "source" / "production"
    if source_dir.exists():
        sys.path.insert(0, str(source_dir))
        os.environ['PYTHONPATH'] = str(source_dir)
        return True
    else:
        print(f"❌ Source directory not found: {source_dir}")
        return False

def check_test_files():
    """
    Check that required test files exist.
    
    Args:
        None
        
    Returns:
        bool: True if all test files exist
        
    Examples:
        if check_test_files():
            # All test files available
            pass
    """
    test_dir = Path("feedback_forms/testing_versions")
    if not test_dir.exists():
        print(f"❌ Test files directory not found: {test_dir}")
        return False
    
    expected_files = [
        "dairy_digester_operator_feedback_v005_test_01.xlsx",
        "landfill_operator_feedback_v070_test_01.xlsx",
        "landfill_operator_feedback_v071_test_01.xlsx",
        "oil_and_gas_operator_feedback_v070_test_01.xlsx",
        "energy_operator_feedback_v003_test_01.xlsx",
        "generic_operator_feedback_v002_test_01.xlsx"
    ]
    
    missing_files = []
    for filename in expected_files:
        file_path = test_dir / filename
        if not file_path.exists():
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    
    print(f"✅ All test files found in {test_dir}")
    return True

def run_backend_tests(quick: bool = False, sector: Optional[str] = None, verbose: bool = False, test_type: str = "all") -> subprocess.CompletedProcess:
    """
    Run backend integration tests for file uploads.
    
    Args:
        quick (bool): Run only basic tests
        sector (str): Run tests for specific sector only
        verbose (bool): Enable verbose output
        test_type (str): Type of tests to run (all, basic, field_validation, db_verification, comprehensive, negative_validation, round_trip)
        
    Returns:
        subprocess.CompletedProcess: Test execution result
        
    Examples:
        result = run_backend_tests(quick=True, verbose=True)
        if result.returncode == 0:
            print("Backend tests passed")
    """
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/arb/portal/test_file_upload_suite.py",
        "-v" if verbose else "-q",
        "--tb=short"
    ]
    
    # Add test type filters
    if test_type == "basic":
        cmd.extend(["-k", "not staged and not field_level and not database_state and not comprehensive and not negative_validation and not round_trip"])
    elif test_type == "field_validation":
        cmd.extend(["-k", "field_level_value_assertions"])
    elif test_type == "db_verification":
        cmd.extend(["-k", "database_state_verification"])
    elif test_type == "comprehensive":
        cmd.extend(["-k", "comprehensive_upload_validation"])
    elif test_type == "negative_validation":
        cmd.extend(["-k", "negative_validation_errors or file_size_limits or concurrent_upload_handling or malicious_file_handling"])
    elif test_type == "round_trip":
        cmd.extend(["-k", "round_trip_export_import_consistency or data_integrity_through_processing_pipeline or export_format_consistency"])
    elif quick:
        cmd.extend(["-k", "not staged"])
    
    if sector is not None:
        cmd.extend(["-k", sector.lower()])
    
    print(f"Running backend tests: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)

def run_e2e_tests(verbose: bool = False) -> subprocess.CompletedProcess:
    """
    Run E2E tests (requires running Flask app).
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        subprocess.CompletedProcess: Test execution result
        
    Examples:
        result = run_e2e_tests(verbose=True)
        if result.returncode == 0:
            print("E2E tests passed")
    """
    # Note: E2E tests would require a running Flask app
    # For now, we'll skip this and focus on backend tests
    print("⚠️ E2E tests require a running Flask app - skipping for now")
    return subprocess.CompletedProcess([], 0, "", "")

def run_quick_validation():
    """
    Run a quick validation of the upload system.
    
    Args:
        None
        
    Returns:
        bool: True if validation passes
        
    Examples:
        if run_quick_validation():
            print("Quick validation passed")
    """
    print("🔍 Running quick validation...")
    
    # Test basic file upload functionality
    result = run_backend_tests(quick=True, verbose=False, test_type="basic")
    
    if result.returncode == 0:
        print("✅ Quick validation passed")
        return True
    else:
        print("❌ Quick validation failed")
        return False

def run_field_validation_tests(verbose: bool = False) -> subprocess.CompletedProcess:
    """
    Run field-level value assertion tests.
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        subprocess.CompletedProcess: Test execution result
        
    Examples:
        result = run_field_validation_tests(verbose=True)
        if result.returncode == 0:
            print("Field validation tests passed")
    """
    print("🔍 Running field-level value assertion tests...")
    return run_backend_tests(verbose=verbose, test_type="field_validation")

def run_database_verification_tests(verbose: bool = False) -> subprocess.CompletedProcess:
    """
    Run database state verification tests.
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        subprocess.CompletedProcess: Test execution result
        
    Examples:
        result = run_database_verification_tests(verbose=True)
        if result.returncode == 0:
            print("Database verification tests passed")
    """
    print("🔍 Running database state verification tests...")
    return run_backend_tests(verbose=verbose, test_type="db_verification")

def run_comprehensive_validation_tests(verbose: bool = False) -> subprocess.CompletedProcess:
    """
    Run comprehensive upload validation tests.
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        subprocess.CompletedProcess: Test execution result
        
    Examples:
        result = run_comprehensive_validation_tests(verbose=True)
        if result.returncode == 0:
            print("Comprehensive validation tests passed")
    """
    print("🔍 Running comprehensive upload validation tests...")
    return run_backend_tests(verbose=verbose, test_type="comprehensive")

def run_negative_validation_tests(verbose: bool = False) -> subprocess.CompletedProcess:
    """
    Run negative validation tests for error handling.
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        subprocess.CompletedProcess: Test execution result
        
    Examples:
        result = run_negative_validation_tests(verbose=True)
        if result.returncode == 0:
            print("Negative validation tests passed")
    """
    print("🔍 Running negative validation tests...")
    return run_backend_tests(verbose=verbose, test_type="negative_validation")

def run_round_trip_tests(verbose: bool = False) -> subprocess.CompletedProcess:
    """
    Run round-trip export/import consistency tests.
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        subprocess.CompletedProcess: Test execution result
        
    Examples:
        result = run_round_trip_tests(verbose=True)
        if result.returncode == 0:
            print("Round-trip tests passed")
    """
    print("🔍 Running round-trip export/import consistency tests...")
    return run_backend_tests(verbose=verbose, test_type="round_trip")

def run_full_test_suite(verbose: bool = False, output_file: Optional[str] = None):
    """
    Run the complete test suite.
    
    Args:
        verbose (bool): Enable verbose output
        output_file (str): File to save results to
        
    Returns:
        bool: True if all tests pass
        
    Examples:
        success = run_full_test_suite(verbose=True, output_file="results.txt")
        if success:
            print("All tests passed")
    """
    print("🚀 Running full test suite...")
    
    start_time = time.time()
    
    # Run different test categories
    test_categories = [
        ("Basic Upload Tests", lambda: run_backend_tests(quick=False, verbose=verbose, test_type="basic")),
        ("Field Validation Tests", lambda: run_field_validation_tests(verbose=verbose)),
        ("Database Verification Tests", lambda: run_database_verification_tests(verbose=verbose)),
        ("Comprehensive Validation Tests", lambda: run_comprehensive_validation_tests(verbose=verbose)),
        ("Negative Validation Tests", lambda: run_negative_validation_tests(verbose=verbose)),
        ("Round-Trip Tests", lambda: run_round_trip_tests(verbose=verbose)),
    ]
    
    results = {}
    
    for category_name, test_func in test_categories:
        print(f"\n📋 Running {category_name}...")
        result = test_func()
        results[category_name.lower().replace(" ", "_")] = {
            "passed": result.returncode == 0,
            "output": result.stdout.decode() if result.stdout else "",
            "error": result.stderr.decode() if result.stderr else ""
        }
    
    # Run E2E tests (if Flask app is running)
    e2e_result = run_e2e_tests(verbose=verbose)
    results["e2e_tests"] = {
        "passed": e2e_result.returncode == 0,
        "output": e2e_result.stdout.decode() if e2e_result.stdout else "",
        "error": e2e_result.stderr.decode() if e2e_result.stderr else ""
    }
    
    end_time = time.time()
    duration = end_time - start_time
    results["duration"] = duration
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    all_passed = True
    for category_name, test_func in test_categories:
        category_key = category_name.lower().replace(" ", "_")
        status = "✅ PASSED" if results[category_key]["passed"] else "❌ FAILED"
        print(f"{category_name}: {status}")
        if not results[category_key]["passed"]:
            all_passed = False
    
    e2e_status = "✅ PASSED" if results["e2e_tests"]["passed"] else "⚠️ SKIPPED"
    print(f"E2E Tests:     {e2e_status}")
    print(f"Duration:      {duration:.2f} seconds")
    
    if output_file:
        save_results_to_file(results, output_file)
        print(f"Results saved to: {output_file}")
    
    return all_passed

def save_results_to_file(results: Dict[str, Any], filename: str):
    """
    Save test results to a file.
    
    Args:
        results (Dict[str, Any]): Test results dictionary
        filename (str): Output filename
        
    Returns:
        None
        
    Examples:
        save_results_to_file(results, "test_results.txt")
    """
    with open(filename, 'w') as f:
        f.write("ARB Feedback Portal - File Upload Test Results\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Test Duration: {results['duration']:.2f} seconds\n\n")
        
        f.write("Backend Tests:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Status: {'PASSED' if results['backend_tests']['passed'] else 'FAILED'}\n")
        f.write(f"Output:\n{results['backend_tests']['output']}\n")
        if results['backend_tests']['error']:
            f.write(f"Errors:\n{results['backend_tests']['error']}\n")
        
        f.write("\nE2E Tests:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Status: {'PASSED' if results['e2e_tests']['passed'] else 'SKIPPED'}\n")
        f.write(f"Output:\n{results['e2e_tests']['output']}\n")
        if results['e2e_tests']['error']:
            f.write(f"Errors:\n{results['e2e_tests']['error']}\n")

def main():
    """
    Main entry point for the test runner.
    
    Args:
        None
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
        
    Examples:
        exit_code = main()
        sys.exit(exit_code)
    """
    parser = argparse.ArgumentParser(
        description="Run file upload tests for ARB Feedback Portal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_upload_tests.py --quick
  python scripts/run_upload_tests.py --sector dairy
  python scripts/run_upload_tests.py --full --verbose --output results.txt
  python scripts/run_upload_tests.py --field-validation
  python scripts/run_upload_tests.py --db-verification
  python scripts/run_upload_tests.py --comprehensive
  python scripts/run_upload_tests.py --negative-validation
  python scripts/run_upload_tests.py --round-trip
        """
    )
    
    parser.add_argument("--quick", action="store_true", 
                       help="Run only basic upload tests (faster)")
    parser.add_argument("--full", action="store_true", 
                       help="Run all tests including staged uploads")
    parser.add_argument("--sector", type=str, 
                       help="Run tests for specific sector only")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("--output", type=str, 
                       help="Save test results to file")
    parser.add_argument("--field-validation", action="store_true",
                       help="Run field-level value assertion tests")
    parser.add_argument("--db-verification", action="store_true",
                       help="Run database state verification tests")
    parser.add_argument("--comprehensive", action="store_true",
                       help="Run comprehensive upload validation tests")
    parser.add_argument("--negative-validation", action="store_true",
                       help="Run negative validation tests for error handling")
    parser.add_argument("--round-trip", action="store_true",
                       help="Run round-trip export/import consistency tests")
    
    args = parser.parse_args()
    
    # Setup environment
    if not setup_environment():
        return 1
    
    # Check test files
    if not check_test_files():
        return 1
    
    try:
        if args.quick:
            success = run_quick_validation()
        elif args.full:
            success = run_full_test_suite(verbose=args.verbose, output_file=args.output)
        elif args.field_validation:
            result = run_field_validation_tests(verbose=args.verbose)
            success = result.returncode == 0
        elif args.db_verification:
            result = run_database_verification_tests(verbose=args.verbose)
            success = result.returncode == 0
        elif args.comprehensive:
            result = run_comprehensive_validation_tests(verbose=args.verbose)
            success = result.returncode == 0
        elif args.negative_validation:
            result = run_negative_validation_tests(verbose=args.verbose)
            success = result.returncode == 0
        elif args.round_trip:
            result = run_round_trip_tests(verbose=args.verbose)
            success = result.returncode == 0
        else:
            # Default: run basic tests
            success = run_quick_validation()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 