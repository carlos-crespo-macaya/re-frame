# API Client Migration Guide

This guide explains how to migrate from the manual API client to the auto-generated TypeScript client.

## Overview

We now have an automated TypeScript client generated from the backend's OpenAPI schema. This ensures:
- Full type safety between frontend and backend
- Automatic synchronization of API contracts
- Better developer experience with autocompletion
- Compile-time validation of API calls

## Generation Workflow

### 1. Backend Updates

When you make API changes in the backend:

```bash
cd backend
# Make your API changes...
# Export the updated OpenAPI schema
uv run poe export-openapi
```

### 2. Frontend Generation

Generate the TypeScript client:

```bash
cd frontend
pnpm run generate:api
```

This command is also run automatically before builds via the `prebuild` script.

## Usage Examples

### Before (Manual Client)

```typescript
import { ApiClient } from '@/lib/api/client'

// No type safety for request/response
const response = await ApiClient.sendMessage(sessionId, {
  mime_type: 'text/plain',
  data: 'SGVsbG8='
})
```

### After (Generated Client)

```typescript
import { generatedApi } from '@/lib/api/generated-client'
import type { MessageRequest } from '@/lib/api/generated/types.gen'

// Full type safety with autocompletion
const request: MessageRequest = {
  mime_type: 'text/plain',  // TypeScript knows the exact property names
  data: 'SGVsbG8='
}

const response = await generatedApi.messages.send(sessionId, request)
// response is typed as MessageResponse
```

## Migration Steps

1. **Keep both clients during migration**
   - The manual client remains in `lib/api/client.ts`
   - Generated client is in `lib/api/generated-client.ts`

2. **Gradually migrate components**
   ```typescript
   // Old
   import { sendMessage } from '@/lib/api/client'
   
   // New
   import { generatedApi } from '@/lib/api/generated-client'
   ```

3. **Update type imports**
   ```typescript
   // Old
   import type { MessageData } from '@/lib/api/types'
   
   // New
   import type { MessageRequest } from '@/lib/api/generated/types.gen'
   ```

## Type Safety Benefits

### Compile-Time Validation

```typescript
// This will fail TypeScript compilation:
await generatedApi.messages.send(sessionId, {
  mimeType: 'text/plain',  // ❌ Wrong property name
  data: 'test'
})

// This is correct:
await generatedApi.messages.send(sessionId, {
  mime_type: 'text/plain',  // ✅ Correct property name
  data: 'test'
})
```

### Enum Validation

```typescript
const health: HealthCheckResponse = {
  status: 'healthy',  // ✅ TypeScript knows this must be 'healthy' | 'unhealthy'
  // status: 'ok',   // ❌ Would fail compilation
  service: 'API',
  timestamp: new Date().toISOString()
}
```

## Special Cases

### Server-Sent Events (SSE)

SSE still requires manual EventSource handling:

```typescript
// Use the generated helper for type-safe URL construction
const url = generatedApi.events.getEndpoint(sessionId, 'true', 'en-US')
const eventSource = new EventSource(`${API_CONFIG.baseUrl}${url}`)
```

### File Downloads

For binary responses (like PDFs), you may need custom handling:

```typescript
// The generated client returns the response
const response = await generatedApi.sessions.downloadPdf(sessionId)

// Manual handling for blob conversion might still be needed
const blob = await response.blob()
```

## Maintaining Sync

To ensure frontend and backend stay in sync:

1. Backend developers should run `uv run poe export-openapi` after API changes
2. Frontend developers should run `pnpm run generate:api` after pulling
3. CI/CD can verify sync by regenerating and checking for changes

## Troubleshooting

### "Property does not exist" errors
- Regenerate the client: `pnpm run generate:api`
- Check that backend exported the latest schema

### Type mismatches
- Ensure you're using the generated types, not the old manual types
- Check for breaking changes in the API

### Missing endpoints
- Verify the endpoint is properly decorated in FastAPI
- Ensure it has proper response_model and operation_id
- Re-export the OpenAPI schema