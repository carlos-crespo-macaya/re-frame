# Frontend CLAUDE.md

This file provides frontend-specific guidance when working in the `/frontend` directory.

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
pnpm run test:e2e                # Run Playwright tests
pnpm run test:e2e:ui             # Run with UI mode
pnpm run test:e2e:debug          # Run in debug mode
pnpm run test:e2e:headed         # Run with browser visible
pnpm run test:e2e:report         # Show test report
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
- Type-safe client generated from OpenAPI schema
- Run `pnpm run generate:api` after backend API changes
- API client exports from `/lib/api/`
- Always handle errors with user-friendly messages

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