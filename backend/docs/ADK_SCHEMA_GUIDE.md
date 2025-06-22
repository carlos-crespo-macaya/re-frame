# Google ADK Schema Guide for re-frame

## Overview

Google ADK's LlmAgent supports structured input and output validation using Pydantic models. This guide outlines how to implement type-safe agents for the re-frame project.

## Key Concepts

### 1. Schema-Based Agents

ADK agents can define:
- `input_schema`: Pydantic model for validating input data
- `output_schema`: Pydantic model for validating output data

Benefits:
- Type safety and validation
- Automatic JSON parsing and formatting
- Clear API contracts between agents
- Better error handling

### 2. Implementation Pattern

```python
from pydantic import BaseModel, Field
from google.adk import agents

# Define input schema
class IntakeInput(BaseModel):
    user_thought: str = Field(..., min_length=3, max_length=2000)
    timestamp: str = Field(default="current")
    context: str = Field(default="initial_intake")

# Define output schema  
class IntakeOutput(BaseModel):
    is_valid: bool
    requires_crisis_support: bool = False
    extracted_elements: ExtractedElements
    identified_patterns: list[str] = Field(default_factory=list)
    validation_notes: str = ""

# Create agent with schemas
intake_agent = agents.LlmAgent(
    name="IntakeAgent",
    model="gemini-1.5-flash",
    instruction=INTAKE_INSTRUCTIONS,
    input_schema=IntakeInput,
    output_schema=IntakeOutput,
)
```

### 3. Multi-Agent Flow with Schemas

```python
# Agent 1: Intake
intake_result: IntakeOutput = await intake_agent.run(
    IntakeInput(user_thought="I feel anxious")
)

# Agent 2: CBT Framework (uses intake output as input)
class CBTInput(BaseModel):
    intake_analysis: IntakeOutput
    techniques_priority: list[str] = Field(default_factory=list)

cbt_result: CBTOutput = await cbt_agent.run(
    CBTInput(intake_analysis=intake_result)
)
```

## re-frame Agent Schemas

### IntakeAgent

**Input Schema:**
```python
class IntakeInput(BaseModel):
    user_thought: str = Field(..., min_length=3, max_length=2000)
    timestamp: str = Field(default="current")
    context: str = Field(default="initial_intake")
```

**Output Schema:**
```python
class IntakeOutput(BaseModel):
    is_valid: bool
    requires_crisis_support: bool = False
    extracted_elements: ExtractedElements
    identified_patterns: list[str] = Field(default_factory=list)
    validation_notes: str = ""

class ExtractedElements(BaseModel):
    situation: str
    thoughts: list[str]
    emotions: list[str]
    behaviors: list[str]
```

### CBTFrameworkAgent

**Input Schema:**
```python
class CBTInput(BaseModel):
    intake_analysis: IntakeOutput
    techniques_priority: list[str] = Field(
        default=["cognitive_restructuring", "evidence_examination", "gradual_exposure"]
    )
```

**Output Schema:**
```python
class CBTOutput(BaseModel):
    original_thought: str
    cognitive_distortions: list[str]
    reframed_thoughts: list[str]
    techniques_applied: list[TechniqueApplication]
    action_suggestions: list[str]
    validation: str

class TechniqueApplication(BaseModel):
    technique_name: str
    description: str
    application: str
```

### SynthesisAgent

**Input Schema:**
```python
class SynthesisInput(BaseModel):
    intake_analysis: IntakeOutput
    cbt_results: CBTOutput
    original_thought: str
```

**Output Schema:**
```python
class SynthesisOutput(BaseModel):
    main_response: str
    key_points: list[str]
    techniques_explained: str
    transparency_summary: str
    encouragement: str
```

## Migration Strategy

### Current State (Dictionary-based)
```python
# Current implementation
result = await self.process_with_transparency(intake_input.model_dump())
if result.get("success") and result.get("response"):
    analysis_dict = self.parse_json_response(result["response"])
    analysis = IntakeAnalysis.model_validate(analysis_dict)
```

### Target State (Schema-based)
```python
# ADK native implementation
result: IntakeOutput = await intake_agent.run(
    IntakeInput(user_thought=user_input)
)
# No parsing needed - ADK handles validation
```

## Benefits for re-frame

1. **Type Safety**: All agent interactions are type-checked
2. **Validation**: Input validation happens automatically
3. **Error Handling**: Schema validation errors are clear and actionable
4. **Documentation**: Schemas serve as API documentation
5. **Testing**: Easier to mock and test with defined schemas

## Implementation Steps

1. **Define all Pydantic models** in `agents/schemas.py`
2. **Update agents** to use ADK's LlmAgent with schemas
3. **Remove manual JSON parsing** code
4. **Update session manager** to work with typed responses
5. **Add schema validation tests**

## Example: Complete IntakeAgent

```python
from google.adk import agents
from .schemas import IntakeInput, IntakeOutput

class IntakeAgent:
    def __init__(self):
        self.agent = agents.LlmAgent(
            name="IntakeAgent",
            model="gemini-1.5-flash",
            instruction=self.INTAKE_INSTRUCTIONS,
            input_schema=IntakeInput,
            output_schema=IntakeOutput,
            global_instruction="Always respond with compassion for AvPD users"
        )
    
    async def process(self, user_thought: str) -> IntakeOutput:
        """Process user input with automatic validation."""
        return await self.agent.run(
            IntakeInput(user_thought=user_thought)
        )
```

## Testing Schemas

```python
import pytest
from agents.schemas import IntakeInput, IntakeOutput

def test_intake_input_validation():
    # Valid input
    valid = IntakeInput(user_thought="I feel anxious in social situations")
    assert valid.user_thought
    
    # Invalid - too short
    with pytest.raises(ValidationError):
        IntakeInput(user_thought="Hi")
    
    # Invalid - too long
    with pytest.raises(ValidationError):
        IntakeInput(user_thought="x" * 2001)
```

## Next Steps

1. Create `agents/schemas.py` with all Pydantic models
2. Refactor agents to use ADK's schema support
3. Update tests to use schema validation
4. Document any ADK-specific behaviors discovered during implementation