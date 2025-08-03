#!/bin/bash

# Generate OpenAPI schema from backend and update frontend
# This script can be run manually or is automatically triggered by pre-commit hooks

set -e

# Get the script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔄 Generating OpenAPI schema from backend..."

# Change to backend directory
cd "$REPO_ROOT/backend"

# Generate OpenAPI schema
uv run python -c "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > "$REPO_ROOT/frontend/openapi.json"

# Check if generation was successful
if [ ! -f "$REPO_ROOT/frontend/openapi.json" ]; then
    echo "❌ Failed to generate OpenAPI schema"
    exit 1
fi

LINES=$(wc -l < "$REPO_ROOT/frontend/openapi.json")
echo "✅ Generated OpenAPI schema ($LINES lines)"

# Verify required endpoints exist
if grep -q "getUiFeatureFlags" "$REPO_ROOT/frontend/openapi.json"; then
    echo "✅ Required endpoints found in schema"
else
    echo "❌ Missing required endpoints in schema"
    exit 1
fi

# Change to frontend directory and regenerate TypeScript client
cd "$REPO_ROOT/frontend"

echo "🔄 Regenerating TypeScript API client..."
pnpm run generate:api

# Verify TypeScript client was generated correctly
if [ ! -f "./lib/api/generated/sdk.gen.ts" ]; then
    echo "❌ Failed to generate TypeScript API client"
    exit 1
fi

if grep -q "getUiFeatureFlags" "./lib/api/generated/sdk.gen.ts"; then
    echo "✅ TypeScript API client generated successfully"
else
    echo "❌ TypeScript API client missing required functions"
    exit 1
fi

echo "🎉 OpenAPI schema and TypeScript client updated successfully!"
