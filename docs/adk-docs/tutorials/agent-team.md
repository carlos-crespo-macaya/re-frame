[ Skip to content ](https://google.github.io/adk-docs/tutorials/agent-team/#build-your-first-intelligent-agent-team-a-progressive-weather-bot-with-adk)
# Build Your First Intelligent Agent Team: A Progressive Weather Bot with ADK[¶](https://google.github.io/adk-docs/tutorials/agent-team/#build-your-first-intelligent-agent-team-a-progressive-weather-bot-with-adk "Permanent link")
[ ![Google Colaboratory logo](https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg) Open in Colab ](https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb)
Share to: [ ![LinkedIn logo](https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg) ](https://www.linkedin.com/sharing/share-offsite/?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on LinkedIn") [ ![Bluesky logo](https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg) ](https://bsky.app/intent/compose?text=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on Bluesky") [ ![X logo](https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg) ](https://twitter.com/intent/tweet?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on X \(Twitter\)") [ ![Reddit logo](https://redditinc.com/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png) ](https://reddit.com/submit?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on Reddit") [ ![Facebook logo](https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg) ](https://www.facebook.com/sharer/sharer.php?u=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb "Share on Facebook")
This tutorial extends from the [Quickstart example](https://google.github.io/adk-docs/get-started/quickstart/) for [Agent Development Kit](https://google.github.io/adk-docs/get-started/). Now, you're ready to dive deeper and construct a more sophisticated, **multi-agent system**.
We'll embark on building a **Weather Bot agent team** , progressively layering advanced features onto a simple foundation. Starting with a single agent that can look up weather, we will incrementally add capabilities like:
  * Leveraging different AI models (Gemini, GPT, Claude).
  * Designing specialized sub-agents for distinct tasks (like greetings and farewells).
  * Enabling intelligent delegation between agents.
  * Giving agents memory using persistent session state.
  * Implementing crucial safety guardrails using callbacks.


**Why a Weather Bot Team?**
This use case, while seemingly simple, provides a practical and relatable canvas to explore core ADK concepts essential for building complex, real-world agentic applications. You'll learn how to structure interactions, manage state, ensure safety, and orchestrate multiple AI "brains" working together.
**What is ADK Again?**
As a reminder, ADK is a Python framework designed to streamline the development of applications powered by Large Language Models (LLMs). It offers robust building blocks for creating agents that can reason, plan, utilize tools, interact dynamically with users, and collaborate effectively within a team.
**In this advanced tutorial, you will master:**
  * ✅ **Tool Definition & Usage:** Crafting Python functions (`tools`) that grant agents specific abilities (like fetching data) and instructing agents on how to use them effectively.
  * ✅ **Multi-LLM Flexibility:** Configuring agents to utilize various leading LLMs (Gemini, GPT-4o, Claude Sonnet) via LiteLLM integration, allowing you to choose the best model for each task.
  * ✅ **Agent Delegation & Collaboration:** Designing specialized sub-agents and enabling automatic routing (`auto flow`) of user requests to the most appropriate agent within a team.
  * ✅ **Session State for Memory:** Utilizing `Session State` and `ToolContext` to enable agents to remember information across conversational turns, leading to more contextual interactions.
  * ✅ **Safety Guardrails with Callbacks:** Implementing `before_model_callback` and `before_tool_callback` to inspect, modify, or block requests/tool usage based on predefined rules, enhancing application safety and control.


**End State Expectation:**
By completing this tutorial, you will have built a functional multi-agent Weather Bot system. This system will not only provide weather information but also handle conversational niceties, remember the last city checked, and operate within defined safety boundaries, all orchestrated using ADK.
**Prerequisites:**
  * ✅ **Solid understanding of Python programming.**
  * ✅ **Familiarity with Large Language Models (LLMs), APIs, and the concept of agents.**
  * ❗ **Crucially: Completion of the ADK Quickstart tutorial(s) or equivalent foundational knowledge of ADK basics (Agent, Runner, SessionService, basic Tool usage).** This tutorial builds directly upon those concepts.
  * ✅ **API Keys** for the LLMs you intend to use (e.g., Google AI Studio for Gemini, OpenAI Platform, Anthropic Console).


**Note on Execution Environment:**
This tutorial is structured for interactive notebook environments like Google Colab, Colab Enterprise, or Jupyter notebooks. Please keep the following in mind:
  * **Running Async Code:** Notebook environments handle asynchronous code differently. You'll see examples using `await` (suitable when an event loop is already running, common in notebooks) or `asyncio.run()` (often needed when running as a standalone `.py` script or in specific notebook setups). The code blocks provide guidance for both scenarios.
  * **Manual Runner/Session Setup:** The steps involve explicitly creating `Runner` and `SessionService` instances. This approach is shown because it gives you fine-grained control over the agent's execution lifecycle, session management, and state persistence.


**Alternative: Using ADK's Built-in Tools (Web UI / CLI / API Server)**
If you prefer a setup that handles the runner and session management automatically using ADK's standard tools, you can find the equivalent code structured for that purpose [here](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial). That version is designed to be run directly with commands like `adk web` (for a web UI), `adk run` (for CLI interaction), or `adk api_server` (to expose an API). Please follow the `README.md` instructions provided in that alternative resource.
**Ready to build your agent team? Let's dive in!**
> **Note:** This tutorial works with adk version 1.0.0 and above
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-0-1)# @title Step 0: Setup and Installation
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-0-2)# Install ADK and LiteLLM for multi-model support
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-0-3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-0-4)!pip install google-adk -q
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-0-5)!pip install litellm -q
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-0-6)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-0-7)print("Installation complete.")

```

```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-1)# @title Import necessary libraries
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-2)importos
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-3)importasyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-4)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-5)fromgoogle.adk.models.lite_llmimport LiteLlm # For multi-model support
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-6)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-7)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-8)fromgoogle.genaiimport types # For creating message Content/Parts
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-10)importwarnings
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-11)# Ignore all warnings
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-12)warnings.filterwarnings("ignore")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-13)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-14)importlogging
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-15)logging.basicConfig(level=logging.ERROR)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-16)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-1-17)print("Libraries imported.")

```

```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-1)# @title Configure API Keys (Replace with your actual keys!)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-3)# --- IMPORTANT: Replace placeholders with your real API keys ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-4)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-5)# Gemini API Key (Get from Google AI Studio: https://aistudio.google.com/app/apikey)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-6)os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY" # <--- REPLACE
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-7)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-8)# [Optional]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-9)# OpenAI API Key (Get from OpenAI Platform: https://platform.openai.com/api-keys)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-10)os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY' # <--- REPLACE
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-11)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-12)# [Optional]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-13)# Anthropic API Key (Get from Anthropic Console: https://console.anthropic.com/settings/keys)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-14)os.environ['ANTHROPIC_REDACTED' # <--- REPLACE
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-15)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-16)# --- Verify Keys (Optional Check) ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-17)print("API Keys Set:")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-18)print(f"Google API Key set: {'Yes'ifos.environ.get('GOOGLE_API_KEY')andos.environ['GOOGLE_API_KEY']!='YOUR_GOOGLE_API_KEY'else'No (REPLACE PLACEHOLDER!)'}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-19)print(f"OpenAI API Key set: {'Yes'ifos.environ.get('OPENAI_API_KEY')andos.environ['OPENAI_API_KEY']!='YOUR_OPENAI_API_KEY'else'No (REPLACE PLACEHOLDER!)'}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-20)print(f"Anthropic API Key set: {'Yes'ifos.environ.get('ANTHROPIC_REDACTED'else'No (REPLACE PLACEHOLDER!)'}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-21)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-22)# Configure ADK to use API keys directly (not Vertex AI for this multi-model setup)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-23)os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-24)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-25)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-2-26)# @markdown **Security Note:** It's best practice to manage API keys securely (e.g., using Colab Secrets or environment variables) rather than hardcoding them directly in the notebook. Replace the placeholder strings above.

```

```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-1)# --- Define Model Constants for easier use ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-3)# More supported models can be referenced here: https://ai.google.dev/gemini-api/docs/models#model-variations
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-4)MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-5)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-6)# More supported models can be referenced here: https://docs.litellm.ai/docs/providers/openai#openai-chat-completion-models
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-7)MODEL_GPT_4O = "openai/gpt-4.1" # You can also try: gpt-4.1-mini, gpt-4o etc.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-8)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-9)# More supported models can be referenced here: https://docs.litellm.ai/docs/providers/anthropic
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-10)MODEL_CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514" # You can also try: claude-opus-4-20250514 , claude-3-7-sonnet-20250219 etc
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-11)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-3-12)print("\nEnvironment configured.")

```

## Step 1: Your First Agent - Basic Weather Lookup[¶](https://google.github.io/adk-docs/tutorials/agent-team/#step-1-your-first-agent-basic-weather-lookup "Permanent link")
Let's begin by building the fundamental component of our Weather Bot: a single agent capable of performing a specific task – looking up weather information. This involves creating two core pieces:
  1. **A Tool:** A Python function that equips the agent with the _ability_ to fetch weather data.
  2. **An Agent:** The AI "brain" that understands the user's request, knows it has a weather tool, and decides when and how to use it.


**1. Define the Tool (`get_weather`)**
In ADK, **Tools** are the building blocks that give agents concrete capabilities beyond just text generation. They are typically regular Python functions that perform specific actions, like calling an API, querying a database, or performing calculations.
Our first tool will provide a _mock_ weather report. This allows us to focus on the agent structure without needing external API keys yet. Later, you could easily swap this mock function with one that calls a real weather service.
**Key Concept: Docstrings are Crucial!** The agent's LLM relies heavily on the function's **docstring** to understand:
  * _What_ the tool does.
  * _When_ to use it.
  * _What arguments_ it requires (`city: str`).
  * _What information_ it returns.


**Best Practice:** Write clear, descriptive, and accurate docstrings for your tools. This is essential for the LLM to use the tool correctly.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-1)# @title Define the get_weather Tool
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-2)defget_weather(city: str) -> dict:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-3)"""Retrieves the current weather report for a specified city.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-4)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-5)  Args:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-6)    city (str): The name of the city (e.g., "New York", "London", "Tokyo").
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-7)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-8)  Returns:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-9)    dict: A dictionary containing the weather information.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-10)       Includes a 'status' key ('success' or 'error').
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-11)       If 'success', includes a 'report' key with weather details.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-12)       If 'error', includes an 'error_message' key.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-13)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-14)  print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-15)  city_normalized = city.lower().replace(" ", "") # Basic normalization
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-16)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-17)  # Mock weather data
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-18)  mock_weather_db = {
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-19)    "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-20)    "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-21)    "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-22)  }
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-23)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-24)  if city_normalized in mock_weather_db:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-25)    return mock_weather_db[city_normalized]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-26)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-27)    return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-28)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-29)# Example tool usage (optional test)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-30)print(get_weather("New York"))
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-4-31)print(get_weather("Paris"))

```

**2. Define the Agent (`weather_agent`)**
Now, let's create the **Agent** itself. An `Agent` in ADK orchestrates the interaction between the user, the LLM, and the available tools.
We configure it with several key parameters:
  * `name`: A unique identifier for this agent (e.g., "weather_agent_v1").
  * `model`: Specifies which LLM to use (e.g., `MODEL_GEMINI_2_0_FLASH`). We'll start with a specific Gemini model.
  * `description`: A concise summary of the agent's overall purpose. This becomes crucial later when other agents need to decide whether to delegate tasks to _this_ agent.
  * `instruction`: Detailed guidance for the LLM on how to behave, its persona, its goals, and specifically _how and when_ to utilize its assigned `tools`.
  * `tools`: A list containing the actual Python tool functions the agent is allowed to use (e.g., `[get_weather]`).


**Best Practice:** Provide clear and specific `instruction` prompts. The more detailed the instructions, the better the LLM can understand its role and how to use its tools effectively. Be explicit about error handling if needed.
**Best Practice:** Choose descriptive `name` and `description` values. These are used internally by ADK and are vital for features like automatic delegation (covered later).
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-1)# @title Define the Weather Agent
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-2)# Use one of the model constants defined earlier
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-3)AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Starting with Gemini
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-4)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-5)weather_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-6)  name="weather_agent_v1",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-7)  model=AGENT_MODEL, # Can be a string for Gemini or a LiteLlm object
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-8)  description="Provides weather information for specific cities.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-9)  instruction="You are a helpful weather assistant. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-10)        "When the user asks for the weather in a specific city, "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-11)        "use the 'get_weather' tool to find the information. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-12)        "If the tool returns an error, inform the user politely. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-13)        "If the tool is successful, present the weather report clearly.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-14)  tools=[get_weather], # Pass the function directly
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-15))
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-16)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-5-17)print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")

```

**3. Setup Runner and Session Service**
To manage conversations and execute the agent, we need two more components:
  * `SessionService`: Responsible for managing conversation history and state for different users and sessions. The `InMemorySessionService` is a simple implementation that stores everything in memory, suitable for testing and simple applications. It keeps track of the messages exchanged. We'll explore state persistence more in Step 4.
  * `Runner`: The engine that orchestrates the interaction flow. It takes user input, routes it to the appropriate agent, manages calls to the LLM and tools based on the agent's logic, handles session updates via the `SessionService`, and yields events representing the progress of the interaction.


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-1)# @title Setup Session Service and Runner
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-3)# --- Session Management ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-4)# Key Concept: SessionService stores conversation history & state.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-5)# InMemorySessionService is simple, non-persistent storage for this tutorial.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-6)session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-7)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-8)# Define constants for identifying the interaction context
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-9)APP_NAME = "weather_tutorial_app"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-10)USER_ID = "user_1"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-11)SESSION_ID = "session_001" # Using a fixed ID for simplicity
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-12)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-13)# Create the specific session where the conversation will happen
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-14)session = await session_service.create_session(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-15)  app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-16)  user_id=USER_ID,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-17)  session_id=SESSION_ID
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-18))
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-19)print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-20)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-21)# --- Runner ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-22)# Key Concept: Runner orchestrates the agent execution loop.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-23)runner = Runner(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-24)  agent=weather_agent, # The agent we want to run
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-25)  app_name=APP_NAME,  # Associates runs with our app
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-26)  session_service=session_service # Uses our session manager
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-27))
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-6-28)print(f"Runner created for agent '{runner.agent.name}'.")

```

**4. Interact with the Agent**
We need a way to send messages to our agent and receive its responses. Since LLM calls and tool executions can take time, ADK's `Runner` operates asynchronously.
We'll define an `async` helper function (`call_agent_async`) that:
  1. Takes a user query string.
  2. Packages it into the ADK `Content` format.
  3. Calls `runner.run_async`, providing the user/session context and the new message.
  4. Iterates through the **Events** yielded by the runner. Events represent steps in the agent's execution (e.g., tool call requested, tool result received, intermediate LLM thought, final response).
  5. Identifies and prints the **final response** event using `event.is_final_response()`.


**Why`async`?** Interactions with LLMs and potentially tools (like external APIs) are I/O-bound operations. Using `asyncio` allows the program to handle these operations efficiently without blocking execution.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-1)# @title Define Agent Interaction Function
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-3)fromgoogle.genaiimport types # For creating message Content/Parts
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-4)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-5)async defcall_agent_async(query: str, runner, user_id, session_id):
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-6)"""Sends a query to the agent and prints the final response."""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-7) print(f"\n>>> User Query: {query}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-8)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-9) # Prepare the user's message in ADK format
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-10) content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-11)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-12) final_response_text = "Agent did not produce a final response." # Default
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-13)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-14) # Key Concept: run_async executes the agent logic and yields Events.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-15) # We iterate through events to find the final answer.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-16) async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-17)   # You can uncomment the line below to see *all* events during execution
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-18)   # print(f" [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-19)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-20)   # Key Concept: is_final_response() marks the concluding message for the turn.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-21)   if event.is_final_response():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-22)     if event.content and event.content.parts:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-23)       # Assuming text response in the first part
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-24)       final_response_text = event.content.parts[0].text
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-25)     elif event.actions and event.actions.escalate: # Handle potential errors/escalations
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-26)       final_response_text = f"Agent escalated: {event.error_messageor'No specific message.'}"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-27)     # Add more checks here if needed (e.g., specific error codes)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-28)     break # Stop processing events once the final response is found
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-29)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-7-30) print(f"<<< Agent Response: {final_response_text}")

```

**5. Run the Conversation**
Finally, let's test our setup by sending a few queries to the agent. We wrap our `async` calls in a main `async` function and run it using `await`.
Watch the output:
  * See the user queries.
  * Notice the `--- Tool: get_weather called... ---` logs when the agent uses the tool.
  * Observe the agent's final responses, including how it handles the case where weather data isn't available (for Paris).


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-1)# @title Run the Initial Conversation
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-3)# We need an async function to await our interaction helper
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-4)async defrun_conversation():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-5)  await call_agent_async("What is the weather like in London?",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-6)                    runner=runner,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-7)                    user_id=USER_ID,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-8)                    session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-10)  await call_agent_async("How about Paris?",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-11)                    runner=runner,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-12)                    user_id=USER_ID,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-13)                    session_id=SESSION_ID) # Expecting the tool's error message
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-14)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-15)  await call_agent_async("Tell me the weather in New York",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-16)                    runner=runner,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-17)                    user_id=USER_ID,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-18)                    session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-19)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-20)# Execute the conversation using await in an async context (like Colab/Jupyter)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-21)await run_conversation()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-22)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-23)# --- OR ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-24)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-25)# Uncomment the following lines if running as a standard Python script (.py file):
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-26)# import asyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-27)# if __name__ == "__main__":
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-28)#   try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-29)#     asyncio.run(run_conversation())
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-30)#   except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-8-31)#     print(f"An error occurred: {e}")

```

Congratulations! You've successfully built and interacted with your first ADK agent. It understands the user's request, uses a tool to find information, and responds appropriately based on the tool's result.
In the next step, we'll explore how to easily switch the underlying Language Model powering this agent.
## Step 2: Going Multi-Model with LiteLLM [Optional][¶](https://google.github.io/adk-docs/tutorials/agent-team/#step-2-going-multi-model-with-litellm-optional "Permanent link")
In Step 1, we built a functional Weather Agent powered by a specific Gemini model. While effective, real-world applications often benefit from the flexibility to use _different_ Large Language Models (LLMs). Why?
  * **Performance:** Some models excel at specific tasks (e.g., coding, reasoning, creative writing).
  * **Cost:** Different models have varying price points.
  * **Capabilities:** Models offer diverse features, context window sizes, and fine-tuning options.
  * **Availability/Redundancy:** Having alternatives ensures your application remains functional even if one provider experiences issues.


ADK makes switching between models seamless through its integration with the [**LiteLLM**](https://github.com/BerriAI/litellm) library. LiteLLM acts as a consistent interface to over 100 different LLMs.
**In this step, we will:**
  1. Learn how to configure an ADK `Agent` to use models from providers like OpenAI (GPT) and Anthropic (Claude) using the `LiteLlm` wrapper.
  2. Define, configure (with their own sessions and runners), and immediately test instances of our Weather Agent, each backed by a different LLM.
  3. Interact with these different agents to observe potential variations in their responses, even when using the same underlying tool.


**1. Import`LiteLlm`**
We imported this during the initial setup (Step 0), but it's the key component for multi-model support:
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-9-1)# @title 1. Import LiteLlm
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-9-2)fromgoogle.adk.models.lite_llmimport LiteLlm

```

**2. Define and Test Multi-Model Agents**
Instead of passing only a model name string (which defaults to Google's Gemini models), we wrap the desired model identifier string within the `LiteLlm` class.
  * **Key Concept:`LiteLlm` Wrapper:** The `LiteLlm(model="provider/model_name")` syntax tells ADK to route requests for this agent through the LiteLLM library to the specified model provider.


Make sure you have configured the necessary API keys for OpenAI and Anthropic in Step 0. We'll use the `call_agent_async` function (defined earlier, which now accepts `runner`, `user_id`, and `session_id`) to interact with each agent immediately after its setup.
Each block below will:
  * Define the agent using a specific LiteLLM model (`MODEL_GPT_4O` or `MODEL_CLAUDE_SONNET`).
  * Create a _new, separate_ `InMemorySessionService` and session specifically for that agent's test run. This keeps the conversation histories isolated for this demonstration.
  * Create a `Runner` configured for the specific agent and its session service.
  * Immediately call `call_agent_async` to send a query and test the agent.


**Best Practice:** Use constants for model names (like `MODEL_GPT_4O`, `MODEL_CLAUDE_SONNET` defined in Step 0) to avoid typos and make code easier to manage.
**Error Handling:** We wrap the agent definitions in `try...except` blocks. This prevents the entire code cell from failing if an API key for a specific provider is missing or invalid, allowing the tutorial to proceed with the models that _are_ configured.
First, let's create and test the agent using OpenAI's GPT-4o.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-1)# @title Define and Test GPT Agent
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-3)# Make sure 'get_weather' function from Step 1 is defined in your environment.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-4)# Make sure 'call_agent_async' is defined from earlier.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-5)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-6)# --- Agent using GPT-4o ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-7)weather_agent_gpt = None # Initialize to None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-8)runner_gpt = None   # Initialize runner to None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-10)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-11)  weather_agent_gpt = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-12)    name="weather_agent_gpt",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-13)    # Key change: Wrap the LiteLLM model identifier
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-14)    model=LiteLlm(model=MODEL_GPT_4O),
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-15)    description="Provides weather information (using GPT-4o).",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-16)    instruction="You are a helpful weather assistant powered by GPT-4o. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-17)          "Use the 'get_weather' tool for city weather requests. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-18)          "Clearly present successful reports or polite error messages based on the tool's output status.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-19)    tools=[get_weather], # Re-use the same tool
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-20)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-21)  print(f"Agent '{weather_agent_gpt.name}' created using model '{MODEL_GPT_4O}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-22)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-23)  # InMemorySessionService is simple, non-persistent storage for this tutorial.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-24)  session_service_gpt = InMemorySessionService() # Create a dedicated service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-25)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-26)  # Define constants for identifying the interaction context
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-27)  APP_NAME_GPT = "weather_tutorial_app_gpt" # Unique app name for this test
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-28)  USER_ID_GPT = "user_1_gpt"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-29)  SESSION_ID_GPT = "session_001_gpt" # Using a fixed ID for simplicity
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-30)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-31)  # Create the specific session where the conversation will happen
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-32)  session_gpt = await session_service_gpt.create_session(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-33)    app_name=APP_NAME_GPT,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-34)    user_id=USER_ID_GPT,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-35)    session_id=SESSION_ID_GPT
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-36)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-37)  print(f"Session created: App='{APP_NAME_GPT}', User='{USER_ID_GPT}', Session='{SESSION_ID_GPT}'")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-38)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-39)  # Create a runner specific to this agent and its session service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-40)  runner_gpt = Runner(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-41)    agent=weather_agent_gpt,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-42)    app_name=APP_NAME_GPT,    # Use the specific app name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-43)    session_service=session_service_gpt # Use the specific session service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-44)    )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-45)  print(f"Runner created for agent '{runner_gpt.agent.name}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-46)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-47)  # --- Test the GPT Agent ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-48)  print("\n--- Testing GPT Agent ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-49)  # Ensure call_agent_async uses the correct runner, user_id, session_id
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-50)  await call_agent_async(query = "What's the weather in Tokyo?",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-51)              runner=runner_gpt,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-52)              user_id=USER_ID_GPT,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-53)              session_id=SESSION_ID_GPT)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-54)  # --- OR ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-55)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-56)  # Uncomment the following lines if running as a standard Python script (.py file):
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-57)  # import asyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-58)  # if __name__ == "__main__":
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-59)  #   try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-60)  #     asyncio.run(call_agent_async(query = "What's the weather in Tokyo?",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-61)  #           runner=runner_gpt,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-62)  #            user_id=USER_ID_GPT,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-63)  #            session_id=SESSION_ID_GPT)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-64)  #   except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-65)  #     print(f"An error occurred: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-66)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-67)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-10-68)  print(f"❌ Could not create or run GPT agent '{MODEL_GPT_4O}'. Check API Key and model name. Error: {e}")

```

Next, we'll do the same for Anthropic's Claude Sonnet.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-1)# @title Define and Test Claude Agent
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-3)# Make sure 'get_weather' function from Step 1 is defined in your environment.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-4)# Make sure 'call_agent_async' is defined from earlier.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-5)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-6)# --- Agent using Claude Sonnet ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-7)weather_agent_claude = None # Initialize to None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-8)runner_claude = None   # Initialize runner to None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-10)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-11)  weather_agent_claude = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-12)    name="weather_agent_claude",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-13)    # Key change: Wrap the LiteLLM model identifier
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-14)    model=LiteLlm(model=MODEL_CLAUDE_SONNET),
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-15)    description="Provides weather information (using Claude Sonnet).",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-16)    instruction="You are a helpful weather assistant powered by Claude Sonnet. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-17)          "Use the 'get_weather' tool for city weather requests. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-18)          "Analyze the tool's dictionary output ('status', 'report'/'error_message'). "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-19)          "Clearly present successful reports or polite error messages.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-20)    tools=[get_weather], # Re-use the same tool
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-21)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-22)  print(f"Agent '{weather_agent_claude.name}' created using model '{MODEL_CLAUDE_SONNET}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-23)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-24)  # InMemorySessionService is simple, non-persistent storage for this tutorial.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-25)  session_service_claude = InMemorySessionService() # Create a dedicated service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-26)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-27)  # Define constants for identifying the interaction context
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-28)  APP_NAME_CLAUDE = "weather_tutorial_app_claude" # Unique app name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-29)  USER_ID_CLAUDE = "user_1_claude"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-30)  SESSION_ID_CLAUDE = "session_001_claude" # Using a fixed ID for simplicity
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-31)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-32)  # Create the specific session where the conversation will happen
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-33)  session_claude = await session_service_claude.create_session(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-34)    app_name=APP_NAME_CLAUDE,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-35)    user_id=USER_ID_CLAUDE,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-36)    session_id=SESSION_ID_CLAUDE
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-37)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-38)  print(f"Session created: App='{APP_NAME_CLAUDE}', User='{USER_ID_CLAUDE}', Session='{SESSION_ID_CLAUDE}'")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-39)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-40)  # Create a runner specific to this agent and its session service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-41)  runner_claude = Runner(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-42)    agent=weather_agent_claude,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-43)    app_name=APP_NAME_CLAUDE,    # Use the specific app name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-44)    session_service=session_service_claude # Use the specific session service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-45)    )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-46)  print(f"Runner created for agent '{runner_claude.agent.name}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-47)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-48)  # --- Test the Claude Agent ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-49)  print("\n--- Testing Claude Agent ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-50)  # Ensure call_agent_async uses the correct runner, user_id, session_id
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-51)  await call_agent_async(query = "Weather in London please.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-52)              runner=runner_claude,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-53)              user_id=USER_ID_CLAUDE,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-54)              session_id=SESSION_ID_CLAUDE)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-55)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-56)  # --- OR ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-57)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-58)  # Uncomment the following lines if running as a standard Python script (.py file):
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-59)  # import asyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-60)  # if __name__ == "__main__":
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-61)  #   try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-62)  #     asyncio.run(call_agent_async(query = "Weather in London please.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-63)  #           runner=runner_claude,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-64)  #            user_id=USER_ID_CLAUDE,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-65)  #            session_id=SESSION_ID_CLAUDE)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-66)  #   except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-67)  #     print(f"An error occurred: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-68)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-69)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-70)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-11-71)  print(f"❌ Could not create or run Claude agent '{MODEL_CLAUDE_SONNET}'. Check API Key and model name. Error: {e}")

```

Observe the output carefully from both code blocks. You should see:
  1. Each agent (`weather_agent_gpt`, `weather_agent_claude`) is created successfully (if API keys are valid).
  2. A dedicated session and runner are set up for each.
  3. Each agent correctly identifies the need to use the `get_weather` tool when processing the query (you'll see the `--- Tool: get_weather called... ---` log).
  4. The _underlying tool logic_ remains identical, always returning our mock data.
  5. However, the **final textual response** generated by each agent might differ slightly in phrasing, tone, or formatting. This is because the instruction prompt is interpreted and executed by different LLMs (GPT-4o vs. Claude Sonnet).


This step demonstrates the power and flexibility ADK + LiteLLM provide. You can easily experiment with and deploy agents using various LLMs while keeping your core application logic (tools, fundamental agent structure) consistent.
In the next step, we'll move beyond a single agent and build a small team where agents can delegate tasks to each other!
## Step 3: Building an Agent Team - Delegation for Greetings & Farewells[¶](https://google.github.io/adk-docs/tutorials/agent-team/#step-3-building-an-agent-team-delegation-for-greetings-farewells "Permanent link")
In Steps 1 and 2, we built and experimented with a single agent focused solely on weather lookups. While effective for its specific task, real-world applications often involve handling a wider variety of user interactions. We _could_ keep adding more tools and complex instructions to our single weather agent, but this can quickly become unmanageable and less efficient.
A more robust approach is to build an **Agent Team**. This involves:
  1. Creating multiple, **specialized agents** , each designed for a specific capability (e.g., one for weather, one for greetings, one for calculations).
  2. Designating a **root agent** (or orchestrator) that receives the initial user request.
  3. Enabling the root agent to **delegate** the request to the most appropriate specialized sub-agent based on the user's intent.


**Why build an Agent Team?**
  * **Modularity:** Easier to develop, test, and maintain individual agents.
  * **Specialization:** Each agent can be fine-tuned (instructions, model choice) for its specific task.
  * **Scalability:** Simpler to add new capabilities by adding new agents.
  * **Efficiency:** Allows using potentially simpler/cheaper models for simpler tasks (like greetings).


**In this step, we will:**
  1. Define simple tools for handling greetings (`say_hello`) and farewells (`say_goodbye`).
  2. Create two new specialized sub-agents: `greeting_agent` and `farewell_agent`.
  3. Update our main weather agent (`weather_agent_v2`) to act as the **root agent**.
  4. Configure the root agent with its sub-agents, enabling **automatic delegation**.
  5. Test the delegation flow by sending different types of requests to the root agent.


**1. Define Tools for Sub-Agents**
First, let's create the simple Python functions that will serve as tools for our new specialist agents. Remember, clear docstrings are vital for the agents that will use them.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-1)# @title Define Tools for Greeting and Farewell Agents
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-2)fromtypingimport Optional # Make sure to import Optional
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-4)# Ensure 'get_weather' from Step 1 is available if running this step independently.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-5)# def get_weather(city: str) -> dict: ... (from Step 1)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-6)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-7)defsay_hello(name: Optional[str] = None) -> str:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-8)"""Provides a simple greeting. If a name is provided, it will be used.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-10)  Args:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-11)    name (str, optional): The name of the person to greet. Defaults to a generic greeting if not provided.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-12)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-13)  Returns:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-14)    str: A friendly greeting message.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-15)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-16)  if name:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-17)    greeting = f"Hello, {name}!"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-18)    print(f"--- Tool: say_hello called with name: {name} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-19)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-20)    greeting = "Hello there!" # Default greeting if name is None or not explicitly passed
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-21)    print(f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-22)  return greeting
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-23)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-24)defsay_goodbye() -> str:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-25)"""Provides a simple farewell message to conclude the conversation."""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-26)  print(f"--- Tool: say_goodbye called ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-27)  return "Goodbye! Have a great day."
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-28)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-29)print("Greeting and Farewell tools defined.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-30)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-31)# Optional self-test
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-32)print(say_hello("Alice"))
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-33)print(say_hello()) # Test with no argument (should use default "Hello there!")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-12-34)print(say_hello(name=None)) # Test with name explicitly as None (should use default "Hello there!")

```

**2. Define the Sub-Agents (Greeting & Farewell)**
Now, create the `Agent` instances for our specialists. Notice their highly focused `instruction` and, critically, their clear `description`. The `description` is the primary information the _root agent_ uses to decide _when_ to delegate to these sub-agents.
**Best Practice:** Sub-agent `description` fields should accurately and concisely summarize their specific capability. This is crucial for effective automatic delegation.
**Best Practice:** Sub-agent `instruction` fields should be tailored to their limited scope, telling them exactly what to do and _what not_ to do (e.g., "Your _only_ task is...").
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-1)# @title Define Greeting and Farewell Sub-Agents
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-3)# If you want to use models other than Gemini, Ensure LiteLlm is imported and API keys are set (from Step 0/2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-4)# from google.adk.models.lite_llm import LiteLlm
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-5)# MODEL_GPT_4O, MODEL_CLAUDE_SONNET etc. should be defined
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-6)# Or else, continue to use: model = MODEL_GEMINI_2_0_FLASH
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-7)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-8)# --- Greeting Agent ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-9)greeting_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-10)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-11)  greeting_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-12)    # Using a potentially different/cheaper model for a simple task
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-13)    model = MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-14)    # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-15)    name="greeting_agent",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-16)    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-17)          "Use the 'say_hello' tool to generate the greeting. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-18)          "If the user provides their name, make sure to pass it to the tool. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-19)          "Do not engage in any other conversation or tasks.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-20)    description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-21)    tools=[say_hello],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-22)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-23)  print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-24)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-25)  print(f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-26)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-27)# --- Farewell Agent ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-28)farewell_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-29)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-30)  farewell_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-31)    # Can use the same or a different model
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-32)    model = MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-33)    # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-34)    name="farewell_agent",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-35)    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-36)          "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-37)          "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-38)          "Do not perform any other actions.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-39)    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-40)    tools=[say_goodbye],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-41)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-42)  print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-43)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-13-44)  print(f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}")

```

**3. Define the Root Agent (Weather Agent v2) with Sub-Agents**
Now, we upgrade our `weather_agent`. The key changes are:
  * Adding the `sub_agents` parameter: We pass a list containing the `greeting_agent` and `farewell_agent` instances we just created.
  * Updating the `instruction`: We explicitly tell the root agent _about_ its sub-agents and _when_ it should delegate tasks to them.


**Key Concept: Automatic Delegation (Auto Flow)** By providing the `sub_agents` list, ADK enables automatic delegation. When the root agent receives a user query, its LLM considers not only its own instructions and tools but also the `description` of each sub-agent. If the LLM determines that a query aligns better with a sub-agent's described capability (e.g., "Handles simple greetings"), it will automatically generate a special internal action to _transfer control_ to that sub-agent for that turn. The sub-agent then processes the query using its own model, instructions, and tools.
**Best Practice:** Ensure the root agent's instructions clearly guide its delegation decisions. Mention the sub-agents by name and describe the conditions under which delegation should occur.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-1)# @title Define the Root Agent with Sub-Agents
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-3)# Ensure sub-agents were created successfully before defining the root agent.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-4)# Also ensure the original 'get_weather' tool is defined.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-5)root_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-6)runner_root = None # Initialize runner
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-7)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-8)if greeting_agent and farewell_agent and 'get_weather' in globals():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-9)  # Let's use a capable Gemini model for the root agent to handle orchestration
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-10)  root_agent_model = MODEL_GEMINI_2_0_FLASH
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-11)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-12)  weather_agent_team = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-13)    name="weather_agent_v2", # Give it a new version name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-14)    model=root_agent_model,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-15)    description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-16)    instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-17)          "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-18)          "You have specialized sub-agents: "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-19)          "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-20)          "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-21)          "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-22)          "If it's a weather request, handle it yourself using 'get_weather'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-23)          "For anything else, respond appropriately or state you cannot handle it.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-24)    tools=[get_weather], # Root agent still needs the weather tool for its core task
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-25)    # Key change: Link the sub-agents here!
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-26)    sub_agents=[greeting_agent, farewell_agent]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-27)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-28)  print(f"✅ Root Agent '{weather_agent_team.name}' created using model '{root_agent_model}' with sub-agents: {[sa.nameforsainweather_agent_team.sub_agents]}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-29)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-30)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-31)  print("❌ Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-32)  if not greeting_agent: print(" - Greeting Agent is missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-33)  if not farewell_agent: print(" - Farewell Agent is missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-14-34)  if 'get_weather' not in globals(): print(" - get_weather function is missing.")

```

**4. Interact with the Agent Team**
Now that we've defined our root agent (`weather_agent_team` - _Note: Ensure this variable name matches the one defined in the previous code block, likely`# @title Define the Root Agent with Sub-Agents` , which might have named it `root_agent`_) with its specialized sub-agents, let's test the delegation mechanism.
The following code block will:
  1. Define an `async` function `run_team_conversation`.
  2. Inside this function, create a _new, dedicated_ `InMemorySessionService` and a specific session (`session_001_agent_team`) just for this test run. This isolates the conversation history for testing the team dynamics.
  3. Create a `Runner` (`runner_agent_team`) configured to use our `weather_agent_team` (the root agent) and the dedicated session service.
  4. Use our updated `call_agent_async` function to send different types of queries (greeting, weather request, farewell) to the `runner_agent_team`. We explicitly pass the runner, user ID, and session ID for this specific test.
  5. Immediately execute the `run_team_conversation` function.


We expect the following flow:
  1. The "Hello there!" query goes to `runner_agent_team`.
  2. The root agent (`weather_agent_team`) receives it and, based on its instructions and the `greeting_agent`'s description, delegates the task.
  3. `greeting_agent` handles the query, calls its `say_hello` tool, and generates the response.
  4. The "What is the weather in New York?" query is _not_ delegated and is handled directly by the root agent using its `get_weather` tool.
  5. The "Thanks, bye!" query is delegated to the `farewell_agent`, which uses its `say_goodbye` tool.


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-1)# @title Interact with the Agent Team
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-2)importasyncio # Ensure asyncio is imported
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-4)# Ensure the root agent (e.g., 'weather_agent_team' or 'root_agent' from the previous cell) is defined.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-5)# Ensure the call_agent_async function is defined.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-6)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-7)# Check if the root agent variable exists before defining the conversation function
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-8)root_agent_var_name = 'root_agent' # Default name from Step 3 guide
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-9)if 'weather_agent_team' in globals(): # Check if user used this name instead
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-10)  root_agent_var_name = 'weather_agent_team'
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-11)elif 'root_agent' not in globals():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-12)  print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-13)  # Assign a dummy value to prevent NameError later if the code block runs anyway
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-14)  root_agent = None # Or set a flag to prevent execution
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-15)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-16)# Only define and run if the root agent exists
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-17)if root_agent_var_name in globals() and globals()[root_agent_var_name]:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-18)  # Define the main async function for the conversation logic.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-19)  # The 'await' keywords INSIDE this function are necessary for async operations.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-20)  async defrun_team_conversation():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-21)    print("\n--- Testing Agent Team Delegation ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-22)    session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-23)    APP_NAME = "weather_tutorial_agent_team"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-24)    USER_ID = "user_1_agent_team"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-25)    SESSION_ID = "session_001_agent_team"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-26)    session = await session_service.create_session(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-27)      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-28)    )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-29)    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-30)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-31)    actual_root_agent = globals()[root_agent_var_name]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-32)    runner_agent_team = Runner( # Or use InMemoryRunner
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-33)      agent=actual_root_agent,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-34)      app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-35)      session_service=session_service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-36)    )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-37)    print(f"Runner created for agent '{actual_root_agent.name}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-38)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-39)    # --- Interactions using await (correct within async def) ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-40)    await call_agent_async(query = "Hello there!",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-41)                runner=runner_agent_team,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-42)                user_id=USER_ID,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-43)                session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-44)    await call_agent_async(query = "What is the weather in New York?",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-45)                runner=runner_agent_team,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-46)                user_id=USER_ID,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-47)                session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-48)    await call_agent_async(query = "Thanks, bye!",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-49)                runner=runner_agent_team,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-50)                user_id=USER_ID,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-51)                session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-52)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-53)  # --- Execute the `run_team_conversation` async function ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-54)  # Choose ONE of the methods below based on your environment.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-55)  # Note: This may require API keys for the models used!
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-56)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-57)  # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-58)  # If your environment supports top-level await (like Colab/Jupyter notebooks),
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-59)  # it means an event loop is already running, so you can directly await the function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-60)  print("Attempting execution using 'await' (default for notebooks)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-61)  await run_team_conversation()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-62)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-63)  # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-64)  # If running this code as a standard Python script from your terminal,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-65)  # the script context is synchronous. `asyncio.run()` is needed to
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-66)  # create and manage an event loop to execute your async function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-67)  # To use this method:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-68)  # 1. Comment out the `await run_team_conversation()` line above.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-69)  # 2. Uncomment the following block:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-70)"""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-71)  import asyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-72)  if __name__ == "__main__": # Ensures this runs only when script is executed directly
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-73)    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-74)    try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-75)      # This creates an event loop, runs your async function, and closes the loop.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-76)      asyncio.run(run_team_conversation())
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-77)    except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-78)      print(f"An error occurred: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-79)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-80)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-81)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-82)  # This message prints if the root agent variable wasn't found earlier
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-15-83)  print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")

```

Look closely at the output logs, especially the `--- Tool: ... called ---` messages. You should observe:
  * For "Hello there!", the `say_hello` tool was called (indicating `greeting_agent` handled it).
  * For "What is the weather in New York?", the `get_weather` tool was called (indicating the root agent handled it).
  * For "Thanks, bye!", the `say_goodbye` tool was called (indicating `farewell_agent` handled it).


This confirms successful **automatic delegation**! The root agent, guided by its instructions and the `description`s of its `sub_agents`, correctly routed user requests to the appropriate specialist agent within the team.
You've now structured your application with multiple collaborating agents. This modular design is fundamental for building more complex and capable agent systems. In the next step, we'll give our agents the ability to remember information across turns using session state.
## Step 4: Adding Memory and Personalization with Session State[¶](https://google.github.io/adk-docs/tutorials/agent-team/#step-4-adding-memory-and-personalization-with-session-state "Permanent link")
So far, our agent team can handle different tasks through delegation, but each interaction starts fresh – the agents have no memory of past conversations or user preferences within a session. To create more sophisticated and context-aware experiences, agents need **memory**. ADK provides this through **Session State**.
**What is Session State?**
  * It's a Python dictionary (`session.state`) tied to a specific user session (identified by `APP_NAME`, `USER_ID`, `SESSION_ID`).
  * It persists information _across multiple conversational turns_ within that session.
  * Agents and Tools can read from and write to this state, allowing them to remember details, adapt behavior, and personalize responses.


**How Agents Interact with State:**
  1. **`ToolContext`(Primary Method):** Tools can accept a `ToolContext` object (automatically provided by ADK if declared as the last argument). This object gives direct access to the session state via `tool_context.state`, allowing tools to read preferences or save results _during_ execution.
  2. **`output_key`(Auto-Save Agent Response):** An `Agent` can be configured with an `output_key="your_key"`. ADK will then automatically save the agent's final textual response for a turn into `session.state["your_key"]`.


**In this step, we will enhance our Weather Bot team by:**
  1. Using a **new** `InMemorySessionService` to demonstrate state in isolation.
  2. Initializing session state with a user preference for `temperature_unit`.
  3. Creating a state-aware version of the weather tool (`get_weather_stateful`) that reads this preference via `ToolContext` and adjusts its output format (Celsius/Fahrenheit).
  4. Updating the root agent to use this stateful tool and configuring it with an `output_key` to automatically save its final weather report to the session state.
  5. Running a conversation to observe how the initial state affects the tool, how manual state changes alter subsequent behavior, and how `output_key` persists the agent's response.


**1. Initialize New Session Service and State**
To clearly demonstrate state management without interference from prior steps, we'll instantiate a new `InMemorySessionService`. We'll also create a session with an initial state defining the user's preferred temperature unit.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-1)# @title 1. Initialize New Session Service and State
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-3)# Import necessary session components
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-4)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-5)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-6)# Create a NEW session service instance for this state demonstration
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-7)session_service_stateful = InMemorySessionService()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-8)print("✅ New InMemorySessionService created for state demonstration.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-10)# Define a NEW session ID for this part of the tutorial
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-11)SESSION_ID_STATEFUL = "session_state_demo_001"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-12)USER_ID_STATEFUL = "user_state_demo"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-13)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-14)# Define initial state data - user prefers Celsius initially
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-15)initial_state = {
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-16)  "user_preference_temperature_unit": "Celsius"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-17)}
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-18)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-19)# Create the session, providing the initial state
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-20)session_stateful = await session_service_stateful.create_session(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-21)  app_name=APP_NAME, # Use the consistent app name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-22)  user_id=USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-23)  session_id=SESSION_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-24)  state=initial_state # <<< Initialize state during creation
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-25))
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-26)print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-27)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-28)# Verify the initial state was set correctly
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-29)retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-30)                             user_id=USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-31)                             session_id = SESSION_ID_STATEFUL)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-32)print("\n--- Initial Session State ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-33)if retrieved_session:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-34)  print(retrieved_session.state)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-35)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-16-36)  print("Error: Could not retrieve session.")

```

**2. Create State-Aware Weather Tool (`get_weather_stateful`)**
Now, we create a new version of the weather tool. Its key feature is accepting `tool_context: ToolContext` which allows it to access `tool_context.state`. It will read the `user_preference_temperature_unit` and format the temperature accordingly.
  * **Key Concept:`ToolContext`** This object is the bridge allowing your tool logic to interact with the session's context, including reading and writing state variables. ADK injects it automatically if defined as the last parameter of your tool function.
  * **Best Practice:** When reading from state, use `dictionary.get('key', default_value)` to handle cases where the key might not exist yet, ensuring your tool doesn't crash.


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-1)fromgoogle.adk.tools.tool_contextimport ToolContext
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-3)defget_weather_stateful(city: str, tool_context: ToolContext) -> dict:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-4)"""Retrieves weather, converts temp unit based on session state."""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-5)  print(f"--- Tool: get_weather_stateful called for {city} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-6)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-7)  # --- Read preference from state ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-8)  preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-9)  print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-10)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-11)  city_normalized = city.lower().replace(" ", "")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-12)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-13)  # Mock weather data (always stored in Celsius internally)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-14)  mock_weather_db = {
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-15)    "newyork": {"temp_c": 25, "condition": "sunny"},
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-16)    "london": {"temp_c": 15, "condition": "cloudy"},
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-17)    "tokyo": {"temp_c": 18, "condition": "light rain"},
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-18)  }
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-19)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-20)  if city_normalized in mock_weather_db:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-21)    data = mock_weather_db[city_normalized]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-22)    temp_c = data["temp_c"]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-23)    condition = data["condition"]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-24)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-25)    # Format temperature based on state preference
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-26)    if preferred_unit == "Fahrenheit":
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-27)      temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-28)      temp_unit = "°F"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-29)    else: # Default to Celsius
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-30)      temp_value = temp_c
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-31)      temp_unit = "°C"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-32)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-33)    report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-34)    result = {"status": "success", "report": report}
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-35)    print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-36)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-37)    # Example of writing back to state (optional for this tool)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-38)    tool_context.state["last_city_checked_stateful"] = city
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-39)    print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-40)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-41)    return result
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-42)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-43)    # Handle city not found
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-44)    error_msg = f"Sorry, I don't have weather information for '{city}'."
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-45)    print(f"--- Tool: City '{city}' not found. ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-46)    return {"status": "error", "error_message": error_msg}
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-47)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-17-48)print("✅ State-aware 'get_weather_stateful' tool defined.")

```

**3. Redefine Sub-Agents and Update Root Agent**
To ensure this step is self-contained and builds correctly, we first redefine the `greeting_agent` and `farewell_agent` exactly as they were in Step 3. Then, we define our new root agent (`weather_agent_v4_stateful`):
  * It uses the new `get_weather_stateful` tool.
  * It includes the greeting and farewell sub-agents for delegation.
  * **Crucially** , it sets `output_key="last_weather_report"` which automatically saves its final weather response to the session state.


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-1)# @title 3. Redefine Sub-Agents and Update Root Agent with output_key
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-3)# Ensure necessary imports: Agent, LiteLlm, Runner
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-4)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-5)fromgoogle.adk.models.lite_llmimport LiteLlm
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-6)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-7)# Ensure tools 'say_hello', 'say_goodbye' are defined (from Step 3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-8)# Ensure model constants MODEL_GPT_4O, MODEL_GEMINI_2_0_FLASH etc. are defined
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-10)# --- Redefine Greeting Agent (from Step 3) ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-11)greeting_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-12)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-13)  greeting_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-14)    model=MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-15)    name="greeting_agent",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-16)    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-17)    description="Handles simple greetings and hellos using the 'say_hello' tool.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-18)    tools=[say_hello],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-19)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-20)  print(f"✅ Agent '{greeting_agent.name}' redefined.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-21)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-22)  print(f"❌ Could not redefine Greeting agent. Error: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-23)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-24)# --- Redefine Farewell Agent (from Step 3) ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-25)farewell_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-26)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-27)  farewell_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-28)    model=MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-29)    name="farewell_agent",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-30)    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-31)    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-32)    tools=[say_goodbye],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-33)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-34)  print(f"✅ Agent '{farewell_agent.name}' redefined.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-35)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-36)  print(f"❌ Could not redefine Farewell agent. Error: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-37)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-38)# --- Define the Updated Root Agent ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-39)root_agent_stateful = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-40)runner_root_stateful = None # Initialize runner
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-41)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-42)# Check prerequisites before creating the root agent
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-43)if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-44)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-45)  root_agent_model = MODEL_GEMINI_2_0_FLASH # Choose orchestration model
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-46)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-47)  root_agent_stateful = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-48)    name="weather_agent_v4_stateful", # New version name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-49)    model=root_agent_model,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-50)    description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-51)    instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-52)          "The tool will format the temperature based on user preference stored in state. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-53)          "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-54)          "Handle only weather requests, greetings, and farewells.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-55)    tools=[get_weather_stateful], # Use the state-aware tool
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-56)    sub_agents=[greeting_agent, farewell_agent], # Include sub-agents
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-57)    output_key="last_weather_report" # <<< Auto-save agent's final weather response
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-58)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-59)  print(f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-60)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-61)  # --- Create Runner for this Root Agent & NEW Session Service ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-62)  runner_root_stateful = Runner(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-63)    agent=root_agent_stateful,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-64)    app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-65)    session_service=session_service_stateful # Use the NEW stateful session service
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-66)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-67)  print(f"✅ Runner created for stateful root agent '{runner_root_stateful.agent.name}' using stateful session service.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-68)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-69)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-70)  print("❌ Cannot create stateful root agent. Prerequisites missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-71)  if not greeting_agent: print(" - greeting_agent definition missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-72)  if not farewell_agent: print(" - farewell_agent definition missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-18-73)  if 'get_weather_stateful' not in globals(): print(" - get_weather_stateful tool missing.")

```

**4. Interact and Test State Flow**
Now, let's execute a conversation designed to test the state interactions using the `runner_root_stateful` (associated with our stateful agent and the `session_service_stateful`). We'll use the `call_agent_async` function defined earlier, ensuring we pass the correct runner, user ID (`USER_ID_STATEFUL`), and session ID (`SESSION_ID_STATEFUL`).
The conversation flow will be:
  1. **Check weather (London):** The `get_weather_stateful` tool should read the initial "Celsius" preference from the session state initialized in Section 1. The root agent's final response (the weather report in Celsius) should get saved to `state['last_weather_report']` via the `output_key` configuration.
  2. **Manually update state:** We will _directly modify_ the state stored within the `InMemorySessionService` instance (`session_service_stateful`).
     * **Why direct modification?** The `session_service.get_session()` method returns a _copy_ of the session. Modifying that copy wouldn't affect the state used in subsequent agent runs. For this testing scenario with `InMemorySessionService`, we access the internal `sessions` dictionary to change the _actual_ stored state value for `user_preference_temperature_unit` to "Fahrenheit". _Note: In real applications, state changes are typically triggered by tools or agent logic returning`EventActions(state_delta=...)` , not direct manual updates._
  3. **Check weather again (New York):** The `get_weather_stateful` tool should now read the updated "Fahrenheit" preference from the state and convert the temperature accordingly. The root agent's _new_ response (weather in Fahrenheit) will overwrite the previous value in `state['last_weather_report']` due to the `output_key`.
  4. **Greet the agent:** Verify that delegation to the `greeting_agent` still works correctly alongside the stateful operations. This interaction will become the _last_ response saved by `output_key` in this specific sequence.
  5. **Inspect final state:** After the conversation, we retrieve the session one last time (getting a copy) and print its state to confirm the `user_preference_temperature_unit` is indeed "Fahrenheit", observe the final value saved by `output_key` (which will be the greeting in this run), and see the `last_city_checked_stateful` value written by the tool.


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-1)# @title 4. Interact to Test State Flow and output_key
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-2)importasyncio # Ensure asyncio is imported
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-4)# Ensure the stateful runner (runner_root_stateful) is available from the previous cell
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-5)# Ensure call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME are defined
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-6)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-7)if 'runner_root_stateful' in globals() and runner_root_stateful:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-8)  # Define the main async function for the stateful conversation logic.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-9)  # The 'await' keywords INSIDE this function are necessary for async operations.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-10)  async defrun_stateful_conversation():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-11)    print("\n--- Testing State: Temp Unit Conversion & output_key ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-12)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-13)    # 1. Check weather (Uses initial state: Celsius)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-14)    print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-15)    await call_agent_async(query= "What's the weather in London?",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-16)                runner=runner_root_stateful,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-17)                user_id=USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-18)                session_id=SESSION_ID_STATEFUL
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-19)               )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-20)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-21)    # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-22)    print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-23)    try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-24)      # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-25)      # NOTE: In production with persistent services (Database, VertexAI), you would
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-26)      # typically update state via agent actions or specific service APIs if available,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-27)      # not by direct manipulation of internal storage.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-28)      stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-29)      stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-30)      # Optional: You might want to update the timestamp as well if any logic depends on it
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-31)      # import time
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-32)      # stored_session.last_update_time = time.time()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-33)      print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit','Not Set')} ---") # Added .get for safety
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-34)    except KeyError:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-35)      print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-36)    except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-37)       print(f"--- Error updating internal session state: {e} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-38)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-39)    # 3. Check weather again (Tool should now use Fahrenheit)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-40)    # This will also update 'last_weather_report' via output_key
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-41)    print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-42)    await call_agent_async(query= "Tell me the weather in New York.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-43)                runner=runner_root_stateful,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-44)                user_id=USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-45)                session_id=SESSION_ID_STATEFUL
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-46)               )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-47)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-48)    # 4. Test basic delegation (should still work)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-49)    # This will update 'last_weather_report' again, overwriting the NY weather report
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-50)    print("\n--- Turn 3: Sending a greeting ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-51)    await call_agent_async(query= "Hi!",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-52)                runner=runner_root_stateful,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-53)                user_id=USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-54)                session_id=SESSION_ID_STATEFUL
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-55)               )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-56)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-57)  # --- Execute the `run_stateful_conversation` async function ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-58)  # Choose ONE of the methods below based on your environment.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-59)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-60)  # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-61)  # If your environment supports top-level await (like Colab/Jupyter notebooks),
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-62)  # it means an event loop is already running, so you can directly await the function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-63)  print("Attempting execution using 'await' (default for notebooks)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-64)  await run_stateful_conversation()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-65)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-66)  # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-67)  # If running this code as a standard Python script from your terminal,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-68)  # the script context is synchronous. `asyncio.run()` is needed to
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-69)  # create and manage an event loop to execute your async function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-70)  # To use this method:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-71)  # 1. Comment out the `await run_stateful_conversation()` line above.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-72)  # 2. Uncomment the following block:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-73)"""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-74)  import asyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-75)  if __name__ == "__main__": # Ensures this runs only when script is executed directly
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-76)    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-77)    try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-78)      # This creates an event loop, runs your async function, and closes the loop.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-79)      asyncio.run(run_stateful_conversation())
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-80)    except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-81)      print(f"An error occurred: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-82)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-83)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-84)  # --- Inspect final session state after the conversation ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-85)  # This block runs after either execution method completes.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-86)  print("\n--- Inspecting Final Session State ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-87)  final_session = await session_service_stateful.get_session(app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-88)                             user_id= USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-89)                             session_id=SESSION_ID_STATEFUL)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-90)  if final_session:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-91)    # Use .get() for safer access to potentially missing keys
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-92)    print(f"Final Preference: {final_session.state.get('user_preference_temperature_unit','Not Set')}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-93)    print(f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report','Not Set')}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-94)    print(f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful','Not Set')}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-95)    # Print full state for detailed view
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-96)    # print(f"Full State Dict: {final_session.state}") # For detailed view
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-97)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-98)    print("\n❌ Error: Could not retrieve final session state.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-99)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-100)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-19-101)  print("\n⚠️ Skipping state test conversation. Stateful root agent runner ('runner_root_stateful') is not available.")

```

By reviewing the conversation flow and the final session state printout, you can confirm:
  * **State Read:** The weather tool (`get_weather_stateful`) correctly read `user_preference_temperature_unit` from state, initially using "Celsius" for London.
  * **State Update:** The direct modification successfully changed the stored preference to "Fahrenheit".
  * **State Read (Updated):** The tool subsequently read "Fahrenheit" when asked for New York's weather and performed the conversion.
  * **Tool State Write:** The tool successfully wrote the `last_city_checked_stateful` ("New York" after the second weather check) into the state via `tool_context.state`.
  * **Delegation:** The delegation to the `greeting_agent` for "Hi!" functioned correctly even after state modifications.
  * **`output_key`:** The `output_key="last_weather_report"` successfully saved the root agent's _final_ response for _each turn_ where the root agent was the one ultimately responding. In this sequence, the last response was the greeting ("Hello, there!"), so that overwrote the weather report in the state key.
  * **Final State:** The final check confirms the preference persisted as "Fahrenheit".


You've now successfully integrated session state to personalize agent behavior using `ToolContext`, manually manipulated state for testing `InMemorySessionService`, and observed how `output_key` provides a simple mechanism for saving the agent's last response to state. This foundational understanding of state management is key as we proceed to implement safety guardrails using callbacks in the next steps.
## Step 5: Adding Safety - Input Guardrail with `before_model_callback`[¶](https://google.github.io/adk-docs/tutorials/agent-team/#step-5-adding-safety-input-guardrail-with-before_model_callback "Permanent link")
Our agent team is becoming more capable, remembering preferences and using tools effectively. However, in real-world scenarios, we often need safety mechanisms to control the agent's behavior _before_ potentially problematic requests even reach the core Large Language Model (LLM).
ADK provides **Callbacks** – functions that allow you to hook into specific points in the agent's execution lifecycle. The `before_model_callback` is particularly useful for input safety.
**What is`before_model_callback`?**
  * It's a Python function you define that ADK executes _just before_ an agent sends its compiled request (including conversation history, instructions, and the latest user message) to the underlying LLM.
  * **Purpose:** Inspect the request, modify it if necessary, or block it entirely based on predefined rules.


**Common Use Cases:**
  * **Input Validation/Filtering:** Check if user input meets criteria or contains disallowed content (like PII or keywords).
  * **Guardrails:** Prevent harmful, off-topic, or policy-violating requests from being processed by the LLM.
  * **Dynamic Prompt Modification:** Add timely information (e.g., from session state) to the LLM request context just before sending.


**How it Works:**
  1. Define a function accepting `callback_context: CallbackContext` and `llm_request: LlmRequest`.
     * `callback_context`: Provides access to agent info, session state (`callback_context.state`), etc.
     * `llm_request`: Contains the full payload intended for the LLM (`contents`, `config`).
  2. Inside the function:
     * **Inspect:** Examine `llm_request.contents` (especially the last user message).
     * **Modify (Use Caution):** You _can_ change parts of `llm_request`.
     * **Block (Guardrail):** Return an `LlmResponse` object. ADK will send this response back immediately, _skipping_ the LLM call for that turn.
     * **Allow:** Return `None`. ADK proceeds to call the LLM with the (potentially modified) request.


**In this step, we will:**
  1. Define a `before_model_callback` function (`block_keyword_guardrail`) that checks the user's input for a specific keyword ("BLOCK").
  2. Update our stateful root agent (`weather_agent_v4_stateful` from Step 4) to use this callback.
  3. Create a new runner associated with this updated agent but using the _same stateful session service_ to maintain state continuity.
  4. Test the guardrail by sending both normal and keyword-containing requests.


**1. Define the Guardrail Callback Function**
This function will inspect the last user message within the `llm_request` content. If it finds "BLOCK" (case-insensitive), it constructs and returns an `LlmResponse` to block the flow; otherwise, it returns `None`.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-1)# @title 1. Define the before_model_callback Guardrail
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-3)# Ensure necessary imports are available
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-4)fromgoogle.adk.agents.callback_contextimport CallbackContext
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-5)fromgoogle.adk.models.llm_requestimport LlmRequest
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-6)fromgoogle.adk.models.llm_responseimport LlmResponse
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-7)fromgoogle.genaiimport types # For creating response content
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-8)fromtypingimport Optional
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-9)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-10)defblock_keyword_guardrail(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-11)  callback_context: CallbackContext, llm_request: LlmRequest
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-12)) -> Optional[LlmResponse]:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-13)"""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-14)  Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-15)  and returns a predefined LlmResponse. Otherwise, returns None to proceed.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-16)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-17)  agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-18)  print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-19)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-20)  # Extract the text from the latest user message in the request history
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-21)  last_user_message_text = ""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-22)  if llm_request.contents:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-23)    # Find the most recent message with role 'user'
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-24)    for content in reversed(llm_request.contents):
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-25)      if content.role == 'user' and content.parts:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-26)        # Assuming text is in the first part for simplicity
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-27)        if content.parts[0].text:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-28)          last_user_message_text = content.parts[0].text
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-29)          break # Found the last user message text
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-30)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-31)  print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # Log first 100 chars
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-32)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-33)  # --- Guardrail Logic ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-34)  keyword_to_block = "BLOCK"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-35)  if REDACTED.upper(): # Case-insensitive check
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-36)    print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-37)    # Optionally, set a flag in state to record the block event
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-38)    callback_context.state["guardrail_block_keyword_triggered"] = True
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-39)    print(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-40)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-41)    # Construct and return an LlmResponse to stop the flow and send this back instead
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-42)    return LlmResponse(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-43)      content=types.Content(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-44)        role="model", # Mimic a response from the agent's perspective
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-45)        parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-46)      )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-47)      # Note: You could also set an error_message field here if needed
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-48)    )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-49)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-50)    # Keyword not found, allow the request to proceed to the LLM
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-51)    print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-52)    return None # Returning None signals ADK to continue normally
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-53)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-20-54)print("✅ block_keyword_guardrail function defined.")

```

**2. Update Root Agent to Use the Callback**
We redefine the root agent, adding the `before_model_callback` parameter and pointing it to our new guardrail function. We'll give it a new version name for clarity.
_Important:_ We need to redefine the sub-agents (`greeting_agent`, `farewell_agent`) and the stateful tool (`get_weather_stateful`) within this context if they are not already available from previous steps, ensuring the root agent definition has access to all its components.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-1)# @title 2. Update Root Agent with before_model_callback
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-4)# --- Redefine Sub-Agents (Ensures they exist in this context) ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-5)greeting_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-6)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-7)  # Use a defined model constant
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-8)  greeting_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-9)    model=MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-10)    name="greeting_agent", # Keep original name for consistency
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-11)    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-12)    description="Handles simple greetings and hellos using the 'say_hello' tool.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-13)    tools=[say_hello],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-14)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-15)  print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-16)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-17)  print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-18)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-19)farewell_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-20)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-21)  # Use a defined model constant
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-22)  farewell_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-23)    model=MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-24)    name="farewell_agent", # Keep original name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-25)    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-26)    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-27)    tools=[say_goodbye],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-28)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-29)  print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-30)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-31)  print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-32)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-33)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-34)# --- Define the Root Agent with the Callback ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-35)root_agent_model_guardrail = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-36)runner_root_model_guardrail = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-37)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-38)# Check all components before proceeding
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-39)if greeting_agent and farewell_agent and 'get_weather_stateful' in globals() and 'block_keyword_guardrail' in globals():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-40)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-41)  # Use a defined model constant
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-42)  root_agent_model = MODEL_GEMINI_2_0_FLASH
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-43)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-44)  root_agent_model_guardrail = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-45)    name="weather_agent_v5_model_guardrail", # New version name for clarity
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-46)    model=root_agent_model,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-47)    description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-48)    instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-49)          "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-50)          "Handle only weather requests, greetings, and farewells.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-51)    tools=[get_weather],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-52)    sub_agents=[greeting_agent, farewell_agent], # Reference the redefined sub-agents
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-53)    output_key="last_weather_report", # Keep output_key from Step 4
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-54)    before_model_callback=block_keyword_guardrail # <<< Assign the guardrail callback
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-55)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-56)  print(f"✅ Root Agent '{root_agent_model_guardrail.name}' created with before_model_callback.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-57)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-58)  # --- Create Runner for this Agent, Using SAME Stateful Session Service ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-59)  # Ensure session_service_stateful exists from Step 4
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-60)  if 'session_service_stateful' in globals():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-61)    runner_root_model_guardrail = Runner(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-62)      agent=root_agent_model_guardrail,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-63)      app_name=APP_NAME, # Use consistent APP_NAME
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-64)      session_service=session_service_stateful # <<< Use the service from Step 4
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-65)    )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-66)    print(f"✅ Runner created for guardrail agent '{runner_root_model_guardrail.agent.name}', using stateful session service.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-67)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-68)    print("❌ Cannot create runner. 'session_service_stateful' from Step 4 is missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-69)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-70)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-71)  print("❌ Cannot create root agent with model guardrail. One or more prerequisites are missing or failed initialization:")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-72)  if not greeting_agent: print("  - Greeting Agent")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-73)  if not farewell_agent: print("  - Farewell Agent")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-74)  if 'get_weather_stateful' not in globals(): print("  - 'get_weather_stateful' tool")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-21-75)  if 'block_REDACTED' callback")

```

**3. Interact to Test the Guardrail**
Let's test the guardrail's behavior. We'll use the _same session_ (`SESSION_ID_STATEFUL`) as in Step 4 to show that state persists across these changes.
  1. Send a normal weather request (should pass the guardrail and execute).
  2. Send a request containing "BLOCK" (should be intercepted by the callback).
  3. Send a greeting (should pass the root agent's guardrail, be delegated, and execute normally).


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-1)# @title 3. Interact to Test the Model Input Guardrail
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-2)importasyncio # Ensure asyncio is imported
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-4)# Ensure the runner for the guardrail agent is available
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-5)if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-6)  # Define the main async function for the guardrail test conversation.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-7)  # The 'await' keywords INSIDE this function are necessary for async operations.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-8)  async defrun_guardrail_test_conversation():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-9)    print("\n--- Testing Model Input Guardrail ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-10)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-11)    # Use the runner for the agent with the callback and the existing stateful session ID
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-12)    # Define a helper lambda for cleaner interaction calls
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-13)    interaction_func = lambda query: call_agent_async(query,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-14)                             runner_root_model_guardrail,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-15)                             USER_ID_STATEFUL, # Use existing user ID
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-16)                             SESSION_ID_STATEFUL # Use existing session ID
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-17)                            )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-18)    # 1. Normal request (Callback allows, should use Fahrenheit from previous state change)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-19)    print("--- Turn 1: Requesting weather in London (expect allowed, Fahrenheit) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-20)    await interaction_func("What is the weather in London?")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-21)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-22)    # 2. Request containing the blocked keyword (Callback intercepts)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-23)    print("\n--- Turn 2: Requesting with blocked keyword (expect blocked) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-24)    await interaction_func("BLOCK the request for weather in Tokyo") # Callback should catch "BLOCK"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-25)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-26)    # 3. Normal greeting (Callback allows root agent, delegation happens)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-27)    print("\n--- Turn 3: Sending a greeting (expect allowed) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-28)    await interaction_func("Hello again")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-29)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-30)  # --- Execute the `run_guardrail_test_conversation` async function ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-31)  # Choose ONE of the methods below based on your environment.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-32)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-33)  # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-34)  # If your environment supports top-level await (like Colab/Jupyter notebooks),
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-35)  # it means an event loop is already running, so you can directly await the function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-36)  print("Attempting execution using 'await' (default for notebooks)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-37)  await run_guardrail_test_conversation()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-38)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-39)  # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-40)  # If running this code as a standard Python script from your terminal,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-41)  # the script context is synchronous. `asyncio.run()` is needed to
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-42)  # create and manage an event loop to execute your async function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-43)  # To use this method:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-44)  # 1. Comment out the `await run_guardrail_test_conversation()` line above.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-45)  # 2. Uncomment the following block:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-46)"""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-47)  import asyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-48)  if __name__ == "__main__": # Ensures this runs only when script is executed directly
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-49)    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-50)    try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-51)      # This creates an event loop, runs your async function, and closes the loop.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-52)      asyncio.run(run_guardrail_test_conversation())
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-53)    except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-54)      print(f"An error occurred: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-55)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-56)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-57)  # --- Inspect final session state after the conversation ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-58)  # This block runs after either execution method completes.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-59)  # Optional: Check state for the trigger flag set by the callback
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-60)  print("\n--- Inspecting Final Session State (After Guardrail Test) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-61)  # Use the session service instance associated with this stateful session
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-62)  final_session = await session_service_stateful.get_session(app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-63)                             user_id=USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-64)                             session_id=SESSION_ID_STATEFUL)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-65)  if final_session:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-66)    # Use .get() for safer access
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-67)    print(f"Guardrail Triggered Flag: {final_session.state.get('guardrail_block_keyword_triggered','Not Set (or False)')}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-68)    print(f"Last Weather Report: {final_session.state.get('last_weather_report','Not Set')}") # Should be London weather if successful
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-69)    print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit','Not Set')}") # Should be Fahrenheit
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-70)    # print(f"Full State Dict: {final_session.state}") # For detailed view
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-71)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-72)    print("\n❌ Error: Could not retrieve final session state.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-73)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-74)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-22-75)  print("\n⚠️ Skipping model guardrail test. Runner ('runner_root_model_guardrail') is not available.")

```

Observe the execution flow:
  1. **London Weather:** The callback runs for `weather_agent_v5_model_guardrail`, inspects the message, prints "Keyword not found. Allowing LLM call.", and returns `None`. The agent proceeds, calls the `get_weather_stateful` tool (which uses the "Fahrenheit" preference from Step 4's state change), and returns the weather. This response updates `last_weather_report` via `output_key`.
  2. **BLOCK Request:** The callback runs again for `weather_agent_v5_model_guardrail`, inspects the message, finds "BLOCK", prints "Blocking LLM call!", sets the state flag, and returns the predefined `LlmResponse`. The agent's underlying LLM is _never called_ for this turn. The user sees the callback's blocking message.
  3. **Hello Again:** The callback runs for `weather_agent_v5_model_guardrail`, allows the request. The root agent then delegates to `greeting_agent`. _Note: The`before_model_callback` defined on the root agent does NOT automatically apply to sub-agents._ The `greeting_agent` proceeds normally, calls its `say_hello` tool, and returns the greeting.


You have successfully implemented an input safety layer! The `before_model_callback` provides a powerful mechanism to enforce rules and control agent behavior _before_ expensive or potentially risky LLM calls are made. Next, we'll apply a similar concept to add guardrails around tool usage itself.
## Step 6: Adding Safety - Tool Argument Guardrail (`before_tool_callback`)[¶](https://google.github.io/adk-docs/tutorials/agent-team/#step-6-adding-safety-tool-argument-guardrail-before_tool_callback "Permanent link")
In Step 5, we added a guardrail to inspect and potentially block user input _before_ it reached the LLM. Now, we'll add another layer of control _after_ the LLM has decided to use a tool but _before_ that tool actually executes. This is useful for validating the _arguments_ the LLM wants to pass to the tool.
ADK provides the `before_tool_callback` for this precise purpose.
**What is`before_tool_callback`?**
  * It's a Python function executed just _before_ a specific tool function runs, after the LLM has requested its use and decided on the arguments.
  * **Purpose:** Validate tool arguments, prevent tool execution based on specific inputs, modify arguments dynamically, or enforce resource usage policies.


**Common Use Cases:**
  * **Argument Validation:** Check if arguments provided by the LLM are valid, within allowed ranges, or conform to expected formats.
  * **Resource Protection:** Prevent tools from being called with inputs that might be costly, access restricted data, or cause unwanted side effects (e.g., blocking API calls for certain parameters).
  * **Dynamic Argument Modification:** Adjust arguments based on session state or other contextual information before the tool runs.


**How it Works:**
  1. Define a function accepting `tool: BaseTool`, `args: Dict[str, Any]`, and `tool_context: ToolContext`.
     * `tool`: The tool object about to be called (inspect `tool.name`).
     * `args`: The dictionary of arguments the LLM generated for the tool.
     * `tool_context`: Provides access to session state (`tool_context.state`), agent info, etc.
  2. Inside the function:
     * **Inspect:** Examine the `tool.name` and the `args` dictionary.
     * **Modify:** Change values within the `args` dictionary _directly_. If you return `None`, the tool runs with these modified args.
     * **Block/Override (Guardrail):** Return a **dictionary**. ADK treats this dictionary as the _result_ of the tool call, completely _skipping_ the execution of the original tool function. The dictionary should ideally match the expected return format of the tool it's blocking.
     * **Allow:** Return `None`. ADK proceeds to execute the actual tool function with the (potentially modified) arguments.


**In this step, we will:**
  1. Define a `before_tool_callback` function (`block_paris_tool_guardrail`) that specifically checks if the `get_weather_stateful` tool is called with the city "Paris".
  2. If "Paris" is detected, the callback will block the tool and return a custom error dictionary.
  3. Update our root agent (`weather_agent_v6_tool_guardrail`) to include _both_ the `before_model_callback` and this new `before_tool_callback`.
  4. Create a new runner for this agent, using the same stateful session service.
  5. Test the flow by requesting weather for allowed cities and the blocked city ("Paris").


**1. Define the Tool Guardrail Callback Function**
This function targets the `get_weather_stateful` tool. It checks the `city` argument. If it's "Paris", it returns an error dictionary that looks like the tool's own error response. Otherwise, it allows the tool to run by returning `None`.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-1)# @title 1. Define the before_tool_callback Guardrail
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-3)# Ensure necessary imports are available
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-4)fromgoogle.adk.tools.base_toolimport BaseTool
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-5)fromgoogle.adk.tools.tool_contextimport ToolContext
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-6)fromtypingimport Optional, Dict, Any # For type hints
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-7)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-8)defblock_paris_tool_guardrail(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-9)  tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-10)) -> Optional[Dict]:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-11)"""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-12)  Checks if 'get_weather_stateful' is called for 'Paris'.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-13)  If so, blocks the tool execution and returns a specific error dictionary.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-14)  Otherwise, allows the tool call to proceed by returning None.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-15)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-16)  tool_name = tool.name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-17)  agent_name = tool_context.agent_name # Agent attempting the tool call
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-18)  print(f"--- Callback: block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-19)  print(f"--- Callback: Inspecting args: {args} ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-20)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-21)  # --- Guardrail Logic ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-22)  target_tool_name = "get_weather_stateful" # Match the function name used by FunctionTool
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-23)  blocked_city = "paris"
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-24)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-25)  # Check if it's the correct tool and the city argument matches the blocked city
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-26)  if tool_name == target_tool_name:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-27)    city_argument = args.get("city", "") # Safely get the 'city' argument
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-28)    if city_argument and city_argument.lower() == blocked_city:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-29)      print(f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-30)      # Optionally update state
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-31)      tool_context.state["guardrail_tool_block_triggered"] = True
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-32)      print(f"--- Callback: Set state 'guardrail_tool_block_triggered': True ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-33)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-34)      # Return a dictionary matching the tool's expected output format for errors
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-35)      # This dictionary becomes the tool's result, skipping the actual tool run.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-36)      return {
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-37)        "status": "error",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-38)        "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled by a tool guardrail."
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-39)      }
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-40)    else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-41)       print(f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-42)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-43)    print(f"--- Callback: Tool '{tool_name}' is not the target tool. Allowing. ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-44)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-45)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-46)  # If the checks above didn't return a dictionary, allow the tool to execute
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-47)  print(f"--- Callback: Allowing tool '{tool_name}' to proceed. ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-48)  return None # Returning None allows the actual tool function to run
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-49)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-23-50)print("✅ block_paris_tool_guardrail function defined.")

```

**2. Update Root Agent to Use Both Callbacks**
We redefine the root agent again (`weather_agent_v6_tool_guardrail`), this time adding the `before_tool_callback` parameter alongside the `before_model_callback` from Step 5.
_Self-Contained Execution Note:_ Similar to Step 5, ensure all prerequisites (sub-agents, tools, `before_model_callback`) are defined or available in the execution context before defining this agent.
```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-1)# @title 2. Update Root Agent with BOTH Callbacks (Self-Contained)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-2)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-3)# --- Ensure Prerequisites are Defined ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-4)# (Include or ensure execution of definitions for: Agent, LiteLlm, Runner, ToolContext,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-5)# MODEL constants, say_hello, say_goodbye, greeting_agent, farewell_agent,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-6)# get_weather_stateful, block_REDACTED)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-7)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-8)# --- Redefine Sub-Agents (Ensures they exist in this context) ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-9)greeting_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-10)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-11)  # Use a defined model constant
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-12)  greeting_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-13)    model=MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-14)    name="greeting_agent", # Keep original name for consistency
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-15)    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-16)    description="Handles simple greetings and hellos using the 'say_hello' tool.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-17)    tools=[say_hello],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-18)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-19)  print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-20)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-21)  print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-22)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-23)farewell_agent = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-24)try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-25)  # Use a defined model constant
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-26)  farewell_agent = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-27)    model=MODEL_GEMINI_2_0_FLASH,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-28)    name="farewell_agent", # Keep original name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-29)    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-30)    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-31)    tools=[say_goodbye],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-32)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-33)  print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-34)except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-35)  print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-36)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-37)# --- Define the Root Agent with Both Callbacks ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-38)root_agent_tool_guardrail = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-39)runner_root_tool_guardrail = None
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-40)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-41)if ('greeting_agent' in globals() and greeting_agent and
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-42)  'farewell_agent' in globals() and farewell_agent and
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-43)  'get_weather_stateful' in globals() and
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-44)  'block_keyword_guardrail' in globals() and
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-45)  'block_paris_tool_guardrail' in globals()):
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-46)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-47)  root_agent_model = MODEL_GEMINI_2_0_FLASH
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-48)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-49)  root_agent_tool_guardrail = Agent(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-50)    name="weather_agent_v6_tool_guardrail", # New version name
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-51)    model=root_agent_model,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-52)    description="Main agent: Handles weather, delegates, includes input AND tool guardrails.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-53)    instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-54)          "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-55)          "Handle only weather, greetings, and farewells.",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-56)    tools=[get_weather_stateful],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-57)    sub_agents=[greeting_agent, farewell_agent],
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-58)    output_key="last_weather_report",
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-59)    before_model_callback=block_keyword_guardrail, # Keep model guardrail
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-60)    before_tool_callback=block_paris_tool_guardrail # <<< Add tool guardrail
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-61)  )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-62)  print(f"✅ Root Agent '{root_agent_tool_guardrail.name}' created with BOTH callbacks.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-63)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-64)  # --- Create Runner, Using SAME Stateful Session Service ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-65)  if 'session_service_stateful' in globals():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-66)    runner_root_tool_guardrail = Runner(
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-67)      agent=root_agent_tool_guardrail,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-68)      app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-69)      session_service=session_service_stateful # <<< Use the service from Step 4/5
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-70)    )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-71)    print(f"✅ Runner created for tool guardrail agent '{runner_root_tool_guardrail.agent.name}', using stateful session service.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-72)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-73)    print("❌ Cannot create runner. 'session_service_stateful' from Step 4/5 is missing.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-74)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-75)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-24-76)  print("❌ Cannot create root agent with tool guardrail. Prerequisites missing.")

```

**3. Interact to Test the Tool Guardrail**
Let's test the interaction flow, again using the same stateful session (`SESSION_ID_STATEFUL`) from the previous steps.
  1. Request weather for "New York": Passes both callbacks, tool executes (using Fahrenheit preference from state).
  2. Request weather for "Paris": Passes `before_model_callback`. LLM decides to call `get_weather_stateful(city='Paris')`. `before_tool_callback` intercepts, blocks the tool, and returns the error dictionary. Agent relays this error.
  3. Request weather for "London": Passes both callbacks, tool executes normally.


```
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-1)# @title 3. Interact to Test the Tool Argument Guardrail
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-2)importasyncio # Ensure asyncio is imported
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-3)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-4)# Ensure the runner for the tool guardrail agent is available
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-5)if 'runner_root_tool_guardrail' in globals() and runner_root_tool_guardrail:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-6)  # Define the main async function for the tool guardrail test conversation.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-7)  # The 'await' keywords INSIDE this function are necessary for async operations.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-8)  async defrun_tool_guardrail_test():
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-9)    print("\n--- Testing Tool Argument Guardrail ('Paris' blocked) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-10)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-11)    # Use the runner for the agent with both callbacks and the existing stateful session
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-12)    # Define a helper lambda for cleaner interaction calls
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-13)    interaction_func = lambda query: call_agent_async(query,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-14)                             runner_root_tool_guardrail,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-15)                             USER_ID_STATEFUL, # Use existing user ID
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-16)                             SESSION_ID_STATEFUL # Use existing session ID
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-17)                            )
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-18)    # 1. Allowed city (Should pass both callbacks, use Fahrenheit state)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-19)    print("--- Turn 1: Requesting weather in New York (expect allowed) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-20)    await interaction_func("What's the weather in New York?")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-21)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-22)    # 2. Blocked city (Should pass model callback, but be blocked by tool callback)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-23)    print("\n--- Turn 2: Requesting weather in Paris (expect blocked by tool guardrail) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-24)    await interaction_func("How about Paris?") # Tool callback should intercept this
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-25)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-26)    # 3. Another allowed city (Should work normally again)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-27)    print("\n--- Turn 3: Requesting weather in London (expect allowed) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-28)    await interaction_func("Tell me the weather in London.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-29)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-30)  # --- Execute the `run_tool_guardrail_test` async function ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-31)  # Choose ONE of the methods below based on your environment.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-32)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-33)  # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-34)  # If your environment supports top-level await (like Colab/Jupyter notebooks),
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-35)  # it means an event loop is already running, so you can directly await the function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-36)  print("Attempting execution using 'await' (default for notebooks)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-37)  await run_tool_guardrail_test()
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-38)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-39)  # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-40)  # If running this code as a standard Python script from your terminal,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-41)  # the script context is synchronous. `asyncio.run()` is needed to
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-42)  # create and manage an event loop to execute your async function.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-43)  # To use this method:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-44)  # 1. Comment out the `await run_tool_guardrail_test()` line above.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-45)  # 2. Uncomment the following block:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-46)"""
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-47)  import asyncio
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-48)  if __name__ == "__main__": # Ensures this runs only when script is executed directly
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-49)    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-50)    try:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-51)      # This creates an event loop, runs your async function, and closes the loop.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-52)      asyncio.run(run_tool_guardrail_test())
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-53)    except Exception as e:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-54)      print(f"An error occurred: {e}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-55)  """
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-56)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-57)  # --- Inspect final session state after the conversation ---
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-58)  # This block runs after either execution method completes.
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-59)  # Optional: Check state for the tool block trigger flag
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-60)  print("\n--- Inspecting Final Session State (After Tool Guardrail Test) ---")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-61)  # Use the session service instance associated with this stateful session
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-62)  final_session = await session_service_stateful.get_session(app_name=APP_NAME,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-63)                             user_id=USER_ID_STATEFUL,
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-64)                             session_id= SESSION_ID_STATEFUL)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-65)  if final_session:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-66)    # Use .get() for safer access
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-67)    print(f"Tool Guardrail Triggered Flag: {final_session.state.get('guardrail_tool_block_triggered','Not Set (or False)')}")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-68)    print(f"Last Weather Report: {final_session.state.get('last_weather_report','Not Set')}") # Should be London weather if successful
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-69)    print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit','Not Set')}") # Should be Fahrenheit
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-70)    # print(f"Full State Dict: {final_session.state}") # For detailed view
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-71)  else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-72)    print("\n❌ Error: Could not retrieve final session state.")
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-73)
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-74)else:
[](https://google.github.io/adk-docs/tutorials/agent-team/#__codelineno-25-75)  print("\n⚠️ Skipping tool guardrail test. Runner ('runner_root_tool_guardrail') is not available.")

```

Analyze the output:
  1. **New York:** The `before_model_callback` allows the request. The LLM requests `get_weather_stateful`. The `before_tool_callback` runs, inspects the args (`{'city': 'New York'}`), sees it's not "Paris", prints "Allowing tool..." and returns `None`. The actual `get_weather_stateful` function executes, reads "Fahrenheit" from state, and returns the weather report. The agent relays this, and it gets saved via `output_key`.
  2. **Paris:** The `before_model_callback` allows the request. The LLM requests `get_weather_stateful(city='Paris')`. The `before_tool_callback` runs, inspects the args, detects "Paris", prints "Blocking tool execution!", sets the state flag, and returns the error dictionary `{'status': 'error', 'error_message': 'Policy restriction...'}`. The actual `get_weather_stateful` function is **never executed**. The agent receives the error dictionary _as if it were the tool's output_ and formulates a response based on that error message.
  3. **London:** Behaves like New York, passing both callbacks and executing the tool successfully. The new London weather report overwrites the `last_weather_report` in the state.


You've now added a crucial safety layer controlling not just _what_ reaches the LLM, but also _how_ the agent's tools can be used based on the specific arguments generated by the LLM. Callbacks like `before_model_callback` and `before_tool_callback` are essential for building robust, safe, and policy-compliant agent applications.
## Conclusion: Your Agent Team is Ready![¶](https://google.github.io/adk-docs/tutorials/agent-team/#conclusion-your-agent-team-is-ready "Permanent link")
Congratulations! You've successfully journeyed from building a single, basic weather agent to constructing a sophisticated, multi-agent team using the Agent Development Kit (ADK).
**Let's recap what you've accomplished:**
  * You started with a **fundamental agent** equipped with a single tool (`get_weather`).
  * You explored ADK's **multi-model flexibility** using LiteLLM, running the same core logic with different LLMs like Gemini, GPT-4o, and Claude.
  * You embraced **modularity** by creating specialized sub-agents (`greeting_agent`, `farewell_agent`) and enabling **automatic delegation** from a root agent.
  * You gave your agents **memory** using **Session State** , allowing them to remember user preferences (`temperature_unit`) and past interactions (`output_key`).
  * You implemented crucial **safety guardrails** using both `before_model_callback` (blocking specific input REDACTED` (blocking tool execution based on arguments like the city "Paris").


Through building this progressive Weather Bot team, you've gained hands-on experience with core ADK concepts essential for developing complex, intelligent applications.
**Key Takeaways:**
  * **Agents & Tools:** The fundamental building blocks for defining capabilities and reasoning. Clear instructions and docstrings are paramount.
  * **Runners & Session Services:** The engine and memory management system that orchestrate agent execution and maintain conversational context.
  * **Delegation:** Designing multi-agent teams allows for specialization, modularity, and better management of complex tasks. Agent `description` is key for auto-flow.
  * **Session State (`ToolContext` , `output_key`):** Essential for creating context-aware, personalized, and multi-turn conversational agents.
  * **Callbacks (`before_model` , `before_tool`):** Powerful hooks for implementing safety, validation, policy enforcement, and dynamic modifications _before_ critical operations (LLM calls or tool execution).
  * **Flexibility (`LiteLlm`):** ADK empowers you to choose the best LLM for the job, balancing performance, cost, and features.


**Where to Go Next?**
Your Weather Bot team is a great starting point. Here are some ideas to further explore ADK and enhance your application:
  1. **Real Weather API:** Replace the `mock_weather_db` in your `get_weather` tool with a call to a real weather API (like OpenWeatherMap, WeatherAPI).
  2. **More Complex State:** Store more user preferences (e.g., preferred location, notification settings) or conversation summaries in the session state.
  3. **Refine Delegation:** Experiment with different root agent instructions or sub-agent descriptions to fine-tune the delegation logic. Could you add a "forecast" agent?
  4. **Advanced Callbacks:**
     * Use `after_model_callback` to potentially reformat or sanitize the LLM's response _after_ it's generated.
     * Use `after_tool_callback` to process or log the results returned by a tool.
     * Implement `before_agent_callback` or `after_agent_callback` for agent-level entry/exit logic.
  5. **Error Handling:** Improve how the agent handles tool errors or unexpected API responses. Maybe add retry logic within a tool.
  6. **Persistent Session Storage:** Explore alternatives to `InMemorySessionService` for storing session state persistently (e.g., using databases like Firestore or Cloud SQL – requires custom implementation or future ADK integrations).
  7. **Streaming UI:** Integrate your agent team with a web framework (like FastAPI, as shown in the ADK Streaming Quickstart) to create a real-time chat interface.


The Agent Development Kit provides a robust foundation for building sophisticated LLM-powered applications. By mastering the concepts covered in this tutorial – tools, state, delegation, and callbacks – you are well-equipped to tackle increasingly complex agentic systems.
Happy building!
Back to top
