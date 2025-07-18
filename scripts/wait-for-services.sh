#!/bin/bash
# Wait for services to be ready before running tests

set -e

# Configuration
MAX_WAIT_TIME=120  # Maximum wait time in seconds
SLEEP_INTERVAL=2   # Sleep interval between checks

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Services to check
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

echo "🔄 Waiting for services to be ready..."

# Function to check if a URL is responding
check_http_service() {
    local url=$1
    local service_name=$2
    local elapsed=0
    
    echo -e "${YELLOW}Checking $service_name at $url...${NC}"
    
    while [ $elapsed -lt $MAX_WAIT_TIME ]; do
        if curl -f -s "$url/health" > /dev/null 2>&1 || curl -f -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $service_name is ready${NC}"
            return 0
        fi
        
        sleep $SLEEP_INTERVAL
        elapsed=$((elapsed + SLEEP_INTERVAL))
        echo -n "."
    done
    
    echo -e "\n${RED}✗ $service_name failed to start within $MAX_WAIT_TIME seconds${NC}"
    return 1
}

# Function to check Redis
check_redis() {
    local elapsed=0
    
    echo -e "${YELLOW}Checking Redis at $REDIS_HOST:$REDIS_PORT...${NC}"
    
    while [ $elapsed -lt $MAX_WAIT_TIME ]; do
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis is ready${NC}"
            return 0
        fi
        
        sleep $SLEEP_INTERVAL
        elapsed=$((elapsed + SLEEP_INTERVAL))
        echo -n "."
    done
    
    echo -e "\n${RED}✗ Redis failed to start within $MAX_WAIT_TIME seconds${NC}"
    return 1
}

# Function to check Docker containers
check_docker_containers() {
    if command -v docker &> /dev/null; then
        echo -e "${YELLOW}Checking Docker containers...${NC}"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    fi
}

# Main checks
FAILED=0

# Check backend
if ! check_http_service "$BACKEND_URL" "Backend API"; then
    FAILED=1
fi

# Check frontend (only if not in CI or if explicitly requested)
if [ "${CHECK_FRONTEND:-true}" = "true" ] && [ "${CI:-false}" != "true" ]; then
    if ! check_http_service "$FRONTEND_URL" "Frontend"; then
        FAILED=1
    fi
fi

# Check Redis (only if Redis is expected to be running)
if [ "${CHECK_REDIS:-false}" = "true" ]; then
    if command -v redis-cli &> /dev/null; then
        if ! check_redis; then
            FAILED=1
        fi
    else
        echo -e "${YELLOW}⚠ Redis CLI not found, skipping Redis check${NC}"
    fi
fi

# Show container status if available
check_docker_containers

# Voice modality specific checks
if [ "${VOICE_MODE_ENABLED:-false}" = "true" ]; then
    echo -e "\n${YELLOW}Performing voice modality checks...${NC}"
    
    # Check if voice endpoint responds
    if curl -f -s "$BACKEND_URL/api/send/test-voice" \
        -H "Content-Type: application/json" \
        -d '{"mime_type": "audio/pcm", "data": ""}' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Voice endpoint is accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Voice endpoint returned an error (this may be expected)${NC}"
    fi
    
    # Check metrics endpoint
    if curl -f -s "$BACKEND_URL/api/metrics" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Metrics endpoint is ready${NC}"
    fi
fi

# Summary
echo -e "\n================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All services are ready!${NC}"
    
    # Additional info for voice mode
    if [ "${VOICE_MODE_ENABLED:-false}" = "true" ]; then
        echo -e "${GREEN}🎤 Voice modality is enabled${NC}"
    fi
else
    echo -e "${RED}❌ Some services failed to start${NC}"
    echo -e "${YELLOW}Check the logs with: docker-compose logs${NC}"
    exit 1
fi

# Optional: Wait a bit more for services to stabilize
if [ "${EXTRA_WAIT:-0}" -gt 0 ]; then
    echo -e "\n${YELLOW}Waiting ${EXTRA_WAIT}s for services to stabilize...${NC}"
    sleep "$EXTRA_WAIT"
fi

echo -e "================================\n"
exit 0