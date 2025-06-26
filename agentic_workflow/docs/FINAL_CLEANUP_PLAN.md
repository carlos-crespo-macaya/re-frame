# Final Cleanup Plan: Remove Obsolete Files

## Files to DELETE

### Agent Files (DELETE ALL)
```bash
# Maya variants
rm reframe/agents/maya_agent.py
rm reframe/agents/maya_conversational_agent.py

# Original 3-agent system
rm reframe/agents/intake_agent.py
rm reframe/agents/reframe_agent.py
rm reframe/agents/pdf_agent.py

# Conversational variants
rm reframe/agents/conversational_intake_agent.py
rm reframe/agents/conversational_reframe_agent.py
rm reframe/agents/conversational_pdf_agent.py

# Other agent variants (if any exist)
rm reframe/agents/agent.py
rm reframe/agents/adk_context_agent.py
rm reframe/agents/adk_native_agent.py
rm reframe/agents/enhanced_conversational_agent.py
rm reframe/agents/proper_adk_agent.py
rm reframe/agents/simple_conversational_agent.py
rm reframe/agents/stateful_conversational_agent.py
rm reframe/agents/unified_conversational_agent.py
```

### Orchestrator Files (DELETE)
```bash
rm reframe/core/orchestrator.py
rm reframe/core/conversational_orchestrator.py
```

### Runner/Test Files (DELETE)
```bash
rm run_adk.py
rm adk_agent.py
rm agent.py
rm test_agent.py
rm test_unified_agent.py
rm test_language_detection.py
```

### Script Files (DELETE if exist)
```bash
rm scripts/start.py
rm scripts/run_cli.py
rm scripts/verify_*.py  # Keep only what's needed
```

### Other Files (DELETE)
```bash
rm reframe/agents/agent.py
rm reframe/agent.py
rm setup_logging.py  # If using config/logging.py instead
```

## Final Structure (After Renaming)

```
agentic_workflow/
├── reframe/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── intake_agent.py          # Renamed from multilingual_intake_agent.py
│   │   ├── analysis_agent.py        # Renamed from multilingual_analysis_agent.py
│   │   ├── pdf_agent.py             # Renamed from multilingual_pdf_agent.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── language_detector.py # Keep as is
│   │   └── callbacks/
│   │       ├── __init__.py
│   │       └── language_callback.py # Keep as is
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py                # Renamed from multilingual_models.py
│   │   └── [DELETE orchestrator.py, conversational_orchestrator.py]
│   ├── orchestrators/
│   │   ├── __init__.py
│   │   └── orchestrator.py          # Renamed from multilingual_orchestrator.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # Keep as is
│   │   └── logging.py               # Keep as is
│   └── infrastructure/
│       ├── __init__.py
│       ├── prompts.py               # Keep as is
│       └── [DELETE cache.py if unused]
├── scripts/
│   ├── __init__.py
│   └── run_web.py                   # Keep updated version
├── tests/
│   └── test_system.py               # Renamed from test_multilingual_system.py
├── docs/
│   ├── DESIGN.md                    # Renamed from MULTILINGUAL_3AGENT_DESIGN.md
│   ├── IMPLEMENTATION.md            # Renamed from MULTILINGUAL_3AGENT_IMPLEMENTATION.md
│   └── [Keep other relevant docs]
├── run_adk.py                       # Renamed from run_multilingual_adk.py
├── pyproject.toml                   # Keep as is
├── requirements.txt                 # Keep as is
└── README.md                        # Update with new structure
```

## Renaming Commands

```bash
# Rename agent files
mv reframe/agents/multilingual_intake_agent.py reframe/agents/intake_agent.py
mv reframe/agents/multilingual_analysis_agent.py reframe/agents/analysis_agent.py
mv reframe/agents/multilingual_pdf_agent.py reframe/agents/pdf_agent.py

# Rename core files
mv reframe/core/multilingual_models.py reframe/core/models.py
mv reframe/orchestrators/multilingual_orchestrator.py reframe/orchestrators/orchestrator.py

# Rename test files
mv tests/test_multilingual_system.py tests/test_system.py

# Rename docs
mv docs/MULTILINGUAL_3AGENT_DESIGN.md docs/DESIGN.md
mv docs/MULTILINGUAL_3AGENT_IMPLEMENTATION.md docs/IMPLEMENTATION.md

# Rename runner
mv run_multilingual_adk.py run_adk.py
```

## Class/Variable Renames

### In intake_agent.py:
- `MultilingualIntakeAgent` → `IntakeAgent`
- Keep function names as they describe functionality

### In analysis_agent.py:
- `MultilingualAnalysisAgent` → `AnalysisAgent`

### In pdf_agent.py:
- `MultilingualPDFAgent` → `PDFAgent`
- `generate_multilingual_pdf` → `generate_pdf`

### In models.py:
- `MultilingualSessionState` → `SessionState`

### In orchestrator.py:
- `MultilingualReframeOrchestrator` → `ReframeOrchestrator`

### Update all imports:
```python
# Before
from reframe.agents.multilingual_intake_agent import MultilingualIntakeAgent
from reframe.core.multilingual_models import MultilingualSessionState

# After
from reframe.agents.intake_agent import IntakeAgent
from reframe.core.models import SessionState
```

## Validation Before Deletion

1. **Test the new system**:
   ```bash
   python tests/test_multilingual_system.py
   adk web
   ```

2. **Verify functionality**:
   - Language detection works
   - 3-agent flow works
   - Exit commands work
   - PDF generation works

3. **Create backup**:
   ```bash
   tar -czf backup_before_cleanup.tar.gz reframe/
   ```

4. **Run cleanup**:
   ```bash
   # Execute all rm commands above
   # Execute all mv commands above
   ```

5. **Update imports in all files**

6. **Test again**:
   ```bash
   python tests/test_system.py
   adk web
   ```

## Notes

- The system will still be multilingual, just without the prefix
- All language detection functionality remains
- The 3-agent architecture is preserved
- ADK best practices are maintained
- Clean, professional naming convention