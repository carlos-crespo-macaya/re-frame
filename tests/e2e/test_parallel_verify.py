#!/usr/bin/env python3
"""
Quick script to verify parallel test execution is working.
"""
import subprocess
import sys


def main():
    """Run a quick test to verify parallel execution."""
    print("Verifying pytest-xdist parallel execution...")
    print("-" * 60)
    
    # Run pytest with dry-run to see worker allocation
    cmd = ["pytest", "--collect-only", "-q"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        test_count = len([line for line in result.stdout.split('\n') if '<Function' in line])
        print(f"Found {test_count} tests")
    
    # Run a quick test with visible workers
    print("\nRunning sample tests to show worker allocation...")
    print("-" * 60)
    
    cmd = ["pytest", "-v", "-k", "test_multi_turn_conversation or test_session_persistence", "--tb=no"]
    subprocess.run(cmd)
    
    print("\n" + "-" * 60)
    print("If you saw [gw0], [gw1], etc. in the output, parallel execution is working!")
    print("Run 'pytest' to execute all tests in parallel.")


if __name__ == "__main__":
    main()