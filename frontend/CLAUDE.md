# Frontend CLAUDE.md

This file provides frontend-specific guidance when working in the `/frontend` directory of the re-frame monorepo.

## Frontend Commands Quick Reference

```bash
pnpm run dev         # Start development server on http://localhost:3000
pnpm run build       # Build for production
pnpm run test        # Run all tests (Jest)
pnpm run test:watch  # Run tests in watch mode
pnpm run test:ci     # Run tests with coverage for CI
pnpm run lint        # Run ESLint
pnpm run typecheck   # TypeScript type checking
pnpm run generate:api # Generate API client from OpenAPI spec
```

## E2E Testing
```bash
# DEPRECATED - Use playwright-js directory instead
pnpm run test:e2e                # Run Playwright tests (LEGACY)
pnpm run test:e2e:ui             # Run with UI mode (LEGACY)
pnpm run test:e2e:debug          # Run in debug mode (LEGACY)
pnpm run test:e2e:headed         # Run with browser visible (LEGACY)
pnpm run test:e2e:report         # Show test report (LEGACY)

# PRIMARY E2E testing is now in /playwright-js directory
# See root CLAUDE.md for E2E testing commands
```

## Pre-Push Checklist
**ALWAYS run before pushing:**
```bash
pnpm run lint && pnpm run typecheck && pnpm run test
```

## Frontend-Specific Guidelines

### Component Development
- Components live in `/components/` with tests alongside (*.test.tsx)
- Follow existing patterns - check similar components first
- Use custom hooks from `/lib/hooks/`
- Keep components focused and testable

### Styling
- Use Tailwind CSS classes
- Custom design tokens in `tailwind.config.ts`
- Avoid inline styles unless absolutely necessary
- Follow mobile-first responsive design

### Audio Handling
- Web Audio API with AudioWorklets in `/public/worklets/`
- Audio processing at 48kHz on frontend
- No audio storage - only transcriptions saved
- Use `/lib/audio/` utilities for audio operations

### Real-time Communication
- Server-Sent Events (SSE) for streaming
- SSE client in `/lib/streaming/sse-client.ts`
- Handle reconnection gracefully
- Show loading states during streaming

### API Integration
- **STRICT RULE: Always use the auto-generated API client from `/lib/api/generated-client.ts`**
- **NEVER manually implement API calls - this prevents contract mismatches**
- Type-safe client generated from OpenAPI schema
- Run `pnpm run generate:api` after backend API changes
- API client exports from `/lib/api/`
- Always handle errors with user-friendly messages
- OpenAPI schema is generated during backend CI and downloaded during frontend build
- When adding new endpoints:
  1. Update backend first
  2. Run `pnpm run generate:api` to regenerate types
  3. Add wrapper methods to `generated-client.ts`
  4. Use the wrapper methods in `client.ts` or directly in components

### API Proxy Route (NEW)
- **Location**: `/app/api/proxy/[...path]/route.ts`
- **Purpose**: Handles service-to-service authentication for Cloud Run backend access
- **Environment Variables**:
  - `BACKEND_INTERNAL_HOST`: Internal backend host for Cloud Run service-to-service communication
  - `BACKEND_PUBLIC_URL`: Public backend URL for authentication audience
- **Authentication**: Uses Google Auth library for Cloud Run service tokens
- **Usage**: Automatically handles auth when deployed to Cloud Run

### Testing Approach
- Unit tests with Jest and React Testing Library
- Test files alongside components (*.test.tsx)
- Mock external dependencies
- Focus on user interactions, not implementation details
- Use existing test utilities from `/test-utils/`

### State Management
- React Context for global state
- Custom hooks for shared logic
- Local state with useState/useReducer
- Avoid prop drilling

### Performance
- Lazy load components where appropriate
- Optimize images with Next.js Image component
- Use React.memo for expensive components
- Monitor bundle size

### Security
- Never expose API keys in frontend code
- Sanitize user inputs
- Use environment variables for configuration
- Follow OWASP guidelines for frontend security

## Frontend Architecture

### Core Technologies
- **Framework**: Next.js 14 with App Router (NOT Pages Router)
- **Language**: TypeScript with strict mode enabled
- **Styling**: Tailwind CSS v3 with custom design tokens
- **State Management**: React Context for global state
- **Internationalization**: next-intl with dynamic locale routing

### Directory Structure
```
frontend/
├── app/                   # Next.js App Router
│   ├── [locale]/         # Internationalized routes
│   └── api/              # API routes
│       └── proxy/        # Service-to-service auth proxy (NEW)
├── components/            # Reusable UI components
│   ├── audio/            # Audio recording & playback
│   ├── forms/            # Form components (ChatInterface)
│   └── ui/               # Base UI components
├── lib/                   # Core functionality
│   ├── api/              # Generated API client
│   ├── audio/            # Audio processing utilities
│   └── streaming/        # SSE client implementation
├── locales/               # Translation files (en, es)
├── public/worklets/       # Web Audio worklets
├── Dockerfile.standalone  # Production Docker build (NEW)
└── openapi.json          # Generated from backend CI (NEW)
```

### Key Features
- **Multi-language Support**: English and Spanish with URL-based routing
- **Audio Recording**: 48kHz WAV format with Web Audio API
- **Real-time Streaming**: SSE for responsive AI interactions
- **Accessibility**: ARIA labels and keyboard navigation
- **Responsive Design**: Mobile-first approach

## Environment Variables (UPDATED)

### Build-time Variables (NEXT_PUBLIC_*)
- `NEXT_PUBLIC_API_URL`: Public API URL for client-side calls
- Must be set during build, not runtime

### Runtime Variables
- `BACKEND_INTERNAL_HOST`: Internal backend host for service-to-service calls
- `BACKEND_PUBLIC_URL`: Public backend URL for authentication audience
- `NODE_ENV`: Environment (development/production)
- `SERVICE_NAME`: Service identifier for logging/monitoring
- `PORT`: Server port (default 3000 for dev, 8080 for production)

## Common Issues & Solutions

### API Client Out of Sync
If TypeScript errors after backend changes:
```bash
pnpm run generate:api
```

### Test Failures
- Check if you need to update mocks
- Look for console errors in test output
- Use `test.only` to isolate failing tests

### Build Errors
- Clear `.next` cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && pnpm install`

## Important Notes
- This is a Next.js 14 App Router project (not Pages Router)
- Strict TypeScript mode is enabled
- All new code must pass linting and type checking
- Follow accessibility best practices (WCAG 2.1 AA)
