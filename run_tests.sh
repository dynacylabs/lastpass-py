ls
#!/bin/bash
# LastPass Python Test Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

print_message "$BLUE" "================================================"
print_message "$BLUE" "   LastPass Python - Test Suite Runner"
print_message "$BLUE" "================================================"
echo

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_message "$RED" "Error: pytest is not installed"
    print_message "$YELLOW" "Install with: pip install -e .[dev]"
    exit 1
fi

# Parse command line arguments
MODE="mock"
COVERAGE=true
VERBOSE=""
LIVE_USERNAME=""
LIVE_PASSWORD=""
LIVE_OTP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --live)
            MODE="live"
            shift
            ;;
        --all)
            MODE="all"
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        --username=*)
            LIVE_USERNAME="${1#*=}"
            shift
            ;;
        --username)
            LIVE_USERNAME="$2"
            shift 2
            ;;
        --password=*)
            LIVE_PASSWORD="${1#*=}"
            shift
            ;;
        --password)
            LIVE_PASSWORD="$2"
            shift 2
            ;;
        --otp=*)
            LIVE_OTP="${1#*=}"
            shift
            ;;
        --otp)
            LIVE_OTP="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --live              Run live API tests (requires credentials)"
            echo "  --all               Run both mock and live tests for full coverage"
            echo "  --no-coverage       Skip coverage report"
            echo "  -v, --verbose       Verbose output"
            echo "  --username EMAIL    LastPass username for live tests"
            echo "  --password PASS     LastPass password for live tests"
            echo "  --otp CODE          Email verification code (if required)"
            echo "  -h, --help          Show this help message"
            echo
            echo "Examples:"
            echo "  $0                  # Run mock tests with coverage"
            echo "  $0 --live --username=user@example.com --password=pass"
            echo "  $0 --all --username=user@example.com --password=pass  # Full coverage"
            echo "  $0 --live --username=user@example.com --password=pass --otp=123456"
            echo "  $0 --no-coverage"
            exit 0
            ;;
        *)
            print_message "$RED" "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest tests/"

if [ "$VERBOSE" != "" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
fi

if [ "$COVERAGE" = false ]; then
    PYTEST_CMD="$PYTEST_CMD --no-cov"
fi

if [ "$MODE" = "live" ]; then
    print_message "$YELLOW" "Running LIVE API tests"
    print_message "$YELLOW" "Warning: This will access the real LastPass API!"
    echo
    
    if [ -z "$LIVE_USERNAME" ] || [ -z "$LIVE_PASSWORD" ]; then
        print_message "$RED" "Error: Live tests require --username and --password"
        exit 1
    fi
    
    PYTEST_CMD="$PYTEST_CMD --live --username=$LIVE_USERNAME --password=$LIVE_PASSWORD"
    
    if [ -n "$LIVE_OTP" ]; then
        PYTEST_CMD="$PYTEST_CMD --otp=$LIVE_OTP"
    fi
elif [ "$MODE" = "all" ]; then
    print_message "$BLUE" "Running ALL tests (mock + live) for complete coverage"
    print_message "$YELLOW" "Warning: This will access the real LastPass API!"
    echo
    
    if [ -z "$LIVE_USERNAME" ] || [ -z "$LIVE_PASSWORD" ]; then
        print_message "$RED" "Error: Live tests require --username and --password"
        exit 1
    fi
    
    PYTEST_CMD="$PYTEST_CMD --live --username=$LIVE_USERNAME --password=$LIVE_PASSWORD"
    
    if [ -n "$LIVE_OTP" ]; then
        PYTEST_CMD="$PYTEST_CMD --otp=$LIVE_OTP"
    fi
else
    print_message "$GREEN" "Running MOCK tests (no API access)"
    echo
    PYTEST_CMD="$PYTEST_CMD -m 'not live'"
fi

# Run tests
print_message "$BLUE" "Executing: $PYTEST_CMD"
echo

eval $PYTEST_CMD
TEST_EXIT_CODE=$?

echo
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_message "$GREEN" "✓ All tests passed!"
else
    print_message "$RED" "✗ Some tests failed"
fi

exit $TEST_EXIT_CODE
