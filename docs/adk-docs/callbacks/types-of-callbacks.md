[ Skip to content ](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#types-of-callbacks)
# Types of Callbacks[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#types-of-callbacks "Permanent link")
The framework provides different types of callbacks that trigger at various stages of an agent's execution. Understanding when each callback fires and what context it receives is key to using them effectively.
## Agent Lifecycle Callbacks[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#agent-lifecycle-callbacks "Permanent link")
These callbacks are available on _any_ agent that inherits from `BaseAgent` (including `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`, etc).
Note
The specific method names or return types may vary slightly by SDK language (e.g., return `None` in Python, return `Optional.empty()` or `Maybe.empty()` in Java). Refer to the language-specific API documentation for details.
### Before Agent Callback[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#before-agent-callback "Permanent link")
**When:** Called _immediately before_ the agent's `_run_async_impl` (or `_run_live_impl`) method is executed. It runs after the agent's `InvocationContext` is created but _before_ its core logic begins.
**Purpose:** Ideal for setting up resources or state needed only for this specific agent's run, performing validation checks on the session state (callback_context.state) before execution starts, logging the entry point of the agent's activity, or potentially modifying the invocation context before the core logic uses it.
Code
[Python](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#python)[Java](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#java)
```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-2)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-6)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-8)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-13)# limitations under the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-15)# # --- Setup Instructions ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-16)# # 1. Install the ADK package:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-17)# !pip install google-adk
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-18)# # Make sure to restart kernel if using colab/jupyter notebooks
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-19)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-20)# # 2. Set up your Gemini API Key:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-21)# #  - Get a key from Google AI Studio: https://aistudio.google.com/app/apikey
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-22)# #  - Set it as an environment variable:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-23)# import os
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-24)# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- REPLACE with your actual key
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-25)# # Or learn about other authentication methods (like Vertex AI):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-26)# # https://google.github.io/adk-docs/agents/models/
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-27)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-28)# ADK Imports
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-29)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-30)fromgoogle.adk.agents.callback_contextimport CallbackContext
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-31)fromgoogle.adk.runnersimport InMemoryRunner # Use InMemoryRunner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-32)fromgoogle.genaiimport types # For types.Content
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-33)fromtypingimport Optional
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-34)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-35)# Define the model - Use the specific model name requested
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-36)GEMINI_2_FLASH="gemini-2.0-flash"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-37)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-38)# --- 1. Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-39)defcheck_if_agent_should_run(callback_context: CallbackContext) -> Optional[types.Content]:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-40)"""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-41)  Logs entry and checks 'skip_llm_agent' in session state.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-42)  If True, returns Content to skip the agent's execution.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-43)  If False or not present, returns None to allow execution.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-44)  """
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-45)  agent_name = callback_context.agent_name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-46)  invocation_id = callback_context.invocation_id
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-47)  current_state = callback_context.state.to_dict()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-48)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-49)  print(f"\n[Callback] Entering agent: {agent_name} (Inv: {invocation_id})")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-50)  print(f"[Callback] Current State: {current_state}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-51)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-52)  # Check the condition in session state dictionary
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-53)  if current_state.get("skip_llm_agent", False):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-54)    print(f"[Callback] State condition 'skip_llm_agent=True' met: Skipping agent {agent_name}.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-55)    # Return Content to skip the agent's run
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-56)    return types.Content(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-57)      parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to state.")],
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-58)      role="model" # Assign model role to the overriding response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-59)    )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-60)  else:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-61)    print(f"[Callback] State condition not met: Proceeding with agent {agent_name}.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-62)    # Return None to allow the LlmAgent's normal execution
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-63)    return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-64)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-65)# --- 2. Setup Agent with Callback ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-66)llm_agent_with_before_cb = LlmAgent(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-67)  name="MyControlledAgent",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-68)  model=GEMINI_2_FLASH,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-69)  instruction="You are a concise assistant.",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-70)  description="An LLM agent demonstrating stateful before_agent_callback",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-71)  before_agent_callback=check_if_agent_should_run # Assign the callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-72))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-73)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-74)# --- 3. Setup Runner and Sessions using InMemoryRunner ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-75)async defmain():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-76)  app_name = "before_agent_demo"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-77)  user_id = "test_user"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-78)  session_id_run = "session_will_run"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-79)  session_id_skip = "session_will_skip"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-80)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-81)  # Use InMemoryRunner - it includes InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-82)  runner = InMemoryRunner(agent=llm_agent_with_before_cb, app_name=app_name)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-83)  # Get the bundled session service to create sessions
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-84)  session_service = runner.session_service
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-85)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-86)  # Create session 1: Agent will run (default empty state)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-87)  session_service.create_session(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-88)    app_name=app_name,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-89)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-90)    session_id=session_id_run
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-91)    # No initial state means 'skip_llm_agent' will be False in the callback check
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-92)  )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-93)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-94)  # Create session 2: Agent will be skipped (state has skip_llm_agent=True)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-95)  session_service.create_session(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-96)    app_name=app_name,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-97)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-98)    session_id=session_id_skip,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-99)    state={"skip_llm_agent": True} # Set the state flag here
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-100)  )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-101)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-102)  # --- Scenario 1: Run where callback allows agent execution ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-103)  print("\n" + "="*20 + f" SCENARIO 1: Running Agent on Session '{session_id_run}' (Should Proceed) " + "="*20)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-104)  async for event in runner.run_async(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-105)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-106)    session_id=session_id_run,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-107)    new_message=types.Content(role="user", parts=[types.Part(text="Hello, please respond.")])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-108)  ):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-109)    # Print final output (either from LLM or callback override)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-110)    if event.is_final_response() and event.content:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-111)      print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-112)    elif event.is_error():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-113)       print(f"Error Event: {event.error_details}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-114)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-115)  # --- Scenario 2: Run where callback intercepts and skips agent ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-116)  print("\n" + "="*20 + f" SCENARIO 2: Running Agent on Session '{session_id_skip}' (Should Skip) " + "="*20)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-117)  async for event in runner.run_async(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-118)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-119)    session_id=session_id_skip,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-120)    new_message=types.Content(role="user", parts=[types.Part(text="This message won't reach the LLM.")])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-121)  ):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-122)     # Print final output (either from LLM or callback override)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-123)     if event.is_final_response() and event.content:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-124)      print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-125)     elif event.is_error():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-126)       print(f"Error Event: {event.error_details}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-127)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-128)# --- 4. Execute ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-129)# In a Python script:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-130)# import asyncio
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-131)# if __name__ == "__main__":
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-132)#   # Make sure GOOGLE_API_KEY environment variable is set if not using Vertex AI auth
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-133)#   # Or ensure Application Default Credentials (ADC) are configured for Vertex AI
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-134)#   asyncio.run(main())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-135)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-136)# In a Jupyter Notebook or similar environment:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-0-137)await main()

```

```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-2)importcom.google.adk.agents.BaseAgent;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-3)importcom.google.adk.agents.CallbackContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-4)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-5)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-6)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-7)importcom.google.adk.sessions.State;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-8)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-9)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-10)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-11)importio.reactivex.rxjava3.core.Maybe;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-12)importjava.util.Map;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-13)importjava.util.concurrent.ConcurrentHashMap;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-15)publicclass BeforeAgentCallbackExample{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-16)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-17)privatestaticfinalStringAPP_NAME="AgentWithBeforeAgentCallback";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-18)privatestaticfinalStringUSER_ID="test_user_456";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-19)privatestaticfinalStringSESSION_ID="session_id_123";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-20)privatestaticfinalStringMODEL_NAME="gemini-2.0-flash";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-21)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-22)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-23)BeforeAgentCallbackExamplecallbackAgent=newBeforeAgentCallbackExample();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-24)callbackAgent.defineAgent("Write a document about a cat");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-25)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-26)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-27)// --- 1. Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-28)/**
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-29)  * Logs entry and checks 'skip_llm_agent' in session state. If True, returns Content to skip the
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-30)  * agent's execution. If False or not present, returns None to allow execution.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-31)  */
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-32)publicMaybe<Content>checkIfAgentShouldRun(CallbackContextcallbackContext){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-33)StringagentName=callbackContext.agentName();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-34)StringinvocationId=callbackContext.invocationId();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-35)StatecurrentState=callbackContext.state();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-36)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-37)System.out.printf("%n[Callback] Entering agent: %s (Inv: %s)%n",agentName,invocationId);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-38)System.out.printf("[Callback] Current State: %s%n",currentState.entrySet());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-39)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-40)// Check the condition in session state dictionary
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-41)if(Boolean.TRUE.equals(currentState.get("skip_llm_agent"))){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-42)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-43)"[Callback] State condition 'skip_llm_agent=True' met: Skipping agent %s",agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-44)// Return Content to skip the agent's run
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-45)returnMaybe.just(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-46)Content.fromParts(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-47)Part.fromText(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-48)String.format(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-49)"Agent %s skipped by before_agent_callback due to state.",agentName))));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-50)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-51)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-52)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-53)"[Callback] State condition 'skip_llm_agent=True' NOT met: Running agent %s \n",agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-54)// Return empty response to allow the LlmAgent's normal execution
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-55)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-56)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-57)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-58)publicvoiddefineAgent(Stringprompt){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-59)// --- 2. Setup Agent with Callback ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-60)BaseAgentllmAgentWithBeforeCallback=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-61)LlmAgent.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-62).model(MODEL_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-63).name(APP_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-64).instruction("You are a concise assistant.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-65).description("An LLM agent demonstrating stateful before_agent_callback")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-66)// You can also use a sync version of this callback "beforeAgentCallbackSync"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-67).beforeAgentCallback(this::checkIfAgentShouldRun)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-68).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-69)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-70)// --- 3. Setup Runner and Sessions using InMemoryRunner ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-71)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-72)// Use InMemoryRunner - it includes InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-73)InMemoryRunnerrunner=newInMemoryRunner(llmAgentWithBeforeCallback,APP_NAME);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-74)// Scenario 1: Initial state is null, which means 'skip_llm_agent' will be false in the callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-75)// check
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-76)runAgent(runner,null,prompt);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-77)// Scenario 2: Agent will be skipped (state has skip_llm_agent=true)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-78)runAgent(runner,newConcurrentHashMap<>(Map.of("skip_llm_agent",true)),prompt);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-79)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-80)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-81)publicvoidrunAgent(InMemoryRunnerrunner,ConcurrentHashMap<String,Object>initialState,Stringprompt){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-82)// InMemoryRunner automatically creates a session service. Create a session using the service.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-83)Sessionsession=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-84)runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-85).sessionService()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-86).createSession(APP_NAME,USER_ID,initialState,SESSION_ID)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-87).blockingGet();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-88)ContentuserMessage=Content.fromParts(Part.fromText(prompt));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-89)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-90)// Run the agent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-91)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-92)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-93)// Print final output (either from LLM or callback override)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-94)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-95)event->{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-96)if(event.finalResponse()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-97)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-98)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-99)});
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-100)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-1-101)}

```

**Note on the`before_agent_callback` Example:**
  * **What it Shows:** This example demonstrates the `before_agent_callback`. This callback runs _right before_ the agent's main processing logic starts for a given request.
  * **How it Works:** The callback function (`check_if_agent_should_run`) looks at a flag (`skip_llm_agent`) in the session's state.
    * If the flag is `True`, the callback returns a `types.Content` object. This tells the ADK framework to **skip** the agent's main execution entirely and use the callback's returned content as the final response.
    * If the flag is `False` (or not set), the callback returns `None` or an empty object. This tells the ADK framework to **proceed** with the agent's normal execution (calling the LLM in this case).
  * **Expected Outcome:** You'll see two scenarios:
    1. In the session _with_ the `skip_llm_agent: True` state, the agent's LLM call is bypassed, and the output comes directly from the callback ("Agent... skipped...").
    2. In the session _without_ that state flag, the callback allows the agent to run, and you see the actual response from the LLM (e.g., "Hello!").
  * **Understanding Callbacks:** This highlights how `before_` callbacks act as **gatekeepers** , allowing you to intercept execution _before_ a major step and potentially prevent it based on checks (like state, input validation, permissions).


### After Agent Callback[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#after-agent-callback "Permanent link")
**When:** Called _immediately after_ the agent's `_run_async_impl` (or `_run_live_impl`) method successfully completes. It does _not_ run if the agent was skipped due to `before_agent_callback` returning content or if `end_invocation` was set during the agent's run.
**Purpose:** Useful for cleanup tasks, post-execution validation, logging the completion of an agent's activity, modifying final state, or augmenting/replacing the agent's final output.
Code
[Python](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#python_1)[Java](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#java_1)
```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-2)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-6)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-8)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-13)# limitations under the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-15)# # --- Setup Instructions ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-16)# # 1. Install the ADK package:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-17)# !pip install google-adk
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-18)# # Make sure to restart kernel if using colab/jupyter notebooks
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-19)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-20)# # 2. Set up your Gemini API Key:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-21)# #  - Get a key from Google AI Studio: https://aistudio.google.com/app/apikey
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-22)# #  - Set it as an environment variable:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-23)# import os
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-24)# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- REPLACE with your actual key
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-25)# # Or learn about other authentication methods (like Vertex AI):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-26)# # https://google.github.io/adk-docs/agents/models/
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-27)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-28)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-29)# ADK Imports
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-30)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-31)fromgoogle.adk.agents.callback_contextimport CallbackContext
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-32)fromgoogle.adk.runnersimport InMemoryRunner # Use InMemoryRunner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-33)fromgoogle.genaiimport types # For types.Content
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-34)fromtypingimport Optional
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-35)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-36)# Define the model - Use the specific model name requested
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-37)GEMINI_2_FLASH="gemini-2.0-flash"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-38)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-39)# --- 1. Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-40)defmodify_output_after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-41)"""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-42)  Logs exit from an agent and checks 'add_concluding_note' in session state.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-43)  If True, returns new Content to *replace* the agent's original output.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-44)  If False or not present, returns None, allowing the agent's original output to be used.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-45)  """
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-46)  agent_name = callback_context.agent_name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-47)  invocation_id = callback_context.invocation_id
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-48)  current_state = callback_context.state.to_dict()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-49)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-50)  print(f"\n[Callback] Exiting agent: {agent_name} (Inv: {invocation_id})")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-51)  print(f"[Callback] Current State: {current_state}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-52)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-53)  # Example: Check state to decide whether to modify the final output
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-54)  if current_state.get("add_concluding_note", False):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-55)    print(f"[Callback] State condition 'add_concluding_note=True' met: Replacing agent {agent_name}'s output.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-56)    # Return Content to *replace* the agent's own output
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-57)    return types.Content(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-58)      parts=[types.Part(text=f"Concluding note added by after_agent_callback, replacing original output.")],
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-59)      role="model" # Assign model role to the overriding response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-60)    )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-61)  else:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-62)    print(f"[Callback] State condition not met: Using agent {agent_name}'s original output.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-63)    # Return None - the agent's output produced just before this callback will be used.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-64)    return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-65)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-66)# --- 2. Setup Agent with Callback ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-67)llm_agent_with_after_cb = LlmAgent(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-68)  name="MySimpleAgentWithAfter",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-69)  model=GEMINI_2_FLASH,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-70)  instruction="You are a simple agent. Just say 'Processing complete!'",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-71)  description="An LLM agent demonstrating after_agent_callback for output modification",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-72)  after_agent_callback=modify_output_after_agent # Assign the callback here
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-73))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-74)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-75)# --- 3. Setup Runner and Sessions using InMemoryRunner ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-76)async defmain():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-77)  app_name = "after_agent_demo"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-78)  user_id = "test_user_after"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-79)  session_id_normal = "session_run_normally"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-80)  session_id_modify = "session_modify_output"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-81)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-82)  # Use InMemoryRunner - it includes InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-83)  runner = InMemoryRunner(agent=llm_agent_with_after_cb, app_name=app_name)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-84)  # Get the bundled session service to create sessions
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-85)  session_service = runner.session_service
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-86)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-87)  # Create session 1: Agent output will be used as is (default empty state)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-88)  session_service.create_session(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-89)    app_name=app_name,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-90)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-91)    session_id=session_id_normal
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-92)    # No initial state means 'add_concluding_note' will be False in the callback check
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-93)  )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-94)  # print(f"Session '{session_id_normal}' created with default state.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-95)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-96)  # Create session 2: Agent output will be replaced by the callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-97)  session_service.create_session(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-98)    app_name=app_name,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-99)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-100)    session_id=session_id_modify,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-101)    state={"add_concluding_note": True} # Set the state flag here
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-102)  )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-103)  # print(f"Session '{session_id_modify}' created with state={{'add_concluding_note': True}}.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-104)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-105)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-106)  # --- Scenario 1: Run where callback allows agent's original output ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-107)  print("\n" + "="*20 + f" SCENARIO 1: Running Agent on Session '{session_id_normal}' (Should Use Original Output) " + "="*20)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-108)  async for event in runner.run_async(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-109)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-110)    session_id=session_id_normal,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-111)    new_message=types.Content(role="user", parts=[types.Part(text="Process this please.")])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-112)  ):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-113)    # Print final output (either from LLM or callback override)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-114)    if event.is_final_response() and event.content:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-115)      print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-116)    elif event.is_error():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-117)       print(f"Error Event: {event.error_details}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-118)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-119)  # --- Scenario 2: Run where callback replaces the agent's output ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-120)  print("\n" + "="*20 + f" SCENARIO 2: Running Agent on Session '{session_id_modify}' (Should Replace Output) " + "="*20)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-121)  async for event in runner.run_async(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-122)    user_id=user_id,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-123)    session_id=session_id_modify,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-124)    new_message=types.Content(role="user", parts=[types.Part(text="Process this and add note.")])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-125)  ):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-126)     # Print final output (either from LLM or callback override)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-127)     if event.is_final_response() and event.content:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-128)      print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-129)     elif event.is_error():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-130)       print(f"Error Event: {event.error_details}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-131)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-132)# --- 4. Execute ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-133)# In a Python script:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-134)# import asyncio
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-135)# if __name__ == "__main__":
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-136)#   # Make sure GOOGLE_API_KEY environment variable is set if not using Vertex AI auth
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-137)#   # Or ensure Application Default Credentials (ADC) are configured for Vertex AI
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-138)#   asyncio.run(main())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-139)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-140)# In a Jupyter Notebook or similar environment:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-2-141)await main()

```

```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-2)importcom.google.adk.agents.CallbackContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-3)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-4)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-5)importcom.google.adk.sessions.State;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-6)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-7)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-8)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-9)importio.reactivex.rxjava3.core.Maybe;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-10)importjava.util.HashMap;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-11)importjava.util.List;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-12)importjava.util.Map;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-13)importjava.util.concurrent.ConcurrentHashMap;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-15)publicclass AfterAgentCallbackExample{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-16)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-17)// --- Constants ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-18)privatestaticfinalStringAPP_NAME="after_agent_demo";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-19)privatestaticfinalStringUSER_ID="test_user_after";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-20)privatestaticfinalStringSESSION_ID_NORMAL="session_run_normally";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-21)privatestaticfinalStringSESSION_ID_MODIFY="session_modify_output";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-22)privatestaticfinalStringMODEL_NAME="gemini-2.0-flash";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-23)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-24)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-25)AfterAgentCallbackExampledemo=newAfterAgentCallbackExample();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-26)demo.defineAgentAndRunScenarios();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-27)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-28)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-29)// --- 1. Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-30)/**
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-31)  * Log exit from an agent and checks 'add_concluding_note' in session state. If True, returns new
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-32)  * Content to *replace* the agent's original output. If False or not present, returns
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-33)  * Maybe.empty(), allowing the agent's original output to be used.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-34)  */
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-35)publicMaybe<Content>modifyOutputAfterAgent(CallbackContextcallbackContext){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-36)StringagentName=callbackContext.agentName();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-37)StringinvocationId=callbackContext.invocationId();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-38)StatecurrentState=callbackContext.state();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-39)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-40)System.out.printf("%n[Callback] Exiting agent: %s (Inv: %s)%n",agentName,invocationId);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-41)System.out.printf("[Callback] Current State: %s%n",currentState.entrySet());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-42)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-43)ObjectaddNoteFlag=currentState.get("add_concluding_note");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-44)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-45)// Example: Check state to decide whether to modify the final output
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-46)if(Boolean.TRUE.equals(addNoteFlag)){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-47)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-48)"[Callback] State condition 'add_concluding_note=True' met: Replacing agent %s's"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-49)+" output.%n",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-50)agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-51)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-52)// Return Content to *replace* the agent's own output
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-53)returnMaybe.just(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-54)Content.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-55).parts(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-56)List.of(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-57)Part.fromText(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-58)"Concluding note added by after_agent_callback, replacing original output.")))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-59).role("model")// Assign model role to the overriding response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-60).build());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-61)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-62)}else{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-63)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-64)"[Callback] State condition not met: Using agent %s's original output.%n",agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-65)// Return None - the agent's output produced just before this callback will be used.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-66)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-67)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-68)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-69)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-70)// --- 2. Setup Agent with Callback ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-71)publicvoiddefineAgentAndRunScenarios(){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-72)LlmAgentllmAgentWithAfterCb=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-73)LlmAgent.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-74).name(APP_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-75).model(MODEL_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-76).description("An LLM agent demonstrating after_agent_callback for output modification")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-77).instruction("You are a simple agent. Just say 'Processing complete!'")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-78).afterAgentCallback(this::modifyOutputAfterAgent)// Assign the callback here
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-79).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-80)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-81)// --- 3. Setup Runner and Sessions using InMemoryRunner ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-82)// Use InMemoryRunner - it includes InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-83)InMemoryRunnerrunner=newInMemoryRunner(llmAgentWithAfterCb,APP_NAME);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-84)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-85)// --- Scenario 1: Run where callback allows agent's original output ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-86)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-87)"%n%s SCENARIO 1: Running Agent (Should Use Original Output) %s%n",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-88)"=".repeat(20),"=".repeat(20));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-89)// No initial state means 'add_concluding_note' will be false in the callback check
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-90)runScenario(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-91)runner,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-92)llmAgentWithAfterCb.name(),// Use agent name for runner's appName consistency
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-93)SESSION_ID_NORMAL,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-94)null,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-95)"Process this please.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-96)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-97)// --- Scenario 2: Run where callback replaces the agent's output ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-98)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-99)"%n%s SCENARIO 2: Running Agent (Should Replace Output) %s%n",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-100)"=".repeat(20),"=".repeat(20));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-101)Map<String,Object>modifyState=newHashMap<>();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-102)modifyState.put("add_concluding_note",true);// Set the state flag here
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-103)runScenario(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-104)runner,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-105)llmAgentWithAfterCb.name(),// Use agent name for runner's appName consistency
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-106)SESSION_ID_MODIFY,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-107)newConcurrentHashMap<>(modifyState),
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-108)"Process this and add note.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-109)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-110)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-111)// --- 3. Method to Run a Single Scenario ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-112)publicvoidrunScenario(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-113)InMemoryRunnerrunner,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-114)StringappName,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-115)StringsessionId,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-116)ConcurrentHashMap<String,Object>initialState,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-117)StringuserQuery){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-118)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-119)// Create session using the runner's bundled session service
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-120)runner.sessionService().createSession(appName,USER_ID,initialState,sessionId).blockingGet();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-121)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-122)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-123)"Running scenario for session: %s, initial state: %s%n",sessionId,initialState);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-124)ContentuserMessage=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-125)Content.builder().role("user").parts(List.of(Part.fromText(userQuery))).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-126)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-127)Flowable<Event>eventStream=runner.runAsync(USER_ID,sessionId,userMessage);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-128)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-129)// Print final output
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-130)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-131)event->{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-132)if(event.finalResponse()&&event.content().isPresent()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-133)Stringauthor=event.author()!=null?event.author():"UNKNOWN";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-134)Stringtext=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-135)event
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-136).content()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-137).flatMap(Content::parts)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-138).filter(parts->!parts.isEmpty())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-139).map(parts->parts.get(0).text().orElse("").trim())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-140).orElse("[No text in final response]");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-141)System.out.printf("Final Output for %s: [%s] %s%n",sessionId,author,text);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-142)}elseif(event.errorCode().isPresent()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-143)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-144)"Error Event for %s: %s%n",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-145)sessionId,event.errorMessage().orElse("Unknown error"));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-146)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-147)});
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-148)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-3-149)}

```

**Note on the`after_agent_callback` Example:**
  * **What it Shows:** This example demonstrates the `after_agent_callback`. This callback runs _right after_ the agent's main processing logic has finished and produced its result, but _before_ that result is finalized and returned.
  * **How it Works:** The callback function (`modify_output_after_agent`) checks a flag (`add_concluding_note`) in the session's state.
    * If the flag is `True`, the callback returns a _new_ `types.Content` object. This tells the ADK framework to **replace** the agent's original output with the content returned by the callback.
    * If the flag is `False` (or not set), the callback returns `None` or an empty object. This tells the ADK framework to **use** the original output generated by the agent.
  * **Expected Outcome:** You'll see two scenarios:
    1. In the session _without_ the `add_concluding_note: True` state, the callback allows the agent's original output ("Processing complete!") to be used.
    2. In the session _with_ that state flag, the callback intercepts the agent's original output and replaces it with its own message ("Concluding note added...").
  * **Understanding Callbacks:** This highlights how `after_` callbacks allow **post-processing** or **modification**. You can inspect the result of a step (the agent's run) and decide whether to let it pass through, change it, or completely replace it based on your logic.


## LLM Interaction Callbacks[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#llm-interaction-callbacks "Permanent link")
These callbacks are specific to `LlmAgent` and provide hooks around the interaction with the Large Language Model.
### Before Model Callback[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#before-model-callback "Permanent link")
**When:** Called just before the `generate_content_async` (or equivalent) request is sent to the LLM within an `LlmAgent`'s flow.
**Purpose:** Allows inspection and modification of the request going to the LLM. Use cases include adding dynamic instructions, injecting few-shot examples based on state, modifying model config, implementing guardrails (like profanity filters), or implementing request-level caching.
**Return Value Effect:** If the callback returns `None` (or a `Maybe.empty()` object in Java), the LLM continues its normal workflow. If the callback returns an `LlmResponse` object, then the call to the LLM is **skipped**. The returned `LlmResponse` is used directly as if it came from the model. This is powerful for implementing guardrails or caching.
Code
[Python](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#python_2)[Java](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#java_2)
```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-2)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-6)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-8)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-13)# limitations under the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-15)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-16)fromgoogle.adk.agents.callback_contextimport CallbackContext
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-17)fromgoogle.adk.modelsimport LlmResponse, LlmRequest
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-18)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-19)fromtypingimport Optional
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-20)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-21)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-22)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-23)GEMINI_2_FLASH="gemini-2.0-flash"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-24)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-25)# --- Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-26)defsimple_before_model_modifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-27)  callback_context: CallbackContext, llm_request: LlmRequest
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-28)) -> Optional[LlmResponse]:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-29)"""Inspects/modifies the LLM request or skips the call."""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-30)  agent_name = callback_context.agent_name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-31)  print(f"[Callback] Before model call for agent: {agent_name}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-32)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-33)  # Inspect the last user message in the request contents
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-34)  last_user_message = ""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-35)  if llm_request.contents and llm_request.contents[-1].role == 'user':
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-36)     if llm_request.contents[-1].parts:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-37)      last_user_message = llm_request.contents[-1].parts[0].text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-38)  print(f"[Callback] Inspecting last user message: '{last_user_message}'")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-39)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-40)  # --- Modification Example ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-41)  # Add a prefix to the system instruction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-42)  original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-43)  prefix = "[Modified by Callback] "
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-44)  # Ensure system_instruction is Content and parts list exists
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-45)  if not isinstance(original_instruction, types.Content):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-46)     # Handle case where it might be a string (though config expects Content)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-47)     original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-48)  if not original_instruction.parts:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-49)    original_instruction.parts.append(types.Part(text="")) # Add an empty part if none exist
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-50)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-51)  # Modify the text of the first part
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-52)  modified_text = prefix + (original_instruction.parts[0].text or "")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-53)  original_instruction.parts[0].text = modified_text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-54)  llm_request.config.system_instruction = original_instruction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-55)  print(f"[Callback] Modified system instruction to: '{modified_text}'")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-56)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-57)  # --- Skip Example ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-58)  # Check if the last user message contains "BLOCK"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-59)  if "BLOCK" in last_user_message.upper():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-60)    print("[Callback] 'BLOCK' keyword found. Skipping LLM call.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-61)    # Return an LlmResponse to skip the actual LLM call
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-62)    return LlmResponse(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-63)      content=types.Content(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-64)        role="model",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-65)        parts=[types.Part(text="LLM call was blocked by before_model_callback.")],
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-66)      )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-67)    )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-68)  else:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-69)    print("[Callback] Proceeding with LLM call.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-70)    # Return None to allow the (modified) request to go to the LLM
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-71)    return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-72)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-73)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-74)# Create LlmAgent and Assign Callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-75)my_llm_agent = LlmAgent(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-76)    name="ModelCallbackAgent",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-77)    model=GEMINI_2_FLASH,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-78)    instruction="You are a helpful assistant.", # Base instruction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-79)    description="An LLM agent demonstrating before_model_callback",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-80)    before_model_callback=simple_before_model_modifier # Assign the function here
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-81))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-82)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-83)APP_NAME = "guardrail_app"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-84)USER_ID = "user_1"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-85)SESSION_ID = "session_001"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-86)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-87)# Session and Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-88)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-89)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-90)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-91)  runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-92)  return session, runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-93)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-94)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-95)# Agent Interaction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-96)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-97)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-98)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-99)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-100)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-101)  async for event in events:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-102)    if event.is_final_response():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-103)      final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-104)      print("Agent Response: ", final_response)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-105)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-106)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-107)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-4-108)await call_agent_async("write a joke on BLOCK")

```

```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-2)importcom.google.adk.agents.CallbackContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-3)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-4)importcom.google.adk.models.LlmRequest;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-5)importcom.google.adk.models.LlmResponse;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-6)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-7)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-8)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-9)importcom.google.common.collect.Iterables;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-10)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-11)importcom.google.genai.types.GenerateContentConfig;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-12)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-13)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-14)importio.reactivex.rxjava3.core.Maybe;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-15)importjava.util.ArrayList;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-16)importjava.util.List;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-17)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-18)publicclass BeforeModelCallbackExample{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-19)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-20)// --- Define Constants ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-21)privatestaticfinalStringAGENT_NAME="ModelCallbackAgent";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-22)privatestaticfinalStringMODEL_NAME="gemini-2.0-flash";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-23)privatestaticfinalStringAGENT_INSTRUCTION="You are a helpful assistant.";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-24)privatestaticfinalStringAGENT_DESCRIPTION=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-25)"An LLM agent demonstrating before_model_callback";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-26)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-27)// For session and runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-28)privatestaticfinalStringAPP_NAME="guardrail_app_java";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-29)privatestaticfinalStringUSER_ID="user_1_java";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-30)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-31)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-32)BeforeModelCallbackExampledemo=newBeforeModelCallbackExample();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-33)demo.defineAgentAndRun();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-34)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-35)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-36)// --- 1. Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-37)// Inspects/modifies the LLM request or skips the actual LLM call.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-38)publicMaybe<LlmResponse>simpleBeforeModelModifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-39)CallbackContextcallbackContext,LlmRequestllmRequest){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-40)StringagentName=callbackContext.agentName();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-41)System.out.printf("%n[Callback] Before model call for agent: %s%n",agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-42)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-43)StringlastUserMessage="";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-44)if(llmRequest.contents()!=null&&!llmRequest.contents().isEmpty()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-45)ContentlastContentItem=Iterables.getLast(llmRequest.contents());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-46)if("user".equals(lastContentItem.role().orElse(null))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-47)&&lastContentItem.parts().isPresent()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-48)&&!lastContentItem.parts().get().isEmpty()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-49)lastUserMessage=lastContentItem.parts().get().get(0).text().orElse("");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-50)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-51)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-52)System.out.printf("[Callback] Inspecting last user message: '%s'%n",lastUserMessage);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-53)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-54)// --- Modification Example ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-55)// Add a prefix to the system instruction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-56)ContentsystemInstructionFromRequest=Content.builder().parts(ImmutableList.of()).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-57)// Ensure system_instruction is Content and parts list exists
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-58)if(llmRequest.config().isPresent()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-59)systemInstructionFromRequest=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-60)llmRequest
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-61).config()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-62).get()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-63).systemInstruction()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-64).orElseGet(()->Content.builder().role("system").parts(ImmutableList.of()).build());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-65)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-66)List<Part>currentSystemParts=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-67)newArrayList<>(systemInstructionFromRequest.parts().orElse(ImmutableList.of()));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-68)// Ensure a part exists for modification
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-69)if(currentSystemParts.isEmpty()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-70)currentSystemParts.add(Part.fromText(""));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-71)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-72)// Modify the text of the first part
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-73)Stringprefix="[Modified by Callback] ";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-74)StringconceptuallyModifiedText=prefix+currentSystemParts.get(0).text().orElse("");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-75)llmRequest=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-76)llmRequest.toBuilder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-77).config(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-78)GenerateContentConfig.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-79).systemInstruction(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-80)Content.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-81).parts(List.of(Part.fromText(conceptuallyModifiedText)))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-82).build())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-83).build())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-84).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-85)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-86)"Modified System Instruction %s",llmRequest.config().get().systemInstruction());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-87)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-88)// --- Skip Example ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-89)// Check if the last user message contains "BLOCK"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-90)if(lastUserMessage.toUpperCase().contains("BLOCK")){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-91)System.out.println("[Callback] 'BLOCK' keyword found. Skipping LLM call.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-92)// Return an LlmResponse to skip the actual LLM call
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-93)returnMaybe.just(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-94)LlmResponse.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-95).content(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-96)Content.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-97).role("model")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-98).parts(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-99)ImmutableList.of(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-100)Part.fromText("LLM call was blocked by before_model_callback.")))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-101).build())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-102).build());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-103)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-104)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-105)// Return Empty response to allow the (modified) request to go to the LLM
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-106)System.out.println("[Callback] Proceeding with LLM call (using the original LlmRequest).");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-107)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-108)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-109)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-110)// --- 2. Define Agent and Run Scenarios ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-111)publicvoiddefineAgentAndRun(){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-112)// Setup Agent with Callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-113)LlmAgentmyLlmAgent=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-114)LlmAgent.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-115).name(AGENT_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-116).model(MODEL_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-117).instruction(AGENT_INSTRUCTION)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-118).description(AGENT_DESCRIPTION)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-119).beforeModelCallback(this::simpleBeforeModelModifier)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-120).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-121)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-122)// Create an InMemoryRunner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-123)InMemoryRunnerrunner=newInMemoryRunner(myLlmAgent,APP_NAME);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-124)// InMemoryRunner automatically creates a session service. Create a session using the service
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-125)Sessionsession=runner.sessionService().createSession(APP_NAME,USER_ID).blockingGet();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-126)ContentuserMessage=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-127)Content.fromParts(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-128)Part.fromText("Tell me about quantum computing. This is a test. So BLOCK."));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-129)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-130)// Run the agent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-131)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-132)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-133)// Stream event response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-134)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-135)event->{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-136)if(event.finalResponse()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-137)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-138)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-139)});
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-140)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-5-141)}

```

### After Model Callback[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#after-model-callback "Permanent link")
**When:** Called just after a response (`LlmResponse`) is received from the LLM, before it's processed further by the invoking agent.
**Purpose:** Allows inspection or modification of the raw LLM response. Use cases include
  * logging model outputs,
  * reformatting responses,
  * censoring sensitive information generated by the model,
  * parsing structured data from the LLM response and storing it in `callback_context.state`
  * or handling specific error codes.

Code
[Python](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#python_3)[Java](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#java_3)
```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-2)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-6)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-8)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-13)# limitations under the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-15)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-16)fromgoogle.adk.agents.callback_contextimport CallbackContext
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-17)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-18)fromtypingimport Optional
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-19)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-20)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-21)fromgoogle.adk.modelsimport LlmResponse
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-22)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-23)GEMINI_2_FLASH="gemini-2.0-flash"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-24)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-25)# --- Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-26)defsimple_after_model_modifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-27)  callback_context: CallbackContext, llm_response: LlmResponse
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-28)) -> Optional[LlmResponse]:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-29)"""Inspects/modifies the LLM response after it's received."""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-30)  agent_name = callback_context.agent_name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-31)  print(f"[Callback] After model call for agent: {agent_name}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-32)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-33)  # --- Inspection ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-34)  original_text = ""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-35)  if llm_response.content and llm_response.content.parts:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-36)    # Assuming simple text response for this example
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-37)    if llm_response.content.parts[0].text:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-38)      original_text = llm_response.content.parts[0].text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-39)      print(f"[Callback] Inspected original response text: '{original_text[:100]}...'") # Log snippet
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-40)    elif llm_response.content.parts[0].function_call:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-41)       print(f"[Callback] Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-42)       return None # Don't modify tool calls in this example
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-43)    else:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-44)       print("[Callback] Inspected response: No text content found.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-45)       return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-46)  elif llm_response.error_message:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-47)    print(f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-48)    return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-49)  else:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-50)    print("[Callback] Inspected response: Empty LlmResponse.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-51)    return None # Nothing to modify
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-52)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-53)  # --- Modification Example ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-54)  # Replace "joke" with "funny story" (case-insensitive)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-55)  search_term = "joke"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-56)  replace_term = "funny story"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-57)  if search_term in original_text.lower():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-58)    print(f"[Callback] Found '{search_term}'. Modifying response.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-59)    modified_text = original_text.replace(search_term, replace_term)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-60)    modified_text = modified_text.replace(search_term.capitalize(), replace_term.capitalize()) # Handle capitalization
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-61)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-62)    # Create a NEW LlmResponse with the modified content
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-63)    # Deep copy parts to avoid modifying original if other callbacks exist
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-64)    modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-65)    modified_parts[0].text = modified_text # Update the text in the copied part
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-66)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-67)    new_response = LlmResponse(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-68)       content=types.Content(role="model", parts=modified_parts),
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-69)       # Copy other relevant fields if necessary, e.g., grounding_metadata
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-70)       grounding_metadata=llm_response.grounding_metadata
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-71)       )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-72)    print(f"[Callback] Returning modified response.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-73)    return new_response # Return the modified response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-74)  else:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-75)    print(f"[Callback] '{search_term}' not found. Passing original response through.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-76)    # Return None to use the original llm_response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-77)    return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-78)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-79)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-80)# Create LlmAgent and Assign Callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-81)my_llm_agent = LlmAgent(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-82)    name="AfterModelCallbackAgent",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-83)    model=GEMINI_2_FLASH,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-84)    instruction="You are a helpful assistant.",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-85)    description="An LLM agent demonstrating after_model_callback",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-86)    after_model_callback=simple_after_model_modifier # Assign the function here
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-87))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-88)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-89)APP_NAME = "guardrail_app"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-90)USER_ID = "user_1"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-91)SESSION_ID = "session_001"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-92)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-93)# Session and Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-94)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-95)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-96)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-97)  runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-98)  return session, runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-99)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-100)# Agent Interaction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-101)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-102) session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-103)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-104) content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-105) events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-106)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-107) async for event in events:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-108)   if event.is_final_response():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-109)     final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-110)     print("Agent Response: ", final_response)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-111)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-112)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-113)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-6-114)await call_agent_async("""write multiple time the word "joke" """)

```

```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-2)importcom.google.adk.agents.CallbackContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-3)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-4)importcom.google.adk.models.LlmResponse;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-5)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-6)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-7)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-8)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-9)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-10)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-11)importio.reactivex.rxjava3.core.Maybe;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-12)importjava.util.ArrayList;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-13)importjava.util.List;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-14)importjava.util.Optional;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-15)importjava.util.regex.Matcher;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-16)importjava.util.regex.Pattern;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-17)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-18)publicclass AfterModelCallbackExample{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-19)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-20)// --- Define Constants ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-21)privatestaticfinalStringAGENT_NAME="AfterModelCallbackAgent";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-22)privatestaticfinalStringMODEL_NAME="gemini-2.0-flash";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-23)privatestaticfinalStringAGENT_INSTRUCTION="You are a helpful assistant.";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-24)privatestaticfinalStringAGENT_DESCRIPTION="An LLM agent demonstrating after_model_callback";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-25)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-26)// For session and runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-27)privatestaticfinalStringAPP_NAME="AfterModelCallbackAgentApp";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-28)privatestaticfinalStringUSER_ID="user_1";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-29)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-30)// For text replacement
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-31)privatestaticfinalStringSEARCH_TERM="joke";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-32)privatestaticfinalStringREPLACE_TERM="funny story";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-33)privatestaticfinalPatternSEARCH_PATTERN=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-34)Pattern.compile("\\b"+Pattern.quote(SEARCH_TERM)+"\\b",Pattern.CASE_INSENSITIVE);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-35)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-36)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-37)AfterModelCallbackExampleexample=newAfterModelCallbackExample();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-38)example.defineAgentAndRun();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-39)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-40)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-41)// --- Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-42)// Inspects/modifies the LLM response after it's received.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-43)publicMaybe<LlmResponse>simpleAfterModelModifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-44)CallbackContextcallbackContext,LlmResponsellmResponse){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-45)StringagentName=callbackContext.agentName();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-46)System.out.printf("%n[Callback] After model call for agent: %s%n",agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-47)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-48)// --- Inspection Phase ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-49)if(llmResponse.errorMessage().isPresent()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-50)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-51)"[Callback] Response has error: '%s'. No modification.%n",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-52)llmResponse.errorMessage().get());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-53)returnMaybe.empty();// Pass through errors
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-54)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-55)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-56)Optional<Part>firstTextPartOpt=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-57)llmResponse
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-58).content()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-59).flatMap(Content::parts)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-60).filter(parts->!parts.isEmpty()&&parts.get(0).text().isPresent())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-61).map(parts->parts.get(0));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-62)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-63)if(!firstTextPartOpt.isPresent()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-64)// Could be a function call, empty content, or no text in the first part
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-65)llmResponse
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-66).content()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-67).flatMap(Content::parts)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-68).filter(parts->!parts.isEmpty()&&parts.get(0).functionCall().isPresent())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-69).ifPresent(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-70)parts->
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-71)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-72)"[Callback] Response is a function call ('%s'). No text modification.%n",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-73)parts.get(0).functionCall().get().name().orElse("N/A")));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-74)if(!llmResponse.content().isPresent()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-75)||!llmResponse.content().flatMap(Content::parts).isPresent()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-76)||llmResponse.content().flatMap(Content::parts).get().isEmpty()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-77)System.out.println(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-78)"[Callback] Response content is empty or has no parts. No modification.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-79)}elseif(!firstTextPartOpt.isPresent()){// Already checked for function call
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-80)System.out.println("[Callback] First part has no text content. No modification.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-81)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-82)returnMaybe.empty();// Pass through non-text or unsuitable responses
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-83)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-84)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-85)StringoriginalText=firstTextPartOpt.get().text().get();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-86)System.out.printf("[Callback] Inspected original text: '%.100s...'%n",originalText);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-87)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-88)// --- Modification Phase ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-89)Matchermatcher=SEARCH_PATTERN.matcher(originalText);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-90)if(!matcher.find()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-91)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-92)"[Callback] '%s' not found. Passing original response through.%n",SEARCH_TERM);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-93)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-94)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-95)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-96)System.out.printf("[Callback] Found '%s'. Modifying response.%n",SEARCH_TERM);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-97)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-98)// Perform the replacement, respecting original capitalization of the found term's first letter
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-99)StringfoundTerm=matcher.group(0);// The actual term found (e.g., "joke" or "Joke")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-100)StringactualReplaceTerm=REPLACE_TERM;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-101)if(Character.isUpperCase(foundTerm.charAt(0))&&REPLACE_TERM.length()>0){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-102)actualReplaceTerm=Character.toUpperCase(REPLACE_TERM.charAt(0))+REPLACE_TERM.substring(1);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-103)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-104)StringmodifiedText=matcher.replaceFirst(Matcher.quoteReplacement(actualReplaceTerm));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-105)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-106)// Create a new LlmResponse with the modified content
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-107)ContentoriginalContent=llmResponse.content().get();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-108)List<Part>originalParts=originalContent.parts().orElse(ImmutableList.of());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-109)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-110)List<Part>modifiedPartsList=newArrayList<>(originalParts.size());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-111)if(!originalParts.isEmpty()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-112)modifiedPartsList.add(Part.fromText(modifiedText));// Replace first part's text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-113)// Add remaining parts as they were (shallow copy)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-114)for(inti=1;i<originalParts.size();i++){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-115)modifiedPartsList.add(originalParts.get(i));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-116)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-117)}else{// Should not happen if firstTextPartOpt was present
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-118)modifiedPartsList.add(Part.fromText(modifiedText));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-119)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-120)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-121)LlmResponse.BuildernewResponseBuilder=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-122)LlmResponse.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-123).content(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-124)originalContent.toBuilder().parts(ImmutableList.copyOf(modifiedPartsList)).build())
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-125).groundingMetadata(llmResponse.groundingMetadata());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-126)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-127)System.out.println("[Callback] Returning modified response.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-128)returnMaybe.just(newResponseBuilder.build());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-129)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-130)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-131)// --- 2. Define Agent and Run Scenarios ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-132)publicvoiddefineAgentAndRun(){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-133)// Setup Agent with Callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-134)LlmAgentmyLlmAgent=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-135)LlmAgent.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-136).name(AGENT_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-137).model(MODEL_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-138).instruction(AGENT_INSTRUCTION)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-139).description(AGENT_DESCRIPTION)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-140).afterModelCallback(this::simpleAfterModelModifier)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-141).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-142)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-143)// Create an InMemoryRunner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-144)InMemoryRunnerrunner=newInMemoryRunner(myLlmAgent,APP_NAME);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-145)// InMemoryRunner automatically creates a session service. Create a session using the service
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-146)Sessionsession=runner.sessionService().createSession(APP_NAME,USER_ID).blockingGet();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-147)ContentuserMessage=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-148)Content.fromParts(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-149)Part.fromText(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-150)"Tell me a joke about quantum computing. Include the word 'joke' in your response"));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-151)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-152)// Run the agent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-153)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-154)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-155)// Stream event response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-156)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-157)event->{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-158)if(event.finalResponse()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-159)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-160)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-161)});
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-162)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-7-163)}

```

## Tool Execution Callbacks[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#tool-execution-callbacks "Permanent link")
These callbacks are also specific to `LlmAgent` and trigger around the execution of tools (including `FunctionTool`, `AgentTool`, etc.) that the LLM might request.
### Before Tool Callback[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#before-tool-callback "Permanent link")
**When:** Called just before a specific tool's `run_async` method is invoked, after the LLM has generated a function call for it.
**Purpose:** Allows inspection and modification of tool arguments, performing authorization checks before execution, logging tool usage attempts, or implementing tool-level caching.
**Return Value Effect:**
  1. If the callback returns `None` (or a `Maybe.empty()` object in Java), the tool's `run_async` method is executed with the (potentially modified) `args`.
  2. If a dictionary (or `Map` in Java) is returned, the tool's `run_async` method is **skipped**. The returned dictionary is used directly as the result of the tool call. This is useful for caching or overriding tool behavior.

Code
[Python](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#python_4)[Java](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#java_4)
```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-2)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-6)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-8)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-13)# limitations under the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-15)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-16)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-17)fromtypingimport Optional
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-18)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-19)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-20)fromgoogle.adk.toolsimport FunctionTool
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-21)fromgoogle.adk.tools.tool_contextimport ToolContext
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-22)fromgoogle.adk.tools.base_toolimport BaseTool
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-23)fromtypingimport Dict, Any
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-24)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-25)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-26)GEMINI_2_FLASH="gemini-2.0-flash"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-27)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-28)defget_capital_city(country: str) -> str:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-29)"""Retrieves the capital city of a given country."""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-30)  print(f"--- Tool 'get_capital_city' executing with country: {country} ---")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-31)  country_capitals = {
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-32)    "united states": "Washington, D.C.",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-33)    "canada": "Ottawa",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-34)    "france": "Paris",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-35)    "germany": "Berlin",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-36)  }
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-37)  return country_capitals.get(country.lower(), f"Capital not found for {country}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-38)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-39)capital_tool = FunctionTool(func=get_capital_city)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-40)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-41)defsimple_before_tool_modifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-42)  tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-43)) -> Optional[Dict]:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-44)"""Inspects/modifies tool args or skips the tool call."""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-45)  agent_name = tool_context.agent_name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-46)  tool_name = tool.name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-47)  print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-48)  print(f"[Callback] Original args: {args}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-49)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-50)  if tool_name == 'get_capital_city' and args.get('country', '').lower() == 'canada':
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-51)    print("[Callback] Detected 'Canada'. Modifying args to 'France'.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-52)    args['country'] = 'France'
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-53)    print(f"[Callback] Modified args: {args}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-54)    return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-55)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-56)  # If the tool is 'get_capital_city' and country is 'BLOCK'
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-57)  if tool_name == 'get_capital_city' and args.get('country', '').upper() == 'BLOCK':
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-58)    print("[Callback] Detected 'BLOCK'. Skipping tool execution.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-59)    return {"result": "Tool execution was blocked by before_tool_callback."}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-60)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-61)  print("[Callback] Proceeding with original or previously modified args.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-62)  return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-63)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-64)my_llm_agent = LlmAgent(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-65)    name="ToolCallbackAgent",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-66)    model=GEMINI_2_FLASH,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-67)    instruction="You are an agent that can find capital cities. Use the get_capital_city tool.",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-68)    description="An LLM agent demonstrating before_tool_callback",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-69)    tools=[capital_tool],
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-70)    before_tool_callback=simple_before_tool_modifier
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-71))
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-72)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-73)APP_NAME = "guardrail_app"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-74)USER_ID = "user_1"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-75)SESSION_ID = "session_001"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-76)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-77)# Session and Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-78)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-79)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-80)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-81)  runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-82)  return session, runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-83)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-84)# Agent Interaction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-85)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-86)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-87)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-88)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-89)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-90)  async for event in events:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-91)    if event.is_final_response():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-92)      final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-93)      print("Agent Response: ", final_response)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-94)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-95)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-96)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-8-97)await call_agent_async("Canada")

```

```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-2)importcom.google.adk.agents.InvocationContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-3)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-4)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-5)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-6)importcom.google.adk.tools.Annotations.Schema;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-7)importcom.google.adk.tools.BaseTool;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-8)importcom.google.adk.tools.FunctionTool;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-9)importcom.google.adk.tools.ToolContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-10)importcom.google.common.collect.ImmutableMap;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-11)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-12)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-13)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-14)importio.reactivex.rxjava3.core.Maybe;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-15)importjava.util.HashMap;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-16)importjava.util.Map;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-17)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-18)publicclass BeforeToolCallbackExample{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-19)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-20)privatestaticfinalStringAPP_NAME="ToolCallbackAgentApp";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-21)privatestaticfinalStringUSER_ID="user_1";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-22)privatestaticfinalStringSESSION_ID="session_001";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-23)privatestaticfinalStringMODEL_NAME="gemini-2.0-flash";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-24)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-25)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-26)BeforeToolCallbackExampleexample=newBeforeToolCallbackExample();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-27)example.runAgent("capital of canada");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-28)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-29)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-30)// --- Define a Simple Tool Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-31)// The Schema is important for the callback "args" to correctly identify the input.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-32)publicstaticMap<String,Object>getCapitalCity(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-33)@Schema(name="country",description="The country to find the capital of.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-34)Stringcountry){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-35)System.out.printf("--- Tool 'getCapitalCity' executing with country: %s ---%n",country);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-36)Map<String,String>countryCapitals=newHashMap<>();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-37)countryCapitals.put("united states","Washington, D.C.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-38)countryCapitals.put("canada","Ottawa");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-39)countryCapitals.put("france","Paris");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-40)countryCapitals.put("germany","Berlin");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-41)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-42)Stringcapital=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-43)countryCapitals.getOrDefault(country.toLowerCase(),"Capital not found for "+country);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-44)// FunctionTool expects a Map<String, Object> as the return type for the method it wraps.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-45)returnImmutableMap.of("capital",capital);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-46)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-47)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-48)// Define the Callback function
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-49)// The Tool callback provides all these parameters by default.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-50)publicMaybe<Map<String,Object>>simpleBeforeToolModifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-51)InvocationContextinvocationContext,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-52)BaseTooltool,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-53)Map<String,Object>args,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-54)ToolContexttoolContext){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-55)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-56)StringagentName=invocationContext.agent().name();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-57)StringtoolName=tool.name();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-58)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-59)"[Callback] Before tool call for tool '%s' in agent '%s'%n",toolName,agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-60)System.out.printf("[Callback] Original args: %s%n",args);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-61)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-62)if("getCapitalCity".equals(toolName)){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-63)StringcountryArg=(String)args.get("country");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-64)if(countryArg!=null){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-65)if("canada".equalsIgnoreCase(countryArg)){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-66)System.out.println("[Callback] Detected 'Canada'. Modifying args to 'France'.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-67)args.put("country","France");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-68)System.out.printf("[Callback] Modified args: %s%n",args);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-69)// Proceed with modified args
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-70)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-71)}elseif("BLOCK".equalsIgnoreCase(countryArg)){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-72)System.out.println("[Callback] Detected 'BLOCK'. Skipping tool execution.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-73)// Return a map to skip the tool call and use this as the result
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-74)returnMaybe.just(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-75)ImmutableMap.of("result","Tool execution was blocked by before_tool_callback."));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-76)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-77)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-78)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-79)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-80)System.out.println("[Callback] Proceeding with original or previously modified args.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-81)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-82)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-83)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-84)publicvoidrunAgent(Stringquery){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-85)// --- Wrap the function into a Tool ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-86)FunctionToolcapitalTool=FunctionTool.create(this.getClass(),"getCapitalCity");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-87)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-88)// Create LlmAgent and Assign Callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-89)LlmAgentmyLlmAgent=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-90)LlmAgent.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-91).name(APP_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-92).model(MODEL_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-93).instruction(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-94)"You are an agent that can find capital cities. Use the getCapitalCity tool.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-95).description("An LLM agent demonstrating before_tool_callback")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-96).tools(capitalTool)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-97).beforeToolCallback(this::simpleBeforeToolModifier)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-98).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-99)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-100)// Session and Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-101)InMemoryRunnerrunner=newInMemoryRunner(myLlmAgent);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-102)Sessionsession=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-103)runner.sessionService().createSession(APP_NAME,USER_ID,null,SESSION_ID).blockingGet();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-104)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-105)ContentuserMessage=Content.fromParts(Part.fromText(query));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-106)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-107)System.out.printf("%n--- Calling agent with query: \"%s\" ---%n",query);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-108)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-109)// Stream event response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-110)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-111)event->{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-112)if(event.finalResponse()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-113)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-114)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-115)});
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-116)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-9-117)}

```

### After Tool Callback[¶](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#after-tool-callback "Permanent link")
**When:** Called just after the tool's `run_async` method completes successfully.
**Purpose:** Allows inspection and modification of the tool's result before it's sent back to the LLM (potentially after summarization). Useful for logging tool results, post-processing or formatting results, or saving specific parts of the result to the session state.
**Return Value Effect:**
  1. If the callback returns `None` (or a `Maybe.empty()` object in Java), the original `tool_response` is used.
  2. If a new dictionary is returned, it **replaces** the original `tool_response`. This allows modifying or filtering the result seen by the LLM.

Code
[Python](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#python_5)[Java](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#java_5)
```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-2)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-6)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-8)#
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-13)# limitations under the License.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-14)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-15)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-16)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-17)fromtypingimport Optional
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-18)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-19)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-20)fromgoogle.adk.toolsimport FunctionTool
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-21)fromgoogle.adk.tools.tool_contextimport ToolContext
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-22)fromgoogle.adk.tools.base_toolimport BaseTool
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-23)fromtypingimport Dict, Any
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-24)fromcopyimport deepcopy
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-25)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-26)GEMINI_2_FLASH="gemini-2.0-flash"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-27)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-28)# --- Define a Simple Tool Function (Same as before) ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-29)defget_capital_city(country: str) -> str:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-30)"""Retrieves the capital city of a given country."""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-31)  print(f"--- Tool 'get_capital_city' executing with country: {country} ---")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-32)  country_capitals = {
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-33)    "united states": "Washington, D.C.",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-34)    "canada": "Ottawa",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-35)    "france": "Paris",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-36)    "germany": "Berlin",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-37)  }
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-38)  return {"result": country_capitals.get(country.lower(), f"Capital not found for {country}")}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-39)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-40)# --- Wrap the function into a Tool ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-41)capital_tool = FunctionTool(func=get_capital_city)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-42)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-43)# --- Define the Callback Function ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-44)defsimple_after_tool_modifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-45)  tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-46)) -> Optional[Dict]:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-47)"""Inspects/modifies the tool result after execution."""
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-48)  agent_name = tool_context.agent_name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-49)  tool_name = tool.name
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-50)  print(f"[Callback] After tool call for tool '{tool_name}' in agent '{agent_name}'")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-51)  print(f"[Callback] Args used: {args}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-52)  print(f"[Callback] Original tool_response: {tool_response}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-53)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-54)  # Default structure for function tool results is {"result": <return_value>}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-55)  original_result_value = tool_response.get("result", "")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-56)  # original_result_value = tool_response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-57)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-58)  # --- Modification Example ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-59)  # If the tool was 'get_capital_city' and result is 'Washington, D.C.'
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-60)  if tool_name == 'get_cREDACTED == "Washington, D.C.":
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-61)    print("[Callback] Detected 'Washington, D.C.'. Modifying tool response.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-62)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-63)    # IMPORTANT: Create a new dictionary or modify a copy
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-64)    modified_response = deepcopy(tool_response)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-65)    modified_response["result"] = f"{original_result_value} (Note: This is the capital of the USA)."
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-66)    modified_response["note_added_by_callback"] = True # Add extra info if needed
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-67)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-68)    print(f"[Callback] Modified tool_response: {modified_response}")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-69)    return modified_response # Return the modified dictionary
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-70)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-71)  print("[Callback] Passing original tool response through.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-72)  # Return None to use the original tool_response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-73)  return None
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-74)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-75)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-76)# Create LlmAgent and Assign Callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-77)my_llm_agent = LlmAgent(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-78)    name="AfterToolCallbackAgent",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-79)    model=GEMINI_2_FLASH,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-80)    instruction="You are an agent that finds capital cities using the get_capital_city tool. Report the result clearly.",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-81)    description="An LLM agent demonstrating after_tool_callback",
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-82)    tools=[capital_tool], # Add the tool
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-83)    after_tool_callback=simple_after_tool_modifier # Assign the callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-84)  )
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-85)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-86)APP_NAME = "guardrail_app"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-87)USER_ID = "user_1"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-88)SESSION_ID = "session_001"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-89)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-90)# Session and Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-91)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-92)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-93)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-94)  runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-95)  return session, runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-96)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-97)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-98)# Agent Interaction
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-99)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-100)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-101)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-102)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-103)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-104)  async for event in events:
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-105)    if event.is_final_response():
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-106)      final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-107)      print("Agent Response: ", final_response)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-108)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-109)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-110)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-10-111)await call_agent_async("united states")

```

```
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-2)importcom.google.adk.agents.InvocationContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-3)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-4)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-5)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-6)importcom.google.adk.tools.Annotations.Schema;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-7)importcom.google.adk.tools.BaseTool;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-8)importcom.google.adk.tools.FunctionTool;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-9)importcom.google.adk.tools.ToolContext;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-10)importcom.google.common.collect.ImmutableMap;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-11)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-12)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-13)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-14)importio.reactivex.rxjava3.core.Maybe;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-15)importjava.util.HashMap;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-16)importjava.util.Map;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-17)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-18)publicclass AfterToolCallbackExample{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-19)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-20)privatestaticfinalStringAPP_NAME="AfterToolCallbackAgentApp";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-21)privatestaticfinalStringUSER_ID="user_1";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-22)privatestaticfinalStringSESSION_ID="session_001";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-23)privatestaticfinalStringMODEL_NAME="gemini-2.0-flash";
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-24)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-25)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-26)AfterToolCallbackExampleexample=newAfterToolCallbackExample();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-27)example.runAgent("What is the capital of the United States?");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-28)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-29)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-30)// --- Define a Simple Tool Function (Same as before) ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-31)@Schema(description="Retrieves the capital city of a given country.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-32)publicstaticMap<String,Object>getCapitalCity(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-33)@Schema(description="The country to find the capital of.")Stringcountry){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-34)System.out.printf("--- Tool 'getCapitalCity' executing with country: %s ---%n",country);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-35)Map<String,String>countryCapitals=newHashMap<>();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-36)countryCapitals.put("united states","Washington, D.C.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-37)countryCapitals.put("canada","Ottawa");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-38)countryCapitals.put("france","Paris");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-39)countryCapitals.put("germany","Berlin");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-40)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-41)Stringcapital=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-42)countryCapitals.getOrDefault(country.toLowerCase(),"Capital not found for "+country);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-43)returnImmutableMap.of("result",capital);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-44)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-45)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-46)// Define the Callback function.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-47)publicMaybe<Map<String,Object>>simpleAfterToolModifier(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-48)InvocationContextinvocationContext,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-49)BaseTooltool,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-50)Map<String,Object>args,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-51)ToolContexttoolContext,
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-52)ObjecttoolResponse){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-53)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-54)// Inspects/modifies the tool result after execution.
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-55)StringagentName=invocationContext.agent().name();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-56)StringtoolName=tool.name();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-57)System.out.printf(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-58)"[Callback] After tool call for tool '%s' in agent '%s'%n",toolName,agentName);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-59)System.out.printf("[Callback] Args used: %s%n",args);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-60)System.out.printf("[Callback] Original tool_response: %s%n",toolResponse);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-61)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-62)if(!(toolResponseinstanceofMap)){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-63)System.out.println("[Callback] toolResponse is not a Map, cannot process further.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-64)// Pass through if not a map
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-65)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-66)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-67)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-68)// Default structure for function tool results is {"result": <return_value>}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-69)@SuppressWarnings("unchecked")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-70)Map<String,Object>responseMap=(Map<String,Object>)toolResponse;
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-71)ObjectoriginalResultValue=responseMap.get("result");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-72)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-73)// --- Modification Example ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-74)// If the tool was 'get_capital_city' and result is 'Washington, D.C.'
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-75)if("getCapitalCity".equals(toolName)&&"Washington, D.C.".equals(originalResultValue)){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-76)System.out.println("[Callback] Detected 'Washington, D.C.'. Modifying tool response.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-77)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-78)// IMPORTANT: Create a new mutable map or modify a copy
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-79)Map<String,Object>modifiedResponse=newHashMap<>(responseMap);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-80)modifiedResponse.put(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-81)"result",originalResultValue+" (Note: This is the capital of the USA).");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-82)modifiedResponse.put("note_added_by_callback",true);// Add extra info if needed
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-83)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-84)System.out.printf("[Callback] Modified tool_response: %s%n",modifiedResponse);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-85)returnMaybe.just(modifiedResponse);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-86)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-87)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-88)System.out.println("[Callback] Passing original tool response through.");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-89)// Return Maybe.empty() to use the original tool_response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-90)returnMaybe.empty();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-91)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-92)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-93)publicvoidrunAgent(Stringquery){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-94)// --- Wrap the function into a Tool ---
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-95)FunctionToolcapitalTool=FunctionTool.create(this.getClass(),"getCapitalCity");
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-96)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-97)// Create LlmAgent and Assign Callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-98)LlmAgentmyLlmAgent=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-99)LlmAgent.builder()
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-100).name(APP_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-101).model(MODEL_NAME)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-102).instruction(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-103)"You are an agent that finds capital cities using the getCapitalCity tool. Report"
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-104)+" the result clearly.")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-105).description("An LLM agent demonstrating after_tool_callback")
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-106).tools(capitalTool)// Add the tool
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-107).afterToolCallback(this::simpleAfterToolModifier)// Assign the callback
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-108).build();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-109)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-110)InMemoryRunnerrunner=newInMemoryRunner(myLlmAgent);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-111)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-112)// Session and Runner
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-113)Sessionsession=
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-114)runner.sessionService().createSession(APP_NAME,USER_ID,null,SESSION_ID).blockingGet();
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-115)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-116)ContentuserMessage=Content.fromParts(Part.fromText(query));
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-117)
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-118)System.out.printf("%n--- Calling agent with query: \"%s\" ---%n",query);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-119)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-120)// Stream event response
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-121)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-122)event->{
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-123)if(event.finalResponse()){
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-124)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-125)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-126)});
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-127)}
[](https://google.github.io/adk-docs/callbacks/types-of-callbacks/#__codelineno-11-128)}

```

Back to top
