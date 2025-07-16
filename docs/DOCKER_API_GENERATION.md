# Docker Build with API Client Generation

This document explains how the Docker build process handles automatic TypeScript client generation from the FastAPI OpenAPI schema.

## Overview

The Docker build process ensures that:
1. Backend generates an up-to-date OpenAPI schema
2. Frontend generates TypeScript client from this schema
3. Both services are built with proper type synchronization

## Build Configurations

### Development Build

Uses `docker-compose.yml` with `docker-compose.override.yml`:

```bash
docker-compose up --build
```

Features:
- Hot reloading for both frontend and backend
- Automatic schema export when backend starts
- Automatic client regeneration when frontend starts
- Shared volume for schema transfer

### Production Build

Uses `docker-compose.prod.yml` with multi-stage builds:

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up
```

Features:
- Optimized production images
- Schema generated during build (not runtime)
- No development dependencies in final images
- Proper security with non-root users

### Schema-Only Export

Just export the schema without running services:

```bash
./scripts/docker-build-with-schema.sh schema-only
```

This is useful for local development when you just need to update types.

## How It Works

### Development Workflow

1. **Backend starts** and exports OpenAPI schema to a shared volume
2. **Frontend waits** for the schema to be available
3. **Frontend generates** TypeScript client before starting dev server
4. Both services run with hot reloading

### Production Workflow

1. **Multi-stage build** compiles backend in first stage
2. **Schema extraction** happens during backend build
3. **Frontend build** copies schema from backend stage
4. **Client generation** happens before Next.js build
5. **Final images** contain only production code

## File Structure

```
re-frame/
├── docker-compose.yml              # Base development config
├── docker-compose.override.yml     # Development overrides for API generation
├── docker-compose.prod.yml         # Production configuration
├── backend/
│   └── Dockerfile                  # Backend with schema export
├── frontend/
│   ├── Dockerfile                  # Standard frontend build
│   └── Dockerfile.multistage       # Production build with schema
└── scripts/
    └── docker-build-with-schema.sh # Helper script
```

## Common Issues

### Schema Not Found

If the frontend can't find the OpenAPI schema:
1. Check that backend is healthy: `docker-compose ps`
2. Verify schema generation: `docker-compose logs backend | grep "OpenAPI"`
3. Check shared volume: `docker volume ls`

### Client Generation Fails

If TypeScript client generation fails:
1. Check that `openapi.json` is valid JSON
2. Verify all backend endpoints have proper type annotations
3. Check frontend logs: `docker-compose logs frontend`

### Type Mismatches

If you get TypeScript errors after generation:
1. Ensure backend is using latest code
2. Rebuild both images: `docker-compose build --no-cache`
3. Check that Pydantic models match frontend usage

## Best Practices

1. **Always rebuild both services** when changing API:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up
   ```

2. **Use production build for deployment**:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

3. **Test locally first**:
   ```bash
   ./scripts/docker-build-with-schema.sh development
   ```

4. **Keep schema in sync**:
   - Backend changes require frontend rebuild
   - Use CI/CD to enforce synchronization

## Environment Variables

### Backend
- `GEMINI_API_KEY`: Required for AI functionality
- `ENVIRONMENT`: Set to `development` or `production`
- `LOG_LEVEL`: Controls logging verbosity

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_ENVIRONMENT`: Environment name

## CI/CD Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Build with API Generation
  run: |
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    docker-compose -f docker-compose.prod.yml run --rm frontend pnpm test
```

## Debugging

Enable verbose logging:

```bash
# See schema generation
docker-compose logs backend | grep -A 20 "Exporting OpenAPI"

# See client generation
docker-compose logs frontend | grep -A 20 "Generating TypeScript"

# Check schema contents
docker-compose exec backend cat /app/exports/openapi.json | jq .

# Verify generated client
docker-compose exec frontend ls -la lib/api/generated/
```