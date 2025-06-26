# Language Detection Fix

## Issue
Maya was sending the English greeting first, then detecting language and switching to Spanish only after the user complained.

## Solution
Updated the agent instructions to emphasize:

1. **ABSOLUTE FIRST RULE**: Detect language BEFORE any greeting
2. **Step-by-step process**:
   - Receive user message
   - Run detect_language tool
   - Store language preference
   - ONLY THEN send greeting in detected language

## Key Changes

### Enhanced Instructions
```
## ABSOLUTE FIRST RULE: DETECT LANGUAGE BEFORE ANY GREETING
WHEN YOU RECEIVE THE VERY FIRST MESSAGE:
- DO NOT send any greeting yet
- FIRST run detect_language tool on the user's message
- THEN store the language preference
- ONLY AFTER THAT send your greeting in the detected language
- NEVER send an English greeting unless English was detected
```

### Clear Greeting Selection
```
## MULTILINGUAL GREETINGS
[Use the greeting that matches the detected language_code from detect_language tool]
```

## Testing

1. Restart ADK web
2. Send: "hola, tengo un problema, estoy auto aislandome"
3. Expected: Maya detects Spanish and responds with Spanish greeting immediately

## What Maya Should Do

1. **Behind the scenes**:
   - detect_language("hola, tengo un problema, estoy auto aislandome")
   - Returns: {"language_code": "es", "language_name": "español", "confidence": 0.99}
   - store_language_preference("es", "español")

2. **User sees**:
   - Spanish greeting immediately (no English first)
   - Entire conversation continues in Spanish
   - PDF generated in Spanish

## Verification

The conversation should look like:

User: "hola, tengo un problema, estoy auto aislandome"

Maya: "¡Hola! Soy Maya, tu compañera de reestructuración cognitiva. 🌱

Estoy aquí para ayudarte a explorar tus pensamientos y sentimientos..."

(NO English greeting should appear)