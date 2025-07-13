# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is re-frame.social, a Next.js 14 application with TypeScript for cognitive reframing support. It's a transparent, AI-assisted tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety.

## Key Commands

### Development
```bash
pnpm run dev        # Start development server on http://localhost:3000
pnpm run build      # Build for production (containerized)
pnpm run start      # Start production server (for testing)
pnpm run lint       # Run ESLint
pnpm run test       # Run all tests
pnpm run test:watch # Run tests in watch mode
pnpm run test:ci    # Run tests with coverage for CI
```

### Running Specific Tests
```bash
pnpm test -- ComponentName.test.tsx  # Run specific test file
pnpm test -- --testNamePattern="test name"  # Run tests matching pattern
```

### Docker Commands
```bash
docker build -t re-frame-frontend .  # Build Docker image
docker run -p 8080:8080 re-frame-frontend  # Run locally
```

## Architecture

### Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS v3 with custom design tokens
- **Audio**: Web Audio API with AudioWorklets
- **Real-time**: Server-Sent Events (SSE) for streaming
- **Testing**: Jest with React Testing Library
- **Package Manager**: pnpm (v10.11.0)
- **CI/CD**: GitHub Actions with automated deployment
- **Deployment**: Google Cloud Run (containerized)

### Directory Structure
- `app/` - Next.js App Router pages and layouts
  - Routes: about, demo, learn-cbt, privacy, support
  - Global styles, fonts, and error boundaries
- `components/` - React components organized by feature
  - `audio/` - Audio-specific components
    - `conversation/` - Conversation mode UI components
  - `common/` - Shared components
  - `error/` - Error handling components
  - `forms/` - Form-related components (includes audio controls)
  - `ui/` - UI primitives (Button, LoadingSpinner, AudioVisualizer, etc.)
- `lib/` - Core functionality
  - `audio/` - Audio recording, playback, and processing
    - `worklets/` - AudioWorklet processors
    - `hooks/` - React hooks for audio features
  - `streaming/` - SSE client and message protocol
  - `theme/` - Theme management with context and scripts
  - `error-logger.ts` - Error logging utilities
- `types/` - TypeScript type definitions
- `.github/workflows/` - CI/CD pipeline configurations

### Key Patterns

1. **Error Handling**: Comprehensive error boundaries at root and component levels
   - `RootErrorBoundary` wraps the entire app
   - Individual error boundaries for specific features
   - Graceful audio feature degradation

2. **Theming**: Dark mode support with system preference detection
   - Theme context in `lib/theme/ThemeContext.tsx`
   - FOUC prevention with theme script injection

3. **Accessibility**: WCAG AA compliance focus
   - Semantic HTML with proper ARIA labels
   - Skip links for keyboard navigation
   - Minimum 44x44px touch targets
   - Screen reader announcements for audio states
   - `aria-pressed` states for recording buttons

4. **Testing**: Test-Driven Development (TDD)
   - Test files named `*.test.tsx` alongside components
   - Jest configuration with path aliases
   - Audio feature mocking for consistent tests

5. **Path Aliases**: Use `@/` for imports from root
   ```typescript
   import Component from '@/components/ui/Button'
   ```

6. **Performance**: Lazy loading for audio components
   ```typescript
   const AudioControls = dynamic(() => import('./AudioControls'), {
     ssr: false,
     loading: () => null
   })
   ```

7. **Audio Features**: Privacy-focused implementation
   - No audio storage, only transcriptions
   - Real-time streaming with SSE
   - Graceful fallback for unsupported browsers

## Important Considerations

1. **Target Audience**: Users with AvPD and social anxiety
   - Keep UI calm, non-judgmental, and supportive
   - Avoid overwhelming interactions
   - Clear, gentle error messages

2. **Mobile-First**: Design and test for mobile devices first
   - Responsive breakpoints in Tailwind
   - Touch-friendly interfaces

3. **Performance**: Optimized for Cloud Run deployment
   - Lazy-loaded audio components
   - Containerized with multi-stage Docker builds
   - Automatic scaling based on load

4. **Security**: Privacy-focused design
   - No audio data storage
   - CSP headers configured for deployment
   - Environment variables prefixed with `NEXT_PUBLIC_` for client access
   - Secure WebSocket connections for audio streaming

## Working with Audio Features

### Audio Modes
1. **Review Mode** (default): Record → Review/Edit → Send
2. **Conversation Mode**: Push-to-talk natural dialogue

### Browser Compatibility
- Always check `checkAudioSupport()` before enabling audio features
- Provide fallback UI for unsupported browsers
- Test on Chrome, Firefox, Safari, and Edge

### Common Audio Tasks
```typescript
// Check audio support
const support = checkAudioSupport();
if (!support.getUserMedia || !support.audioContext) {
  // Disable audio features
}

// Use audio recorder hook
const audioRecorder = useAudioRecorder({
  onData: (data) => console.log('Audio data:', data),
  onError: (error) => console.error('Audio error:', error)
});
```