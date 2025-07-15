#!/bin/bash
# Script to export OpenAPI schema from backend
# This avoids complex shell escaping in docker-compose.override.yml

set -e

# Change to backend directory
cd /app/backend

# Export OpenAPI schema
uv run python -c "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > /app/frontend/openapi.json

echo "OpenAPI schema exported successfully to /app/frontend/openapi.json"