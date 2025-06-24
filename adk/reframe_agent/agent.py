"""Main agent definition for re-frame cognitive reframing assistant."""

from pathlib import Path

from google.adk.agents import Agent as LlmAgent, SequentialAgent

from langfuse import get_client
 
langfuse = get_client()

from .intake_tool import update_intake_state
from .tools import create_pdf_report, process_reframe_data
from langfuse import get_clientt

langfuse = get_client()
# 1. INTAKE AGENT - Handles the intake conversation one turn at a time
prompt = langfuse.prompt()
intake_agent = LlmAgent(
    name=langfuse.get_prompt("intake_agent.md").name,
    model=langfuse.get_model("gemini-2.0-flash"),
    description=langfuse.get_prompt("intake_agent.md").description,
    instruction=langfuse.get_prompt("intake_agent.md").content,
    tools=[update_intake_state],
    key="intake_agent",
)

# 2. REFRAME AGENT - Analyzes and reframes negative thoughts
reframe_agent = LlmAgent(
    name=langfuse.get_prompt("reframe_agent.md").name,
    model=langfuse.get_model("gemini-2.0-flash"),
    description=langfuse.get_prompt("reframe_agent.md").description,
    instruction=langfuse.get_prompt("reframe_agent.md").content,
    + """
    
    The intake agent has collected information from the user.
    Review the conversation history to extract:
    - The trigger situation (when/where/who)
    - The automatic negative thought (exact words)
    - The emotion and intensity rating
    
    Apply CBT techniques to create a balanced reframe.
    
    IMPORTANT: Do NOT output JSON directly to the user. Instead, call the 
    process_reframe_data tool with your analysis results. The tool takes these parameters:
    - distortions: list of cognitive distortion codes (e.g., ["MW", "FT"])
    - evidence_for: list of evidence supporting the negative thought
    - evidence_against: list of evidence contradicting the negative thought
    - balanced_thought: the balanced perspective you create
    - micro_action: a small actionable step (≤10 minutes)
    - certainty_before: initial certainty in the negative thought (0-100)
    - certainty_after: certainty after reframing (0-100)
    """,
    tools=[process_reframe_data],
)

# 3. REPORT AGENT - Generates the final report
report_agent = LlmAgent(
    name=langfuse.get_prompt("synthesis_agent.md").name,
    model=langfuse.get_model("gemini-2.0-flash"),
    description=langfuse.get_prompt("synthesis_agent.md").description,
    instruction=langfuse.get_prompt("synthesis_agent.md").content
    + """
    
    Review the conversation history and reframe analysis to create a report.
    
    Extract from the conversation:
    - The trigger situation, automatic thought, and emotion data
    - The reframe analysis from the previous agent
    - Whether any crisis was detected
    
    If no crisis was detected, call create_pdf_report with anonymized session data.
    """,
    tools=[create_pdf_report],
)

# 4. REFRAME PIPELINE - Runs after intake is complete
reframe_pipeline = SequentialAgent(
    name="ReFramePipeline",
    sub_agents=[
        reframe_agent,  # Analyzes and creates reframe
        report_agent,   # Generates final report
    ],
    description="Processes the collected data to create a reframe and report",
)

# The root agent for now is just the intake agent
# The application should check state["collection_complete"] and switch to reframe_pipeline
root_agent = intake_agent
