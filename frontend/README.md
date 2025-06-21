# re-frame.social Frontend

This is the frontend for re-frame.social, a transparent AI-assisted cognitive reframing tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS v3
- **Language**: TypeScript
- **Deployment**: Static export for Firebase Hosting

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
# Build the static export
npm run build

# The output will be in the 'out' directory
```

## Project Structure

```
frontend/
├── app/                  # Next.js App Router
│   ├── layout.tsx       # Root layout with metadata
│   ├── page.tsx         # Landing page
│   ├── loading.tsx      # Loading UI
│   ├── error.tsx        # Error boundary
│   └── globals.css      # Global styles
├── components/          # React components
│   ├── common/          # Shared components
│   ├── input/           # Form input components
│   └── reframing/       # Reframing-specific components
├── lib/                 # Utility functions
├── public/              # Static assets
└── next.config.mjs      # Next.js configuration
```

## Key Features

- **Mobile-first design**: Optimized for mobile devices with responsive breakpoints
- **Accessibility**: WCAG AA compliant with proper ARIA labels and keyboard navigation
- **Dark mode**: Automatic dark mode support based on system preferences
- **Performance**: Static export with optimized assets and font loading
- **Security**: CSP headers and no client-side data storage

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

Currently no environment variables are required for the frontend. When connecting to the backend API, add:

```env
NEXT_PUBLIC_API_URL=https://api.re-frame.social
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production (static export)
- `npm run start` - Start production server (for testing)
- `npm run lint` - Run ESLint

## Deployment

The frontend is configured for static export to Firebase Hosting:

1. Build the project: `npm run build`
2. Deploy the `out` directory to Firebase Hosting
3. Ensure proper headers are set for security (CSP, HSTS, etc.)

## Contributing

When making changes:

1. Ensure all changes maintain WCAG AA compliance
2. Test on mobile devices and with keyboard navigation
3. Consider the target audience (people with AvPD) in all UX decisions
4. Keep the interface calm, non-judgmental, and supportive
