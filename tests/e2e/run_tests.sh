#!/bin/bash
# E2E Test Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Running E2E Tests${NC}"

# Change to test directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt
playwright install --with-deps chromium

# Export test environment variables
export $(cat .env.test | xargs)

# Start Docker Compose services
echo -e "${YELLOW}Starting Docker services...${NC}"
docker-compose -f ../../docker-compose.yml -f docker-compose.test.yml up -d

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    if [ "${KEEP_SERVICES:-false}" != "true" ]; then
        docker-compose -f ../../docker-compose.yml -f docker-compose.test.yml down
    fi
    deactivate
}
trap cleanup EXIT

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
max_wait=60
waited=0
while ! curl -s http://localhost:8000/health > /dev/null 2>&1 || ! curl -s http://localhost:3000 > /dev/null 2>&1; do
    if [ $waited -ge $max_wait ]; then
        echo -e "${RED}Services did not become healthy in time${NC}"
        docker-compose -f ../../docker-compose.yml -f docker-compose.test.yml logs
        exit 1
    fi
    sleep 2
    waited=$((waited + 2))
    echo -n "."
done
echo -e "\n${GREEN}Services are ready!${NC}"

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
pytest "$@"

echo -e "${GREEN}✅ Tests completed${NC}"