#!/bin/bash
# Script to export OpenAPI schema from backend
# This avoids complex shell escaping in docker-compose.override.yml

set -e

# Use environment variable for output path, with fallback to default
OUTPUT_PATH="${OPENAPI_OUTPUT_PATH:-/app/frontend/openapi.json}"

# Change to backend directory
cd /app/backend

# Export OpenAPI schema
uv run python -c "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > "$OUTPUT_PATH"

echo "OpenAPI schema exported successfully to $OUTPUT_PATH"