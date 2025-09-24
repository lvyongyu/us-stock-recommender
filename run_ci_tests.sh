#!/bin/bash
# Continuous Integration Test Script for US Stock Recommendation System

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "US Stock Recommendation System - CI Tests"
echo "=========================================="
echo "Current directory: $(pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$2" -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
    fi
}

# Initialize error counter
ERROR_COUNT=0

# Check Python version
echo "Python version: $(python3 --version)"

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "No virtual environment found. Using system Python."
else
    echo "Using virtual environment: $VIRTUAL_ENV"
fi

echo ""

# Check dependencies
echo "Checking dependencies..."
pip3 show yfinance pandas scikit-learn > /dev/null 2>&1
DEPS_STATUS=$?

if [ $DEPS_STATUS -ne 0 ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip3 install -r requirements.txt
    DEPS_STATUS=$?
fi

print_status "Dependencies check" $DEPS_STATUS

echo ""

# Run syntax check
echo "Running syntax check..."
python3 -m py_compile stock_recommender.py
SYNTAX_STATUS=$?
print_status "Syntax check" $SYNTAX_STATUS
if [ $SYNTAX_STATUS -ne 0 ]; then
    ((ERROR_COUNT++))
fi

echo ""

# Run unit tests
echo "Running unit tests..."
(cd tests && python3 run_tests.py --quick) > test_output.log 2>&1
UNIT_TEST_STATUS=$?
print_status "Unit tests" $UNIT_TEST_STATUS

if [ $UNIT_TEST_STATUS -ne 0 ]; then
    echo "Unit test failures detected. Last 20 lines of output:"
    tail -20 test_output.log
    ((ERROR_COUNT++))
fi

echo ""

# Run integration tests
echo "Running integration tests..."
(cd tests && python3 run_tests.py --integration) >> test_output.log 2>&1
INTEGRATION_TEST_STATUS=$?
print_status "Integration tests" $INTEGRATION_TEST_STATUS

if [ $INTEGRATION_TEST_STATUS -ne 0 ]; then
    echo "Integration test failures detected. Last 20 lines of output:"
    tail -20 test_output.log
    ((ERROR_COUNT++))
fi

echo ""

# Run smoke test (basic functionality)
echo "Running smoke test..."
{
    echo "Testing basic functionality..."
    python3 -c "
import sys
sys.path.append('src')
from src.languages.config import LanguageConfig
config = LanguageConfig('en')
print('Language config test: PASSED')
"
} > smoke_test.log 2>&1
SMOKE_TEST_STATUS=$?

print_status "Smoke test" $SMOKE_TEST_STATUS

if [ $SMOKE_TEST_STATUS -ne 0 ]; then
    echo "Smoke test failures:"
    cat smoke_test.log
    ((ERROR_COUNT++))
else
    echo "$(cat smoke_test.log)"
fi

echo ""

# Performance test (optional)
echo "Running performance test..."
{
    echo "Testing mock data generation performance..."
    python3 -c "
import sys
sys.path.append('tests')
import time
from test_utils import MockStockData

start_time = time.time()
data = MockStockData.create_sample_data(100)
end_time = time.time()

execution_time = end_time - start_time
if execution_time < 1.0:
    print(f'Performance test: PASSED ({execution_time:.3f}s)')
else:
    print(f'Performance test: SLOW ({execution_time:.3f}s)')
    exit(1)
"
} > perf_test.log 2>&1
PERF_TEST_STATUS=$?

print_status "Performance test" $PERF_TEST_STATUS

if [ $PERF_TEST_STATUS -ne 0 ]; then
    ((ERROR_COUNT++))
else
    echo "$(cat perf_test.log)"
fi

echo ""

# Cleanup
rm -f test_output.log smoke_test.log perf_test.log

# Summary
echo "=========================================="
echo "OVERALL TEST RESULTS:"
echo "=========================================="

if [ $SYNTAX_STATUS -ne 0 ]; then
    echo -e "${RED}✗ Syntax Check${NC}"
fi

if [ $UNIT_TEST_STATUS -ne 0 ]; then
    echo -e "${RED}✗ Unit Tests${NC}"
fi

if [ $INTEGRATION_TEST_STATUS -ne 0 ]; then
    echo -e "${RED}✗ Integration Tests${NC}"
fi

if [ $SMOKE_TEST_STATUS -ne 0 ]; then
    echo -e "${RED}✗ Smoke Test${NC}"
fi

if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! System is ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERROR_COUNT test suite(s) failed. Please check the issues above.${NC}"
    exit 1
fi
