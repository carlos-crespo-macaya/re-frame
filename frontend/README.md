# Frontend - re-frame.social

This directory contains the Next.js 14 frontend application for the CBT Assistant.

## Quick Start

```bash
cd frontend
pnpm install
pnpm run dev
```

## Environment Configuration

### Local Development with Docker

1. Copy the environment template:
```bash
cp .env.local.example .env.local
```

2. The default configuration is set up for Docker Compose:
```
NEXT_PUBLIC_API_URL=http://backend:8000
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://backend:8000` | Yes |
| `NODE_ENV` | Environment mode | `development` | No |
| `SERVICE_NAME` | Service identifier for health checks | `re-frame-frontend` | No |
| `PORT` | Port to run the frontend on | `3000` | No |

### Development Modes

#### Docker Compose (Recommended)
From the root directory:
```bash
docker-compose up frontend
```

The frontend will be available at http://localhost:3000 with hot reload enabled.

#### Standalone Development
If running without Docker:
```bash
# Update .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Install dependencies
pnpm install

# Run development server
pnpm dev
```

## Features

- **Hot Reload**: Automatic refresh on code changes in development mode
- **Health Check**: Available at `/api/health`
- **Docker Network**: Service discovery via container names
- **Environment Isolation**: Separate configs for dev/prod

## Build

```bash
pnpm run build
pnpm run start
```

## Testing

```bash
pnpm run test
pnpm run test:watch
```

## Troubleshooting

1. **API Connection Issues**: Check that backend is running and healthy
2. **Hot Reload Not Working**: Ensure volumes are mounted correctly in docker-compose.yml
3. **Environment Variables**: Restart the container after changing .env.local

See the main [README.md](../README.md) for full project documentation.
