# ADK Migration Plan

## Migration Approach

This document outlines the migration from legacy custom agents to the official Google ADK framework.

### What Changed

#### Removed Legacy Components
- `base.py` - Custom ReFrameAgent base class
- `intake_agent.py` - Legacy intake agent
- `cbt_framework_agent.py` - Legacy CBT agent  
- `synthesis_agent.py` - Legacy synthesis agent
- `framework.py` - Legacy framework abstractions
- `intake.py` - Legacy intake utilities
- `synthesis.py` - Legacy synthesis utilities
- `test_base_agent.py` - Legacy test files
- `test_cbt_agent.py` - Legacy test files

#### Added ADK Components
- `adk_base.py` - ADK-based ReFrame agent foundation
- `adk_intake_agent.py` - ADK intake agent with enhanced validation
- `adk_cbt_agent.py` - ADK CBT agent with tool integration
- `adk_synthesis_agent.py` - ADK synthesis agent with crisis handling
- `adk_session_manager.py` - Complete workflow orchestration
- `adk_tools.py` - Structured tools for enhanced analysis
- `adk_config.py` - Configuration management system
- `adk_observability.py` - Monitoring and debugging capabilities
- Comprehensive test suite for all components

### API Changes

#### Before (Legacy)
```python
from agents import IntakeAgent, CBTFrameworkAgent, SynthesisAgent

intake_agent = IntakeAgent()
cbt_agent = CBTFrameworkAgent()
synthesis_agent = SynthesisAgent()

# Manual orchestration required
intake_result = await intake_agent.process_user_input(user_input)
cbt_result = await cbt_agent.apply_cbt_techniques(intake_result)
synthesis_result = await synthesis_agent.create_user_response(cbt_result)
```

#### After (ADK)
```python
from agents import ADKSessionManager

session_manager = ADKSessionManager()

# Automatic orchestration with session management
result = await session_manager.process_user_input(user_input)
```

### Configuration Migration

#### Environment Variables
No changes required - ADK uses the same Google AI API key and settings.

#### New Configuration Options
```python
from agents import config_manager

# Access ADK-specific configuration
model_config = config_manager.get_model_config()
observability_config = config_manager.get_observability_config()
safety_config = config_manager.get_safety_config()
```

### Monitoring and Observability

#### New Capabilities
```python
from agents import observability_manager

# Enable debug mode for troubleshooting
observability_manager.enable_debug_mode()

# Get performance metrics
performance = observability_manager.get_performance_summary()
errors = observability_manager.get_error_analysis()
```

### Breaking Changes

1. **Import Changes**: Legacy agent classes no longer available
2. **Response Format**: ADK responses include enhanced transparency data
3. **Error Handling**: Improved error classification and user-friendly messages
4. **Session Management**: Automatic session tracking with cleanup

### Migration Benefits

✅ **Better Architecture**: Uses Google's battle-tested ADK patterns  
✅ **Enhanced Observability**: Built-in monitoring and debugging  
✅ **Improved Safety**: Multi-level crisis detection and content filtering  
✅ **Better Performance**: Optimized async workflows and error handling  
✅ **Tool Integration**: Native support for structured analysis tools  
✅ **Configuration Management**: Centralized, validated configuration  

### Testing Changes

#### Legacy Tests Removed
- Tests for custom agent implementations
- Tests for manual workflow orchestration

#### New Test Coverage
- ADK base agent functionality
- Session management and workflow orchestration
- Tool integration and error handling
- Configuration and observability features

### Deployment Considerations

1. **Dependencies**: Google ADK 1.4.2 already included in requirements
2. **Environment**: No additional environment setup required
3. **Configuration**: Existing settings continue to work
4. **Monitoring**: New observability endpoints available for admin use
5. **Session Cleanup**: Automatic cleanup after 24 hours for privacy

### Rollback Plan

If issues arise with the ADK implementation:

1. **Immediate**: Disable the new endpoints and return error responses
2. **Short-term**: The migration is complete, so rollback would require reverting the entire PR
3. **Long-term**: ADK provides better reliability and should be the path forward

### Post-Migration Tasks

1. **Performance Monitoring**: Monitor the new observability endpoints
2. **Error Analysis**: Review error patterns using ADK observability
3. **Configuration Tuning**: Adjust ADK settings based on usage patterns
4. **Documentation**: Update API documentation to reflect new capabilities
5. **Team Training**: Ensure team familiarity with ADK concepts and tools

### Support and Documentation

- **ADK Documentation**: https://google.github.io/adk-docs/
- **Migration Summary**: See `ADK_MIGRATION_SUMMARY.md`
- **Code Examples**: See test files for usage patterns
- **Configuration Reference**: See `adk_config.py` for all available settings