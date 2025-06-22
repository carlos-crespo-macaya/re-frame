# re-frame API Usage Guide

## Overview

The re-frame API provides AI-assisted cognitive reframing support for individuals with Avoidant Personality Disorder (AvPD). This guide covers how to use the API effectively.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://api.re-frame.social`

## Authentication

Currently, the API uses session-based tracking without authentication. In production, Firebase Auth will be integrated.

## Rate Limiting

- **Limit**: 10 requests per hour per IP address
- **Headers**: Rate limit information is included in response headers:
  - `X-RateLimit-Limit`: Total allowed requests
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## Main Endpoints

### 1. Reframe a Thought

Process a thought through cognitive reframing using multiple therapeutic frameworks.

**Endpoint**: `POST /api/reframe/`

**Request Body**:
```json
{
  "thought": "Everyone will judge me if I speak up in the meeting",
  "context": "I have a presentation tomorrow"  // optional
}
```

**Validation**:
- `thought`: Required, 5-2000 characters
- `context`: Optional, max 500 characters

**Success Response** (200 OK):
```json
{
  "success": true,
  "response": "It's understandable to feel anxious about speaking up. Consider that others might actually appreciate your input...",
  "transparency": {
    "techniques_applied": ["cognitive_restructuring", "perspective_taking"],
    "reasoning_path": [
      "Identified mind-reading cognitive distortion",
      "Challenged assumption about others' thoughts",
      "Offered balanced perspective"
    ],
    "confidence": 0.85,
    "crisis_detected": false
  },
  "techniques_used": ["cognitive_restructuring", "perspective_taking"],
  "error": null
}
```

**Error Responses**:

- **422 Unprocessable Entity**: Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "thought"],
      "msg": "String should have at least 5 characters",
      "type": "string_too_short"
    }
  ]
}
```

- **429 Too Many Requests**: Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded. Please try again in 3600 seconds."
}
```

### 2. List Available Techniques

Get information about all CBT techniques used by the system.

**Endpoint**: `GET /api/reframe/techniques`

**Response** (200 OK):
```json
{
  "techniques": {
    "cognitive_restructuring": {
      "name": "Cognitive Restructuring",
      "description": "Identifying and challenging negative thought patterns",
      "helpful_for": ["catastrophizing", "black-and-white thinking", "mind reading"]
    },
    "evidence_analysis": {
      "name": "Evidence For/Against",
      "description": "Examining evidence that supports or contradicts a thought",
      "helpful_for": ["assumptions", "jumping to conclusions", "negative predictions"]
    }
    // ... more techniques
  },
  "note": "These techniques are particularly selected for their effectiveness with AvPD-related challenges."
}
```

### 3. Get Session History

Retrieve interaction history for a specific session.

**Endpoint**: `GET /api/reframe/session/{session_id}/history`

**Response** (200 OK):
```json
{
  "session": {
    "session_id": "session-123abc",
    "created_at": "2024-01-20T10:00:00Z",
    "last_activity": "2024-01-20T10:30:00Z",
    "interactions": [
      {
        "timestamp": "2024-01-20T10:00:00Z",
        "thought": "I can't go to the party",
        "response": "It's understandable to feel anxious about social events...",
        "techniques_used": ["cognitive_restructuring", "behavioral_experiments"]
      }
    ],
    "total_interactions": 1
  },
  "error": null,
  "note": "Session data is automatically cleaned up after 24 hours for privacy."
}
```

**Session Not Found** (200 OK):
```json
{
  "session": null,
  "error": "Session not found",
  "note": "Session data is automatically cleaned up after 24 hours for privacy."
}
```

## Health Monitoring

### Basic Health Check

**Endpoint**: `GET /api/health`

Verifies the service is running.

### Detailed Health Check

**Endpoint**: `GET /api/health/detailed`

Provides comprehensive health status including dependencies.

### Kubernetes Probes

- **Liveness**: `GET /api/health/live`
- **Readiness**: `GET /api/health/ready`
- **Startup**: `GET /api/health/startup`

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message",
  "error_type": "error_classification",
  "request_id": "req_123abc"
}
```

Common error types:
- `validation_error`: Input validation failed
- `rate_limit`: Rate limit exceeded
- `internal_error`: Server error
- `toxic_content`: Content flagged as harmful

## Best Practices

### 1. Handle Rate Limits

Always check rate limit headers and implement exponential backoff:

```python
import time
import requests

def make_request_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=data)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 3600))
            if attempt < max_retries - 1:
                time.sleep(min(retry_after, 300))  # Cap at 5 minutes
                continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

### 2. Validate Input

Always validate thought length and content before sending:

```javascript
function validateThought(thought) {
  if (!thought || thought.length < 5) {
    return { valid: false, error: "Thought must be at least 5 characters" };
  }
  
  if (thought.length > 2000) {
    return { valid: false, error: "Thought must be less than 2000 characters" };
  }
  
  return { valid: true };
}
```

### 3. Handle Crisis Responses

When `crisis_detected` is true, always display crisis resources:

```javascript
if (response.transparency.crisis_detected) {
  showCrisisResources();
  // Display: "If you're in crisis, please call 988 (US) or your local crisis line"
}
```

### 4. Show Transparency

Always display the reasoning path and techniques to build trust:

```javascript
// Show which techniques were used
response.techniques_used.forEach(technique => {
  displayTechnique(technique);
});

// Show reasoning steps
response.transparency.reasoning_path.forEach(step => {
  displayReasoningStep(step);
});
```

### 5. Session Management

Store the session ID client-side for continuity:

```javascript
// Store session ID from response headers
const sessionId = response.headers['X-Session-ID'];
localStorage.setItem('reframe_session_id', sessionId);

// Include in future requests
headers['X-Session-ID'] = localStorage.getItem('reframe_session_id');
```

## Testing

### Using cURL

```bash
# Basic reframe request
curl -X POST http://localhost:8000/api/reframe/ \
  -H "Content-Type: application/json" \
  -d '{"thought": "Everyone hates me"}'

# With context
curl -X POST http://localhost:8000/api/reframe/ \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "I cant handle social situations",
    "context": "After avoiding parties for years"
  }'

# Get techniques
curl http://localhost:8000/api/reframe/techniques

# Health check
curl http://localhost:8000/api/health
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Reframe a thought
response = requests.post(
    f"{BASE_URL}/api/reframe/",
    json={
        "thought": "I'll embarrass myself if I speak up",
        "context": "Team meeting tomorrow"
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Reframed: {data['response']}")
    print(f"Techniques: {', '.join(data['techniques_used'])}")
else:
    print(f"Error: {response.status_code} - {response.json()}")
```

### Using JavaScript/TypeScript

```typescript
interface ReframeRequest {
  thought: string;
  context?: string;
}

interface ReframeResponse {
  success: boolean;
  response: string;
  transparency: {
    techniques_applied: string[];
    reasoning_path: string[];
    confidence?: number;
    crisis_detected: boolean;
  };
  techniques_used: string[];
  error?: string;
}

async function reframeThought(request: ReframeRequest): Promise<ReframeResponse> {
  const response = await fetch('http://localhost:8000/api/reframe/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// Usage
try {
  const result = await reframeThought({
    thought: "Nobody wants to be around me",
    context: "Feeling isolated at work"
  });
  
  console.log('Reframed:', result.response);
  console.log('Techniques:', result.techniques_used);
} catch (error) {
  console.error('Error:', error);
}
```

## API Documentation

- **OpenAPI Spec**: `GET /api/openapi.json`
- **Swagger UI**: `GET /api/docs`
- **ReDoc**: `GET /api/redoc`

## Support

For issues or questions:
- GitHub Issues: https://github.com/macayaven/re-frame/issues
- API Status: Check `/api/health/detailed`

## Privacy & Security

- No personally identifiable information (PII) is stored
- Session data is automatically deleted after 24 hours
- All communication should use HTTPS in production
- Content is filtered for harmful or toxic language