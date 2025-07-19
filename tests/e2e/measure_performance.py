#!/usr/bin/env python3
"""
Script to measure E2E test performance with and without parallelization.
"""
import subprocess
import time
import sys
import os


def run_tests(parallel=True):
    """Run tests and measure execution time."""
    cmd = ["pytest"]
    if not parallel:
        cmd.extend(["-n", "0"])  # Disable parallelization
    
    print(f"\n{'='*60}")
    print(f"Running tests {'in parallel' if parallel else 'serially'}...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, "HEADLESS": "true"}
        )
        
        elapsed_time = time.time() - start_time
        
        # Extract test count from output
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if "passed" in line or "failed" in line:
                print(line)
        
        return elapsed_time, result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 0, False


def main():
    """Compare serial vs parallel test execution."""
    print("E2E Test Performance Comparison")
    print("==============================")
    
    # Ensure we're in the right directory
    if not os.path.exists("pytest.ini"):
        print("Error: Must be run from tests/e2e directory")
        sys.exit(1)
    
    # Run tests serially
    serial_time, serial_success = run_tests(parallel=False)
    
    # Run tests in parallel
    parallel_time, parallel_success = run_tests(parallel=True)
    
    # Calculate improvement
    if serial_time > 0 and parallel_time > 0:
        speedup = serial_time / parallel_time
        improvement = ((serial_time - parallel_time) / serial_time) * 100
        
        print(f"\n{'='*60}")
        print("Performance Summary:")
        print(f"{'='*60}")
        print(f"Serial execution:   {serial_time:.2f} seconds")
        print(f"Parallel execution: {parallel_time:.2f} seconds")
        print(f"Speedup:            {speedup:.2f}x")
        print(f"Time saved:         {serial_time - parallel_time:.2f} seconds ({improvement:.1f}%)")
        print(f"\nSerial tests {'passed' if serial_success else 'failed'}")
        print(f"Parallel tests {'passed' if parallel_success else 'failed'}")
    else:
        print("\nError: Could not measure performance")


if __name__ == "__main__":
    main()