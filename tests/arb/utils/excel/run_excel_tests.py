#!/usr/bin/env python3
"""
Enhanced Excel Testing Suite Runner

This script provides a comprehensive way to run the complete Excel testing suite
with enhanced features including:
- Test discovery and organization
- Performance metrics and timing
- Coverage reporting
- Test result analysis
- Configuration management
- Error reporting and debugging
- HTML report generation
"""

import sys
import subprocess
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import our path utility
try:
    from arb.utils.path_utils import find_repo_root
except ImportError:
    # Fallback if the module isn't available
    def find_repo_root(start_path: Path) -> Path:
        """Find repository root by looking for .git directory."""
        current = start_path.resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return start_path


class ExcelTestRunner:
    """Enhanced Excel test runner with comprehensive features."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.excel_tests_dir = repo_root / "tests" / "arb" / "utils" / "excel"
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def discover_test_files(self) -> List[Path]:
        """Discover all test files in the Excel tests directory."""
        test_files = []
        
        if not self.excel_tests_dir.exists():
            print(f"❌ Excel tests directory not found: {self.excel_tests_dir}")
            return test_files
        
        # Find all Python test files
        for test_file in self.excel_tests_dir.glob("test_*.py"):
            if test_file.is_file():
                test_files.append(test_file)
        
        # Find any other test-related files
        for test_file in self.excel_tests_dir.glob("*_test.py"):
            if test_file.is_file() and test_file not in test_files:
                test_files.append(test_file)
        
        return sorted(test_files)
    
    def analyze_test_structure(self) -> Dict[str, any]:
        """Analyze the structure of test files."""
        test_files = self.discover_test_files()
        structure = {
            'total_files': len(test_files),
            'files': [],
            'estimated_tests': 0,
            'categories': set()
        }
        
        for test_file in test_files:
            file_info = {
                'name': test_file.name,
                'path': str(test_file.relative_to(self.excel_tests_dir)),
                'size': test_file.stat().st_size,
                'lines': len(test_file.read_text().splitlines())
            }
            
            # Estimate test count based on file content
            content = test_file.read_text()
            test_methods = content.count('def test_')
            file_info['estimated_tests'] = test_methods
            structure['estimated_tests'] += test_methods
            
            # Categorize by filename
            if 'xl_create' in test_file.name:
                structure['categories'].add('Excel Creation')
            elif 'xl_parse' in test_file.name:
                structure['categories'].add('Excel Parsing')
            elif 'xl_misc' in test_file.name:
                structure['categories'].add('Excel Utilities')
            elif 'content_validator' in test_file.name:
                structure['categories'].add('Content Validation')
            else:
                structure['categories'].add('Other')
            
            structure['files'].append(file_info)
        
        structure['categories'] = list(structure['categories'])
        return structure
    
    def run_tests_with_coverage(self, 
                               verbose: bool = True,
                               coverage: bool = True,
                               html_report: bool = True,
                               xml_report: bool = True,
                               parallel: bool = False) -> Tuple[int, Dict]:
        """Run tests with coverage and return results."""
        self.start_time = time.time()
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add coverage options
        if coverage:
            cmd.extend([
                "--cov=arb.utils.excel",
                "--cov-report=term-missing"
            ])
            
            if html_report:
                cmd.append("--cov-report=html:htmlcov")
            if xml_report:
                cmd.append("--cov-report=xml")
        
        # Add other options
        if verbose:
            cmd.append("-v")
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add test discovery
        cmd.append(".")
        
        print(f"🚀 Running Excel tests with command: {' '.join(cmd)}")
        print(f"📁 Working directory: {self.excel_tests_dir}")
        print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)
        
        # Run the tests
        try:
            result = subprocess.run(
                cmd,
                cwd=self.excel_tests_dir,
                capture_output=False,  # Let output go to terminal
                text=True
            )
            
            self.end_time = time.time()
            duration = self.end_time - self.start_time
            
            # Collect results
            self.results = {
                'exit_code': result.returncode,
                'duration': duration,
                'success': result.returncode == 0,
                'timestamp': datetime.now().isoformat(),
                'command': ' '.join(cmd)
            }
            
            return result.returncode, self.results
            
        except Exception as e:
            self.end_time = time.time()
            self.results = {
                'exit_code': 1,
                'duration': self.end_time - self.start_time if self.start_time else 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'command': ' '.join(cmd)
            }
            return 1, self.results
    
    def run_individual_test_files(self, test_files: List[str] = None) -> Dict[str, any]:
        """Run individual test files and collect results."""
        if test_files is None:
            test_files = [f.name for f in self.discover_test_files()]
        
        results = {}
        
        for test_file in test_files:
            if not test_file.endswith('.py'):
                test_file += '.py'
            
            test_path = self.excel_tests_dir / test_file
            if not test_path.exists():
                print(f"⚠️  Test file not found: {test_file}")
                continue
            
            print(f"\n🧪 Running individual test: {test_file}")
            
            cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
            
            start_time = time.time()
            result = subprocess.run(cmd, cwd=self.excel_tests_dir, capture_output=True, text=True)
            end_time = time.time()
            
            # Parse output for test counts
            output = result.stdout + result.stderr
            passed = output.count('PASSED')
            failed = output.count('FAILED')
            errors = output.count('ERROR')
            
            results[test_file] = {
                'exit_code': result.returncode,
                'duration': end_time - start_time,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'success': result.returncode == 0
            }
            
            status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
            print(f"   {status} - {passed} passed, {failed} failed, {errors} errors in {end_time - start_time:.2f}s")
        
        return results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        if not self.results:
            return "No test results available."
        
        report = []
        report.append("=" * 80)
        report.append("EXCEL TESTING SUITE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration: {self.results.get('duration', 0):.2f} seconds")
        report.append(f"Status: {'✅ SUCCESS' if self.results.get('success') else '❌ FAILED'}")
        report.append("")
        
        # Test structure analysis
        structure = self.analyze_test_structure()
        report.append("TEST STRUCTURE:")
        report.append(f"  Total test files: {structure['total_files']}")
        report.append(f"  Estimated total tests: {structure['estimated_tests']}")
        report.append(f"  Categories: {', '.join(structure['categories'])}")
        report.append("")
        
        # File details
        report.append("TEST FILES:")
        for file_info in structure['files']:
            status = "✅" if file_info['estimated_tests'] > 0 else "⚠️"
            report.append(f"  {status} {file_info['name']} ({file_info['estimated_tests']} tests, {file_info['lines']} lines)")
        
        report.append("")
        
        # Results summary
        if 'error' in self.results:
            report.append("ERRORS:")
            report.append(f"  {self.results['error']}")
        else:
            report.append("EXECUTION:")
            report.append(f"  Command: {self.results.get('command', 'N/A')}")
            report.append(f"  Exit code: {self.results.get('exit_code', 'N/A')}")
        
        report.append("")
        report.append("COVERAGE REPORTS:")
        if self.excel_tests_dir.exists():
            html_cov = self.excel_tests_dir / "htmlcov"
            xml_cov = self.excel_tests_dir / "coverage.xml"
            
            if html_cov.exists():
                report.append(f"  📊 HTML Report: {html_cov}")
            if xml_cov.exists():
                report.append(f"  📊 XML Report: {xml_cov}")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, output_file: str = "excel_test_results.json"):
        """Save test results to a JSON file."""
        if not self.results:
            print("⚠️  No results to save.")
            return
        
        output_path = self.excel_tests_dir / output_file
        
        # Add structure analysis to results
        self.results['test_structure'] = self.analyze_test_structure()
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"💾 Results saved to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")


def main():
    """Main entry point for the Excel test runner."""
    parser = argparse.ArgumentParser(description="Enhanced Excel Testing Suite Runner")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--no-html", action="store_true", help="Skip HTML coverage report")
    parser.add_argument("--no-xml", action="store_true", help="Skip XML coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--individual", action="store_true", help="Run individual test files")
    parser.add_argument("--save-results", action="store_true", help="Save results to JSON file")
    parser.add_argument("--test-files", nargs="+", help="Specific test files to run")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    try:
        # Find repository root
        repo_root = find_repo_root(Path(__file__))
        if not args.quiet:
            print(f"🏠 Repository root: {repo_root}")
        
        # Initialize test runner
        runner = ExcelTestRunner(repo_root)
        
        # Analyze test structure
        if not args.quiet:
            structure = runner.analyze_test_structure()
            print(f"📊 Discovered {structure['total_files']} test files with ~{structure['estimated_tests']} tests")
            print(f"📁 Test categories: {', '.join(structure['categories'])}")
            print()
        
        # Run tests
        if args.individual:
            # Run individual test files
            test_files = args.test_files if args.test_files else None
            results = runner.run_individual_test_files(test_files)
            
            if not args.quiet:
                print("\n📋 Individual Test Results:")
                for test_file, result in results.items():
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} {test_file}: {result['passed']} passed, {result['failed']} failed")
        else:
            # Run full test suite
            exit_code, results = runner.run_tests_with_coverage(
                verbose=not args.quiet,
                coverage=not args.no_coverage,
                html_report=not args.no_html,
                xml_report=not args.no_xml,
                parallel=args.parallel
            )
            
            # Generate and display report
            if not args.quiet:
                print("\n" + runner.generate_report())
            
            # Save results if requested
            if args.save_results:
                runner.save_results()
            
            return exit_code
        
        return 0
        
    except Exception as e:
        print(f"❌ Error running Excel tests: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
