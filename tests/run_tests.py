#!/usr/bin/env python3
"""
Test runner for US Stock Recommendation System
Run all unit tests and integration tests
"""

import unittest
import sys
import os
from io import StringIO

# Add src directory to path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, parent_dir)
sys.path.insert(0, src_dir)


def run_tests(verbosity=2, pattern='test_*.py'):
    """
    Run all tests
    
    Args:
        verbosity: Test verbosity level (0=quiet, 1=normal, 2=verbose)
        pattern: Test file pattern to match
    """
    print("=" * 70)
    print("US STOCK RECOMMENDATION SYSTEM - TEST SUITE")
    print("=" * 70)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    test_dir = os.path.dirname(__file__)
    suite = loader.discover(test_dir, pattern=pattern)
    
    # Count tests
    test_count = suite.countTestCases()
    print(f"Found {test_count} tests")
    print("-" * 70)
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=False,
        buffer=True
    )
    
    result = runner.run(suite)
    
    print("-" * 70)
    print("TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Error:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    print("=" * 70)
    
    return result.wasSuccessful()


def run_specific_test(test_module):
    """
    Run a specific test module
    
    Args:
        test_module: Name of test module (e.g., 'test_strategies')
    """
    print(f"Running specific test: {test_module}")
    print("-" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_quick_tests():
    """Run only quick unit tests (exclude integration tests)"""
    print("Running quick unit tests (excluding integration tests)...")
    return run_tests(verbosity=1, pattern='test_*.py')


def run_integration_tests_only():
    """Run only integration tests"""
    print("Running integration tests only...")
    return run_tests(verbosity=2, pattern='test_integration.py')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for US Stock Recommendation System')
    parser.add_argument('--quick', action='store_true', 
                       help='Run only quick unit tests')
    parser.add_argument('--integration', action='store_true', 
                       help='Run only integration tests')
    parser.add_argument('--module', type=str, 
                       help='Run specific test module (e.g., test_strategies)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        if args.module:
            success = run_specific_test(args.module)
        elif args.quick:
            success = run_quick_tests()
        elif args.integration:
            success = run_integration_tests_only()
        else:
            verbosity = 2 if args.verbose else 1
            success = run_tests(verbosity=verbosity)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running tests: {e}")
        sys.exit(1)
