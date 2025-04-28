#!/usr/bin/env python
"""
Custom test runner that bypasses the Django migrations system
and uses an in-memory SQLite database for testing.
"""
import os
import sys
import subprocess

def main():
    """Run tests with pytest and proper configuration"""
    # Determine the test path from arguments or run all tests
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
    else:
        test_path = "base/tests/"
    
    # Build command
    command = [
        "python", "-m", "pytest", 
        test_path,
        "--nomigrations",  # Skip migrations
        "-v"               # Verbose output
    ]
    
    # Run pytest with the proper configuration
    result = subprocess.run(command)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 