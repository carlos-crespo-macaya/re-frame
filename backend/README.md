# re-frame Backend

AI-assisted cognitive reframing support tool for people with Avoidant Personality Disorder (AvPD).

## Overview

This backend service uses Google's Agent Development Kit (ADK) to implement a multi-agent architecture for transparent, CBT-based cognitive reframing. The system prioritizes user trust through complete transparency of AI reasoning processes.

## Architecture

### Agents (using Google ADK)

1. **IntakeAgent**: Validates user input and extracts key elements
2. **CBTFrameworkAgent**: Applies evidence-based CBT techniques
3. **SynthesisAgent**: Creates warm, supportive responses with transparency

### Tech Stack

- **Framework**: FastAPI with async support
- **AI/LLM**: Google ADK + Gemini 1.5 Flash (via Google AI Studio)
- **Middleware**: CORS, structured logging, rate limiting
- **Python**: 3.12+

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- Google AI Studio API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Create virtual environment**:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_AI_API_KEY
```

4. **Run the application**:
```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Or use the built-in runner
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, you can access:
- Interactive API docs: `http://localhost:8000/api/docs`
- ReDoc documentation: `http://localhost:8000/api/redoc`
- Health check: `http://localhost:8000/api/health`

## Key Endpoints

### POST /api/reframe
Processes a thought for cognitive reframing.

**Request**:
```json
{
  "thought": "Everyone at the party will judge me negatively",
  "context": "Invited to a friend's birthday party"
}
```

**Response**:
```json
{
  "success": true,
  "response": "I understand that social situations...",
  "transparency": {
    "intake": {...},
    "cbt_analysis": {...},
    "synthesis": {...}
  },
  "techniques_used": ["cognitive_restructuring", "evidence_analysis"]
}
```

### GET /api/reframe/techniques
Lists available CBT techniques used by the system.

## Development

### Project Structure
```
backend/
├── agents/          # ADK agent implementations
├── api/            # FastAPI endpoints
├── config/         # Configuration management
├── middleware/     # CORS, logging, rate limiting
├── tests/          # Test files (pytest)
└── main.py         # Application entry point
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_agents.py
```

### Environment Variables

Key configuration options (see `.env.example`):
- `GOOGLE_AI_API_KEY`: Your Google AI Studio API key (required)
- `GOOGLE_AI_MODEL`: Model to use (default: gemini-1.5-flash)
- `RATE_LIMIT_REQUESTS`: Requests per hour (default: 10)
- `LOG_LEVEL`: Logging level (default: INFO)

## Security & Privacy

- No PII storage - all sessions are ephemeral
- Rate limiting: 10 requests/hour per IP
- Content filtering for harmful inputs
- CORS configured for frontend origins
- All responses include transparency data

## Rate Limiting

The API implements rate limiting to ensure fair usage:
- Default: 10 requests per hour per IP address
- Headers included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Monitoring

The application includes structured JSON logging with:
- Request IDs for tracing
- Performance metrics
- Error tracking
- Component health status

## Phase 0 Alpha Goals

- ✅ Single endpoint for thought reframing
- ✅ CBT-based processing with transparency
- ✅ Rate limiting implementation
- ✅ Basic content filtering
- ✅ Health check endpoints
- ⏳ Integration with frontend
- ⏳ Deployment to Google Cloud Run

## Contributing

This is the alpha phase focusing on core functionality. Key priorities:
1. Cost efficiency (stay within GCP credits)
2. Transparency of AI reasoning
3. AvPD-sensitive communication
4. Reliable CBT technique application

## License

[Pending - to be determined]