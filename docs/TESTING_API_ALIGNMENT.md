# Testing API Alignment

This document provides instructions for testing the frontend-backend integration after completing the API alignment work.

## Prerequisites

1. Ensure you have the Gemini API key set:
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```

2. Make sure all dependencies are installed:
   ```bash
   # Frontend
   cd frontend && pnpm install
   
   # Backend
   cd backend && pip install -r requirements.txt
   ```

## Testing Steps

### 1. Start the Backend

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

The backend should start on http://localhost:8000

### 2. Start the Frontend

In a new terminal:

```bash
cd frontend
pnpm dev
```

The frontend should start on http://localhost:3000

### 3. Test Basic Page with Language Selector

1. Navigate to http://localhost:3000
2. You should see a language selector in the header
3. Try changing the language
4. The form should still work for text input

### 4. Test Conversation Demo

1. Navigate to http://localhost:3000/demo
2. You should see the conversation interface
3. Language selector should be present
4. Click the microphone button to start recording
5. Speak a message
6. Stop recording
7. You should see:
   - Your transcribed message
   - An AI response in the selected language

### 5. Test SSE Connection

1. Open browser developer tools
2. Go to Network tab
3. Start a conversation
4. Look for SSE connection to `/api/events/{session_id}`
5. Verify the URL includes the language parameter

### 6. Test Different Languages

1. Select Spanish (Español)
2. Record a message in Spanish
3. The AI should respond in Spanish
4. Try other languages

## Troubleshooting

### CORS Errors
- Make sure the backend is running on port 8000
- Check that NEXT_PUBLIC_API_URL is set correctly

### Connection Refused
- Verify both frontend and backend are running
- Check the ports are correct

### No Audio Recording
- Check browser permissions for microphone
- Ensure HTTPS or localhost is being used

### No AI Response
- Check the backend logs for errors
- Verify GEMINI_API_KEY is set
- Check SSE connection in browser network tab

## Expected Results

When everything is working correctly:
1. Language selector changes the conversation language
2. Audio recording works and transcribes speech
3. AI responds in the selected language
4. SSE streaming shows real-time updates
5. Session management works (new session button)