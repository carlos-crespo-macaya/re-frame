[ Skip to content ](https://google.github.io/adk-docs/tools/built-in-tools/#built-in-tools)
# Built-in tools[¶](https://google.github.io/adk-docs/tools/built-in-tools/#built-in-tools "Permanent link")
These built-in tools provide ready-to-use functionality such as Google Search or code executors that provide agents with common capabilities. For instance, an agent that needs to retrieve information from the web can directly use the **google_search** tool without any additional setup.
## How to Use[¶](https://google.github.io/adk-docs/tools/built-in-tools/#how-to-use "Permanent link")
  1. **Import:** Import the desired tool from the tools module. This is `agents.tools` in Python or `com.google.adk.tools` in Java.
  2. **Configure:** Initialize the tool, providing required parameters if any.
  3. **Register:** Add the initialized tool to the **tools** list of your Agent.


Once added to an agent, the agent can decide to use the tool based on the **user prompt** and its **instructions**. The framework handles the execution of the tool when the agent calls it. Important: check the **_Limitations_** section of this page.
## Available Built-in tools[¶](https://google.github.io/adk-docs/tools/built-in-tools/#available-built-in-tools "Permanent link")
Note: Java only supports Google Search and Code Execution tools currently.
### Google Search[¶](https://google.github.io/adk-docs/tools/built-in-tools/#google-search "Permanent link")
The `google_search` tool allows the agent to perform web searches using Google Search. The `google_search` tool is only compatible with Gemini 2 models. For further details of the tool, see [Understanding Google Search grounding](https://google.github.io/adk-docs/grounding/google_search_grounding/).
Additional requirements when using the `google_search` tool
When you use grounding with Google Search, and you receive Search suggestions in your response, you must display the Search suggestions in production and in your applications. For more information on grounding with Google Search, see Grounding with Google Search documentation for [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions). The UI code (HTML) is returned in the Gemini response as `renderedContent`, and you will need to show the HTML in your app, in accordance with the policy.
[Python](https://google.github.io/adk-docs/tools/built-in-tools/#python)[Java](https://google.github.io/adk-docs/tools/built-in-tools/#java)
```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-2)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-6)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-8)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-13)# limitations under the License.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-14)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-15)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-16)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-17)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-18)fromgoogle.adk.toolsimport google_search
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-19)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-20)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-21)APP_NAME="google_search_agent"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-22)USER_ID="user1234"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-23)SESSION_ID="1234"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-24)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-25)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-26)root_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-27)  name="basic_search_agent",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-28)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-29)  description="Agent to answer questions using Google Search.",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-30)  instruction="I can answer your questions by searching the internet. Just ask me anything!",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-31)  # google_search is a pre-built tool which allows the agent to perform Google searches.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-32)  tools=[google_search]
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-33))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-34)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-35)# Session and Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-36)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-37)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-38)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-39)  runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-40)  return session, runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-41)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-42)# Agent Interaction
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-43)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-44)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-45)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-46)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-47)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-48)  async for event in events:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-49)    if event.is_final_response():
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-50)      final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-51)      print("Agent Response: ", final_response)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-52)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-53)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-54)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-0-55)await call_agent_async("what's the latest ai news?")

```

```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-1)importcom.google.adk.agents.BaseAgent;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-3)importcom.google.adk.runner.Runner;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-4)importcom.google.adk.sessions.InMemorySessionService;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-5)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-6)importcom.google.adk.tools.GoogleSearchTool;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-7)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-8)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-9)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-10)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-11)publicclass GoogleSearchAgentApp{
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-12)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-13)privatestaticfinalStringAPP_NAME="Google Search_agent";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-14)privatestaticfinalStringUSER_ID="user1234";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-15)privatestaticfinalStringSESSION_ID="1234";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-16)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-17)/**
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-18)  * Calls the agent with the given query and prints the final response.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-19)  *
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-20)  * @param runner The runner to use.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-21)  * @param query The query to send to the agent.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-22)  */
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-23)publicstaticvoidcallAgent(Runnerrunner,Stringquery){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-24)Contentcontent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-25)Content.fromParts(Part.fromText(query));
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-26)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-27)InMemorySessionServicesessionService=(InMemorySessionService)runner.sessionService();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-28)Sessionsession=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-29)sessionService
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-30).createSession(APP_NAME,USER_ID,/* state= */null,SESSION_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-31).blockingGet();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-32)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-33)runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-34).runAsync(session.userId(),session.id(),content)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-35).forEach(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-36)event->{
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-37)if(event.finalResponse()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-38)&&event.content().isPresent()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-39)&&event.content().get().parts().isPresent()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-40)&&!event.content().get().parts().get().isEmpty()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-41)&&event.content().get().parts().get().get(0).text().isPresent()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-42)StringfinalResponse=event.content().get().parts().get().get(0).text().get();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-43)System.out.println("Agent Response: "+finalResponse);
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-44)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-45)});
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-46)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-47)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-48)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-49)// Google Search is a pre-built tool which allows the agent to perform Google searches.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-50)GoogleSearchToolgoogleSearchTool=newGoogleSearchTool();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-51)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-52)BaseAgentrootAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-53)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-54).name("basic_search_agent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-55).model("gemini-2.0-flash")// Ensure to use a Gemini 2.0 model for Google Search Tool
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-56).description("Agent to answer questions using Google Search.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-57).instruction(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-58)"I can answer your questions by searching the internet. Just ask me anything!")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-59).tools(ImmutableList.of(googleSearchTool))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-60).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-61)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-62)// Session and Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-63)InMemorySessionServicesessionService=newInMemorySessionService();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-64)Runnerrunner=newRunner(rootAgent,APP_NAME,null,sessionService);
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-65)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-66)// Agent Interaction
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-67)callAgent(runner,"what's the latest ai news?");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-68)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-1-69)}

```

### Code Execution[¶](https://google.github.io/adk-docs/tools/built-in-tools/#code-execution "Permanent link")
The `built_in_code_execution` tool enables the agent to execute code, specifically when using Gemini 2 models. This allows the model to perform tasks like calculations, data manipulation, or running small scripts.
[Python](https://google.github.io/adk-docs/tools/built-in-tools/#python_1)[Java](https://google.github.io/adk-docs/tools/built-in-tools/#java_1)
```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-2)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-6)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-8)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-13)# limitations under the License.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-14)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-15)importasyncio
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-16)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-17)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-18)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-19)fromgoogle.adk.code_executorsimport BuiltInCodeExecutor
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-20)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-21)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-22)AGENT_NAME = "calculator_agent"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-23)APP_NAME = "calculator"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-24)USER_ID = "user1234"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-25)SESSION_ID = "session_code_exec_async"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-26)GEMINI_MODEL = "gemini-2.0-flash"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-27)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-28)# Agent Definition
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-29)code_agent = LlmAgent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-30)  name=AGENT_NAME,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-31)  model=GEMINI_MODEL,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-32)  code_executor=BuiltInCodeExecutor(),
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-33)  instruction="""You are a calculator agent.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-34)  When given a mathematical expression, write and execute Python code to calculate the result.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-35)  Return only the final numerical result as plain text, without markdown or code blocks.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-36)  """,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-37)  description="Executes Python code to perform calculations.",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-38))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-39)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-40)# Session and Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-41)session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-42)session = asyncio.run(session_service.create_session(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-43)  app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-44)))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-45)runner = Runner(agent=code_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-46)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-47)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-48)# Agent Interaction (Async)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-49)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-50)  content = types.Content(role="user", parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-51)  print(f"\n--- Running Query: {query} ---")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-52)  final_response_text = "No final text response captured."
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-53)  try:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-54)    # Use run_async
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-55)    async for event in runner.run_async(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-56)      user_id=USER_ID, session_id=SESSION_ID, new_message=content
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-57)    ):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-58)      print(f"Event ID: {event.id}, Author: {event.author}")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-59)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-60)      # --- Check for specific parts FIRST ---
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-61)      has_specific_part = False
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-62)      if event.content and event.content.parts:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-63)        for part in event.content.parts: # Iterate through all parts
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-64)          if part.executable_code:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-65)            # Access the actual code string via .code
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-66)            print(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-67)              f" Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-68)            )
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-69)            has_specific_part = True
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-70)          elif part.code_execution_result:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-71)            # Access outcome and output correctly
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-72)            print(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-73)              f" Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-74)            )
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-75)            has_specific_part = True
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-76)          # Also print any text parts found in any event for debugging
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-77)          elif part.text and not part.text.isspace():
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-78)            print(f" Text: '{part.text.strip()}'")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-79)            # Do not set has_specific_part=True here, as we want the final response logic below
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-80)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-81)      # --- Check for final response AFTER specific parts ---
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-82)      # Only consider it final if it doesn't have the specific code parts we just handled
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-83)      if not has_specific_part and event.is_final_response():
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-84)        if (
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-85)          event.content
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-86)          and event.content.parts
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-87)          and event.content.parts[0].text
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-88)        ):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-89)          final_response_text = event.content.parts[0].text.strip()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-90)          print(f"==> Final Agent Response: {final_response_text}")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-91)        else:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-92)          print("==> Final Agent Response: [No text content in final event]")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-93)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-94)  except Exception as e:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-95)    print(f"ERROR during agent run: {e}")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-96)  print("-" * 30)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-97)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-98)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-99)# Main async function to run the examples
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-100)async defmain():
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-101)  await call_agent_async("Calculate the value of (5 + 7) * 3")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-102)  await call_agent_async("What is 10 factorial?")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-103)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-104)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-105)# Execute the main async function
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-106)try:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-107)  asyncio.run(main())
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-108)except RuntimeError as e:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-109)  # Handle specific error when running asyncio.run in an already running loop (like Jupyter/Colab)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-110)  if "cannot be called from a running event loop" in str(e):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-111)    print("\nRunning in an existing event loop (like Colab/Jupyter).")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-112)    print("Please run `await main()` in a notebook cell instead.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-113)    # If in an interactive environment like a notebook, you might need to run:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-114)    # await main()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-115)  else:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-2-116)    raise e # Re-raise other runtime errors

```

```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-1)importcom.google.adk.agents.BaseAgent;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-3)importcom.google.adk.runner.Runner;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-4)importcom.google.adk.sessions.InMemorySessionService;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-5)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-6)importcom.google.adk.tools.BuiltInCodeExecutionTool;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-7)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-8)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-9)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-10)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-11)publicclass CodeExecutionAgentApp{
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-12)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-13)privatestaticfinalStringAGENT_NAME="calculator_agent";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-14)privatestaticfinalStringAPP_NAME="calculator";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-15)privatestaticfinalStringUSER_ID="user1234";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-16)privatestaticfinalStringSESSION_ID="session_code_exec_sync";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-17)privatestaticfinalStringGEMINI_MODEL="gemini-2.0-flash";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-18)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-19)/**
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-20)  * Calls the agent with a query and prints the interaction events and final response.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-21)  *
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-22)  * @param runner The runner instance for the agent.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-23)  * @param query The query to send to the agent.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-24)  */
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-25)publicstaticvoidcallAgent(Runnerrunner,Stringquery){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-26)Contentcontent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-27)Content.builder().role("user").parts(ImmutableList.of(Part.fromText(query))).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-28)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-29)InMemorySessionServicesessionService=(InMemorySessionService)runner.sessionService();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-30)Sessionsession=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-31)sessionService
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-32).createSession(APP_NAME,USER_ID,/* state= */null,SESSION_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-33).blockingGet();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-34)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-35)System.out.println("\n--- Running Query: "+query+" ---");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-36)finalString[]finalResponseText={"No final text response captured."};
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-37)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-38)try{
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-39)runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-40).runAsync(session.userId(),session.id(),content)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-41).forEach(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-42)event->{
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-43)System.out.println("Event ID: "+event.id()+", Author: "+event.author());
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-44)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-45)booleanhasSpecificPart=false;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-46)if(event.content().isPresent()&&event.content().get().parts().isPresent()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-47)for(Partpart:event.content().get().parts().get()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-48)if(part.executableCode().isPresent()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-49)System.out.println(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-50)" Debug: Agent generated code:\n```python\n"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-51)+part.executableCode().get().code()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-52)+"\n```");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-53)hasSpecificPart=true;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-54)}elseif(part.codeExecutionResult().isPresent()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-55)System.out.println(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-56)" Debug: Code Execution Result: "
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-57)+part.codeExecutionResult().get().outcome()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-58)+" - Output:\n"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-59)+part.codeExecutionResult().get().output());
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-60)hasSpecificPart=true;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-61)}elseif(part.text().isPresent()&&!part.text().get().trim().isEmpty()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-62)System.out.println(" Text: '"+part.text().get().trim()+"'");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-63)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-64)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-65)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-66)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-67)if(!hasSpecificPart&&event.finalResponse()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-68)if(event.content().isPresent()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-69)&&event.content().get().parts().isPresent()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-70)&&!event.content().get().parts().get().isEmpty()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-71)&&event.content().get().parts().get().get(0).text().isPresent()){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-72)finalResponseText[0]=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-73)event.content().get().parts().get().get(0).text().get().trim();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-74)System.out.println("==> Final Agent Response: "+finalResponseText[0]);
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-75)}else{
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-76)System.out.println(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-77)"==> Final Agent Response: [No text content in final event]");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-78)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-79)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-80)});
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-81)}catch(Exceptione){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-82)System.err.println("ERROR during agent run: "+e.getMessage());
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-83)e.printStackTrace();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-84)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-85)System.out.println("------------------------------");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-86)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-87)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-88)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-89)BuiltInCodeExecutionToolcodeExecutionTool=newBuiltInCodeExecutionTool();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-90)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-91)BaseAgentcodeAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-92)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-93).name(AGENT_NAME)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-94).model(GEMINI_MODEL)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-95).tools(ImmutableList.of(codeExecutionTool))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-96).instruction(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-97)"""
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-98)                You are a calculator agent.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-99)                When given a mathematical expression, write and execute Python code to calculate the result.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-100)                Return only the final numerical result as plain text, without markdown or code blocks.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-101)                """)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-102).description("Executes Python code to perform calculations.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-103).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-104)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-105)InMemorySessionServicesessionService=newInMemorySessionService();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-106)Runnerrunner=newRunner(codeAgent,APP_NAME,null,sessionService);
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-107)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-108)callAgent(runner,"Calculate the value of (5 + 7) * 3");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-109)callAgent(runner,"What is 10 factorial?");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-110)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-3-111)}

```

### Vertex AI Search[¶](https://google.github.io/adk-docs/tools/built-in-tools/#vertex-ai-search "Permanent link")
The `vertex_ai_search_tool` uses Google Cloud's Vertex AI Search, enabling the agent to search across your private, configured data stores (e.g., internal documents, company policies, knowledge bases). This built-in tool requires you to provide the specific data store ID during configuration. For further details of the tool, see [Understanding Vertex AI Search grounding](https://google.github.io/adk-docs/grounding/vertex_ai_search_grounding/).
```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-1)importasyncio
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-2)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-3)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-4)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-5)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-6)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-7)fromgoogle.adk.toolsimport VertexAiSearchTool
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-8)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-9)# Replace with your actual Vertex AI Search Datastore ID
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-10)# Format: projects/<PROJECT_ID>/locations/<LOCATION>/collections/default_collection/dataStores/<DATASTORE_ID>
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-11)# e.g., "projects/12345/locations/us-central1/collections/default_collection/dataStores/my-datastore-123"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-12)YOUR_DATASTORE_ID = "YOUR_DATASTORE_ID_HERE"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-13)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-14)# Constants
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-15)APP_NAME_VSEARCH = "vertex_search_app"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-16)USER_ID_VSEARCH = "user_vsearch_1"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-17)SESSION_ID_VSEARCH = "session_vsearch_1"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-18)AGENT_NAME_VSEARCH = "doc_qa_agent"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-19)GEMINI_2_FLASH = "gemini-2.0-flash"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-20)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-21)# Tool Instantiation
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-22)# You MUST provide your datastore ID here.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-23)vertex_search_tool = VertexAiSearchTool(data_store_id=YOUR_DATASTORE_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-24)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-25)# Agent Definition
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-26)doc_qa_agent = LlmAgent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-27)  name=AGENT_NAME_VSEARCH,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-28)  model=GEMINI_2_FLASH, # Requires Gemini model
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-29)  tools=[vertex_search_tool],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-30)  instruction=f"""You are a helpful assistant that answers questions based on information found in the document store: {YOUR_DATASTORE_ID}.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-31)  Use the search tool to find relevant information before answering.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-32)  If the answer isn't in the documents, say that you couldn't find the information.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-33)  """,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-34)  description="Answers questions using a specific Vertex AI Search datastore.",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-35))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-36)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-37)# Session and Runner Setup
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-38)session_service_vsearch = InMemorySessionService()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-39)runner_vsearch = Runner(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-40)  agent=doc_qa_agent, app_name=APP_NAME_VSEARCH, session_service=session_service_vsearch
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-41))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-42)session_vsearch = session_service_vsearch.create_session(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-43)  app_name=APP_NAME_VSEARCH, user_id=USER_ID_VSEARCH, session_id=SESSION_ID_VSEARCH
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-44))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-45)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-46)# Agent Interaction Function
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-47)async defcall_vsearch_agent_async(query):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-48)  print("\n--- Running Vertex AI Search Agent ---")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-49)  print(f"Query: {query}")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-50)  if "YOUR_DATASTORE_ID_HERE" in YOUR_DATASTORE_ID:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-51)    print("Skipping execution: Please replace YOUR_DATASTORE_ID_HERE with your actual datastore ID.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-52)    print("-" * 30)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-53)    return
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-54)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-55)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-56)  final_response_text = "No response received."
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-57)  try:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-58)    async for event in runner_vsearch.run_async(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-59)      user_id=USER_ID_VSEARCH, session_id=SESSION_ID_VSEARCH, new_message=content
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-60)    ):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-61)      # Like Google Search, results are often embedded in the model's response.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-62)      if event.is_final_response() and event.content and event.content.parts:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-63)        final_response_text = event.content.parts[0].text.strip()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-64)        print(f"Agent Response: {final_response_text}")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-65)        # You can inspect event.grounding_metadata for source citations
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-66)        if event.grounding_metadata:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-67)          print(f" (Grounding metadata found with {len(event.grounding_metadata.grounding_attributions)} attributions)")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-68)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-69)  except Exception as e:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-70)    print(f"An error occurred: {e}")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-71)    print("Ensure your datastore ID is correct and the service account has permissions.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-72)  print("-" * 30)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-73)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-74)# --- Run Example ---
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-75)async defrun_vsearch_example():
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-76)  # Replace with a question relevant to YOUR datastore content
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-77)  await call_vsearch_agent_async("Summarize the main points about the Q2 strategy document.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-78)  await call_vsearch_agent_async("What safety procedures are mentioned for lab X?")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-79)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-80)# Execute the example
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-81)# await run_vsearch_example()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-82)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-83)# Running locally due to potential colab asyncio issues with multiple awaits
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-84)try:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-85)  asyncio.run(run_vsearch_example())
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-86)except RuntimeError as e:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-87)  if "cannot be called from a running event loop" in str(e):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-88)    print("Skipping execution in running event loop (like Colab/Jupyter). Run locally.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-89)  else:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-4-90)    raise e

```

### BigQuery[¶](https://google.github.io/adk-docs/tools/built-in-tools/#bigquery "Permanent link")
These are a set of tools aimed to provide integration with BigQuery, namely:
  * **`list_dataset_ids`**: Fetches BigQuery dataset ids present in a GCP project.
  * **`get_dataset_info`**: Fetches metadata about a BigQuery dataset.
  * **`list_table_ids`**: Fetches table ids present in a BigQuery dataset.
  * **`get_table_info`**: Fetches metadata about a BigQuery table.
  * **`execute_sql`**: Runs a SQL query in BigQuery and fetch the result.


They are packaged in the toolset `BigQueryToolset`.
```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-2)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-6)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-8)#
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-13)# limitations under the License.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-14)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-15)importasyncio
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-16)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-17)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-18)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-19)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-20)fromgoogle.adk.tools.bigqueryimport BigQueryCredentialsConfig
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-21)fromgoogle.adk.tools.bigqueryimport BigQueryToolset
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-22)fromgoogle.adk.tools.bigquery.configimport BigQueryToolConfig
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-23)fromgoogle.adk.tools.bigquery.configimport WriteMode
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-24)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-25)importgoogle.auth
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-26)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-27)# Define constants for this example agent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-28)AGENT_NAME = "bigquery_agent"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-29)APP_NAME = "bigquery_app"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-30)USER_ID = "user1234"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-31)SESSION_ID = "1234"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-32)GEMINI_MODEL = "gemini-2.0-flash"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-33)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-34)# Define a tool configuration to block any write operations
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-35)tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-36)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-37)# Define a credentials config - in this example we are using application default
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-38)# credentials
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-39)# https://cloud.google.com/docs/authentication/provide-credentials-adc
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-40)application_default_credentials, _ = google.auth.default()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-41)credentials_config = BigQueryCredentialsConfig(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-42)  credentials=application_default_credentials
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-43))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-44)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-45)# Instantiate a BigQuery toolset
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-46)bigquery_toolset = BigQueryToolset(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-47)  credentials_config=credentials_config, bigquery_tool_config=tool_config
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-48))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-49)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-50)# Agent Definition
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-51)bigquery_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-52)  model=GEMINI_MODEL,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-53)  name=AGENT_NAME,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-54)  description=(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-55)    "Agent to answer questions about BigQuery data and models and execute"
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-56)    " SQL queries."
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-57)  ),
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-58)  instruction="""\
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-59)    You are a data science agent with access to several BigQuery tools.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-60)    Make use of those tools to answer the user's questions.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-61)  """,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-62)  tools=[bigquery_toolset],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-63))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-64)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-65)# Session and Runner
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-66)session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-67)session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-68)runner = Runner(agent=bigquery_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-69)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-70)# Agent Interaction
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-71)defcall_agent(query):
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-72)"""
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-73)  Helper function to call the agent with a query.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-74)  """
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-75)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-76)  events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-77)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-78)  print("USER:", query)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-79)  for event in events:
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-80)    if event.is_final_response():
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-81)      final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-82)      print("AGENT:", final_response)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-83)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-84)call_agent("Are there any ml datasets in bigquery-public-data project?")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-85)call_agent("Tell me more about ml_datasets.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-86)call_agent("Which all tables does it have?")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-87)call_agent("Tell me more about the census_adult_income table.")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-5-88)call_agent("How many rows are there per income bracket?")

```

## Use Built-in tools with other tools[¶](https://google.github.io/adk-docs/tools/built-in-tools/#use-built-in-tools-with-other-tools "Permanent link")
The following code sample demonstrates how to use multiple built-in tools or how to use built-in tools with other tools by using multiple agents:
[Python](https://google.github.io/adk-docs/tools/built-in-tools/#python_2)[Java](https://google.github.io/adk-docs/tools/built-in-tools/#java_2)
```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-1)fromgoogle.adk.toolsimport agent_tool
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-2)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-3)fromgoogle.adk.toolsimport google_search
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-4)fromgoogle.adk.code_executorsimport BuiltInCodeExecutor
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-5)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-6)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-7)search_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-8)  model='gemini-2.0-flash',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-9)  name='SearchAgent',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-10)  instruction="""
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-11)  You're a specialist in Google Search
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-12)  """,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-13)  tools=[google_search],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-14))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-15)coding_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-16)  model='gemini-2.0-flash',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-17)  name='CodeAgent',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-18)  instruction="""
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-19)  You're a specialist in Code Execution
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-20)  """,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-21)  tools=[BuiltInCodeExecutor],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-22))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-23)root_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-24)  name="RootAgent",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-25)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-26)  description="Root Agent",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-27)  tools=[agent_tool.AgentTool(agent=search_agent), agent_tool.AgentTool(agent=coding_agent)],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-6-28))

```

```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-1)importcom.google.adk.agents.BaseAgent;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-3)importcom.google.adk.tools.AgentTool;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-4)importcom.google.adk.tools.BuiltInCodeExecutionTool;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-5)importcom.google.adk.tools.GoogleSearchTool;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-6)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-7)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-8)publicclass NestedAgentApp{
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-9)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-10)privatestaticfinalStringMODEL_ID="gemini-2.0-flash";
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-11)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-12)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-13)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-14)// Define the SearchAgent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-15)LlmAgentsearchAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-16)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-17).model(MODEL_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-18).name("SearchAgent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-19).instruction("You're a specialist in Google Search")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-20).tools(newGoogleSearchTool())// Instantiate GoogleSearchTool
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-21).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-22)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-23)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-24)// Define the CodingAgent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-25)LlmAgentcodingAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-26)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-27).model(MODEL_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-28).name("CodeAgent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-29).instruction("You're a specialist in Code Execution")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-30).tools(newBuiltInCodeExecutionTool())// Instantiate BuiltInCodeExecutionTool
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-31).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-32)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-33)// Define the RootAgent, which uses AgentTool.create() to wrap SearchAgent and CodingAgent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-34)BaseAgentrootAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-35)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-36).name("RootAgent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-37).model(MODEL_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-38).description("Root Agent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-39).tools(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-40)AgentTool.create(searchAgent),// Use create method
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-41)AgentTool.create(codingAgent)// Use create method
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-42))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-43).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-44)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-45)// Note: This sample only demonstrates the agent definitions.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-46)// To run these agents, you'd need to integrate them with a Runner and SessionService,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-47)// similar to the previous examples.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-48)System.out.println("Agents defined successfully:");
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-49)System.out.println(" Root Agent: "+rootAgent.name());
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-50)System.out.println(" Search Agent (nested): "+searchAgent.name());
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-51)System.out.println(" Code Agent (nested): "+codingAgent.name());
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-52)}
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-7-53)}

```

### Limitations[¶](https://google.github.io/adk-docs/tools/built-in-tools/#limitations "Permanent link")
Warning
Currently, for each root agent or single agent, only one built-in tool is supported. No other tools of any type can be used in the same agent.
For example, the following approach that uses **_a built-in tool along with other tools_** within a single agent is **not** currently supported:
[Python](https://google.github.io/adk-docs/tools/built-in-tools/#python_3)[Java](https://google.github.io/adk-docs/tools/built-in-tools/#java_3)
```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-8-1)root_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-8-2)  name="RootAgent",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-8-3)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-8-4)  description="Root Agent",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-8-5)  tools=[custom_function, BuiltInCodeExecutor], # <-- BuiltInCodeExecutor not supported when used with tools
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-8-6))

```

```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-9-1)LlmAgentsearchAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-9-2)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-9-3).model(MODEL_ID)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-9-4).name("SearchAgent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-9-5).instruction("You're a specialist in Google Search")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-9-6).tools(newGoogleSearchTool(),newYourCustomTool())// <-- not supported
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-9-7).build();

```

Warning
Built-in tools cannot be used within a sub-agent.
For example, the following approach that uses built-in tools within sub-agents is **not** currently supported:
[Python](https://google.github.io/adk-docs/tools/built-in-tools/#python_4)[Java](https://google.github.io/adk-docs/tools/built-in-tools/#java_4)
```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-1)search_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-2)  model='gemini-2.0-flash',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-3)  name='SearchAgent',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-4)  instruction="""
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-5)  You're a specialist in Google Search
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-6)  """,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-7)  tools=[google_search],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-8))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-9)coding_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-10)  model='gemini-2.0-flash',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-11)  name='CodeAgent',
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-12)  instruction="""
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-13)  You're a specialist in Code Execution
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-14)  """,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-15)  tools=[BuiltInCodeExecutor],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-16))
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-17)root_agent = Agent(
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-18)  name="RootAgent",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-19)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-20)  description="Root Agent",
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-21)  sub_agents=[
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-22)    search_agent,
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-23)    coding_agent
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-24)  ],
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-10-25))

```

```
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-1)LlmAgentsearchAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-2)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-3).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-4).name("SearchAgent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-5).instruction("You're a specialist in Google Search")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-6).tools(newGoogleSearchTool())
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-7).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-8)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-9)LlmAgentcodingAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-10)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-11).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-12).name("CodeAgent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-13).instruction("You're a specialist in Code Execution")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-14).tools(newBuiltInCodeExecutionTool())
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-15).build();
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-16)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-17)
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-18)LlmAgentrootAgent=
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-19)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-20).name("RootAgent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-21).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-22).description("Root Agent")
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-23).subAgents(searchAgent,codingAgent)// Not supported, as the sub agents use built in tools.
[](https://google.github.io/adk-docs/tools/built-in-tools/#__codelineno-11-24).build();

```

Back to top
