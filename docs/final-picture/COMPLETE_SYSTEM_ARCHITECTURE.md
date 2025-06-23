# Complete Multi-Agent System Architecture

## System Overview

The Re-frame system consists of two main components:
1. **Therapeutic Multi-Agent System** - ADK-based agents for cognitive reframing
2. **User Management Backend** - Separate API for authentication, data storage, and session management

## Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend"
        UI[React Frontend]
    end
    
    subgraph "API Gateway"
        GW[API Gateway/Load Balancer]
        AUTH[Auth Middleware]
        GUARD[Guardrails Service]
    end
    
    subgraph "User Management Backend"
        UAPI[User API - FastAPI]
        UAUTH[Auth Service - JWT]
        SESS[Session Manager]
        MEM[Episodic Memory Service]
        PDF[PDF Generator]
        
        subgraph "Storage"
            UDB[(User DB - PostgreSQL)]
            DOC[(Document Store - MongoDB)]
            CACHE[(Redis Cache)]
        end
    end
    
    subgraph "ADK Multi-Agent System"
        ORCH[Main Orchestrator]
        
        subgraph "Conversation Phase"
            LOOP[LoopAgent]
            CONV[ConversationAgent]
            VAL[InfoValidator]
        end
        
        subgraph "Framework Phase"
            SEL[FrameworkSelector]
            PAR[ParallelAgent]
            CBT[CBT Agent]
            DBT[DBT Agent]
            ACT[ACT Agent]
            STOIC[Stoicism Agent]
        end
        
        subgraph "Synthesis Phase"
            SYN[SynthesisAgent]
            ACTION[ActionPlanner]
        end
        
        STATE[(Session State)]
    end
    
    subgraph "External Services"
        AI[Google AI Studio]
        OBS[Observability]
    end
    
    UI --> GW
    GW --> AUTH
    AUTH --> GUARD
    GUARD --> UAPI
    GUARD --> ORCH
    
    UAPI --> UAUTH
    UAPI --> SESS
    UAPI --> MEM
    UAPI --> PDF
    
    SESS --> UDB
    MEM --> DOC
    SESS --> CACHE
    PDF --> DOC
    
    ORCH --> LOOP
    LOOP --> CONV
    LOOP --> VAL
    
    VAL --> SEL
    SEL --> PAR
    PAR --> CBT
    PAR --> DBT
    PAR --> ACT
    PAR --> STOIC
    
    CBT --> SYN
    DBT --> SYN
    ACT --> SYN
    STOIC --> SYN
    
    SYN --> ACTION
    ACTION --> PDF
    
    All --> STATE
    All --> AI
    AI --> OBS
```

## Component Specifications

### 1. User Management Backend API

```python
# src/user_api/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastREDACTED
from sqlalchemy.orm import Session
import jwt

app = FastAPI(title="Re-frame User Management API")

# Endpoints
@app.post("/api/v1/auth/register")
async def register(user_data: UserRegistration):
    """Register new user with email verification"""
    
@app.post("/api/v1/auth/login")
async def login(credentials: LoginCredentials):
    """Authenticate and return JWT tokens"""
    
@app.post("/api/v1/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    
@app.get("/api/v1/users/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user profile"""
    
@app.post("/api/v1/sessions")
async def create_session(user_id: str):
    """Create new therapy session"""
    
@app.get("/api/v1/sessions/{session_id}/history")
async def get_session_history(session_id: str, user_id: str):
    """Get anonymized session history"""
    
@app.post("/api/v1/feedback")
async def submit_feedback(session_id: str, feedback: SessionFeedback):
    """Store user feedback for session"""
    
@app.get("/api/v1/documents")
async def list_documents(user_id: str):
    """List user's session PDFs"""
    
@app.delete("/api/v1/users/me")
async def delete_account(user_id: str):
    """GDPR-compliant account deletion"""
```

### 2. Guardrails Service

```python
# src/guardrails/guardrails_service.py
from typing import Dict, Tuple, List
import re
from transformers import pipeline

class GuardrailsService:
    """Input/output validation and topic filtering"""
    
    def __init__(self):
        self.toxicity_classifier = pipeline("text-classification", 
                                          model="unitary/toxic-bert")
        self.pii_patterns = self._compile_pii_patterns()
        self.allowed_topics = self._load_allowed_topics()
        
    async def validate_input(self, text: str) -> Tuple[bool, str, Dict]:
        """
        Validate input for:
        1. Therapeutic relevance
        2. Harmful content
        3. PII detection
        4. Length limits
        """
        # Check length
        if len(text) > 2000:
            return False, "Input too long. Please keep under 2000 characters.", {}
            
        # Check toxicity
        toxicity = self.toxicity_classifier(text)
        if toxicity[0]['label'] == 'TOXIC' and toxicity[0]['score'] > 0.8:
            return False, "Please rephrase in a more constructive way.", {}
            
        # Check therapeutic relevance
        if not self._is_therapeutic_topic(text):
            return False, "I'm designed to help with emotional and mental health concerns. Could you share what's troubling you emotionally?", {}
            
        # Mask PII
        masked_text, pii_found = self._mask_pii(text)
        
        return True, masked_text, {"pii_masked": pii_found}
    
    async def validate_output(self, response: Dict) -> Tuple[bool, Dict]:
        """
        Validate output for:
        1. No harmful advice
        2. Therapeutic boundaries
        3. PII removal
        """
        # Check for harmful suggestions
        if self._contains_harmful_advice(response['message']):
            return False, self._safe_alternative_response()
            
        # Remove any PII
        response['message'] = self._remove_pii(response['message'])
        
        # Ensure therapeutic boundaries
        if not self._maintains_boundaries(response['message']):
            response['message'] = self._add_boundary_reminder(response['message'])
            
        return True, response
    
    def _mask_pii(self, text: str) -> Tuple[str, List[str]]:
        """Mask personally identifiable information"""
        pii_found = []
        masked = text
        
        # Phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, text):
            pii_found.append("phone")
            masked = re.sub(phone_pattern, "[PHONE]", masked)
            
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            pii_found.append("email")
            masked = re.sub(email_pattern, "[EMAIL]", masked)
            
        # Names (more complex, use NER)
        # SSN, addresses, etc.
        
        return masked, pii_found
```

### 3. Episodic Memory Service

```python
# src/memory/episodic_memory.py
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer

class EpisodicMemoryService:
    """Pattern recognition and memory for personalization"""
    
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.memory_store = {}  # In production, use vector DB
        
    async def store_session_patterns(self, user_id: str, session_data: Dict):
        """Store patterns from completed session"""
        patterns = {
            'timestamp': datetime.now(),
            'thought_patterns': self._extract_thought_patterns(session_data),
            'emotional_patterns': self._extract_emotional_patterns(session_data),
            'framework_effectiveness': self._calculate_effectiveness(session_data),
            'techniques_used': session_data.get('techniques_applied', []),
            'user_feedback': session_data.get('feedback', {})
        }
        
        # Encode for similarity search
        patterns['embedding'] = self.encoder.encode(
            f"{patterns['thought_patterns']} {patterns['emotional_patterns']}"
        )
        
        if user_id not in self.memory_store:
            self.memory_store[user_id] = []
        self.memory_store[user_id].append(patterns)
        
    async def retrieve_relevant_patterns(self, user_id: str, current_thought: str) -> Dict:
        """Retrieve relevant past patterns for current situation"""
        if user_id not in self.memory_store:
            return {}
            
        current_embedding = self.encoder.encode(current_thought)
        
        # Find similar past situations
        similarities = []
        for memory in self.memory_store[user_id]:
            similarity = np.dot(current_embedding, memory['embedding'])
            similarities.append((similarity, memory))
            
        # Get top 3 most relevant
        similarities.sort(key=lambda x: x[0], reverse=True)
        relevant_memories = [m[1] for m in similarities[:3]]
        
        return {
            'recurring_patterns': self._identify_recurring_patterns(relevant_memories),
            'effective_frameworks': self._get_effective_frameworks(relevant_memories),
            'successful_techniques': self._get_successful_techniques(relevant_memories)
        }
    
    async def analyze_progress(self, user_id: str) -> Dict:
        """Analyze user's progress over time"""
        if user_id not in self.memory_store:
            return {}
            
        memories = self.memory_store[user_id]
        
        return {
            'total_sessions': len(memories),
            'common_patterns': self._analyze_common_patterns(memories),
            'framework_preferences': self._analyze_framework_usage(memories),
            'emotional_trends': self._analyze_emotional_trends(memories),
            'growth_indicators': self._identify_growth(memories)
        }
```

### 4. PDF Generation Service

```python
# src/documents/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import hashlib
from datetime import datetime

class SessionPDFGenerator:
    """Generate anonymized session documentation"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    async def generate_session_pdf(self, session_data: Dict, user_id: str) -> bytes:
        """Generate PDF with masked PII"""
        # Anonymize session data
        anonymized = self._anonymize_data(session_data)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Cognitive Reframing Session Report", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Session Info
        session_id = hashlib.sha256(f"{user_id}{session_data['timestamp']}".encode()).hexdigest()[:8]
        story.append(Paragraph(f"Session ID: {session_id}", self.styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Situation Summary
        story.append(Paragraph("Situation", self.styles['Heading2']))
        story.append(Paragraph(anonymized['situation'], self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Frameworks Used
        story.append(Paragraph("Therapeutic Approach", self.styles['Heading2']))
        story.append(Paragraph(f"Frameworks: {', '.join(anonymized['frameworks'])}", self.styles['Normal']))
        story.append(Paragraph(f"Selection Reasoning: {anonymized['framework_reasoning']}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Framework Explanations
        for framework in anonymized['frameworks']:
            story.append(Paragraph(framework, self.styles['Heading3']))
            story.append(Paragraph(self._get_framework_description(framework), self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Therapeutic Response
        story.append(Paragraph("Therapeutic Insights", self.styles['Heading2']))
        story.append(Paragraph(anonymized['response'], self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Action Plan
        story.append(Paragraph("Action Plan", self.styles['Heading2']))
        for i, action in enumerate(anonymized['actions'], 1):
            story.append(Paragraph(f"{i}. {action}", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Encrypt before storage
        encrypted_pdf = self._encrypt_pdf(pdf_bytes, user_id)
        
        return encrypted_pdf
    
    def _anonymize_data(self, data: Dict) -> Dict:
        """Remove all PII from session data"""
        anonymized = data.copy()
        
        # Replace names with placeholders
        anonymized['situation'] = self._replace_names(data.get('situation', ''))
        anonymized['response'] = self._replace_names(data.get('response', ''))
        
        # Remove specific details that could identify
        anonymized['situation'] = self._generalize_details(anonymized['situation'])
        
        return anonymized
```

### 5. Complete ADK Agent Implementation

```python
# src/agents/complete_multiagent_system.py
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.tools import Tool, GoogleSearchTool
from typing import AsyncGenerator, Dict, Any

# Crisis Detection Agent
class CrisisDetectionAgent(BaseAgent):
    """First line of defense for crisis situations"""
    
    name = "CrisisDetector"
    description = "Detects crisis indicators requiring immediate intervention"
    
    async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
        thought = ctx.session.state.get("user_thought", "").lower()
        intensity = ctx.session.state.get("emotion_intensity", 0)
        
        crisis_keywords = ["suicide", "kill myself", "end it all", "can't go on", 
                          "harm myself", "hurt myself", "not worth living"]
        
        is_crisis = any(keyword in thought for keyword in crisis_keywords) or intensity >= 9
        
        if is_crisis:
            ctx.session.state["crisis_detected"] = True
            ctx.session.state["processing_mode"] = "crisis"
            
            crisis_response = {
                "message": "I'm very concerned about what you're sharing. Your safety is the most important thing right now.",
                "resources": [
                    "988 Suicide & Crisis Lifeline (call or text)",
                    "Crisis Text Line: Text HOME to 741741",
                    "Emergency Services: 911"
                ],
                "immediate_support": "Would you like me to help you create a safety plan while you consider reaching out for support?"
            }
            
            ctx.session.state["crisis_response"] = crisis_response
            
            yield Event(
                author=self.name,
                content="Crisis detected - switching to crisis protocol",
                actions=EventActions(escalate=True)
            )
        else:
            ctx.session.state["crisis_detected"] = False
            ctx.session.state["processing_mode"] = "normal"
            
            yield Event(
                author=self.name,
                content="No crisis indicators detected - proceeding with normal flow"
            )

# Information Gathering Agents
conversation_agent = Agent(
    name="ConversationAgent",
    model="gemini-2.0-flash-002",
    description="Empathetic conversationalist for information gathering",
    instruction="""You are a warm, empathetic therapist specializing in AvPD.
    
    Your task is to gather essential information through natural conversation:
    1. The specific thought or worry
    2. Current emotional state and intensity (1-10)
    3. Situational context
    4. What matters to them (values)
    
    Current state:
    - Thought: {user_thought?}
    - Emotion: {emotion_name?} (intensity: {emotion_intensity?})
    - Situation: {situation_context?}
    - Values: {user_values?}
    - Missing: {missing_elements?}
    
    Guidelines:
    - Be conversational and caring
    - Validate their experience
    - Ask one thing at a time
    - Use their words back to them
    - If they seem overwhelmed, slow down
    
    Store information using your tools.""",
    tools=[
        UpdateStateTool(),
        EmotionScaleTool(),
        ValidateInputTool()
    ],
    output_REDACTED"
)

class InformationValidator(BaseAgent):
    """Validates completeness of gathered information"""
    
    name = "InformationValidator"
    description = "Checks if we have sufficient information"
    
    async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        
        # Check required elements
        has_thought = bool(state.get("user_thought"))
        has_emotion = bool(state.get("emotion_name"))
        has_intensity = state.get("emotion_intensity") is not None
        has_context = bool(state.get("situation_context"))
        
        complete = all([has_thought, has_emotion, has_intensity])
        
        missing = []
        if not has_thought:
            missing.append("specific thought or worry")
        if not has_emotion:
            missing.append("emotional state")
        if not has_intensity:
            missing.append("emotion intensity (1-10)")
        if not has_context:
            missing.append("situation context")
            
        state["information_complete"] = complete
        state["missing_elements"] = missing
        
        yield Event(
            author=self.name,
            content=f"Validation: {'Complete' if complete else f'Missing {missing}'}",
            actions=EventActions(escalate=complete)  # Exit loop when complete
        )

# Framework Selection Agent
framework_selector = Agent(
    name="FrameworkSelector",
    model="gemini-2.0-flash-002",
    description="Selects appropriate therapeutic frameworks",
    instruction="""Select 1-3 therapeutic frameworks based on the user's needs.
    
    User information:
    - Thought: {user_thought}
    - Emotion: {emotion_name} (intensity: {emotion_intensity})
    - Situation: {situation_context}
    - Values: {user_values?}
    - Past effective frameworks: {effective_frameworks?}
    
    Selection criteria:
    - High distress (7+): Prioritize DBT for immediate coping
    - Catastrophizing/distortions: CBT for thought challenging
    - Values conflict: ACT for values clarification
    - Control struggles: Stoicism for acceptance
    
    Consider user history if available.
    Store selections in state['selected_frameworks'] and reasoning in state['framework_reasoning'].""",
    tools=[UpdateStateTool()],
    output_key="framework_selection"
)

# Framework Agents
cbt_agent = Agent(
    name="CBTAgent",
    model="gemini-2.0-flash-002",
    description="Cognitive Behavioral Therapy specialist",
    instruction="""You are a CBT therapist specializing in AvPD.
    
    Apply CBT techniques to:
    - Thought: {user_thought}
    - Emotion: {emotion_name} ({emotion_intensity}/10)
    - Situation: {situation_context}
    
    Tasks:
    1. Identify cognitive distortions (use tool)
    2. Gather evidence for/against
    3. Create balanced reframes
    4. Suggest behavioral experiment
    
    Be collaborative, use Socratic questioning.
    Store output in state['cbt_output'].""",
    tools=[
        CognitiveDistortionIdentifier(),
        ThoughtChallengingTool(),
        BehavioralExperimentDesigner(),
        UpdateStateTool()
    ],
    output_key="cbt_response"
)

dbt_agent = Agent(
    name="DBTAgent", 
    model="gemini-2.0-flash-002",
    description="Dialectical Behavior Therapy specialist",
    instruction="""You are a DBT therapist specializing in AvPD.
    
    User state:
    - Thought: {user_thought}
    - Emotion: {emotion_name} ({emotion_intensity}/10)
    - Situation: {situation_context}
    
    Apply DBT principles:
    1. Validate AND promote change
    2. If distress >= 7: Prioritize TIPP/distress tolerance
    3. Use dialectical thinking (both/and)
    4. Teach specific skills
    
    Store output in state['dbt_output'].""",
    tools=[
        DistressToleranceTool(),
        EmotionRegulationTool(),
        InterpersonalEffectivenessTool(),
        UpdateStateTool()
    ],
    output_key="dbt_response"
)

act_agent = Agent(
    name="ACTAgent",
    model="gemini-2.0-flash-002", 
    description="Acceptance and Commitment Therapy specialist",
    instruction="""You are an ACT therapist specializing in AvPD.
    
    Focus on psychological flexibility:
    - Thought: {user_thought}
    - Values hint: {user_values?}
    
    Apply ACT processes:
    1. Cognitive defusion
    2. Values clarification
    3. Committed action despite anxiety
    4. Acceptance of difficult emotions
    
    Never promise anxiety will go away.
    Store output in state['act_output'].""",
    tools=[
        DefusionTool(),
        ValuesClarificationTool(),
        CommittedActionTool(),
        UpdateStateTool()
    ],
    output_key="act_response"
)

stoicism_agent = Agent(
    name="StoicismAgent",
    model="gemini-2.0-flash-002",
    description="Stoic philosophy specialist",
    instruction="""You are a Stoic philosopher helping with AvPD.
    
    Apply Stoic principles to:
    - Thought: {user_thought}
    - Situation: {situation_context}
    
    Focus on:
    1. Dichotomy of control
    2. Virtue over external validation
    3. Cosmic perspective
    4. Present moment action
    
    Use accessible language and metaphors.
    Store output in state['stoicism_output'].""",
    tools=[
        DichotomyOfControlTool(),
        VirtueEthicsTool(),
        PerspectiveTool(),
        UpdateStateTool()
    ],
    output_key="stoic_response"
)

# Synthesis Agent
synthesis_agent = Agent(
    name="SynthesisAgent",
    model="gemini-2.0-flash-002",
    description="Creates unified therapeutic response",
    instruction="""Create a cohesive, warm response from multiple frameworks.
    
    Available insights:
    - CBT: {cbt_response?}
    - DBT: {dbt_response?}
    - ACT: {act_response?}
    - Stoicism: {stoic_response?}
    
    Requirements:
    1. Start with validation
    2. Integrate insights naturally
    3. Provide 2-3 concrete actions
    4. Maintain hope
    5. Be transparent about approaches
    6. Keep under 300 words
    
    Focus on AvPD sensitivity.""",
    tools=[UpdateStateTool()],
    output_REDACTED"
)

# Action Planning Agent
action_planner = Agent(
    name="ActionPlanner",
    model="gemini-2.0-flash-002",
    description="Creates personalized action plans",
    instruction="""Create a specific action plan based on the therapeutic insights.
    
    Synthesis: {synthesized_response}
    User values: {user_values?}
    
    Generate:
    1. Immediate action (next 10 minutes)
    2. Today's practice 
    3. This week's goal
    4. Optional homework
    
    Make it specific, achievable, and AvPD-appropriate.""",
    tools=[
        ActionPlanFormatter(),
        UpdateStateTool()
    ],
    output_key="action_plan"
)

# Workflow Assembly
information_loop = LoopAgent(
    name="InformationGatheringLoop",
    description="Conversational information gathering",
    max_iterations=5,
    sub_agents=[conversation_agent, InformationValidator()]
)

framework_processor = ParallelAgent(
    name="FrameworkProcessor",
    description="Parallel framework processing",
    sub_agents=[cbt_agent, dbt_agent, act_agent, stoicism_agent]
)

therapeutic_pipeline = SequentialAgent(
    name="TherapeuticPipeline",
    description="Main therapeutic workflow",
    sub_agents=[
        framework_selector,
        framework_processor,
        synthesis_agent,
        action_planner
    ]
)

# Main Orchestrator
main_orchestrator = SequentialAgent(
    name="MainOrchestrator",
    description="Complete therapeutic support system",
    sub_agents=[
        CrisisDetectionAgent(),
        information_loop,
        therapeutic_pipeline
    ]
)

# Session Handler
async def process_therapy_session(
    user_message: str,
    user_id: str,
    auth_token: str,
    session_service,
    memory_service,
    pdf_service,
    guardrails_service
) -> Dict[str, Any]:
    """Complete session processing with all services"""
    
    # Validate input
    valid, processed_message, validation_info = await guardrails_service.validate_input(user_message)
    if not valid:
        return {
            "status": "invalid_input",
            "message": processed_message
        }
    
    # Create session
    session = session_service.create_session(user_id)
    session.state["user_message"] = processed_message
    session.state["user_thought"] = processed_message  # Initial assumption
    session.state["user_id"] = user_id
    
    # Retrieve relevant memory
    if user_id:
        memory_context = await memory_service.retrieve_relevant_patterns(user_id, processed_message)
        session.state["effective_frameworks"] = memory_context.get("effective_frameworks", [])
        session.state["recurring_patterns"] = memory_context.get("recurring_patterns", [])
    
    # Create invocation context
    ctx = InvocationContext(
        session=session,
        author="user"
    )
    
    # Process through orchestrator
    events = []
    async for event in main_orchestrator.run_async(ctx):
        events.append(event)
        
        # Handle crisis immediately
        if session.state.get("crisis_detected"):
            return {
                "status": "crisis",
                "response": session.state.get("crisis_response"),
                "session_id": session.id
            }
    
    # Validate output
    response = {
        "message": session.state.get("synthesized_response"),
        "action_plan": session.state.get("action_plan"),
        "frameworks_used": session.state.get("selected_frameworks"),
        "REDACTED(session.state)
    }
    
    valid, validated_response = await guardrails_service.validate_output(response)
    if not valid:
        return {
            "status": "error",
            "message": "Unable to generate appropriate response"
        }
    
    # Store patterns for future
    if user_id:
        await memory_service.store_session_patterns(user_id, {
            "thought_patterns": session.state.get("user_thought"),
            "emotional_patterns": session.state.get("emotion_name"),
            "frameworks_used": session.state.get("selected_frameworks"),
            "response": validated_response,
            "effectiveness": "pending_feedback"
        })
    
    # Generate PDF
    pdf_data = {
        "situation": f"{session.state.get('user_thought')} in {session.state.get('situation_context')}",
        "frameworks": session.state.get("selected_frameworks"),
        "framework_reasoning": session.state.get("framework_reasoning"),
        "response": validated_response["message"],
        "actions": validated_response["action_plan"],
        "timestamp": datetime.now()
    }
    
    pdf_bytes = await pdf_service.generate_session_pdf(pdf_data, user_id)
    document_id = await store_encrypted_pdf(pdf_bytes, user_id, session.id)
    
    # Return complete response
    return {
        "status": "success",
        "session_id": session.id,
        "response": validated_response,
        "document_id": document_id,
        "feedback_requested": True
    }
```

## Deployment Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # User Management API
  user-api:
    build: ./user-api
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/reframe
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    depends_on:
      - postgres
      - redis
      - mongodb
    ports:
      - "8001:8000"
      
  # ADK Agent Service
  agent-service:
    build: ./agent-service
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - USER_API_URL=http://user-api:8000
    ports:
      - "8002:8000"
      
  # Guardrails Service
  guardrails:
    build: ./guardrails
    ports:
      - "8003:8000"
      
  # Databases
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=reframe
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  mongodb:
    image: mongo:6
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret
    volumes:
      - mongo_data:/data/db
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
      
  # API Gateway
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - user-api
      - agent-service
      - guardrails

volumes:
  postgres_data:
  mongo_data:
  redis_data:
```

## Security Considerations

1. **Data Encryption**:
   - All PII encrypted at rest using AES-256
   - User-specific encryption keys
   - TLS 1.3 for all communications

2. **Authentication**:
   - JWT tokens with short expiry
   - Refresh token rotation
   - MFA support

3. **Privacy**:
   - GDPR compliant
   - Data minimization
   - Right to deletion
   - Data portability

4. **Session Security**:
   - Session tokens expire after 30 minutes
   - Encrypted session state
   - No PII in logs

## Monitoring & Observability

1. **Google AI Studio** provides:
   - LLM request/response traces
   - Token usage metrics
   - Latency tracking
   - Error rates

2. **Custom Metrics**:
   - User engagement rates
   - Framework effectiveness
   - Crisis detection accuracy
   - Session completion rates
   - PDF generation success

3. **Alerts**:
   - High crisis detection rate
   - Unusual token usage
   - Service latency > 5s
   - Error rate > 1%

## This completes the full system architecture with all requested features!