"""ADK Agent Registry for re-frame.

This module registers all ADK agents so they can be discovered and used
by the ADK web interface and other ADK tools.
"""

import logging
from typing import Any

from google.generativeai import adk

from .adk_cbt_agent import ADKCBTFrameworkAgent
from .adk_intake_agent import ADKIntakeAgent
from .adk_session_manager import ADKSessionManager
from .adk_synthesis_agent import ADKSynthesisAgent

logger = logging.getLogger(__name__)


def register_agents():
    """Register all re-frame agents with ADK.
    
    This function should be called when starting the ADK web interface
    or when initializing the agent system.
    """
    try:
        # Register the session manager as the main agent
        session_manager = ADKSessionManager()
        
        # Create a wrapper agent that coordinates the multi-agent flow
        @adk.agent(
            name="ReFrameAssistant",
            description="AI-powered cognitive reframing assistant for AvPD support",
            instructions="""You are a compassionate AI assistant helping users with Avoidant Personality Disorder (AvPD) 
            reframe their thoughts using evidence-based therapeutic techniques.
            
            When a user shares a thought or situation:
            1. Process it through the intake agent to validate and extract key elements
            2. Apply CBT techniques to identify distortions and generate reframes
            3. Synthesize a warm, supportive response
            
            Always be gentle, non-judgmental, and transparent about your process."""
        )
        async def reframe_assistant(user_thought: str) -> dict[str, Any]:
            """Process user thought through the multi-agent workflow."""
            logger.info(f"Processing thought: {user_thought[:50]}...")
            
            # Use the session manager to coordinate agents
            session_id = session_manager.create_session()
            result = await session_manager.process_user_input(session_id, user_thought)
            
            return {
                "response": result.get("response", ""),
                "transparency": result.get("transparency", {}),
                "techniques_used": result.get("transparency", {}).get("techniques_applied", []),
                "session_id": session_id
            }
        
        # Register individual agents for testing
        @adk.agent(
            name="IntakeAgent",
            description="Validates and extracts elements from user input",
            instructions=ADKIntakeAgent.INSTRUCTIONS
        )
        async def intake_agent(user_thought: str) -> dict[str, Any]:
            """Test the intake agent directly."""
            agent = ADKIntakeAgent()
            return await agent.process_user_input(user_thought)
        
        @adk.agent(
            name="CBTAgent", 
            description="Applies CBT techniques to reframe thoughts",
            instructions=ADKCBTFrameworkAgent.INSTRUCTIONS
        )
        async def cbt_agent(intake_data: dict[str, Any]) -> dict[str, Any]:
            """Test the CBT agent directly."""
            agent = ADKCBTFrameworkAgent()
            return await agent.apply_cbt_techniques(intake_data)
        
        @adk.agent(
            name="SynthesisAgent",
            description="Creates warm, supportive responses from CBT analysis",
            instructions=ADKSynthesisAgent.INSTRUCTIONS
        )
        async def synthesis_agent(synthesis_data: dict[str, Any]) -> dict[str, Any]:
            """Test the synthesis agent directly."""
            agent = ADKSynthesisAgent()
            return await agent.create_user_response(synthesis_data)
        
        logger.info("Successfully registered all ADK agents")
        logger.info("Registered agents: ReFrameAssistant, IntakeAgent, CBTAgent, SynthesisAgent")
        
        return {
            "reframe_assistant": reframe_assistant,
            "intake_agent": intake_agent,
            "cbt_agent": cbt_agent,
            "synthesis_agent": synthesis_agent
        }
        
    except Exception as e:
        logger.error(f"Failed to register agents: {e}")
        raise


# Auto-register agents when module is imported
if __name__ == "__main__":
    register_agents()