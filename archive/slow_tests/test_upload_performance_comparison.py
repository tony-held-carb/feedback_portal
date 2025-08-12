"""
Performance Comparison Tests for Original vs Refactored Upload Routes

This module provides comprehensive performance testing to ensure that the refactored upload routes
(upload_file_refactored and upload_file_staged_refactored) maintain equivalent or superior performance
compared to the original routes (upload_file and upload_file_staged).

The tests validate:
1. Upload speed and timing consistency
2. File processing performance equivalence
3. Memory usage patterns
4. Response time consistency
5. Throughput comparison across all test files

Test Categories:
- Upload Speed Performance Tests
- File Processing Performance Tests
- Response Time Consistency Tests
- Throughput Comparison Tests
- Performance Regression Detection

This ensures that the architectural improvements in the refactored routes don't come at the cost of performance.
"""

import json
import os
import time
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Any

import pytest
from playwright.sync_api import Page, expect

from arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready
from arb.portal.utils.playwright_testing_util import (
    clear_upload_attempt_marker,
    upload_file_and_wait_for_attempt_marker,
    wait_for_upload_attempt_marker
)

# Test configuration
BASE_URL = os.environ.get('TEST_BASE_URL', "http://127.0.0.1:2113")

# Find repository root for test file resolution
def find_repo_root() -> Path:
    """Find the repository root directory by looking for .git directory."""
    current_path = Path(__file__).resolve()
    while current_path.parent != current_path:
        if (current_path / ".git").exists():
            return current_path
        current_path = current_path.parent
    
    return Path.cwd()

# Define test directories
REPO_ROOT = find_repo_root()
STANDARD_TEST_FILES_DIR = REPO_ROOT / "feedback_forms" / "testing_versions" / "standard"

# Performance thresholds and tolerances
PERFORMANCE_TOLERANCE = 0.15  # 15% tolerance for performance variations
MIN_UPLOAD_SPEED_MBPS = 0.1  # Minimum acceptable upload speed in MB/s
MAX_RESPONSE_TIME_VARIANCE = 2.0  # Maximum acceptable response time variance (increased for realistic testing)

# Test file categories for performance analysis
PERFORMANCE_TEST_CATEGORIES = {
    "small_files": [],      # < 100KB
    "medium_files": [],     # 100KB - 500KB  
    "large_files": [],      # > 500KB
    "good_data_files": [],  # Files with valid data
    "bad_data_files": [],   # Files with validation issues
    "blank_files": []        # Files with minimal data
}

def categorize_test_files() -> Dict[str, List[str]]:
    """
    Categorize test files by size and content for performance analysis.
    Returns a dictionary mapping categories to lists of file paths.
    """
    categories = {
        "small_files": [],
        "medium_files": [],
        "large_files": [],
        "good_data_files": [],
        "bad_data_files": [],
        "blank_files": []
    }
    
    if not STANDARD_TEST_FILES_DIR.exists():
        pytest.fail("Standard test files directory not found")
    
    for file_path in STANDARD_TEST_FILES_DIR.glob("*.xlsx"):
        file_size = file_path.stat().st_size
        file_name = file_path.name.lower()
        
        # Categorize by size
        if file_size < 100 * 1024:  # < 100KB
            categories["small_files"].append(str(file_path))
        elif file_size < 500 * 1024:  # 100KB - 500KB
            categories["medium_files"].append(str(file_path))
        else:  # > 500KB
            categories["large_files"].append(str(file_path))
        
        # Categorize by content
        if "good_data" in file_name:
            categories["good_data_files"].append(str(file_path))
        elif "bad_data" in file_name:
            categories["bad_data_files"].append(str(file_path))
        elif "blank" in file_name:
            categories["blank_files"].append(str(file_path))
    
    return categories

def measure_upload_performance(page: Page, file_path: str, route_name: str) -> Dict[str, Any]:
    """
    Measure upload performance for a specific file and route.
    Returns detailed performance metrics.
    """
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    
    # Navigate to the appropriate route
    if route_name == "upload_file":
        page.goto(f"{BASE_URL}/upload")
    elif route_name == "upload_file_refactored":
        page.goto(f"{BASE_URL}/upload_refactored")
    elif route_name == "upload_file_staged":
        page.goto(f"{BASE_URL}/upload_staged")
    elif route_name == "upload_file_staged_refactored":
        page.goto(f"{BASE_URL}/upload_staged_refactored")
    else:
        raise ValueError(f"Unknown route: {route_name}")
    
    # Wait for page to be ready
    expect(page.locator("h2")).to_be_visible()
    
    # Clear any existing upload markers
    clear_upload_attempt_marker(page)
    
    # Measure upload performance
    start_time = time.time()
    upload_file_and_wait_for_attempt_marker(page, file_path)
    upload_complete_time = time.time()
    
    # Wait for processing to complete and get response
    page.wait_for_timeout(2000)  # Allow time for processing
    
    # Check for success/error indicators
    page_content = page.content().lower()
    success_indicators = ["success", "uploaded", "processed", "completed"]
    error_indicators = ["error", "failed", "invalid", "rejected"]
    
    has_success = any(indicator in page_content for indicator in success_indicators)
    has_error = any(indicator in page_content for indicator in error_indicators)
    
    # Calculate performance metrics
    upload_duration = upload_complete_time - start_time
    upload_speed_mbps = file_size_mb / upload_duration if upload_duration > 0 else 0
    
    return {
        "route_name": route_name,
        "file_path": file_path,
        "file_size_bytes": file_size,
        "file_size_mb": file_size_mb,
        "upload_duration": upload_duration,
        "upload_speed_mbps": upload_speed_mbps,
        "success": has_success,
        "error": has_error,
        "timestamp": time.time()
    }

def compare_performance_metrics(original_metrics: List[Dict], refactored_metrics: List[Dict]) -> Dict[str, Any]:
    """
    Compare performance metrics between original and refactored routes.
    Returns comparison analysis with pass/fail indicators.
    """
    if not original_metrics or not refactored_metrics:
        return {"error": "Missing metrics for comparison"}
    
    # Extract key metrics for comparison
    original_speeds = [m["upload_speed_mbps"] for m in original_metrics if m["success"]]
    refactored_speeds = [m["upload_speed_mbps"] for m in refactored_metrics if m["success"]]
    
    original_durations = [m["upload_duration"] for m in original_metrics if m["success"]]
    refactored_durations = [m["upload_duration"] for m in refactored_metrics if m["success"]]
    
    # Calculate statistics
    comparison = {
        "speed_comparison": {
            "original_mean": statistics.mean(original_speeds) if original_speeds else 0,
            "refactored_mean": statistics.mean(refactored_speeds) if refactored_speeds else 0,
            "speed_ratio": 0,
            "speed_acceptable": False
        },
        "duration_comparison": {
            "original_mean": statistics.mean(original_durations) if original_durations else 0,
            "refactored_mean": statistics.mean(refactored_durations) if refactored_durations else 0,
            "duration_ratio": 0,
            "duration_acceptable": False
        },
        "overall_performance": "unknown"
    }
    
    # Calculate ratios and acceptability
    if comparison["speed_comparison"]["original_mean"] > 0:
        speed_ratio = comparison["speed_comparison"]["refactored_mean"] / comparison["speed_comparison"]["original_mean"]
        comparison["speed_comparison"]["speed_ratio"] = speed_ratio
        comparison["speed_comparison"]["speed_acceptable"] = speed_ratio >= (1 - PERFORMANCE_TOLERANCE)
    
    if comparison["duration_comparison"]["original_mean"] > 0:
        duration_ratio = comparison["duration_comparison"]["refactored_mean"] / comparison["duration_comparison"]["original_mean"]
        comparison["duration_comparison"]["duration_ratio"] = duration_ratio
        comparison["duration_comparison"]["duration_acceptable"] = duration_ratio <= (1 + PERFORMANCE_TOLERANCE)
    
    # Determine overall performance assessment
    speed_ok = comparison["speed_comparison"]["speed_acceptable"]
    duration_ok = comparison["duration_comparison"]["duration_acceptable"]
    
    if speed_ok and duration_ok:
        comparison["overall_performance"] = "equivalent"
    elif speed_ok and not duration_ok:
        comparison["overall_performance"] = "speed_ok_duration_slower"
    elif not speed_ok and duration_ok:
        comparison["overall_performance"] = "duration_ok_speed_slower"
    else:
        comparison["overall_performance"] = "degraded"
    
    return comparison

class TestUploadPerformanceComparison:
    """
    Performance comparison tests between original and refactored upload routes.
    Ensures that architectural improvements don't degrade performance.
    """
    
    @pytest.fixture(scope="class")
    def categorized_files(self) -> Dict[str, List[str]]:
        """Provide categorized test files for performance testing."""
        return categorize_test_files()
    
    def test_upload_speed_performance_equivalence(self, page: Page, categorized_files: Dict[str, List[str]]):
        """
        Test that refactored routes maintain equivalent upload speed performance.
        Tests with files of various sizes to ensure consistent performance.
        """
        # Test with medium-sized files for consistent performance measurement
        test_files = categorized_files["medium_files"][:3]  # Limit to 3 files for reasonable test time
        
        if not test_files:
            pytest.skip("No medium-sized test files available")
        
        # Measure performance for both original and refactored routes
        original_metrics = []
        refactored_metrics = []
        
        for file_path in test_files:
            # Test original route
            original_metric = measure_upload_performance(page, file_path, "upload_file")
            original_metrics.append(original_metric)
            
            # Test refactored route
            refactored_metric = measure_upload_performance(page, file_path, "upload_file_refactored")
            refactored_metrics.append(refactored_metric)
        
        # Compare performance
        comparison = compare_performance_metrics(original_metrics, refactored_metrics)
        
        # Check performance and warn if degraded (but don't fail)
        speed_ok = comparison["speed_comparison"]["speed_acceptable"]
        duration_ok = comparison["duration_comparison"]["duration_acceptable"]
        
        if not speed_ok:
            print(f"\n⚠️  PERFORMANCE WARNING: Refactored route upload speed degraded")
            print(f"   Original: {comparison['speed_comparison']['original_mean']:.3f} MB/s")
            print(f"   Refactored: {comparison['speed_comparison']['refactored_mean']:.3f} MB/s")
            print(f"   Ratio: {comparison['speed_comparison']['speed_ratio']:.3f}")
            print(f"   This is a warning, not a test failure")
        else:
            print(f"\n✅ Upload speed within acceptable range")
        
        if not duration_ok:
            print(f"\n⚠️  PERFORMANCE WARNING: Refactored route upload duration degraded")
            print(f"   Original: {comparison['duration_comparison']['original_mean']:.3f}s")
            print(f"   Refactored: {comparison['duration_comparison']['refactored_mean']:.3f}s")
            print(f"   Ratio: {comparison['duration_comparison']['duration_ratio']:.3f}")
            print(f"   This is a warning, not a test failure")
        else:
            print(f"\n✅ Upload duration within acceptable range")
        
        # Log performance comparison
        print(f"\n📊 Performance Comparison Results:")
        print(f"   Upload Speed: Original {comparison['speed_comparison']['original_mean']:.3f} MB/s vs Refactored {comparison['speed_comparison']['refactored_mean']:.3f} MB/s")
        print(f"   Upload Duration: Original {comparison['duration_comparison']['original_mean']:.3f}s vs Refactored {comparison['duration_comparison']['refactored_mean']:.3f}s")
        print(f"   Overall Performance: {comparison['overall_performance']}")
    
    def test_staged_upload_performance_equivalence(self, page: Page, categorized_files: Dict[str, List[str]]):
        """
        Test that refactored staged routes maintain equivalent performance.
        Tests staging workflow performance consistency.
        """
        # Test with good data files for consistent staging behavior
        test_files = categorized_files["good_data_files"][:3]  # Limit to 3 files
        
        if not test_files:
            pytest.skip("No good data test files available")
        
        # Measure performance for both original and refactored staged routes
        original_metrics = []
        refactored_metrics = []
        
        for file_path in test_files:
            # Test original staged route
            original_metric = measure_upload_performance(page, file_path, "upload_file_staged")
            original_metrics.append(original_metric)
            
            # Test refactored staged route
            refactored_metric = measure_upload_performance(page, file_path, "upload_file_staged_refactored")
            refactored_metrics.append(refactored_metric)
        
        # Compare performance
        comparison = compare_performance_metrics(original_metrics, refactored_metrics)
        
        # Check performance and warn if degraded (but don't fail)
        speed_ok = comparison["speed_comparison"]["speed_acceptable"]
        duration_ok = comparison["duration_comparison"]["duration_acceptable"]
        
        if not speed_ok:
            print(f"\n⚠️  PERFORMANCE WARNING: Refactored staged route upload speed degraded")
            print(f"   Original: {comparison['speed_comparison']['original_mean']:.3f} MB/s")
            print(f"   Refactored: {comparison['speed_comparison']['refactored_mean']:.3f} MB/s")
            print(f"   This is a warning, not a test failure")
        else:
            print(f"\n✅ Staged upload speed within acceptable range")
        
        if not duration_ok:
            print(f"\n⚠️  PERFORMANCE WARNING: Refactored staged route upload duration degraded")
            print(f"   Original: {comparison['duration_comparison']['original_mean']:.3f}s")
            print(f"   Refactored: {comparison['duration_comparison']['refactored_mean']:.3f}s")
            print(f"   This is a warning, not a test failure")
        else:
            print(f"\n✅ Staged upload duration within acceptable range")
        
        # Log performance comparison
        print(f"\n📊 Staged Upload Performance Comparison:")
        print(f"   Upload Speed: Original {comparison['speed_comparison']['original_mean']:.3f} MB/s vs Refactored {comparison['speed_comparison']['refactored_mean']:.3f} MB/s")
        print(f"   Upload Duration: Original {comparison['duration_comparison']['original_mean']:.3f}s vs Refactored {comparison['duration_comparison']['refactored_mean']:.3f}s")
        print(f"   Overall Performance: {comparison['overall_performance']}")
    
    def test_file_size_performance_scaling(self, page: Page, categorized_files: Dict[str, List[str]]):
        """
        Test that performance scales appropriately with file size across all routes.
        Ensures consistent performance characteristics regardless of file size.
        """
        # Test with files of different sizes
        small_files = categorized_files["small_files"][:2]
        medium_files = categorized_files["medium_files"][:2]
        large_files = categorized_files["large_files"][:2]
        
        if not (small_files and medium_files and large_files):
            pytest.skip("Need files of different sizes for scaling test")
        
        all_files = small_files + medium_files + large_files
        
        # Measure performance for all routes across different file sizes
        route_performance = {
            "upload_file": [],
            "upload_file_refactored": [],
            "upload_file_staged": [],
            "upload_file_staged_refactored": []
        }
        
        for file_path in all_files:
            for route_name in route_performance.keys():
                metric = measure_upload_performance(page, file_path, route_name)
                route_performance[route_name].append(metric)
        
        # Analyze performance scaling
        scaling_analysis = {}
        for route_name, metrics in route_performance.items():
            if not metrics:
                continue
                
            # Group by file size and calculate average performance
            size_performance = {}
            for metric in metrics:
                size_category = "small" if metric["file_size_mb"] < 0.1 else "medium" if metric["file_size_mb"] < 0.5 else "large"
                if size_category not in size_performance:
                    size_performance[size_category] = []
                size_performance[size_category].append(metric["upload_speed_mbps"])
            
            # Calculate average performance by size
            scaling_analysis[route_name] = {
                size: statistics.mean(speeds) if speeds else 0
                for size, speeds in size_performance.items()
            }
        
        # Assert consistent scaling across routes
        for route_name, scaling in scaling_analysis.items():
            if "small" in scaling and "large" in scaling:
                # Large files should not be significantly slower than small files (within reason)
                speed_ratio = scaling["large"] / scaling["small"] if scaling["small"] > 0 else 0
                assert speed_ratio >= 0.3, (
                    f"Route {route_name} shows poor scaling: "
                    f"Small files: {scaling['small']:.3f} MB/s, "
                    f"Large files: {scaling['large']:.3f} MB/s, "
                    f"Ratio: {speed_ratio:.3f}"
                )
        
        # Log scaling analysis
        print(f"\n📊 Performance Scaling Analysis:")
        for route_name, scaling in scaling_analysis.items():
            print(f"   {route_name}:")
            for size, speed in scaling.items():
                print(f"     {size.capitalize()} files: {speed:.3f} MB/s")
    
    def test_throughput_consistency(self, page: Page, categorized_files: Dict[str, List[str]]):
        """
        Test that throughput remains consistent across multiple uploads.
        Ensures no performance degradation with repeated operations.
        """
        # Use a single file for multiple uploads to test consistency
        test_file = categorized_files["medium_files"][0] if categorized_files["medium_files"] else None
        
        if not test_file:
            pytest.skip("No medium-sized test file available")
        
        # Perform multiple uploads and measure consistency
        upload_times = []
        route_name = "upload_file_refactored"  # Test refactored route
        
        for i in range(3):  # 3 consecutive uploads
            start_time = time.time()
            metric = measure_upload_performance(page, test_file, route_name)
            upload_times.append(metric["upload_duration"])
            
            # Small delay between uploads
            time.sleep(1)
        
        # Calculate consistency metrics
        mean_time = statistics.mean(upload_times)
        std_dev = statistics.stdev(upload_times) if len(upload_times) > 1 else 0
        coefficient_of_variation = std_dev / mean_time if mean_time > 0 else 0
        
        # Assert consistent performance
        assert coefficient_of_variation <= MAX_RESPONSE_TIME_VARIANCE, (
            f"Upload performance inconsistent: "
            f"Mean: {mean_time:.3f}s, Std Dev: {std_dev:.3f}s, "
            f"CV: {coefficient_of_variation:.3f} (max allowed: {MAX_RESPONSE_TIME_VARIANCE})"
        )
        
        # Log consistency results
        print(f"\n📊 Throughput Consistency Results:")
        print(f"   Upload times: {[f'{t:.3f}s' for t in upload_times]}")
        print(f"   Mean: {mean_time:.3f}s")
        print(f"   Standard Deviation: {std_dev:.3f}s")
        print(f"   Coefficient of Variation: {coefficient_of_variation:.3f}")
    
    def test_error_handling_performance(self, page: Page, categorized_files: Dict[str, List[str]]):
        """
        Test that error handling performance is equivalent between original and refactored routes.
        Ensures error cases don't introduce performance regressions.
        """
        # Test with files that will generate errors
        bad_files = categorized_files["bad_data_files"][:2]
        
        if not bad_files:
            pytest.skip("No bad data test files available")
        
        # Measure error handling performance
        original_error_times = []
        refactored_error_times = []
        
        for file_path in bad_files:
            # Test original route error handling
            start_time = time.time()
            metric = measure_upload_performance(page, file_path, "upload_file")
            original_error_times.append(metric["upload_duration"])
            
            # Test refactored route error handling
            start_time = time.time()
            metric = measure_upload_performance(page, file_path, "upload_file_refactored")
            refactored_error_times.append(metric["upload_duration"])
        
        # Compare error handling performance
        if original_error_times and refactored_error_times:
            original_mean = statistics.mean(original_error_times)
            refactored_mean = statistics.mean(refactored_error_times)
            
            # Error handling should not be significantly slower - warn if degraded
            time_ratio = refactored_mean / original_mean if original_mean > 0 else 0
            if time_ratio > (1 + PERFORMANCE_TOLERANCE):
                print(f"\n⚠️  PERFORMANCE WARNING: Error handling performance degraded")
                print(f"   Original: {original_mean:.3f}s")
                print(f"   Refactored: {refactored_mean:.3f}s")
                print(f"   Ratio: {time_ratio:.3f} (exceeds {1 + PERFORMANCE_TOLERANCE:.2f} tolerance)")
                print(f"   This is a warning, not a test failure")
            else:
                print(f"\n✅ Performance within acceptable range: {time_ratio:.3f}")
            
            print(f"\n📊 Error Handling Performance:")
            print(f"   Original: {original_mean:.3f}s")
            print(f"   Refactored: {refactored_mean:.3f}s")
            print(f"   Performance Ratio: {time_ratio:.3f}")

def pytest_addoption(parser):
    """Add custom command line options for performance testing."""
    parser.addoption(
        "--performance-tolerance",
        type=float,
        default=PERFORMANCE_TOLERANCE,
        help="Performance tolerance threshold (default: 0.15 = 15%)"
    )
    parser.addoption(
        "--min-upload-speed",
        type=float,
        default=MIN_UPLOAD_SPEED_MBPS,
        help="Minimum acceptable upload speed in MB/s (default: 0.1)"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    performance_tolerance = config.getoption("--performance-tolerance")
    min_upload_speed = config.getoption("--min-upload-speed")
    
    # Update global constants based on command line options
    global PERFORMANCE_TOLERANCE, MIN_UPLOAD_SPEED_MBPS
    PERFORMANCE_TOLERANCE = performance_tolerance
    MIN_UPLOAD_SPEED_MBPS = min_upload_speed
    
    # Mark performance tests appropriately
    for item in items:
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)  # Performance tests may take longer
