# re-frame.social Frontend

This is the frontend for re-frame.social, a transparent AI-assisted cognitive reframing tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS v3
- **Language**: TypeScript
- **Audio**: Web Audio API with AudioWorklets
- **Real-time**: Server-Sent Events (SSE) for streaming
- **Deployment**: Google Cloud Run (containerized)
- **CI/CD**: GitHub Actions with automated testing and deployment

## Getting Started

### Prerequisites

- Node.js 18+ 
- pnpm 10.11.0 (required)
- Docker (for containerized deployment)

### Installation

1. Install dependencies:
```bash
pnpm install
```

2. Run the development server:
```bash
pnpm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
# Build for production
pnpm run build

# Build Docker image
docker build -t re-frame-frontend .

# Run locally
docker run -p 8080:8080 re-frame-frontend
```

## Project Structure

```
re-frame/
├── app/                  # Next.js App Router
│   ├── layout.tsx       # Root layout with error boundary
│   ├── page.tsx         # Landing page
│   ├── demo/            # Demo page with audio features
│   ├── learn-cbt/       # CBT educational content
│   └── globals.css      # Global styles
├── components/          # React components
│   ├── audio/           # Audio components
│   │   └── conversation/# Conversation mode UI
│   ├── common/          # Shared components
│   ├── error/           # Error handling components
│   ├── forms/           # Form components with audio
│   └── ui/              # UI primitives
├── lib/                 # Core functionality
│   ├── audio/           # Audio recording/playback
│   │   ├── worklets/    # AudioWorklet processors
│   │   └── hooks/       # Audio React hooks
│   ├── streaming/       # SSE client implementation
│   └── theme/           # Theme management
├── .github/workflows/   # CI/CD pipelines
├── Dockerfile           # Container configuration
└── next.config.mjs      # Next.js configuration
```

## Key Features

- **Voice Input**: Speak your thoughts with real-time transcription
- **Audio Modes**: 
  - Review Mode: Record → Review/Edit → Send
  - Conversation Mode: Natural back-and-forth dialogue
- **Mobile-first design**: Optimized for mobile devices with responsive breakpoints
- **Accessibility**: WCAG AA compliant with screen reader support and keyboard navigation
- **Dark mode**: Automatic dark mode support based on system preferences
- **Performance**: Lazy-loaded audio components, optimized bundle size
- **Security**: CSP headers, no audio storage, privacy-focused
- **Real-time Streaming**: Server-Sent Events for instant audio/text exchange

## Development Guidelines

### Accessibility

- All interactive elements must have a minimum touch target of 44x44px
- Use semantic HTML and ARIA labels where appropriate
- Ensure color contrast ratios meet WCAG AA standards
- Support keyboard navigation throughout the application

### Styling

- Use Tailwind CSS utility classes
- Follow mobile-first approach
- Use the custom color palette defined in `tailwind.config.ts`
- Respect user's motion preferences with `prefers-reduced-motion`

### Components

- Keep components small and focused
- Use TypeScript for type safety
- Follow the established folder structure
- Write accessible, semantic markup

## Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://api.re-frame.social

# Google Cloud Configuration (for deployment)
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
```

## Scripts

- `pnpm run dev` - Start development server
- `pnpm run build` - Build for production
- `pnpm run start` - Start production server (for testing)
- `pnpm run lint` - Run ESLint
- `pnpm run test` - Run all tests
- `pnpm run test:watch` - Run tests in watch mode
- `pnpm run test:ci` - Run tests in CI mode with coverage

## Deployment

The application is deployed to Google Cloud Run:

1. **Automatic Deployment**: Push to `main` branch triggers deployment via GitHub Actions
2. **Manual Deployment**:
   ```bash
   # Build and push to Artifact Registry
   gcloud builds submit --tag gcr.io/PROJECT_ID/re-frame-frontend
   
   # Deploy to Cloud Run
   gcloud run deploy re-frame-frontend --image gcr.io/PROJECT_ID/re-frame-frontend
   ```
3. **Configuration**: The app runs on port 8080 with automatic scaling

## Audio Features

### Voice Input Capabilities
- **Real-time transcription**: Speak naturally and see your words appear
- **Push-to-talk**: Hold spacebar or button for conversation mode
- **Audio feedback**: Hear AI responses with natural voice synthesis
- **Privacy-first**: No audio is stored, only transcribed text

### Browser Support
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

### Technical Implementation
- Web Audio API with AudioWorklets for low-latency processing
- Server-Sent Events for real-time bidirectional streaming
- Graceful fallback when audio features unavailable
- Lazy loading for optimal performance

## Testing

```bash
# Run all tests
pnpm test

# Run specific test file
pnpm test ComponentName.test.tsx

# Run with coverage
pnpm test:ci
```

## Contributing

When making changes:

1. Follow Test-Driven Development (TDD) practices
2. Ensure all changes maintain WCAG AA compliance
3. Test on mobile devices and with keyboard navigation
4. Test audio features across different browsers
5. Consider the target audience (people with AvPD) in all UX decisions
6. Keep the interface calm, non-judgmental, and supportive
7. Run linting and tests before committing:
   ```bash
   pnpm lint
   pnpm test
   ```
