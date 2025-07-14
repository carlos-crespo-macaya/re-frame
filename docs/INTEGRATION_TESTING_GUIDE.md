# Integration Testing Guide

This guide explains how to run end-to-end integration tests locally for the re-frame CBT Assistant POC.

## Overview

The integration tests use Playwright to verify the complete workflow between frontend and backend services. Tests cover:
- Text and audio thought submission
- Real-time SSE streaming
- PDF download functionality
- Mobile responsiveness
- Error handling

## Prerequisites

1. **Node.js** 18+ and **pnpm**
2. **Python** 3.11+ with virtual environment
3. **Docker** and **Docker Compose** (optional, for containerized testing)

## Installation

### 1. Install Playwright

From the project root:

```bash
pnpm test:e2e:install
```

This installs Playwright and all required browser binaries.

### 2. Verify Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Running Tests

### Option 1: Local Development Mode

This runs tests against your local development servers.

1. **Start both services** (in separate terminals):
   ```bash
   # Terminal 1: Frontend
   pnpm dev:frontend

   # Terminal 2: Backend
   pnpm dev:backend
   ```

2. **Run tests**:
   ```bash
   pnpm test:e2e
   ```

### Option 2: Automated Test Mode

This automatically starts both services and runs tests:

```bash
# From project root
pnpm test:e2e
```

Playwright will:
1. Start frontend on http://localhost:3000
2. Start backend on http://localhost:8000
3. Run all integration tests
4. Shut down services when complete

### Option 3: Docker Compose Mode

For testing in a production-like environment:

1. **Build and start containers**:
   ```bash
   docker-compose up --build
   ```

2. **Run tests** (in another terminal):
   ```bash
   pnpm test:e2e
   ```

## Test Commands

- **Run all tests**: `pnpm test:e2e`
- **Run with UI mode**: `pnpm test:e2e:ui` (interactive test runner)
- **Debug mode**: `pnpm test:e2e:debug` (step through tests)
- **Headed mode**: `pnpm test:e2e:headed` (see browser)
- **View report**: `pnpm test:e2e:report` (after tests run)

## Test Structure

Tests are located in `tests/e2e/`:

```
tests/e2e/
├── full-workflow.spec.ts    # Main integration tests
├── audio.spec.ts           # Audio-specific tests (if added)
└── mobile.spec.ts          # Mobile-specific tests (if added)
```

### Key Test Scenarios

1. **Homepage Flow**
   - Load application
   - Submit text thought
   - Verify SSE response

2. **Audio Recording** (requires microphone)
   - Request permissions
   - Record audio
   - Verify transmission

3. **Session End**
   - Complete session
   - Download PDF summary
   - Verify file download

4. **Error Handling**
   - Network failures
   - Invalid inputs
   - Backend errors

## Configuration

### Environment Variables

Create `.env.local` in frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Playwright Config

The `playwright.config.ts` includes:
- Multiple browser testing (Chrome, Firefox, Safari)
- Mobile viewport testing
- Automatic screenshot/video on failure
- Parallel test execution

## Debugging Failed Tests

### 1. Check Test Reports

After running tests:
```bash
pnpm test:e2e:report
```

This opens an HTML report with:
- Test results
- Screenshots on failure
- Video recordings
- Network logs

### 2. Run Specific Tests

Run a single test file:
```bash
cd frontend
pnpm playwright test full-workflow.spec.ts
```

Run tests matching a pattern:
```bash
pnpm playwright test -g "should submit text thought"
```

### 3. Debug Mode

Step through tests interactively:
```bash
pnpm test:e2e:debug
```

### 4. Check Service Health

Verify services are running:
```bash
# Frontend health
curl http://localhost:3000/api/health

# Backend health
curl http://localhost:8000/health
```

## Common Issues

### Port Conflicts

If ports 3000 or 8000 are in use:
```bash
# Find processes
lsof -i :3000
lsof -i :8000

# Kill processes if needed
kill -9 <PID>
```

### Browser Installation

If browser binaries are missing:
```bash
cd frontend
pnpm playwright install chromium firefox webkit
```

### Permission Errors

For audio tests, ensure microphone permissions:
- macOS: System Preferences > Security & Privacy > Microphone
- Linux: Check browser settings
- Windows: Settings > Privacy > Microphone

### Docker Network Issues

For Docker Compose testing:
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## CI/CD Integration

While these tests are designed for local development, they can be added to CI/CD:

```yaml
# Example GitHub Actions step
- name: Run Integration Tests
  run: |
    pnpm install
    pnpm test:e2e:install
    pnpm test:e2e
```

## Manual Testing Checklist

After automated tests, verify manually:

- [ ] Text thought submission works
- [ ] Audio recording captures voice
- [ ] SSE streaming shows responses
- [ ] PDF download saves file
- [ ] Mobile layout is responsive
- [ ] Error messages display correctly
- [ ] Session state persists
- [ ] Network interruptions are handled

## Extending Tests

To add new test scenarios:

1. Create new spec file in `tests/e2e/`
2. Use existing patterns from `full-workflow.spec.ts`
3. Follow Playwright best practices:
   - Use data-testid attributes
   - Avoid hard-coded waits
   - Check for element visibility
   - Handle async operations

Example:
```typescript
test('should handle new feature', async ({ page }) => {
  await page.goto('/')
  await page.click('[data-testid="new-feature-button"]')
  await expect(page.locator('[data-testid="result"]')).toBeVisible()
})
```

## Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)