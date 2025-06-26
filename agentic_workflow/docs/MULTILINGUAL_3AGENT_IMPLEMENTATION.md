# Multilingual Three-Agent Implementation Guide

## Quick Start

This guide implements the multilingual 3-agent cognitive reframing system with Google Cloud Translation API and ADK best practices.

## Prerequisites

1. **Google Cloud Setup**
```bash
# Enable Translation API
gcloud services enable translate.googleapis.com

# Set authentication (choose one)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
# OR
gcloud auth application-default login
```

2. **Install Dependencies**
```bash
cd /Users/carlos/workspace/re-frame/agentic_workflow
uv pip install google-cloud-translate
```

## Step 1: Create Language Detection Module

### File: `reframe/agents/utils/language_detector.py`
```python
"""Language detection utilities for multilingual support."""

import re
from typing import Tuple, Dict, Optional
from google.cloud import translate_v2 as translate
from google.api_core import exceptions
import logging

logger = logging.getLogger(__name__)

# Language patterns for fast detection
LANGUAGE_PATTERNS = {
    'es': {
        'patterns': [
            r'\b(hola|estoy|tengo|problema|ayuda|ansiedad|pensamiento|sentimiento)\b',
            r'\b(me|mi|soy|es|la|el|un|una|que|para|por)\b'
        ],
        'name': 'español',
        'threshold': 3
    },
    'en': {
        'patterns': [
            r'\b(hello|hi|I|am|feeling|problem|help|anxiety|thought)\b',
            r'\b(the|is|are|my|have|with|about|for)\b'
        ],
        'name': 'English',
        'threshold': 3
    },
    'fr': {
        'patterns': [
            r'\b(bonjour|je|suis|problème|aide|anxiété|pensée)\b',
            r'\b(le|la|un|une|est|avec|pour|mon|ma)\b'
        ],
        'name': 'français',
        'threshold': 3
    },
    'de': {
        'patterns': [
            r'\b(hallo|ich|bin|problem|hilfe|angst|gedanke)\b',
            r'\b(der|die|das|ein|eine|ist|mit|für|mein)\b'
        ],
        'name': 'Deutsch',
        'threshold': 3
    },
    'it': {
        'patterns': [
            r'\b(ciao|sono|ho|problema|aiuto|ansia|pensiero)\b',
            r'\b(il|la|un|una|è|con|per|mio|mia)\b'
        ],
        'name': 'italiano',
        'threshold': 3
    },
    'pt': {
        'patterns': [
            r'\b(olá|oi|estou|tenho|problema|ajuda|ansiedade)\b',
            r'\b(o|a|um|uma|é|com|para|meu|minha)\b'
        ],
        'name': 'português',
        'threshold': 3
    },
    'ca': {
        'patterns': [
            r'\b(hola|estic|tinc|problema|ajuda|ansietat)\b',
            r'\b(el|la|un|una|és|amb|per|meu|meva)\b'
        ],
        'name': 'català',
        'threshold': 3
    }
}

# Exit command patterns by language
EXIT_PATTERNS = {
    'es': ['/salir', '/exit', '/terminar', '/fin'],
    'en': ['/exit', '/quit', '/done', '/end', '/stop'],
    'fr': ['/sortir', '/exit', '/terminer', '/fin'],
    'de': ['/beenden', '/exit', '/fertig', '/ende'],
    'it': ['/esci', '/uscire', '/exit', '/fine'],
    'pt': ['/sair', '/exit', '/terminar', '/fim'],
    'ca': ['/sortir', '/exit', '/acabar', '/fi'],
    '*': ['/exit', '/quit', '/done']  # Universal
}


def detect_language_pattern(text: str) -> Tuple[str, float]:
    """
    Detect language using pattern matching.
    Returns (language_code, confidence).
    """
    text_lower = text.lower()
    scores = {}
    
    for lang_code, config in LANGUAGE_PATTERNS.items():
        score = 0
        for pattern in config['patterns']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            score += matches
        
        if score >= config['threshold']:
            scores[lang_code] = score
    
    if scores:
        best_lang = max(scores.items(), key=lambda x: x[1])
        # Calculate confidence (0.5 to 1.0 based on match strength)
        confidence = min(0.5 + (best_lang[1] / 20), 1.0)
        return best_lang[0], confidence
    
    return 'es', 0.3  # Default to Spanish with low confidence


def detect_language_google(text: str) -> Tuple[str, float]:
    """
    Detect language using Google Cloud Translation API.
    Returns (language_code, confidence).
    """
    try:
        client = translate.Client()
        result = client.detect_language(text)
        
        return result['language'], result['confidence']
        
    except exceptions.GoogleAPIError as e:
        logger.error(f"Google API error: {e}")
        return detect_language_pattern(text)
    except Exception as e:
        logger.error(f"Unexpected error in language detection: {e}")
        return 'es', 0.0


def detect_language_with_fallback(text: str) -> Dict[str, any]:
    """
    Detect language with multi-tier fallback strategy.
    Returns dict with language_code, language_name, confidence, and method.
    """
    # Try pattern matching first (fast)
    lang_code, confidence = detect_language_pattern(text)
    
    if confidence >= 0.8:
        return {
            'language_code': lang_code,
            'language_name': LANGUAGE_PATTERNS[lang_code]['name'],
            'confidence': confidence,
            'method': 'pattern'
        }
    
    # Use Google API for better accuracy
    try:
        lang_code, confidence = detect_language_google(text)
        
        # Get human-readable name
        if lang_code in LANGUAGE_PATTERNS:
            lang_name = LANGUAGE_PATTERNS[lang_code]['name']
        else:
            lang_name = lang_code.upper()
        
        return {
            'language_code': lang_code,
            'language_name': lang_name,
            'confidence': confidence,
            'method': 'google_api'
        }
    except:
        # Final fallback
        return {
            'language_code': 'es',
            'language_name': 'español',
            'confidence': 0.3,
            'method': 'fallback'
        }


def check_exit_command(message: str, language: str) -> bool:
    """Check if message contains exit command in any supported format."""
    message_lower = message.lower().strip()
    
    # Check language-specific patterns
    if language in EXIT_PATTERNS:
        for pattern in EXIT_PATTERNS[language]:
            if pattern in message_lower:
                return True
    
    # Check universal patterns
    for pattern in EXIT_PATTERNS['*']:
        if pattern in message_lower:
            return True
    
    return False
```

## Step 2: Create Multilingual Models

### File: `reframe/core/multilingual_models.py`
```python
"""Data models for multilingual cognitive reframing system."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ConversationPhase(Enum):
    INTAKE = "intake"
    ANALYSIS = "analysis"
    SUMMARY = "summary"


@dataclass
class ConversationTurn:
    """Single turn in the conversation."""
    timestamp: datetime
    speaker: str  # "user" or "assistant"
    content: str
    phase: ConversationPhase
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntakeData:
    """Data collected during intake phase."""
    situation: str
    automatic_thoughts: str
    emotions: str
    emotion_intensity: int
    crisis_indicators: List[str] = field(default_factory=list)


@dataclass
class AnalysisData:
    """Data generated during analysis phase."""
    cognitive_distortions: List[str]
    evidence_for: List[str]
    evidence_against: List[str]
    balanced_thought: str
    micro_action: str
    confidence_before: int
    confidence_after: int
    follow_up_insights: List[str] = field(default_factory=list)


@dataclass
class MultilingualSessionState:
    """Complete session state for multilingual support."""
    # Language settings
    user_language: str  # ISO 639-1 code
    language_name: str  # Human-readable name
    language_confidence: float
    
    # Conversation data
    intake_data: Optional[IntakeData] = None
    analysis_data: Optional[AnalysisData] = None
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    
    # Metadata
    session_id: str = ""
    user_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Flags
    exit_requested: bool = False
    crisis_detected: bool = False
    
    def add_turn(self, speaker: str, content: str, phase: ConversationPhase):
        """Add a conversation turn to history."""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            speaker=speaker,
            content=content,
            phase=phase
        )
        self.conversation_history.append(turn)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'user_language': self.user_language,
            'language_name': self.language_name,
            'language_confidence': self.language_confidence,
            'intake_data': self.intake_data.__dict__ if self.intake_data else None,
            'analysis_data': self.analysis_data.__dict__ if self.analysis_data else None,
            'conversation_history': [
                {
                    'timestamp': turn.timestamp.isoformat(),
                    'speaker': turn.speaker,
                    'content': turn.content,
                    'phase': turn.phase.value
                }
                for turn in self.conversation_history
            ],
            'session_id': self.session_id,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'exit_requested': self.exit_requested,
            'crisis_detected': self.crisis_detected
        }
```

## Step 3: Implement ADK Callback for Language Detection

### File: `reframe/agents/callbacks/language_callback.py`
```python
"""ADK callback for automatic language detection."""

from google.adk.agents.callback_context import CallbackContext
from reframe.agents.utils.language_detector import detect_language_with_fallback
import logging

logger = logging.getLogger(__name__)


def language_detection_callback(context: CallbackContext) -> CallbackContext:
    """
    Pre-agent callback to detect user language on first message.
    Stores language in session state for all agents to use.
    """
    # Only detect on first user message
    if "user_language" not in context.state and context.messages:
        # Find the first user message
        user_message = None
        for msg in context.messages:
            if msg.role == "user":
                user_message = msg.content
                break
        
        if user_message:
            # Detect language
            lang_result = detect_language_with_fallback(user_message)
            
            # Store in state
            context.state["user_language"] = lang_result["language_code"]
            context.state["language_name"] = lang_result["language_name"]
            context.state["language_confidence"] = lang_result["confidence"]
            context.state["language_method"] = lang_result["method"]
            
            logger.info(
                f"Language detected: {lang_result['language_name']} "
                f"({lang_result['language_code']}) "
                f"confidence: {lang_result['confidence']:.2f} "
                f"method: {lang_result['method']}"
            )
    
    return context
```

## Step 4: Create the Three Agents

### File: `reframe/agents/multilingual_intake_agent.py`
```python
"""Multilingual Intake Agent - Collects initial information."""

from google.adk.agents import LlmAgent
from google.genai import types
from reframe.agents.callbacks.language_callback import language_detection_callback
from reframe.agents.utils.language_detector import LANGUAGE_PATTERNS
from reframe.infrastructure.prompts import prompt_manager
from reframe.core.multilingual_models import IntakeData
import json


def validate_intake_completion(state: dict) -> dict:
    """Check if all required intake data has been collected."""
    required_fields = ['situation', 'automatic_thoughts', 'emotions']
    
    collected = all(
        field in state and state[field] 
        for field in required_fields
    )
    
    return {
        'complete': collected,
        'missing': [f for f in required_fields if f not in state or not state[f]]
    }


def detect_crisis_multilingual(text: str, language: str) -> dict:
    """Detect crisis indicators in user's language."""
    # Crisis keywords by language
    crisis_keywords = {
        'es': ['suicidio', 'morir', 'muerte', 'acabar con todo', 'no vale la pena'],
        'en': ['suicide', 'die', 'death', 'end it all', 'not worth living'],
        'fr': ['suicide', 'mourir', 'mort', 'en finir', 'ne vaut pas la peine'],
        'de': ['selbstmord', 'sterben', 'tod', 'alles beenden', 'nicht lebenswert'],
        'it': ['suicidio', 'morire', 'morte', 'farla finita', 'non vale la pena'],
        'pt': ['suicídio', 'morrer', 'morte', 'acabar com tudo', 'não vale a pena'],
        'ca': ['suïcidi', 'morir', 'mort', 'acabar amb tot', 'no val la pena'],
    }
    
    text_lower = text.lower()
    detected_keywords = []
    
    if language in crisis_keywords:
        for keyword in crisis_keywords[language]:
            if keyword in text_lower:
                detected_keywords.append(keyword)
    
    return {
        'crisis_detected': len(detected_keywords) > 0,
        'keywords': detected_keywords
    }


class MultilingualIntakeAgent(LlmAgent):
    """Intake agent that collects information in user's detected language."""
    
    def __init__(self):
        # Load base instruction template
        instruction_template = prompt_manager.get_prompt("multilingual-intake-instructions")
        
        # Add language-specific greetings
        greetings = self._build_greeting_instructions()
        
        full_instruction = f"""
{instruction_template}

## LANGUAGE-SPECIFIC GREETINGS

{greetings}

## CONVERSATION FLOW

1. On first message: Detect language and greet appropriately
2. Collect situation (what's happening)
3. Identify automatic thoughts
4. Assess emotions and intensity (1-10)
5. Transition when all data collected

## IMPORTANT
- Always respond in the detected language
- Be warm and validating
- Keep questions open-ended
- Check for crisis indicators
"""
        
        super().__init__(
            name="multilingual_intake_agent",
            model="gemini-2.0-flash-exp",
            instruction=full_instruction,
            tools=[
                validate_intake_completion,
                detect_crisis_multilingual,
            ],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=400,
                top_p=0.9,
            ),
            before_agent_callback=language_detection_callback,
        )
    
    def _build_greeting_instructions(self) -> str:
        """Build greeting instructions for all supported languages."""
        greetings = []
        
        greetings.append("""
### Spanish (es):
¡Hola! Soy tu asistente de reestructuración cognitiva. 🌱

Estoy aquí para ayudarte a explorar tus pensamientos y sentimientos. Trabajaremos juntos en tres pasos:
1. Entender tu situación
2. Analizar tus pensamientos
3. Crear un resumen personalizado

¿Qué está pasando que te preocupa?
""")
        
        greetings.append("""
### English (en):
Hello! I'm your cognitive reframing assistant. 🌱

I'm here to help you explore your thoughts and feelings. We'll work together in three steps:
1. Understand your situation
2. Analyze your thoughts
3. Create a personalized summary

What's on your mind?
""")
        
        greetings.append("""
### French (fr):
Bonjour! Je suis votre assistant de restructuration cognitive. 🌱

Je suis ici pour vous aider à explorer vos pensées et sentiments. Nous travaillerons ensemble en trois étapes:
1. Comprendre votre situation
2. Analyser vos pensées
3. Créer un résumé personnalisé

Qu'est-ce qui vous préoccupe?
""")
        
        # Add more languages...
        
        return "\n".join(greetings)
```

### File: `reframe/agents/multilingual_analysis_agent.py`
```python
"""Multilingual Analysis Agent - Provides CBT analysis with conversation support."""

from google.adk.agents import LlmAgent
from google.genai import types
from reframe.agents.utils.language_detector import check_exit_command
from reframe.infrastructure.prompts import prompt_manager
from typing import List, Dict


def identify_cognitive_distortions(thoughts: str, language: str) -> Dict[str, List[str]]:
    """Identify cognitive distortions in user's thoughts."""
    # This would normally use more sophisticated analysis
    # For now, returning example distortions
    distortion_names = {
        'es': {
            'catastrophizing': 'Catastrofización',
            'mind_reading': 'Lectura de mente',
            'all_or_nothing': 'Todo o nada',
            'personalization': 'Personalización',
            'filtering': 'Filtrado mental'
        },
        'en': {
            'catastrophizing': 'Catastrophizing',
            'mind_reading': 'Mind Reading',
            'all_or_nothing': 'All-or-Nothing Thinking',
            'personalization': 'Personalization',
            'filtering': 'Mental Filtering'
        },
        # Add more languages...
    }
    
    # Example detection logic
    detected = []
    if 'nunca' in thoughts.lower() or 'siempre' in thoughts.lower() or 'never' in thoughts.lower() or 'always' in thoughts.lower():
        detected.append('all_or_nothing')
    if 'terrible' in thoughts.lower() or 'horrible' in thoughts.lower():
        detected.append('catastrophizing')
    
    lang_distortions = distortion_names.get(language, distortion_names['en'])
    
    return {
        'distortions': [lang_distortions.get(d, d) for d in detected],
        'codes': detected
    }


def check_for_exit(message: str, language: str) -> bool:
    """Check if user wants to exit the conversation."""
    return check_exit_command(message, language)


class MultilingualAnalysisAgent(LlmAgent):
    """Analysis agent providing CBT support with extended conversation."""
    
    def __init__(self):
        instruction_template = prompt_manager.get_prompt("multilingual-analysis-instructions")
        
        # Add exit command instructions by language
        exit_instructions = self._build_exit_instructions()
        
        full_instruction = f"""
{instruction_template}

## EXIT COMMAND SUPPORT

{exit_instructions}

## CONVERSATION GUIDELINES

1. Provide initial CBT analysis
2. Inform user about /exit command
3. Support follow-up questions
4. Deepen understanding as needed
5. Exit gracefully when requested

## THERAPEUTIC APPROACH
- Identify 1-2 main cognitive distortions
- Explore evidence for and against thoughts
- Co-create balanced perspectives
- Suggest small, actionable steps
- Be curious and collaborative
"""
        
        super().__init__(
            name="multilingual_analysis_agent",
            model="gemini-2.0-flash-exp",
            instruction=full_instruction,
            tools=[
                identify_cognitive_distortions,
                check_for_exit,
            ],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=600,
                top_p=0.9,
            ),
        )
    
    def _build_exit_instructions(self) -> str:
        """Build exit command instructions for all languages."""
        instructions = []
        
        instructions.append("""
### Spanish:
"Puedes escribir /salir en cualquier momento para terminar y recibir tu resumen."

### English:
"You can type /exit at any time to end the conversation and receive your summary."

### French:
"Vous pouvez taper /sortir à tout moment pour terminer et recevoir votre résumé."

### German:
"Sie können jederzeit /beenden eingeben, um das Gespräch zu beenden und Ihre Zusammenfassung zu erhalten."
""")
        
        return "\n".join(instructions)
```

### File: `reframe/agents/multilingual_pdf_agent.py`
```python
"""Multilingual PDF Agent - Generates session summary in user's language."""

from google.adk.agents import LlmAgent
from google.genai import types
from reframe.infrastructure.prompts import prompt_manager
from reframe.core.multilingual_models import MultilingualSessionState
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import base64


def generate_multilingual_pdf(
    session_state: MultilingualSessionState,
    language: str
) -> str:
    """Generate PDF summary in user's language."""
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Translations for PDF sections
    translations = {
        'es': {
            'title': 'Resumen de Sesión de Reestructuración Cognitiva',
            'date': 'Fecha',
            'situation': 'Situación',
            'thoughts': 'Pensamientos Automáticos',
            'emotions': 'Emociones',
            'distortions': 'Distorsiones Cognitivas',
            'balanced': 'Pensamiento Equilibrado',
            'action': 'Micro-Acción',
            'insights': 'Insights Adicionales',
            'anonymous': 'Cliente'
        },
        'en': {
            'title': 'Cognitive Reframing Session Summary',
            'date': 'Date',
            'situation': 'Situation',
            'thoughts': 'Automatic Thoughts',
            'emotions': 'Emotions',
            'distortions': 'Cognitive Distortions',
            'balanced': 'Balanced Thought',
            'action': 'Micro-Action',
            'insights': 'Additional Insights',
            'anonymous': 'Client'
        },
        # Add more languages...
    }
    
    t = translations.get(language, translations['en'])
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=30,
    )
    story.append(Paragraph(t['title'], title_style))
    
    # Date
    story.append(Paragraph(f"<b>{t['date']}:</b> {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Session content
    if session_state.intake_data:
        data = [
            [t['situation'], session_state.intake_data.situation],
            [t['thoughts'], session_state.intake_data.automatic_thoughts],
            [t['emotions'], f"{session_state.intake_data.emotions} ({session_state.intake_data.emotion_intensity}/10)"],
        ]
        
        if session_state.analysis_data:
            data.extend([
                [t['distortions'], ', '.join(session_state.analysis_data.cognitive_distortions)],
                [t['balanced'], session_state.analysis_data.balanced_thought],
                [t['action'], session_state.analysis_data.micro_action],
            ])
        
        # Create table
        table = Table(data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        story.append(table)
    
    # Build PDF
    doc.build(story)
    
    # Encode to base64
    pdf_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return pdf_base64


class MultilingualPDFAgent(LlmAgent):
    """PDF generation agent that creates summaries in user's language."""
    
    def __init__(self):
        instruction_template = prompt_manager.get_prompt("multilingual-pdf-instructions")
        
        full_instruction = f"""
{instruction_template}

## PDF GENERATION PROCESS

1. Read session data from state
2. Generate comprehensive summary
3. Format in user's language
4. Create downloadable PDF
5. Provide closing message

## LANGUAGE HANDLING
- Use language stored in session state
- Apply appropriate date/time formats
- Translate all labels and sections
- Maintain therapeutic terminology

## PRIVACY
- Anonymize any personal information
- Replace names with "Client"
- Remove identifying details
"""
        
        super().__init__(
            name="multilingual_pdf_agent",
            model="gemini-2.0-flash-exp",
            instruction=full_instruction,
            tools=[generate_multilingual_pdf],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=800,
                top_p=0.9,
            ),
        )
```

## Step 5: Create the Orchestrator

### File: `reframe/orchestrators/multilingual_orchestrator.py`
```python
"""Multilingual orchestrator managing the 3-agent pipeline."""

import os
from typing import Any, Optional
from datetime import datetime

from google.adk.agents import SequentialAgent
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from langfuse import Langfuse

from reframe.agents.multilingual_intake_agent import MultilingualIntakeAgent
from reframe.agents.multilingual_analysis_agent import MultilingualAnalysisAgent
from reframe.agents.multilingual_pdf_agent import MultilingualPDFAgent
from reframe.core.multilingual_models import MultilingualSessionState
from reframe.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class MultilingualReframeOrchestrator:
    """Orchestrator for multilingual 3-agent cognitive reframing."""
    
    def __init__(self):
        """Initialize the multilingual orchestrator."""
        self.settings = get_settings()
        
        # Initialize Langfuse for tracing
        self.langfuse = Langfuse(
            host=self.settings.langfuse_host,
            public_key=self.settings.langfuse_public_key,
            secret_key=self.settings.langfuse_secret_key,
        )
        
        # Initialize session service
        db_url = os.getenv("SUPABASE_REFRAME_DB_CONNECTION_STRING")
        if not db_url:
            logger.warning("Using InMemorySessionService - set SUPABASE_REFRAME_DB_CONNECTION_STRING for persistence")
            self.session_service = InMemorySessionService()
        else:
            self.session_service = DatabaseSessionService(db_url)
            logger.info("Using DatabaseSessionService with Supabase")
        
        # Initialize agents
        self.intake_agent = MultilingualIntakeAgent()
        self.analysis_agent = MultilingualAnalysisAgent()
        self.pdf_agent = MultilingualPDFAgent()
        
        # Create sequential pipeline
        self.pipeline = SequentialAgent(
            name="multilingual_cognitive_reframing_pipeline",
            sub_agents=[
                self.intake_agent,
                self.analysis_agent,
                self.pdf_agent,
            ],
            description=(
                "Multilingual cognitive reframing assistant with three phases: "
                "intake (collect information), analysis (CBT support with /exit), "
                "and summary (PDF generation)"
            ),
        )
        
        logger.info("Multilingual orchestrator initialized with 3 agents")
    
    def create_session(self, user_id: str, session_id: Optional[str] = None) -> str:
        """Create a new session for the user."""
        if not session_id:
            session_id = f"ml_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
        
        # Initialize session state
        initial_state = MultilingualSessionState(
            session_id=session_id,
            user_id=user_id,
            user_language="",  # Will be detected on first message
            language_name="",
            language_confidence=0.0,
        )
        
        # Create session in service
        self.session_service.create_session(
            app_name="multilingual_reframe",
            user_id=user_id,
            session_id=session_id,
            state=initial_state.to_dict()
        )
        
        logger.info(f"Created session: {session_id} for user: {user_id}")
        return session_id
```

## Step 6: Update ADK Runner Configuration

### File: `run_adk.py`
```python
"""ADK runner for multilingual cognitive reframing assistant."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from google.adk.runner import Runner
from reframe.orchestrators.multilingual_orchestrator import MultilingualReframeOrchestrator

# Initialize orchestrator
orchestrator = MultilingualReframeOrchestrator()

# Create runner
runner = Runner(
    agent=orchestrator.pipeline,
    app_name="multilingual_reframe_assistant",
    session_service=orchestrator.session_service,
)

print("✅ Multilingual ADK Runner configured")
print("🌐 Language detection: Google Cloud Translation API")
print("👥 Three agents: Intake → Analysis (with /exit) → PDF")
print("💾 Session management:", type(orchestrator.session_service).__name__)
```

## Step 7: Testing the Implementation

### File: `test_multilingual_system.py`
```python
"""Test script for multilingual 3-agent system."""

import asyncio
from reframe.agents.utils.language_detector import (
    detect_language_with_fallback,
    check_exit_command
)
from reframe.orchestrators.multilingual_orchestrator import MultilingualReframeOrchestrator


def test_language_detection():
    """Test language detection with various inputs."""
    test_cases = [
        ("Hola, me siento muy ansioso", "es"),
        ("Hello, I'm feeling anxious", "en"),
        ("Bonjour, je suis anxieux", "fr"),
        ("Ciao, sono ansioso", "it"),
        ("Hallo, ich bin nervös", "de"),
        ("Olá, estou ansioso", "pt"),
        ("Hola, estic nerviós", "ca"),
    ]
    
    print("Testing Language Detection:")
    print("-" * 50)
    
    for text, expected in test_cases:
        result = detect_language_with_fallback(text)
        status = "✅" if result['language_code'] == expected else "❌"
        print(f"{status} '{text[:30]}...'")
        print(f"   Detected: {result['language_name']} ({result['language_code']})")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Method: {result['method']}")
        print()


def test_exit_commands():
    """Test exit command detection."""
    test_cases = [
        ("/exit", "en", True),
        ("/salir", "es", True),
        ("/sortir", "fr", True),
        ("I want to continue", "en", False),
        ("Quiero continuar", "es", False),
    ]
    
    print("\nTesting Exit Commands:")
    print("-" * 50)
    
    for command, lang, expected in test_cases:
        result = check_exit_command(command, lang)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{command}' in {lang}: {result}")


async def test_orchestrator():
    """Test the complete orchestrator setup."""
    print("\nTesting Orchestrator Setup:")
    print("-" * 50)
    
    try:
        orchestrator = MultilingualReframeOrchestrator()
        print("✅ Orchestrator initialized")
        
        # Create test session
        session_id = orchestrator.create_session("test_user_123")
        print(f"✅ Session created: {session_id}")
        
        print("\nTo test the full system:")
        print("1. Run: adk web")
        print("2. Try messages in different languages")
        print("3. Use /exit command during analysis phase")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests."""
    print("Multilingual 3-Agent System Tests")
    print("=" * 50)
    
    test_language_detection()
    test_exit_commands()
    asyncio.run(test_orchestrator())
    
    print("\n" + "=" * 50)
    print("Testing complete!")


if __name__ == "__main__":
    main()
```

## Step 8: Deployment and Running

### Running the System
```bash
# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export SUPABASE_REFRAME_DB_CONNECTION_STRING="postgresql://..."
export LANGFUSE_HOST="https://..."
export LANGFUSE_PUBLIC_KEY="..."
export LANGFUSE_SECRET_KEY="..."

# Run tests
uv run python test_multilingual_system.py

# Start ADK web interface
adk web --port 8000
```

### Testing Different Languages
1. **Spanish**: "Hola, estoy muy preocupado por mi trabajo"
2. **English**: "Hello, I'm worried about my job"
3. **French**: "Bonjour, je suis inquiet pour mon travail"
4. **German**: "Hallo, ich mache mir Sorgen um meine Arbeit"

### Testing Exit Command
During the analysis phase, try:
- Spanish: "/salir"
- English: "/exit"
- French: "/sortir"

## Monitoring and Debugging

### Check Language Detection
```python
# Add to detect_language_with_fallback for debugging
import json
print(f"Detection result: {json.dumps(result, indent=2)}")
```

### Monitor Agent Transitions
```python
# In orchestrator, add logging
logger.info(f"Transitioning from {current_agent} to {next_agent}")
logger.info(f"Session state: {session_state.to_dict()}")
```

### Trace with Langfuse
All agent interactions are automatically traced. Check your Langfuse dashboard for:
- Language detection events
- Agent transitions
- Exit command usage
- PDF generation success

## Troubleshooting

### Common Issues

1. **Google API Authentication Error**
   ```bash
   # Check credentials
   echo $GOOGLE_APPLICATION_CREDENTIALS
   
   # Test API directly
   gcloud auth application-default print-access-token
   ```

2. **Language Not Detected**
   - Check if text is too short (< 10 characters)
   - Verify Google API is enabled
   - Check network connectivity

3. **Exit Command Not Working**
   - Ensure exact pattern match (e.g., "/exit" not "exit")
   - Check language is correctly stored in state
   - Verify analysis agent is checking for exit

4. **PDF Generation Fails**
   - Check reportlab is installed: `uv pip install reportlab`
   - Verify session state contains all required data
   - Check language translations exist

## Performance Optimization

### Caching Language Detection
```python
# Add to language_detector.py
from functools import lru_cache

@lru_cache(maxsize=1000)
def detect_language_cached(text: str) -> Tuple[str, float]:
    return detect_language_google(text)
```

### Optimize PDF Generation
```python
# Pre-compile PDF templates
PDF_TEMPLATES = {
    'es': load_template('es'),
    'en': load_template('en'),
    # ...
}
```

---

This implementation provides a complete multilingual 3-agent system following ADK best practices with proper language detection, conversation flow, and exit command support.