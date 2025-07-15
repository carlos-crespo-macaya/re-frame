#!/bin/bash
# Script to build Docker images with proper OpenAPI schema generation

set -e

echo "🔧 Building re-frame with OpenAPI schema generation..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: This script must be run from the project root directory"
    exit 1
fi

# Parse arguments
BUILD_MODE=${1:-development}
EXPORT_SCHEMA_ONLY=${2:-false}

print_step "Build mode: $BUILD_MODE"

if [ "$BUILD_MODE" = "production" ]; then
    # Production build with multi-stage Dockerfile
    print_step "Building production images..."
    
    # Build using the production compose file
    docker-compose -f docker-compose.prod.yml build
    
    print_success "Production images built successfully!"
    
elif [ "$BUILD_MODE" = "development" ]; then
    # Development build
    print_step "Building development images..."
    
    # Build the standard images
    docker-compose build
    
    print_success "Development images built successfully!"
    
elif [ "$BUILD_MODE" = "schema-only" ]; then
    # Just export the schema
    print_step "Exporting OpenAPI schema only..."
    
    # Build and run backend temporarily to export schema
    docker-compose run --rm -T backend sh -c "
        uv run python -c 'from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))'
    " > frontend/openapi.json
    
    print_success "OpenAPI schema exported to frontend/openapi.json"
    
    # Generate TypeScript client
    print_step "Generating TypeScript client..."
    cd frontend && pnpm run generate:api
    
    print_success "TypeScript client generated!"
    
else
    echo "Usage: $0 [development|production|schema-only]"
    exit 1
fi

# Final instructions
echo ""
print_step "Next steps:"
if [ "$BUILD_MODE" = "production" ]; then
    echo "  Run: docker-compose -f docker-compose.prod.yml up"
elif [ "$BUILD_MODE" = "development" ]; then
    echo "  Run: docker-compose up"
elif [ "$BUILD_MODE" = "schema-only" ]; then
    echo "  The TypeScript client has been generated in frontend/lib/api/generated/"
fi