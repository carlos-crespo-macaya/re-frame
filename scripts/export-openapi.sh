#!/bin/bash
# Script to export OpenAPI schema from backend
# This avoids complex shell escaping in docker-compose.override.yml

set -e

# Use environment variable for output path, with fallback to default
OUTPUT_PATH="${OPENAPI_OUTPUT_PATH:-/app/exports/openapi.json}"

# Ensure the output directory exists with proper permissions
OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
mkdir -p "$OUTPUT_DIR" || true
chmod 777 "$OUTPUT_DIR" || true

# Change to backend directory
cd /app

# Export OpenAPI schema
uv run python -c "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > "$OUTPUT_PATH"

echo "OpenAPI schema exported successfully to $OUTPUT_PATH"