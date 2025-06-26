# Language Detection Solution

## Problem
The ADK automatic function calling was failing with the error:
```
Failed to parse the parameter cognitive_distortions: list[str] | None = None
```

This was caused by:
1. Python 3.10+ union syntax (`list[str] | None`) not being compatible with ADK's function parser
2. Complex callback implementations conflicting with ADK's execution model

## Solution
Created a simplified agent (`MayaSimpleMultilingualAgent`) that:
1. Uses instruction-based language detection (no callbacks)
2. Uses compatible type annotations (`Optional[List[str]]`)
3. Provides clear language detection rules in the agent instructions

## How It Works

### Language Detection Through Instructions
The agent is instructed to:
1. Analyze the user's first message for language indicators
2. Match words against language-specific patterns
3. Select the appropriate greeting based on detected language

### Key Changes
1. **Simplified Architecture**: No callbacks, just clear instructions
2. **Compatible Types**: Using `Optional[List[str]]` instead of `list[str] | None`
3. **Pattern Matching**: Direct word matching in instructions

## Testing

1. **Start ADK Web**:
```bash
cd /Users/carlos/workspace/re-frame/agentic_workflow
adk web
```

2. **Test Spanish** (most common):
```
hola, tengo un problema, estoy auto aislandome
```

Expected: Spanish greeting immediately

3. **Test Other Languages**:
- French: "Bonjour, j'ai un problème"
- Italian: "Ciao, ho un problema"
- English: "Hello, I have a problem"

## Files Changed
- `/reframe/agents/maya_simple_multilingual_agent.py` - New simplified agent
- `/reframe/agent.py` - Updated to use simple agent
- `/run_adk.py` - Updated to use simple agent
- `/scripts/run_web.py` - Updated to use simple agent

## Advantages
1. **No Complex Dependencies**: Works with standard ADK
2. **Clear Logic**: Language detection is in the instructions
3. **Fallback**: Defaults to English if no match
4. **Extensible**: Easy to add more languages

## Next Steps
Once this works reliably:
1. Add more sophisticated language detection
2. Implement voice input/output
3. Add session state management for language preference