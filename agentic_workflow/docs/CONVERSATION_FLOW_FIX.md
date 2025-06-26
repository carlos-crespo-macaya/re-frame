# Conversation Flow Fix

## Issue
The agent was mentioning PDF generation too early in the conversation, before gathering all necessary information through the discovery and reframing phases.

## Solution
Created `MayaConversationalMultilingualAgent` with proper conversation flow management:

### Conversation Phases

1. **GREETING (First message)**
   - Detect language from user's first message
   - Provide greeting in detected language
   - Explain the three phases
   - Ask what's on their mind

2. **DISCOVERY (Messages 2-4)**
   - Ask about the specific situation
   - Ask about automatic thoughts
   - Ask about emotions
   - NO mention of PDF

3. **REFRAMING (Messages 5-7)**
   - Identify cognitive distortions
   - Help create balanced thoughts
   - Suggest micro-actions
   - Get confidence ratings
   - Still NO mention of PDF

4. **SUMMARY (Message 8+)**
   - Summarize the session
   - ASK if user wants a PDF summary
   - Only generate PDF if explicitly requested

## Key Features

1. **Phase Management**: Clear instructions for each conversation phase
2. **PDF Control**: PDF is only mentioned after completing all phases
3. **User Consent**: PDF is only generated if user explicitly asks for it
4. **Language Consistency**: Maintains detected language throughout

## Testing

1. Start ADK web:
```bash
cd /Users/carlos/workspace/re-frame/agentic_workflow
adk web
```

2. Test conversation flow:
```
User: "hola, tengo un problema con mi ansiedad"
Maya: [Spanish greeting, asks what's on mind]

User: [Describes situation]
Maya: [Asks about thoughts - NO PDF mention]

User: [Describes thoughts]
Maya: [Asks about emotions - NO PDF mention]

User: [Describes emotions]
Maya: [Moves to reframing - NO PDF mention]

User: [Works on reframing]
Maya: [Helps with balanced thoughts - NO PDF mention]

User: [Completes reframing]
Maya: [Summarizes session, THEN asks if they want PDF]

User: "sí, me gustaría el PDF"
Maya: [Now generates PDF]
```

## Benefits

1. **Natural Flow**: Conversation follows CBT session structure
2. **Complete Information**: Ensures all data is gathered before summary
3. **User Control**: PDF only created when requested
4. **Professional**: Mirrors real therapy session progression