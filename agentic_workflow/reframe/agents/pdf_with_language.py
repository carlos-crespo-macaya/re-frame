"""PDF summary agent that uses language from state."""

from google.adk.agents import LlmAgent
from google.genai import types
from reframe.infrastructure.prompts import prompt_manager
import logging

logger = logging.getLogger(__name__)


def get_session_info(state: dict) -> dict:
    """Get language and session data from state."""
    return {
        'language': state.get('user_language', 'en'),
        'language_name': state.get('language_name', 'English'),
        'has_data': bool(state)
    }


class PDFWithLanguageAgent(LlmAgent):
    """PDF agent that creates summary in user's language."""
    
    def __init__(self):
        base_instructions = prompt_manager.get_prompt("synthesis-agent-adk-instructions")
        
        enhanced_instructions = f"""{base_instructions}

## CRITICAL: LANGUAGE CONTINUITY
1. Call get_session_info to get the user's language
2. Create the ENTIRE summary in that language
3. Language codes: 'es' (Spanish), 'en' (English), 'fr' (French)

## LANGUAGE-SPECIFIC SUMMARIES

### Spanish Summary Format:
"🌟 RESUMEN DE TU SESIÓN DE REENCUADRE COGNITIVO

**Tu Situación:**
[Lo que compartiste sobre la situación]

**Pensamientos Automáticos:**
[Los pensamientos que identificamos]

**Emociones:**
[Las emociones que sentiste y su intensidad]

**Patrones de Pensamiento Identificados:**
[Las distorsiones cognitivas que encontramos]

**Perspectiva Equilibrada:**
[El pensamiento más balanceado que desarrollamos]

**Tu Micro-Acción:**
[La acción pequeña que acordamos]

**Progreso:**
[Cualquier cambio en tu confianza]

¡Has mostrado gran valentía al explorar tus pensamientos! Cada pequeño paso cuenta. Recuerda que el cambio es un proceso gradual. 🌱

*Si necesitas apoyo inmediato en España: 024 (línea de prevención del suicidio) o 112*"

### English Summary Format:
"🌟 YOUR COGNITIVE REFRAMING SESSION SUMMARY

**Your Situation:**
[What you shared about the situation]

**Automatic Thoughts:**
[The thoughts we identified]

**Emotions:**
[The emotions you felt and their intensity]

**Thinking Patterns Identified:**
[The cognitive distortions we found]

**Balanced Perspective:**
[The more balanced thought we developed]

**Your Micro-Action:**
[The small action we agreed on]

**Progress:**
[Any shift in your confidence]

You've shown great courage exploring your thoughts! Every small step matters. Remember that change is a gradual process. 🌱

*If you need immediate support: 988 (US) or your local emergency services*"

### French Summary Format:
"🌟 RÉSUMÉ DE VOTRE SESSION DE RECADRAGE COGNITIF

**Votre Situation:**
[Ce que vous avez partagé sur la situation]

**Pensées Automatiques:**
[Les pensées que nous avons identifiées]

**Émotions:**
[Les émotions ressenties et leur intensité]

**Schémas de Pensée Identifiés:**
[Les distorsions cognitives trouvées]

**Perspective Équilibrée:**
[La pensée plus équilibrée développée]

**Votre Micro-Action:**
[La petite action convenue]

**Progrès:**
[Tout changement dans votre confiance]

Vous avez montré beaucoup de courage en explorant vos pensées! Chaque petit pas compte. Rappelez-vous que le changement est un processus graduel. 🌱

*Si vous avez besoin d'aide immédiate en France: 3114 (prévention suicide) ou 15*"

## IMPORTANT
- Use get_session_info to determine the language
- Create the ENTIRE summary in that language
- Be warm and encouraging
- Include appropriate crisis resources for the language/region"""
        
        super().__init__(
            name="pdf_with_language",
            description="Creates final summary in user's language",
            model="gemini-2.0-flash-exp",
            instruction=enhanced_instructions,
            tools=[get_session_info],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=600,
            ),
        )