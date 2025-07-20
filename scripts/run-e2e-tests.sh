#!/bin/bash
# E2E test runner for re-frame CBT Assistant
# Uses docker-compose.integration.yml for containerized testing

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Default options
TEST_TYPE=""
HEADED=""
DEBUG=""
UI=""
KEEP_RUNNING=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --text)
      TEST_TYPE="text"
      shift
      ;;
    --voice)
      TEST_TYPE="voice"
      shift
      ;;
    --headed)
      HEADED="--headed"
      shift
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    --ui)
      UI="--ui"
      shift
      ;;
    --keep-running)
      KEEP_RUNNING=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --text         Run only text-based tests"
      echo "  --voice        Run only voice-based tests"
      echo "  --headed       Run tests with browser visible"
      echo "  --debug        Run tests in debug mode"
      echo "  --ui           Run tests in Playwright UI mode"
      echo "  --keep-running Keep containers running after tests"
      echo "  --help         Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

echo -e "${GREEN}🧪 Re-frame E2E Testing (Docker)${NC}"
echo "======================================="

# Build test filter
TEST_FILTER=""
if [ "$TEST_TYPE" = "text" ]; then
  TEST_FILTER="--grep text"
  echo "Running: Text workflow tests only"
elif [ "$TEST_TYPE" = "voice" ]; then
  TEST_FILTER="--grep voice"
  echo "Running: Voice workflow tests only"
else
  echo "Running: All E2E tests"
fi

# Clean up function
cleanup() {
  if [ "$KEEP_RUNNING" = false ]; then
    echo -e "\n${YELLOW}Cleaning up Docker containers...${NC}"
    docker-compose -f docker-compose.integration.yml down -v
  else
    echo -e "\n${YELLOW}Keeping containers running. To stop: docker-compose -f docker-compose.integration.yml down${NC}"
  fi
}

trap cleanup EXIT INT TERM

# Start services
echo -e "\n${YELLOW}Starting Docker services...${NC}"
docker-compose -f docker-compose.integration.yml up -d --build frontend-test backend-test

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
./scripts/wait-for-services.sh http://localhost:3000 http://localhost:8000/health

# Build Playwright command with all options
PLAYWRIGHT_ARGS=""
if [ -n "$TEST_FILTER" ]; then
  PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS $TEST_FILTER"
fi
if [ -n "$HEADED" ]; then
  PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS $HEADED"
fi
if [ -n "$DEBUG" ]; then
  PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS $DEBUG"
fi
if [ -n "$UI" ]; then
  PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS $UI"
fi

# Run Playwright tests in container
echo -e "\n${GREEN}Running E2E tests...${NC}"
docker-compose -f docker-compose.integration.yml run --rm playwright pnpm playwright test $PLAYWRIGHT_ARGS

echo -e "\n${GREEN}✅ E2E tests completed!${NC}"