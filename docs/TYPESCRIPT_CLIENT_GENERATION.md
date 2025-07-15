# TypeScript Client Generation from FastAPI

This document describes the automated TypeScript client generation workflow implemented for the re-frame project.

## Overview

The backend FastAPI application automatically generates an OpenAPI 3.1.0 schema, which is used to generate a fully type-safe TypeScript client for the frontend. This ensures perfect synchronization between backend API contracts and frontend code.

## Architecture

```
Backend (FastAPI)                Frontend (Next.js)
       |                                |
       v                                v
  Pydantic Models  ---OpenAPI--->  TypeScript Types
       |                                |
       v                                v
   API Endpoints   ---Schema---->   API Client
       |                                |
       v                                v
    main.py        ---JSON---->    generated/
```

## Implementation Details

### Backend Setup

1. **Pydantic Models** (`backend/src/models/api.py`)
   - Request/response models with validation
   - Automatic OpenAPI schema generation
   - Rich field descriptions and examples

2. **FastAPI Endpoints** (`backend/src/main.py`)
   - Type-annotated with Pydantic models
   - Operation IDs for clean function names
   - Proper HTTP response codes

3. **Export Task** (`backend/pyproject.toml`)
   ```toml
   [tool.poe.tasks]
   export-openapi = { shell = "python -c \"...\" > ../frontend/openapi.json" }
   ```

### Frontend Setup

1. **OpenAPI TypeScript** (`@hey-api/openapi-ts`)
   - Generates types and client from OpenAPI schema
   - Supports multiple HTTP clients (axios, fetch, etc.)
   - Full TypeScript support

2. **Generation Script** (`frontend/package.json`)
   ```json
   "generate:api": "openapi-ts --input ./openapi.json --output ./lib/api/generated --client legacy/axios"
   ```

3. **Client Wrapper** (`frontend/lib/api/generated-client.ts`)
   - Configures generated client with API settings
   - Provides convenient API grouping
   - Re-exports types

## Workflow

### For Backend Developers

1. Create/update Pydantic models:
   ```python
   class MessageRequest(BaseModel):
       mime_type: str = Field(..., description="MIME type")
       data: str = Field(..., description="Base64 data")
   ```

2. Use models in endpoints:
   ```python
   @app.post("/api/send/{session_id}", response_model=MessageResponse)
   async def send_message(session_id: str, message: MessageRequest):
       # Implementation
   ```

3. Export schema after changes:
   ```bash
   cd backend
   uv run poe export-openapi
   ```

### For Frontend Developers

1. Generate TypeScript client:
   ```bash
   cd frontend
   pnpm run generate:api
   ```

2. Use the generated client:
   ```typescript
   import { generatedApi } from '@/lib/api/generated-client'
   
   const response = await generatedApi.messages.send(sessionId, {
     mime_type: 'text/plain',
     data: 'SGVsbG8='
   })
   ```

## Benefits

1. **Type Safety**: All API calls are fully typed
2. **Autocompletion**: IDE knows all endpoints and their parameters
3. **Validation**: TypeScript catches API mismatches at compile time
4. **Documentation**: JSDoc comments from backend appear in frontend
5. **Consistency**: Single source of truth for API contracts

## Best Practices

1. **Always use Pydantic models** for request/response types
2. **Add descriptions** to fields for better documentation
3. **Use operation_ids** for cleaner generated function names
4. **Version your API** when making breaking changes
5. **Run generation in CI** to catch sync issues

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Run `pnpm run generate:api` to regenerate client
   - Check that `openapi.json` exists

2. **Type mismatches**
   - Ensure backend models match frontend usage
   - Re-export and regenerate after changes

3. **Missing endpoints**
   - Verify endpoint has `response_model`
   - Check that route is registered in FastAPI

### Debugging

1. Check the generated schema:
   ```bash
   curl http://localhost:8000/openapi.json | jq
   ```

2. Inspect generated types:
   ```bash
   cat frontend/lib/api/generated/types.gen.ts
   ```

3. Verify client methods:
   ```bash
   cat frontend/lib/api/generated/sdk.gen.ts
   ```

## Future Enhancements

1. **Automatic generation on backend changes**
   - File watcher to detect API changes
   - Automatic schema export and client generation

2. **CI/CD Integration**
   - Verify client is up-to-date in PR checks
   - Automatic generation on merge

3. **Mock Server Generation**
   - Generate mock server from OpenAPI for testing
   - Type-safe test fixtures

4. **Client Customization**
   - Custom error handling
   - Request/response interceptors
   - Retry logic

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI TypeScript](https://github.com/hey-api/openapi-ts)
- [Pydantic Documentation](https://docs.pydantic.dev/)