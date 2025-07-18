#!/bin/bash

# Integration testing script for re-frame CBT Assistant POC
# This script provides multiple options for running integration tests

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_MODE="local"
HEADED=false
DEBUG=false
UI=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --docker)
      TEST_MODE="docker"
      shift
      ;;
    --headed)
      HEADED=true
      shift
      ;;
    --debug)
      DEBUG=true
      shift
      ;;
    --ui)
      UI=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --docker    Run tests in Docker containers"
      echo "  --headed    Run tests with browser visible"
      echo "  --debug     Run tests in debug mode"
      echo "  --ui        Run tests in Playwright UI mode"
      echo "  --help      Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

echo -e "${GREEN}Re-frame Integration Testing${NC}"
echo "================================"
echo "Test mode: $TEST_MODE"

cd "$PROJECT_ROOT"

# Function to check if a port is in use
check_port() {
  local port=$1
  if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Function to wait for a service to be ready
wait_for_service() {
  local url=$1
  local name=$2
  local max_attempts=30
  local attempt=0
  
  echo -n "Waiting for $name to be ready..."
  while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "$url" > /dev/null 2>&1; then
      echo -e " ${GREEN}Ready!${NC}"
      return 0
    fi
    echo -n "."
    sleep 1
    attempt=$((attempt + 1))
  done
  
  echo -e " ${RED}Failed!${NC}"
  return 1
}

# Function to cleanup on exit
cleanup() {
  echo ""
  echo "Cleaning up..."
  if [ "$TEST_MODE" = "docker" ]; then
    docker-compose -f docker-compose.integration.yml down
  fi
}

trap cleanup EXIT

# Install Playwright if needed
if [ ! -d "frontend/node_modules/@playwright" ]; then
  echo -e "${YELLOW}Installing Playwright...${NC}"
  pnpm test:e2e:install
fi

if [ "$TEST_MODE" = "docker" ]; then
  echo -e "${YELLOW}Starting Docker containers...${NC}"
  
  # Build and start containers
  docker-compose -f docker-compose.integration.yml up -d --build
  
  # Wait for services
  wait_for_service "http://localhost:3000" "Frontend" || exit 1
  wait_for_service "http://localhost:8000/health" "Backend" || exit 1
  
  # Run tests in container
  echo -e "${YELLOW}Running tests in Docker...${NC}"
  docker-compose -f docker-compose.integration.yml run --rm playwright
  
else
  # Local mode
  echo -e "${YELLOW}Checking local services...${NC}"
  
  # Check if services are already running
  FRONTEND_RUNNING=false
  BACKEND_RUNNING=false
  
  if check_port 3000; then
    echo "Frontend already running on port 3000"
    FRONTEND_RUNNING=true
  fi
  
  if check_port 8000; then
    echo "Backend already running on port 8000"
    BACKEND_RUNNING=true
  fi
  
  # Start services if not running
  if [ "$FRONTEND_RUNNING" = false ] || [ "$BACKEND_RUNNING" = false ]; then
    echo -e "${YELLOW}Starting required services...${NC}"
    
    # This will use Playwright's webServer config to start services
    # No need to manually start them
  fi
  
  # Build command based on options
  TEST_CMD="pnpm test:e2e"
  
  if [ "$UI" = true ]; then
    TEST_CMD="pnpm test:e2e:ui"
  elif [ "$DEBUG" = true ]; then
    TEST_CMD="pnpm test:e2e:debug"
  elif [ "$HEADED" = true ]; then
    TEST_CMD="pnpm test:e2e:headed"
  fi
  
  # Run tests
  echo -e "${YELLOW}Running tests...${NC}"
  echo "Command: $TEST_CMD"
  
  $TEST_CMD
fi

# Check test results
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ All tests passed!${NC}"
  
  # Offer to show report
  echo ""
  echo "View test report with: pnpm test:e2e:report"
else
  echo -e "${RED}✗ Some tests failed${NC}"
  echo ""
  echo "View detailed results with: pnpm test:e2e:report"
  exit 1
fi