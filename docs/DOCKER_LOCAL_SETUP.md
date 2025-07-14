# Local Docker Development Setup

This document describes how to run the CBT Assistant POC locally using Docker Compose.

## Prerequisites

1. Docker Desktop installed and running
2. Docker Compose (included with Docker Desktop)
3. Gemini API key for the backend

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/macayaven/re-frame.git
   cd re-frame
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Build and start the services**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Health: http://localhost:8000/health

## Docker Configuration Details

### Backend Service
- **Port**: 8000
- **Dockerfile**: `backend/Dockerfile`
- **Base Image**: Python 3.12-slim
- **Key Features**:
  - uv package manager for fast dependency installation
  - Audio processing libraries (libsndfile1, ffmpeg)
  - Health check endpoint
  - Non-root user for security
  - Volume mounts for hot reload (src and prompts directories)

### Frontend Service  
- **Port**: 3000
- **Dockerfile**: `frontend/Dockerfile`
- **Base Image**: Node.js 18-alpine
- **Key Features**:
  - pnpm package manager
  - Development hot reload
  - Depends on backend health check
  - Volume mount with node_modules exclusion

### Network
- Services communicate via `cbt-assistant-network`
- Frontend accesses backend via `http://backend:8000` internally

## Environment Variables

### Backend
- `GEMINI_API_KEY`: Required for Google AI services
- `ENVIRONMENT`: Set to `development`
- `LOG_LEVEL`: Set to `debug` for development
- `PORT`: Backend port (default: 8000)
- `PYTHONUNBUFFERED`: Set to 1 for real-time logs

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `NODE_ENV`: Set to `development`

## Common Commands

```bash
# Start services
docker compose up

# Start with rebuild
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# Rebuild specific service
docker compose build backend
docker compose build frontend

# Execute commands in containers
docker compose exec backend bash
docker compose exec frontend sh

# Run backend tests
docker compose exec backend uv run poe test

# Run frontend tests  
docker compose exec frontend pnpm test
```

## Troubleshooting

### Docker daemon not running
```
Cannot connect to the Docker daemon at unix:///...
```
**Solution**: Start Docker Desktop

### Port already in use
```
bind: address already in use
```
**Solution**: Stop other services on ports 3000 or 8000, or modify ports in docker-compose.yml

### Backend health check failing
- Check backend logs: `docker compose logs backend`
- Verify GEMINI_API_KEY is set correctly
- Ensure all Python dependencies installed correctly

### Frontend can't connect to backend
- Verify backend is healthy: `curl http://localhost:8000/health`
- Check NEXT_PUBLIC_API_URL is set correctly
- Ensure both services are on the same Docker network

## Development Workflow

1. Make code changes in your editor
2. Backend changes in `src/` or `prompts/` auto-reload
3. Frontend changes auto-reload with Next.js fast refresh
4. No need to rebuild unless:
   - Changing dependencies
   - Modifying Dockerfile
   - Changing environment variables

## Security Notes

- Backend runs as non-root user `appuser`
- Source directories mounted as read-only in production mode
- Sensitive environment variables kept in `.env` (not committed)
- Health checks ensure service availability

## Next Steps

After successful local Docker setup:
1. Implement backend API routes (Issue #141)
2. Set up audio conversion (Issue #142)
3. Configure SSE for streaming (Issue #144, #148)
4. Run integration tests (Issue #145, #151)