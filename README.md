# re-frame - CBT Assistant POC Monorepo

A transparent, AI-assisted cognitive behavioral therapy (CBT) tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety. This monorepo combines a Next.js 14 frontend with a FastAPI backend powered by Google's Agent Development Kit (ADK).

## ✨ Features

- **Multi-modal Interaction**: Text-based chat and optional voice conversations
- **Real-time Streaming**: Responses stream as they're generated via Server-Sent Events (SSE)
- **Internationalization**: Support for multiple languages (English and Spanish)
- **Feature Flags**: Dynamic feature toggling with ConfigCat integration
- **Privacy-focused**: No audio storage, only transcriptions are kept
- **Evidence-based**: Uses proven cognitive behavioral therapy techniques
- **Multi-phase Conversation**: Structured flow through greeting, discovery, reframing, and summary
- **Safety First**: Crisis detection at every user input with fail-safe responses
- **Accessibility**: ARIA labels, keyboard navigation, and screen reader support

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS v3
- **Audio**: Web Audio API with AudioWorklets
- **Real-time**: Server-Sent Events (SSE)
- **Testing**: Jest + React Testing Library + Playwright
- **API Client**: Generated from OpenAPI schema

### Backend
- **Framework**: FastAPI with lifespan management
- **Language**: Python 3.12 (specifically required)
- **AI**: Google ADK with Gemini 2.0 Flash
- **Package Manager**: uv (NOT pip or poetry)
- **Testing**: pytest with 80% coverage requirement + pytest-xdist
- **Code Quality**: black, isort, ruff, mypy
- **Voice** (optional): Google Cloud Speech-to-Text & Text-to-Speech
- **Feature Flags**: ConfigCat for dynamic configuration

## 🏗️ Monorepo Structure

```
re-frame/
├── frontend/                # Next.js 14 frontend application
│   ├── app/                # Next.js App Router pages
│   ├── components/         # React components with tests
│   ├── lib/                # Core functionality (SSE, audio, API)
│   ├── public/worklets/    # Web Audio worklets
│   └── CLAUDE.md          # Frontend-specific AI assistant guidance
├── backend/                # FastAPI backend with Google ADK
│   ├── src/               # Source code (NOT app/)
│   │   ├── agents/        # ADK Sequential Agents
│   │   ├── knowledge/     # CBT context and techniques
│   │   ├── services/      # Session management, language detection
│   │   └── main.py        # FastAPI app entry point
│   ├── tests/             # Comprehensive test suite
│   └── CLAUDE.md          # Backend-specific AI assistant guidance
├── tests/                  # Integration and E2E tests
│   ├── e2e/               # Python E2E tests with pytest-xdist
│   └── load/              # Load testing (k6, locust)
├── playwright-js/          # JavaScript Playwright tests
│   └── tests/             # Voice modality E2E tests
├── docs/                   # Project documentation
├── scripts/                # Deployment and utility scripts
├── docker-compose.yml      # Base Docker configuration
├── Makefile               # Development commands
└── CLAUDE.md              # Project-wide AI assistant guidance
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- pnpm 10.11.0+
- Python 3.12 (specifically required)
- uv (Python package manager)
- Docker & Docker Compose
- Gemini API key

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/macayaven/re-frame.git
   cd re-frame
   ```

2. **Quick setup with Make**
   ```bash
   make setup  # Installs pnpm, uv, and all dependencies
   ```

   Or manually:
   ```bash
   # Install package managers
   npm install -g pnpm
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   cd frontend && pnpm install && cd ..
   cd backend && uv sync --all-extras && cd ..
   ```

3. **Set up environment variables**
   ```bash
   # Backend (.env)
   GEMINI_API_KEY=your-gemini-api-key
   ```

4. **Run development servers**
   ```bash
   # Using npm scripts
   npm run dev:frontend    # Frontend only (http://localhost:3000)
   npm run dev:backend     # Backend only (http://localhost:8000)
   npm run dev:all         # Both concurrently

   # Or using Make
   make dev-frontend
   make dev-backend
   make dev  # Full Docker development environment
   ```

5. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

## 📚 Documentation

- [Frontend README](./frontend/README.md) - Detailed frontend documentation
- [Backend README](./backend/README.md) - Backend documentation
- [Team Coordination Guide](./docs/TEAM_COORDINATION_GUIDE.md) - Development workflow
- [CLAUDE.md Files](./CLAUDE.md) - AI assistant context and guidance
- [Linear Project](https://linear.app/carlos-crespo/project/re-framesocial-cbt-assistant-6c36f6288cc8) - Primary project tracking

## ✅ Quality Checks

**IMPORTANT**: Always run checks before pushing:

```bash
# Frontend
cd frontend && pnpm run lint && pnpm run typecheck && pnpm run test

# Backend
cd backend && uv run poe check  # Runs format-check, lint, typecheck, and tests

# Or use Make
make pre-commit  # Runs all checks
```

## 🧪 Testing

### Testing Infrastructure
- **Frontend**: Jest for unit tests, Playwright for E2E
- **Backend**: pytest with 80% coverage requirement
- **E2E Tests**: Dual infrastructure (JavaScript & Python)
- **Load Testing**: k6 and locust for performance testing

### Running Tests

```bash
# Quick test everything
make test

# Frontend tests
cd frontend && pnpm test             # Unit tests with Jest
cd frontend && pnpm test:watch       # Watch mode
cd frontend && pnpm test:ci          # CI mode with coverage

# Backend tests  
cd backend && uv run poe test        # All tests with coverage
cd backend && uv run pytest -n auto   # Parallel execution
cd backend && uv run poe test-cov    # Generate HTML coverage report

# E2E tests - JavaScript (recommended)
cd playwright-js && npm test          # All E2E tests
cd playwright-js && npm test tests/text-*.spec.js   # Text tests only
cd playwright-js && npm test tests/voice-*.spec.js  # Voice tests only

# E2E tests - Python
cd tests/e2e && ./run_tests.sh       # Docker-based E2E tests

# Load testing
cd tests/load && k6 run text-load-test.js
cd tests/load && locust -f voice_load_test.py
```

## 🐳 Docker Development

### Docker Compose Files

This project uses multiple Docker Compose configurations for different environments:

| File | Purpose | Usage |
|------|---------|-------|
| `docker-compose.yml` | Base configuration for local development | `docker-compose up` |
| `docker-compose.override.yml` | Auto-loaded development overrides (CORS settings) | Loaded automatically |
| `docker-compose.dev.yml` | Extended dev with Redis & MailHog | `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up` |
| `docker-compose.prod.yml` | Production testing configuration | `docker-compose -f docker-compose.prod.yml up` |
| `docker-compose.integration.yml` | Integration testing with Playwright | Used by `make test-integration` |
| `tests/e2e/docker-compose.test.yml` | E2E test overrides | Used by E2E test suite |

### Common Docker Commands

```bash
# Basic development (frontend + backend)
docker-compose up --build

# Full development environment (includes Redis, MailHog)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run E2E tests
cd tests/e2e && ./run_tests.sh

# Production testing
docker-compose -f docker-compose.prod.yml up

# Stop all services
docker-compose down

# Clean up volumes
docker-compose down -v
```

## 🎤 Voice Modality (Optional)

The backend supports voice functionality through Google Cloud services:

### Setup
```bash
# Install voice dependencies
cd backend && uv sync --extra voice

# Required environment variables
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### Features
- **Speech-to-Text**: Transcribes user voice input
- **Text-to-Speech**: Generates natural voice responses
- **Real-time streaming**: Low-latency audio processing
- **Multi-language support**: Automatic language detection

### Testing
```bash
# Run voice unit tests
cd backend && uv run pytest tests/test_voice_*.py

# Run voice E2E tests
cd playwright-js && npm test tests/voice-*.spec.js

# Load testing
cd tests/load && k6 run voice-load-test.js
```

## 🚢 Deployment

### Overview

The application is deployed to Google Cloud Run with automated CI/CD:

- **Frontend**: Next.js application served from Cloud Run (Europe-West1)
- **Backend**: FastAPI with Google ADK agents on Cloud Run (Europe-West1)
- **Load Balancer**: Global HTTPS load balancer with SSL certificates
- **CI/CD**: GitHub Actions with Workload Identity Federation
- **Feature Flags**: ConfigCat for runtime configuration

### Quick Deployment

1. **Set up GCP infrastructure**:
   ```bash
   ./scripts/setup-gcp-infrastructure.sh
   ```

2. **Configure Workload Identity Federation** (Recommended):
   ```bash
   ./scripts/setup-workload-identity.sh
   ```

3. **Configure GitHub Secrets**:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_REGION`: Deployment region (e.g., us-central1)
   - `GCP_BILLING_ACCOUNT_ID`: Your GCP billing account ID
   - `WIF_PROVIDER`: Workload Identity Provider (from setup script)
   - `WIF_SERVICE_ACCOUNT`: Service account email
   - `GEMINI_API_KEY`: Your Gemini API key
   - `IAP_CLIENT_ID`: OAuth client ID for IAP
   - `IAP_CLIENT_SECRET`: OAuth client secret
   - `AUTHORIZED_DOMAIN`: Your organization domain

4. **Deploy**:
   ```bash
   # Create a release tag
   git tag v1.0.0
   git push origin v1.0.0
   ```

### Local Testing with Docker

```bash
# Test with production configuration
docker-compose -f docker-compose.prod.yml up

# Access at:
# - Frontend: http://localhost:8080
# - Backend: http://localhost:8000
```

### Manual Deployment

```bash
# Build and push images
docker build -t ghcr.io/your-org/re-frame-backend:latest ./backend
docker build -f ./frontend/Dockerfile.standalone \
  -t ghcr.io/your-org/re-frame-frontend:latest ./frontend

# Push to registry
docker push ghcr.io/your-org/re-frame-backend:latest
docker push ghcr.io/your-org/re-frame-frontend:latest

# Deploy to Cloud Run
gcloud run deploy re-frame-backend \
  --image ghcr.io/your-org/re-frame-backend:latest \
  --region us-central1

gcloud run deploy re-frame-frontend \
  --image ghcr.io/your-org/re-frame-frontend:latest \
  --region us-central1
```

## 📋 Project Management

### Linear
- **Project Board**: [Linear Project](https://linear.app/carlos-crespo/project/re-framesocial-cbt-assistant-6c36f6288cc8)
- **Issue Tracking**: All features and bugs tracked in Linear
- **Sprint Planning**: Two-week sprints with defined goals

### GitHub
- **Repository**: [macayaven/re-frame](https://github.com/macayaven/re-frame)
- **Issues**: Synced with Linear for transparency
- **Pull Requests**: Feature branches with CI/CD checks

### Branch Strategy
```bash
main                    # Production-ready code
├── feature/*          # New features (e.g., feature/feature-flags)
├── fix/*              # Bug fixes
└── recovery/*         # Recovery branches for complex work
```

### Deployment Architecture

```mermaid
graph TD
    A[User] --> B[IAP]
    B --> C[Cloud Run Frontend]
    C --> D[Cloud Run Backend]
    D --> E[Gemini API]
    
    F[GitHub Actions] --> G[Container Registry]
    G --> C
    G --> D
```

## 🤝 Contributing

### Development Workflow
1. Check Linear for available issues
2. Create a feature branch from `main`
3. Follow the coding standards in CLAUDE.md
4. Write/update tests (maintain 80% coverage)
5. Run quality checks: `make pre-commit`
6. Submit PR with Linear issue reference
7. Ensure all CI checks pass

### Commit Message Format
```
[BE-XXX] Backend changes
[FE-XXX] Frontend changes
[ALL-XXX] Monorepo/shared changes
[INF-XXX] Infrastructure changes
```

### Code Quality Standards
- **Frontend**: ESLint, TypeScript strict mode, Jest coverage
- **Backend**: black, isort, ruff, mypy, pytest coverage
- **Pre-commit**: All checks must pass before pushing

## 🔐 Security

- No audio data is stored
- All data transmission is encrypted
- Regular security updates via Dependabot
- CSP headers configured for production

## 📚 Documentation

- **[CLAUDE.md](./CLAUDE.md)** - AI assistant guidance for development
- **[Backend README](./backend/README.md)** - Backend-specific documentation
- **[Frontend README](./frontend/README.md)** - Frontend-specific documentation
- **[API Documentation](http://localhost:8000/docs)** - FastAPI automatic docs (when running)

## 🔗 Links

- **Live Demo**: Coming soon
- **Linear Project**: [Project Board](https://linear.app/carlos-crespo/project/re-framesocial-cbt-assistant-6c36f6288cc8)
- **GitHub**: [macayaven/re-frame](https://github.com/macayaven/re-frame)

## 📄 License

Apache-2.0

---

**Status**: Production-ready with active development of new features.