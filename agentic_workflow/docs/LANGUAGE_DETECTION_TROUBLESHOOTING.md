# Language Detection Troubleshooting Guide

## Quick Verification Steps

### 1. Test the Detection Logic
```bash
cd /Users/carlos/workspace/re-frame/agentic_workflow
uv run python test_language_detection.py
```

This will test:
- Simple pattern-based detection (always works)
- API-based detection (if credentials available)
- Agent initialization

### 2. Run ADK Web
```bash
adk web
```

### 3. Test with Spanish Input
Send this as your FIRST message:
```
hola, tengo un problema, estoy auto aislandome
```

## Expected Behavior

### ✅ Correct (What should happen now):
```
User: hola, tengo un problema, estoy auto aislandome

Maya: ¡Hola! Soy Maya, tu compañera de reestructuración cognitiva. 🌱
[Rest of Spanish greeting...]
```

### ❌ Incorrect (What was happening before):
```
User: hola, tengo un problema, estoy auto aislandome

Maya: Hello! I'm Maya, your cognitive reframing companion. 🌱
[English greeting first, then switches to Spanish]
```

## How It Works

### 1. **Enhanced Agent with State-Based Detection**
The agent now:
- Checks session state for `user_language` on every message
- If not found, detects language from the current message
- Stores the detected language in state
- Responds in the detected language immediately

### 2. **Fallback Detection**
If Google Cloud Translation API fails:
- Uses pattern matching for common words
- Supports: Spanish, French, Italian, Portuguese, Catalan, German, English
- Defaults to English if no clear match

### 3. **Updated Entry Points**
All entry points now use `MayaEnhancedMultilingualAgent`:
- `/reframe/agent.py` - Main agent module
- `/scripts/run_web.py` - ADK web runner
- `/run_adk.py` - Direct ADK runner

## Common Issues

### Issue: Still Getting English First
**Cause**: Old agent might be cached
**Solution**: 
1. Stop ADK web (Ctrl+C)
2. Clear any Python cache: `find . -name "*.pyc" -delete`
3. Restart ADK web

### Issue: Language Not Detected
**Cause**: Message doesn't have enough language markers
**Solution**: The agent will default to English, but you can explicitly state your language preference

### Issue: Google Translation API Error
**Cause**: Missing credentials or API not enabled
**Solution**: The fallback detection will automatically activate - no action needed

## Debug Checklist

1. **Verify correct agent is loaded**:
   - Check ADK web console for: "Successfully loaded Maya Enhanced - Multilingual cognitive reframing assistant"

2. **Check state management**:
   - In ADK web UI, check the Debug tab to see if `user_language` is being stored

3. **Test pattern detection**:
   ```bash
   uv run python test_language_detection.py
   ```

4. **Verify file updates**:
   ```bash
   grep -n "MayaEnhancedMultilingualAgent" reframe/agent.py scripts/run_web.py run_adk.py
   ```

## Language Examples

Test with these first messages:

- **Spanish**: "hola, necesito ayuda con mi ansiedad"
- **French**: "bonjour, j'ai besoin d'aide avec mon anxiété"
- **Italian**: "ciao, ho bisogno di aiuto con la mia ansia"
- **Portuguese**: "olá, preciso de ajuda com minha ansiedade"
- **Catalan**: "hola, necessito ajuda amb la meva ansietat"
- **German**: "hallo, ich brauche Hilfe bei meiner Angst"
- **English**: "hello, I need help with my anxiety"

## Next Steps: Voice Support

Once language detection is working correctly:
1. Integrate Web Speech API for voice input
2. Add Google Cloud Text-to-Speech for voice responses
3. Ensure language consistency across modalities