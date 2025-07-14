# E2E Integration Tests

This directory contains end-to-end integration tests for the re-frame CBT Assistant POC.

## Quick Start

```bash
# Install Playwright (first time only)
pnpm test:e2e:install

# Run all tests
pnpm test:e2e

# Run in UI mode (recommended for development)
pnpm test:e2e:ui
```

## Test Files

- `full-workflow.spec.ts` - Complete user workflow tests including:
  - Homepage interaction
  - Text thought submission
  - Navigation between pages
  - Health endpoint verification
  - Session end and PDF download
  - Mobile responsiveness
  - Error handling
  - Backend integration (SSE, audio)

## Writing New Tests

1. Create a new `.spec.ts` file
2. Import Playwright test utilities:
   ```typescript
   import { test, expect } from '@playwright/test'
   ```
3. Follow existing patterns for page interactions
4. Use data-testid attributes when possible

## Tips

- Tests run in parallel by default
- Each test gets a fresh browser context
- Screenshots and videos are saved on failure
- Use `--headed` flag to see the browser during tests
- Use `--debug` flag to step through tests interactively