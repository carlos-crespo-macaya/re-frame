[ Skip to content ](https://google.github.io/adk-docs/sessions/memory/#memory-long-term-knowledge-with-memoryservice)
# Memory: Long-Term Knowledge with `MemoryService`[¶](https://google.github.io/adk-docs/sessions/memory/#memory-long-term-knowledge-with-memoryservice "Permanent link")
![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue)
We've seen how `Session` tracks the history (`events`) and temporary data (`state`) for a _single, ongoing conversation_. But what if an agent needs to recall information from _past_ conversations or access external knowledge bases? This is where the concept of **Long-Term Knowledge** and the **`MemoryService`**come into play.
Think of it this way:
  * **`Session`/`State` :** Like your short-term memory during one specific chat.
  * **Long-Term Knowledge (`MemoryService`)**: Like a searchable archive or knowledge library the agent can consult, potentially containing information from many past chats or other sources.


## The `MemoryService` Role[¶](https://google.github.io/adk-docs/sessions/memory/#the-memoryservice-role "Permanent link")
The `BaseMemoryService` defines the interface for managing this searchable, long-term knowledge store. Its primary responsibilities are:
  1. **Ingesting Information (`add_session_to_memory`):** Taking the contents of a (usually completed) `Session` and adding relevant information to the long-term knowledge store.
  2. **Searching Information (`search_memory`):** Allowing an agent (typically via a `Tool`) to query the knowledge store and retrieve relevant snippets or context based on a search query.


## Choosing the Right Memory Service[¶](https://google.github.io/adk-docs/sessions/memory/#choosing-the-right-memory-service "Permanent link")
The ADK offers two distinct `MemoryService` implementations, each tailored to different use cases. Use the table below to decide which is the best fit for your agent.
**Feature** | **InMemoryMemoryService** | **[NEW!] VertexAiMemoryBankService**
---|---|---
**Persistence** | None (data is lost on restart) | Yes (Managed by Vertex AI)
**Primary Use Case** | Prototyping, local development, and simple testing. | Building meaningful, evolving memories from user conversations.
**Memory Extraction** | Stores full conversation | Extracts [meaningful information](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories) from conversations and consolidates it with existing memories (powered by LLM)
**Search Capability** | Basic keyword matching. | Advanced semantic search.
**Setup Complexity** | None. It's the default. | Low. Requires an [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) in Vertex AI.
**Dependencies** | None. | Google Cloud Project, Vertex AI API
**When to use it** | When you want to search across multiple sessions’ chat histories for prototyping. | When you want your agent to remember and learn from past interactions.
## In-Memory Memory[¶](https://google.github.io/adk-docs/sessions/memory/#in-memory-memory "Permanent link")
The `InMemoryMemoryService` stores session information in the application's memory and performs basic keyword matching for searches. It requires no setup and is best for prototyping and simple testing scenarios where persistence isn't required.
```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-0-1)fromgoogle.adk.memoryimport InMemoryMemoryService
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-0-2)memory_service = InMemoryMemoryService()

```

**Example: Adding and Searching Memory**
This example demonstrates the basic flow using the `InMemoryMemoryService` for simplicity.
Full Code
```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-1)importasyncio
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-2)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-3)fromgoogle.adk.sessionsimport InMemorySessionService, Session
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-4)fromgoogle.adk.memoryimport InMemoryMemoryService # Import MemoryService
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-5)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-6)fromgoogle.adk.toolsimport load_memory # Tool to query memory
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-7)fromgoogle.genai.typesimport Content, Part
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-8)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-9)# --- Constants ---
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-10)APP_NAME = "memory_example_app"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-11)USER_ID = "mem_user"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-12)MODEL = "gemini-2.0-flash" # Use a valid model
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-13)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-14)# --- Agent Definitions ---
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-15)# Agent 1: Simple agent to capture information
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-16)info_capture_agent = LlmAgent(
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-17)  model=MODEL,
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-18)  name="InfoCaptureAgent",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-19)  instruction="Acknowledge the user's statement.",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-20)  # output_key="captured_info" # Could optionally save to state too
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-21))
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-22)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-23)# Agent 2: Agent that can use memory
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-24)memory_recall_agent = LlmAgent(
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-25)  model=MODEL,
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-26)  name="MemoryRecallAgent",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-27)  instruction="Answer the user's question. Use the 'load_memory' tool "
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-28)        "if the answer might be in past conversations.",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-29)  tools=[load_memory] # Give the agent the tool
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-30))
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-31)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-32)# --- Services and Runner ---
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-33)session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-34)memory_service = InMemoryMemoryService() # Use in-memory for demo
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-35)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-36)runner = Runner(
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-37)  # Start with the info capture agent
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-38)  agent=info_capture_agent,
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-39)  app_name=APP_NAME,
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-40)  session_service=session_service,
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-41)  memory_service=memory_service # Provide the memory service to the Runner
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-42))
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-43)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-44)# --- Scenario ---
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-45)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-46)# Turn 1: Capture some information in a session
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-47)print("--- Turn 1: Capturing Information ---")
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-48)session1_id = "session_info"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-49)session1 = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-50)user_input1 = Content(parts=[Part(text="My favorite project is Project Alpha.")], role="user")
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-51)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-52)# Run the agent
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-53)final_response_text = "(No final response)"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-54)async for event in runner.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-55)  if event.is_final_response() and event.content and event.content.parts:
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-56)    final_response_text = event.content.parts[0].text
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-57)print(f"Agent 1 Response: {final_response_text}")
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-58)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-59)# Get the completed session
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-60)completed_session1 = await runner.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-61)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-62)# Add this session's content to the Memory Service
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-63)print("\n--- Adding Session 1 to Memory ---")
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-64)memory_service = await memory_service.add_session_to_memory(completed_session1)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-1-65)print("Session added to memory.")

```

## Vertex AI Memory Bank[¶](https://google.github.io/adk-docs/sessions/memory/#vertex-ai-memory-bank "Permanent link")
The `VertexAiMemoryBankService` connects your agent to [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview), a fully managed Google Cloud service that provides sophisticated, persistent memory capabilities for conversational agents.
### How It Works[¶](https://google.github.io/adk-docs/sessions/memory/#how-it-works "Permanent link")
The service automatically handles two key operations:
  * **Generating Memories:** At the end of a conversation, the ADK sends the session's events to the Memory Bank, which intelligently processes and stores the information as "memories."
  * **Retrieving Memories:** Your agent code can issue a search query against the Memory Bank to retrieve relevant memories from past conversations.


### Prerequisites[¶](https://google.github.io/adk-docs/sessions/memory/#prerequisites "Permanent link")
Before you can use this feature, you must have:
  1. **A Google Cloud Project:** With the Vertex AI API enabled.
  2. **An Agent Engine:** You need to create an Agent Engine in Vertex AI. This will provide you with the **Agent Engine ID** required for configuration.
  3. **Authentication:** Ensure your local environment is authenticated to access Google Cloud services. The simplest way is to run:
```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-2-1)gcloudauthapplication-defaultlogin

```

  4. **Environment Variables:** The service requires your Google Cloud Project ID and Location. Set them as environment variables:
```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-3-1)exportGOOGLE_CLOUD_PROJECT="your-gcp-project-id"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-3-2)exportGOOGLE_CLOUD_LOCATION="your-gcp-location"

```



### Configuration[¶](https://google.github.io/adk-docs/sessions/memory/#configuration "Permanent link")
To connect your agent to the Memory Bank, you use the `--memory_service_uri` flag when starting the ADK server (`adk web` or `adk api_server`). The URI must be in the format `agentengine://<agent_engine_id>`.
bash```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-4-1)adkwebpath/to/your/agents_dir--memory_service_uri="agentengine://1234567890"

```

Or, you can configure your agent to use the Memory Bank by manually instantiating the `VertexAiMemoryBankService` and passing it to the `Runner`.
```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-1)fromgoogle.adk.memoryimport VertexAiMemoryBankService
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-2)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-3)agent_engine_id = agent_engine.api_resource.name.split("/")[-1]
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-4)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-5)memory_service = VertexAiMemoryBankService(
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-6)  project="PROJECT_ID",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-7)  location="LOCATION",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-8)  agent_engine_id=agent_engine_id
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-9))
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-10)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-11)runner = adk.Runner(
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-12)  ...
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-13)  memory_service=memory_service
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-5-14))

```

### Using Memory in Your Agent[¶](https://google.github.io/adk-docs/sessions/memory/#using-memory-in-your-agent "Permanent link")
With the service configured, the ADK automatically saves session data to the Memory Bank. To make your agent use this memory, you need to call the `search_memory` method from your agent's code.
This is typically done at the beginning of a turn to fetch relevant context before generating a response.
**Example:**
```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-1)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-2)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-3)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-4)classMyAgent(Agent):
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-5)  async defrun(self, request: types.Content, **kwargs) -> types.Content:
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-6)    # Get the user's latest message
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-7)    user_query = request.parts[0].text
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-8)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-9)    # Search the memory for context related to the user's query
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-10)    search_result = await self.search_memory(query=user_query)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-11)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-12)    # Create a prompt that includes the retrieved memories
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-13)    prompt = f"Based on my memory, here's what I recall about your query: {search_result.memories}\n\nNow, please respond to: {user_query}"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-14)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-15)    # Call the LLM with the enhanced prompt
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-6-16)    return await self.llm.generate_content_async(prompt)

```

## Advanced Concepts[¶](https://google.github.io/adk-docs/sessions/memory/#advanced-concepts "Permanent link")
### How Memory Works in Practice[¶](https://google.github.io/adk-docs/sessions/memory/#how-memory-works-in-practice "Permanent link")
The memory workflow internally involves these steps:
  1. **Session Interaction:** A user interacts with an agent via a `Session`, managed by a `SessionService`. Events are added, and state might be updated.
  2. **Ingestion into Memory:** At some point (often when a session is considered complete or has yielded significant information), your application calls `memory_service.add_session_to_memory(session)`. This extracts relevant information from the session's events and adds it to the long-term knowledge store (in-memory dictionary or RAG Corpus).
  3. **Later Query:** In a _different_ (or the same) session, the user might ask a question requiring past context (e.g., "What did we discuss about project X last week?").
  4. **Agent Uses Memory Tool:** An agent equipped with a memory-retrieval tool (like the built-in `load_memory` tool) recognizes the need for past context. It calls the tool, providing a search query (e.g., "discussion project X last week").
  5. **Search Execution:** The tool internally calls `memory_service.search_memory(app_name, user_id, query)`.
  6. **Results Returned:** The `MemoryService` searches its store (using keyword matching or semantic search) and returns relevant snippets as a `SearchMemoryResponse` containing a list of `MemoryResult` objects (each potentially holding events from a relevant past session).
  7. **Agent Uses Results:** The tool returns these results to the agent, usually as part of the context or function response. The agent can then use this retrieved information to formulate its final answer to the user.


### Can an agent have access to more than one memory service?[¶](https://google.github.io/adk-docs/sessions/memory/#can-an-agent-have-access-to-more-than-one-memory-service "Permanent link")
  * **Through Standard Configuration: No.** The framework (`adk web`, `adk api_server`) is designed to be configured with one single memory service at a time via the `--memory_service_uri` flag. This single service is then provided to the agent and accessed through the built-in `self.search_memory()` method. From a configuration standpoint, you can only choose one backend (`InMemory`, `VertexAiMemoryBankService`) for all agents served by that process.
  * **Within Your Agent's Code: Yes, absolutely.** There is nothing preventing you from manually importing and instantiating another memory service directly inside your agent's code. This allows you to access multiple memory sources within a single agent turn.


For example, your agent could use the framework-configured `VertexAiMemoryBankService` to recall conversational history, and also manually instantiate a `InMemoryMemoryService` to look up information in a technical manual.
#### Example: Using Two Memory Services[¶](https://google.github.io/adk-docs/sessions/memory/#example-using-two-memory-services "Permanent link")
Here’s how you could implement that in your agent's code:
```
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-1)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-2)fromgoogle.adk.memoryimport InMemoryMemoryService, VertexAiMemoryBankService
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-3)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-4)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-5)classMultiMemoryAgent(Agent):
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-6)  def__init__(self, **kwargs):
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-7)    super().__init__(**kwargs)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-8)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-9)    self.memory_service = InMemoryMemoryService()
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-10)    # Manually instantiate a second memory service for document lookups
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-11)    self.vertexai_memorybank_service = VertexAiMemoryBankService(
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-12)      project="PROJECT_ID",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-13)      location="LOCATION",
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-14)      agent_engine_id="AGENT_ENGINE_ID"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-15)    )
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-16)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-17)  async defrun(self, request: types.Content, **kwargs) -> types.Content:
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-18)    user_query = request.parts[0].text
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-19)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-20)    # 1. Search conversational history using the framework-provided memory
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-21)    #  (This would be InMemoryMemoryService if configured)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-22)    conversation_context = await self.search_memory(query=user_query)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-23)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-24)    # 2. Search the document knowledge base using the manually created service
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-25)    document_context = await self.vertexai_memorybank_service.search_memory(query=user_query)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-26)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-27)    # Combine the context from both sources to generate a better response
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-28)    prompt = "From our past conversations, I remember:\n"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-29)    prompt += f"{conversation_context.memories}\n\n"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-30)    prompt += "From the technical manuals, I found:\n"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-31)    prompt += f"{document_context.memories}\n\n"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-32)    prompt += f"Based on all this, here is my answer to '{user_query}':"
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-33)
[](https://google.github.io/adk-docs/sessions/memory/#__codelineno-7-34)    return await self.llm.generate_content_async(prompt)

```

Back to top
