# Testing Guide: Multilingual 3-Agent System with ADK Web

## Prerequisites

1. **Ensure all environment variables are set**:
```bash
# Required
export GOOGLE_API_KEY="your-google-api-key"
export LANGFUSE_HOST="your-langfuse-host"
export LANGFUSE_PUBLIC_KEY="your-public-key"
export LANGFUSE_SECRET_KEY="your-secret-key"

# Optional but recommended
export SUPABASE_REFRAME_DB_CONNECTION_STRING="your-supabase-connection"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"  # For Google Translation API
```

2. **Install dependencies**:
```bash
cd /Users/carlos/workspace/re-frame/agentic_workflow
uv pip install -e ".[dev]"
uv pip install google-cloud-translate
```

## Step 1: Run the Test Script

First, verify the system is set up correctly:

```bash
uv run python tests/test_multilingual_system.py
```

You should see:
- ✅ Environment variables checked
- ✅ Language detection tests passing
- ✅ Exit command tests passing
- ✅ Orchestrator initialized

## Step 2: Start ADK Web Interface

```bash
# From the agentic_workflow directory
# ADK will automatically find runner.py in the current directory
adk web

# Or with session service if you have Supabase configured:
adk web --session_service_uri="${SUPABASE_REFRAME_DB_CONNECTION_STRING}"

# Or to specify the port:
adk web --port 8080
```

You should see:
```
✅ Multilingual ADK Runner configured
🌐 Language detection: Google Cloud Translation API
👥 Three agents: Intake → Analysis (with /exit) → PDF
💾 Session management: DatabaseSessionService (or InMemorySessionService)
📊 Observability: Langfuse + Arize

ADK Web Server started
For local testing, access at http://localhost:8000.
```

## Step 3: Navigate to the Interface

1. Open your browser to: http://localhost:8000
2. You should see the ADK Dev UI
3. The app should be listed as "multilingual_reframe_assistant"

## Step 4: Test Language Detection

### Test 1: Spanish
Type: `Hola, me siento muy ansioso por una presentación en el trabajo`

Expected response:
- Greeting in Spanish
- Questions about your situation in Spanish
- All responses continue in Spanish

### Test 2: English
Start a new session and type: `Hello, I'm feeling anxious about a work presentation`

Expected response:
- Greeting in English
- Questions in English
- All responses in English

### Test 3: French
Start a new session and type: `Bonjour, je suis anxieux à propos d'une présentation au travail`

Expected response:
- Greeting in French
- Questions in French

## Step 5: Test the 3-Agent Flow

### Phase 1: Intake Agent (2-4 messages)
The agent should:
1. Detect your language and greet you
2. Ask about your situation
3. Ask about your automatic thoughts
4. Ask about your emotions and intensity (1-10)

### Phase 2: Analysis Agent (unlimited with /exit)
The agent should:
1. Provide CBT analysis
2. **Inform you about the /exit command in your language**
3. Allow follow-up questions
4. Continue conversation until you're ready

Test the exit command:
- Spanish: Type `/salir`
- English: Type `/exit`
- French: Type `/sortir`

### Phase 3: PDF Agent (1 message)
After using the exit command:
1. Agent generates PDF summary
2. Provides closing message in your language
3. PDF should contain all session information

## Step 6: Verify Features

### Language Consistency
- [ ] All agents respond in the detected language
- [ ] No language switching mid-conversation
- [ ] PDF generated in correct language

### Exit Command
- [ ] Analysis agent mentions the /exit command
- [ ] Exit command works in detected language
- [ ] Smooth transition to PDF generation

### Session State
- [ ] Information carries between agents
- [ ] Language preference maintained
- [ ] All data appears in final PDF

## Troubleshooting

### Issue: "Module not found" errors
```bash
# Make sure you're in the right directory
cd /Users/carlos/workspace/re-frame/agentic_workflow

# Reinstall in development mode
uv pip install -e .
```

### Issue: Language not detected
- Check if message is long enough (>10 characters)
- Verify Google Cloud credentials if using API
- Pattern detection works offline as fallback

### Issue: Agents not transitioning
- Check Langfuse dashboard for errors
- Verify all required prompts exist in Langfuse:
  - intake-agent-adk-instructions
  - reframe-agent-adk-instructions
  - synthesis-agent-adk-instructions

### Issue: Exit command not working
- Make sure to use exact command: `/exit`, `/salir`, etc.
- Command must be at the beginning of the message
- Check console logs for command detection

## Viewing Logs

To see detailed logs:

```bash
# Run with debug logging
LOGLEVEL=DEBUG adk web

# Or check ADK logs
tail -f ~/.adk/logs/web.log
```

## Check Observability

1. **Langfuse Dashboard**: 
   - View all agent interactions
   - Check prompt usage
   - See conversation flow

2. **Arize Dashboard** (if configured):
   - Monitor model performance
   - Track language detection accuracy
   - View conversation metrics

## Example Full Conversation

```
User: Hola, tengo mucha ansiedad por una reunión importante

Intake Agent: ¡Hola! Soy tu asistente de reestructuración cognitiva. 🌱
[Continues in Spanish collecting information]

Analysis Agent: [Provides CBT analysis in Spanish]
Puedes escribir /salir en cualquier momento para terminar y recibir tu resumen.

User: /salir

PDF Agent: ¡Gracias por trabajar conmigo hoy! 🌱 Tu resumen está listo...
[Generates PDF in Spanish]
```

## Success Criteria

✅ Language detected from first message
✅ All agents respond in detected language  
✅ Conversation flows through 3 agents
✅ Exit command works properly
✅ PDF generated with complete information
✅ Session persisted (if Supabase configured)
✅ Traces visible in Langfuse