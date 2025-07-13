# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is re-frame.social, a Next.js 14 application with TypeScript for cognitive reframing support. It's a transparent, AI-assisted tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety.

## Key Commands

### Development
```bash
npm run dev        # Start development server on http://localhost:3000
npm run build      # Build static export (output in 'out' directory)
npm run start      # Start production server (for testing)
npm run lint       # Run ESLint
npm run test       # Run all tests
npm run test:watch # Run tests in watch mode
```

### Running Specific Tests
```bash
npm test -- ComponentName.test.tsx  # Run specific test file
npm test -- --testNamePattern="test name"  # Run tests matching pattern
```

## Architecture

### Tech Stack
- **Framework**: Next.js 14 (App Router with static export)
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS v3 with custom design tokens
- **Testing**: Jest with React Testing Library
- **Package Manager**: pnpm (v10.11.0)

### Directory Structure
- `app/` - Next.js App Router pages and layouts
  - Routes: about, demo, learn-cbt, privacy, support
  - Global styles, fonts, and error boundaries
- `components/` - React components organized by feature
  - `common/` - Shared components
  - `error/` - Error handling components
  - `forms/` - Form-related components
  - `ui/` - UI primitives (Button, LoadingSpinner, etc.)
- `lib/` - Utility functions and contexts
  - `theme/` - Theme management with context and scripts
  - `error-logger.ts` - Error logging utilities
  - `socket.ts` - WebSocket utilities
- `types/` - TypeScript type definitions

### Key Patterns

1. **Error Handling**: Comprehensive error boundaries at root and component levels
   - `RootErrorBoundary` wraps the entire app
   - Individual error boundaries for specific features

2. **Theming**: Dark mode support with system preference detection
   - Theme context in `lib/theme/ThemeContext.tsx`
   - FOUC prevention with theme script injection

3. **Accessibility**: WCAG AA compliance focus
   - Semantic HTML with proper ARIA labels
   - Skip links for keyboard navigation
   - Minimum 44x44px touch targets

4. **Testing**: Component tests alongside source files
   - Test files named `*.test.tsx`
   - Jest configuration with path aliases

5. **Path Aliases**: Use `@/` for imports from root
   ```typescript
   import Component from '@/components/ui/Button'
   ```

## Important Considerations

1. **Target Audience**: Users with AvPD and social anxiety
   - Keep UI calm, non-judgmental, and supportive
   - Avoid overwhelming interactions
   - Clear, gentle error messages

2. **Mobile-First**: Design and test for mobile devices first
   - Responsive breakpoints in Tailwind
   - Touch-friendly interfaces

3. **Performance**: Static export for Firebase Hosting
   - No server-side rendering
   - Client-side only features

4. **Security**: No client-side data storage currently
   - CSP headers configured for deployment
   - Environment variables prefixed with `NEXT_PUBLIC_` for client access