# Docker Setup for re-frame Backend

This guide explains how to build and run the re-frame backend using Docker.

## Prerequisites

- Docker installed on your system
- Google API key for Gemini AI

## Building the Image

```bash
# Build the Docker image
docker build -t re-frame-backend:latest .

# Build with specific platform (for deployment)
docker build --platform linux/amd64 -t re-frame-backend:latest .
```

## Running Locally

### Using Docker Run

```bash
# Run with environment variables
docker run -d \
  --name re-frame-backend \
  -p 8000:8000 \
  -e GOOGLE_API_KEY="your-api-key-here" \
  -e PORT=8000 \
  re-frame-backend:latest

# Check logs
docker logs re-frame-backend

# Stop and remove
docker stop re-frame-backend
docker rm re-frame-backend
```

### Using Docker Compose

```bash
# Create .env file with your Google API key
echo "GOOGLE_API_KEY=your-api-key-here" > .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Health Check

The container includes a health check that verifies the API is responding:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' re-frame-backend

# Test health endpoint directly
curl http://localhost:8000/api/health
```

## Cloud Run Deployment

The Dockerfile is optimized for Google Cloud Run:

1. **Multi-stage build** - Reduces final image size
2. **Non-root user** - Security best practice
3. **PORT environment variable** - Cloud Run requirement
4. **Health check** - For container orchestration

To deploy to Cloud Run:

```bash
# Build and push to Google Container Registry
docker build --platform linux/amd64 -t gcr.io/PROJECT_ID/re-frame-backend:latest .
docker push gcr.io/PROJECT_ID/re-frame-backend:latest

# Deploy to Cloud Run
gcloud run deploy re-frame-backend \
  --image gcr.io/PROJECT_ID/re-frame-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="your-api-key"
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI Studio API key | Yes |
| `PORT` | Port to run the server on (default: 8000) | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | No |

## Security Notes

1. **Never** build secrets directly into the image
2. Use environment variables or mounted files for sensitive data
3. The image runs as non-root user `appuser` (UID 1000)
4. For production, use Google Secret Manager or similar

## Troubleshooting

### Container fails to start
- Check logs: `docker logs re-frame-backend`
- Verify environment variables are set
- Ensure port 8000 is not already in use

### Health check failing
- Verify GOOGLE_API_KEY is valid
- Check network connectivity
- Review application logs for errors

### Image size concerns
The image is approximately 650MB due to Python dependencies and Google Cloud libraries. This is normal and optimized as much as possible while maintaining functionality.