# Project Structure & Organization

## Monorepo Layout

```
re-frame/
├── frontend/                 # Next.js 14 frontend application
├── backend/                  # FastAPI backend with ADK agents
├── docs/                     # Shared documentation
├── scripts/                  # Utility scripts
├── tests/                    # Integration tests
├── .kiro/                    # Kiro AI assistant configuration
├── docker-compose.yml        # Local development setup
├── Makefile                  # Development commands
└── package.json              # Root workspace configuration
```

## Frontend Structure (`frontend/`)

```
frontend/
├── app/                      # Next.js App Router
│   ├── api/                  # API routes
│   ├── about/                # Static pages
│   ├── demo/                 # Demo/chat interface
│   ├── learn-cbt/            # Educational content
│   ├── privacy/              # Privacy policy
│   ├── support/              # Support pages
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Home page
├── components/               # React components
│   ├── audio/                # Audio recording/playback
│   ├── common/               # Shared components
│   ├── error/                # Error handling
│   ├── forms/                # Form components
│   └── ui/                   # UI primitives
├── lib/                      # Core functionality
│   ├── audio/                # Audio processing
│   ├── streaming/            # SSE/WebSocket handling
│   ├── theme/                # Theme configuration
│   └── utils.ts              # Utility functions
├── types/                    # TypeScript definitions
└── public/                   # Static assets
```

## Backend Structure (`backend/`)

```
backend/
├── src/                      # Source code
│   ├── agents/               # ADK conversational agents
│   │   ├── cbt_assistant.py  # Main CBT assistant
│   │   ├── greeting_agent.py # Greeting phase
│   │   ├── discovery_agent.py# Discovery phase
│   │   ├── reframing_agent.py# Reframing phase
│   │   └── summary_agent.py  # Summary phase
│   ├── knowledge/            # CBT domain knowledge
│   │   └── cbt_context.py    # CBT knowledge base
│   ├── tools/                # ADK tools
│   │   └── cbt_knowledge_tool.py # Knowledge query tool
│   ├── services/             # Business logic
│   │   └── audio_pipeline.py # Audio processing
│   ├── utils/                # Utilities
│   │   ├── audio_converter.py# Audio format conversion
│   │   ├── language_detection.py # Language detection
│   │   ├── pdf_generator.py  # PDF summary generation
│   │   ├── session_manager.py# Session state management
│   │   └── safety_response.py# Crisis detection
│   ├── prompts/              # AI prompts
│   └── main.py               # FastAPI application
├── tests/                    # Test files
├── main.py                   # CLI entry point
└── pyproject.toml            # Python project configuration
```

## Key Conventions

### File Naming
- **Frontend**: kebab-case for files, PascalCase for components
- **Backend**: snake_case for all Python files
- **Tests**: `test_*.py` pattern for backend, `*.test.ts` for frontend

### Import Organization
- **Frontend**: Absolute imports from project root
- **Backend**: Relative imports within modules, absolute for cross-module

### Configuration Files
- **Environment**: `.env` files for secrets, separate dev/prod configs
- **Docker**: Multi-stage builds with development targets
- **CI/CD**: GitHub Actions workflows in `.github/workflows/`

### Documentation Structure
```
docs/
├── project-setup/            # Project management docs
├── templates/                # Issue/PR templates  
├── CI_CD_WORKFLOW_PLAN.md   # Deployment processes
├── INTEGRATION_TESTING_GUIDE.md # Testing strategies
└── TEAM_COORDINATION_GUIDE.md   # Development workflow
```

### Testing Organization
- **Unit tests**: Co-located with source code
- **Integration tests**: `tests/` directory at root
- **E2E tests**: `frontend/` Playwright tests
- **Coverage**: 80% minimum for backend

### Session & State Management
- **Frontend**: React state + session storage for UI state
- **Backend**: ADK InMemoryRunner for conversation state
- **Communication**: SSE for real-time streaming, REST for commands

### Audio Processing Pipeline
- **Input**: Multiple formats supported (webm, wav, mp3)
- **Processing**: Conversion to PCM format for ADK
- **Output**: PCM audio streamed via SSE
- **Storage**: No persistent audio storage (privacy-first)

### Security & Privacy
- **API Keys**: Environment variables only
- **CORS**: Strict origin allowlists
- **Headers**: Security headers configured
- **Data**: No long-term storage of conversations
- **Logging**: No PII in logs