[ Skip to content ](https://google.github.io/adk-docs/agents/multi-agents/#multi-agent-systems-in-adk)
# Multi-Agent Systems in ADK[¶](https://google.github.io/adk-docs/agents/multi-agents/#multi-agent-systems-in-adk "Permanent link")
As agentic applications grow in complexity, structuring them as a single, monolithic agent can become challenging to develop, maintain, and reason about. The Agent Development Kit (ADK) supports building sophisticated applications by composing multiple, distinct `BaseAgent` instances into a **Multi-Agent System (MAS)**.
In ADK, a multi-agent system is an application where different agents, often forming a hierarchy, collaborate or coordinate to achieve a larger goal. Structuring your application this way offers significant advantages, including enhanced modularity, specialization, reusability, maintainability, and the ability to define structured control flows using dedicated workflow agents.
You can compose various types of agents derived from `BaseAgent` to build these systems:
  * **LLM Agents:** Agents powered by large language models. (See [LLM Agents](https://google.github.io/adk-docs/agents/llm-agents/))
  * **Workflow Agents:** Specialized agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) designed to manage the execution flow of their sub-agents. (See [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/))
  * **Custom agents:** Your own agents inheriting from `BaseAgent` with specialized, non-LLM logic. (See [Custom Agents](https://google.github.io/adk-docs/agents/custom-agents/))


The following sections detail the core ADK primitives—such as agent hierarchy, workflow agents, and interaction mechanisms—that enable you to construct and manage these multi-agent systems effectively.
## 1. ADK Primitives for Agent Composition[¶](https://google.github.io/adk-docs/agents/multi-agents/#1-adk-primitives-for-agent-composition "Permanent link")
ADK provides core building blocks—primitives—that enable you to structure and manage interactions within your multi-agent system.
Note
The specific parameters or method names for the primitives may vary slightly by SDK language (e.g., `sub_agents` in Python, `subAgents` in Java). Refer to the language-specific API documentation for details.
### 1.1. Agent Hierarchy (Parent agent, Sub Agents)[¶](https://google.github.io/adk-docs/agents/multi-agents/#11-agent-hierarchy-parent-agent-sub-agents "Permanent link")
The foundation for structuring multi-agent systems is the parent-child relationship defined in `BaseAgent`.
  * **Establishing Hierarchy:** You create a tree structure by passing a list of agent instances to the `sub_agents` argument when initializing a parent agent. ADK automatically sets the `parent_agent` attribute on each child agent during initialization.
  * **Single Parent Rule:** An agent instance can only be added as a sub-agent once. Attempting to assign a second parent will result in a `ValueError`.
  * **Importance:** This hierarchy defines the scope for [Workflow Agents](https://google.github.io/adk-docs/agents/multi-agents/#12-workflow-agents-as-orchestrators) and influences the potential targets for LLM-Driven Delegation. You can navigate the hierarchy using `agent.parent_agent` or find descendants using `agent.find_agent(name)`.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-1)# Conceptual Example: Defining Hierarchy
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-2)fromgoogle.adk.agentsimport LlmAgent, BaseAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-4)# Define individual agents
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-5)greeter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-6)task_doer = BaseAgent(name="TaskExecutor") # Custom non-LLM agent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-7)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-8)# Create parent agent and assign children via sub_agents
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-9)coordinator = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-10)  name="Coordinator",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-11)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-12)  description="I coordinate greetings and tasks.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-13)  sub_agents=[ # Assign sub_agents here
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-14)    greeter,
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-15)    task_doer
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-16)  ]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-17))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-18)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-19)# Framework automatically sets:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-20)# assert greeter.parent_agent == coordinator
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-0-21)# assert task_doer.parent_agent == coordinator

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-1)// Conceptual Example: Defining Hierarchy
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-2)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-3)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-5)// Define individual agents
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-6)LlmAgentgreeter=LlmAgent.builder().name("Greeter").model("gemini-2.0-flash").build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-7)SequentialAgenttaskDoer=SequentialAgent.builder().name("TaskExecutor").subAgents(...).build();// Sequential Agent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-8)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-9)// Create parent agent and assign sub_agents
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-10)LlmAgentcoordinator=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-11).name("Coordinator")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-12).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-13).description("I coordinate greetings and tasks")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-14).subAgents(greeter,taskDoer)// Assign sub_agents here
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-15).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-16)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-17)// Framework automatically sets:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-18)// assert greeter.parentAgent().equals(coordinator);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-1-19)// assert taskDoer.parentAgent().equals(coordinator);

```

### 1.2. Workflow Agents as Orchestrators[¶](https://google.github.io/adk-docs/agents/multi-agents/#12-workflow-agents-as-orchestrators "Permanent link")
ADK includes specialized agents derived from `BaseAgent` that don't perform tasks themselves but orchestrate the execution flow of their `sub_agents`.
  * **[`SequentialAgent`](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/):** Executes its `sub_agents` one after another in the order they are listed.
    * **Context:** Passes the _same_ [`InvocationContext`](https://google.github.io/adk-docs/runtime/) sequentially, allowing agents to easily pass results via shared state.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_1)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_1)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-1)# Conceptual Example: Sequential Pipeline
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-2)fromgoogle.adk.agentsimport SequentialAgent, LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-4)step1 = LlmAgent(name="Step1_Fetch", output_key="data") # Saves output to state['data']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-5)step2 = LlmAgent(name="Step2_Process", instruction="Process data from {data}.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-7)pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-2-8)# When pipeline runs, Step2 can access the state['data'] set by Step1.

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-1)// Conceptual Example: Sequential Pipeline
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-2)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-3)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-5)LlmAgentstep1=LlmAgent.builder().name("Step1_Fetch").outputKey("data").build();// Saves output to state.get("data")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-6)LlmAgentstep2=LlmAgent.builder().name("Step2_Process").instruction("Process data from {data}.").build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-7)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-8)SequentialAgentpipeline=SequentialAgent.builder().name("MyPipeline").subAgents(step1,step2).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-3-9)// When pipeline runs, Step2 can access the state.get("data") set by Step1.

```

  * **[`ParallelAgent`](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/):** Executes its `sub_agents` in parallel. Events from sub-agents may be interleaved.
    * **Context:** Modifies the `InvocationContext.branch` for each child agent (e.g., `ParentBranch.ChildName`), providing a distinct contextual path which can be useful for isolating history in some memory implementations.
    * **State:** Despite different branches, all parallel children access the _same shared_ `session.state`, enabling them to read initial state and write results (use distinct keys to avoid race conditions).


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_2)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_2)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-1)# Conceptual Example: Parallel Execution
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-2)fromgoogle.adk.agentsimport ParallelAgent, LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-4)fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-5)fetch_news = LlmAgent(name="NewsFetcher", output_key="news")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-7)gatherer = ParallelAgent(name="InfoGatherer", sub_agents=[fetch_weather, fetch_news])
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-8)# When gatherer runs, WeatherFetcher and NewsFetcher run concurrently.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-4-9)# A subsequent agent could read state['weather'] and state['news'].

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-1)// Conceptual Example: Parallel Execution
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-3)importcom.google.adk.agents.ParallelAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-5)LlmAgentfetchWeather=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-6).name("WeatherFetcher")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-7).outputKey("weather")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-8).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-9)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-10)LlmAgentfetchNews=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-11).name("NewsFetcher")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-12).instruction("news")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-13).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-14)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-15)ParallelAgentgatherer=ParallelAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-16).name("InfoGatherer")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-17).subAgents(fetchWeather,fetchNews)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-18).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-19)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-20)// When gatherer runs, WeatherFetcher and NewsFetcher run concurrently.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-5-21)// A subsequent agent could read state['weather'] and state['news'].

```

  * **[`LoopAgent`](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/):** Executes its `sub_agents` sequentially in a loop.
    * **Termination:** The loop stops if the optional `max_iterations` is reached, or if any sub-agent returns an [`Event`](https://google.github.io/adk-docs/events/) with `escalate=True` in it's Event Actions.
    * **Context & State:** Passes the _same_ `InvocationContext` in each iteration, allowing state changes (e.g., counters, flags) to persist across loops.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_3)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_3)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-1)# Conceptual Example: Loop with Condition
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-2)fromgoogle.adk.agentsimport LoopAgent, LlmAgent, BaseAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-3)fromgoogle.adk.eventsimport Event, EventActions
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-4)fromgoogle.adk.agents.invocation_contextimport InvocationContext
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-5)fromtypingimport AsyncGenerator
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-7)classCheckCondition(BaseAgent): # Custom agent to check state
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-8)  async def_run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-9)    status = ctx.session.state.get("status", "pending")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-10)    is_done = (status == "completed")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-11)    yield Event(author=self.name, actions=EventActions(escalate=is_done)) # Escalate if done
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-12)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-13)process_step = LlmAgent(name="ProcessingStep") # Agent that might update state['status']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-14)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-15)poller = LoopAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-16)  name="StatusPoller",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-17)  max_iterations=10,
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-18)  sub_agents=[process_step, CheckCondition(name="Checker")]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-19))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-20)# When poller runs, it executes process_step then Checker repeatedly
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-6-21)# until Checker escalates (state['status'] == 'completed') or 10 iterations pass.

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-1)// Conceptual Example: Loop with Condition
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-2)// Custom agent to check state and potentially escalate
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-3)publicstaticclass CheckConditionAgentextendsBaseAgent{
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-4)publicCheckConditionAgent(Stringname,Stringdescription){
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-5)super(name,description,List.of(),null,null);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-6)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-7)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-8)@Override
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-9)protectedFlowable<Event>runAsyncImpl(InvocationContextctx){
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-10)Stringstatus=(String)ctx.session().state().getOrDefault("status","pending");
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-11)booleanisDone="completed".equalsIgnoreCase(status);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-12)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-13)// Emit an event that signals to escalate (exit the loop) if the condition is met.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-14)// If not done, the escalate flag will be false or absent, and the loop continues.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-15)EventcheckEvent=Event.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-16).author(name())
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-17).id(Event.generateEventId())// Important to give events unique IDs
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-18).actions(EventActions.builder().escalate(isDone).build())// Escalate if done
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-19).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-20)returnFlowable.just(checkEvent);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-21)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-22)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-23)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-24)// Agent that might update state.put("status")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-25)LlmAgentprocessingStepAgent=LlmAgent.builder().name("ProcessingStep").build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-26)// Custom agent instance for checking the condition
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-27)CheckConditionAgentconditionCheckerAgent=newCheckConditionAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-28)"ConditionChecker",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-29)"Checks if the status is 'completed'."
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-30));
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-31)LoopAgentpoller=LoopAgent.builder().name("StatusPoller").maxIterations(10).subAgents(processingStepAgent,conditionCheckerAgent).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-32)// When poller runs, it executes processingStepAgent then conditionCheckerAgent repeatedly
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-7-33)// until Checker escalates (state.get("status") == "completed") or 10 iterations pass.

```

### 1.3. Interaction & Communication Mechanisms[¶](https://google.github.io/adk-docs/agents/multi-agents/#13-interaction-communication-mechanisms "Permanent link")
Agents within a system often need to exchange data or trigger actions in one another. ADK facilitates this through:
#### a) Shared Session State (`session.state`)[¶](https://google.github.io/adk-docs/agents/multi-agents/#a-shared-session-state-sessionstate "Permanent link")
The most fundamental way for agents operating within the same invocation (and thus sharing the same [`Session`](https://google.github.io/adk-docs/sessions/session/) object via the `InvocationContext`) to communicate passively.
  * **Mechanism:** One agent (or its tool/callback) writes a value (`context.state['data_key'] = processed_data`), and a subsequent agent reads it (`data = context.state.get('data_key')`). State changes are tracked via [`CallbackContext`](https://google.github.io/adk-docs/callbacks/).
  * **Convenience:** The `output_key` property on [`LlmAgent`](https://google.github.io/adk-docs/agents/llm-agents/) automatically saves the agent's final response text (or structured output) to the specified state key.
  * **Nature:** Asynchronous, passive communication. Ideal for pipelines orchestrated by `SequentialAgent` or passing data across `LoopAgent` iterations.
  * **See Also:** [State Management](https://google.github.io/adk-docs/sessions/state/)


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_4)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_4)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-1)# Conceptual Example: Using output_key and reading state
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-2)fromgoogle.adk.agentsimport LlmAgent, SequentialAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-4)agent_A = LlmAgent(name="AgentA", instruction="Find the capital of France.", output_key="capital_city")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-5)agent_B = LlmAgent(name="AgentB", instruction="Tell me about the city stored in {capital_city}.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-7)pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-8)# AgentA runs, saves "Paris" to state['capital_city'].
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-8-9)# AgentB runs, its instruction processor reads state['capital_city'] to get "Paris".

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-1)// Conceptual Example: Using outputKey and reading state
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-3)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-5)LlmAgentagentA=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-6).name("AgentA")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-7).instruction("Find the capital of France.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-8).outputKey("capital_city")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-9).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-10)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-11)LlmAgentagentB=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-12).name("AgentB")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-13).instruction("Tell me about the city stored in {capital_city}.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-14).outputKey("capital_city")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-15).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-16)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-17)SequentialAgentpipeline=SequentialAgent.builder().name("CityInfo").subAgents(agentA,agentB).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-18)// AgentA runs, saves "Paris" to state('capital_city').
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-9-19)// AgentB runs, its instruction processor reads state.get("capital_city") to get "Paris".

```

#### b) LLM-Driven Delegation (Agent Transfer)[¶](https://google.github.io/adk-docs/agents/multi-agents/#b-llm-driven-delegation-agent-transfer "Permanent link")
Leverages an [`LlmAgent`](https://google.github.io/adk-docs/agents/llm-agents/)'s understanding to dynamically route tasks to other suitable agents within the hierarchy.
  * **Mechanism:** The agent's LLM generates a specific function call: `transfer_to_agent(agent_name='target_agent_name')`.
  * **Handling:** The `AutoFlow`, used by default when sub-agents are present or transfer isn't disallowed, intercepts this call. It identifies the target agent using `root_agent.find_agent()` and updates the `InvocationContext` to switch execution focus.
  * **Requires:** The calling `LlmAgent` needs clear `instructions` on when to transfer, and potential target agents need distinct `description`s for the LLM to make informed decisions. Transfer scope (parent, sub-agent, siblings) can be configured on the `LlmAgent`.
  * **Nature:** Dynamic, flexible routing based on LLM interpretation.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_5)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_5)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-1)# Conceptual Setup: LLM Transfer
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-2)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-4)booking_agent = LlmAgent(name="Booker", description="Handles flight and hotel bookings.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-5)info_agent = LlmAgent(name="Info", description="Provides general information and answers questions.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-7)coordinator = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-8)  name="Coordinator",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-9)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-10)  instruction="You are an assistant. Delegate booking tasks to Booker and info requests to Info.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-11)  description="Main coordinator.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-12)  # AutoFlow is typically used implicitly here
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-13)  sub_agents=[booking_agent, info_agent]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-14))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-15)# If coordinator receives "Book a flight", its LLM should generate:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-16)# FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-10-17)# ADK framework then routes execution to booking_agent.

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-1)// Conceptual Setup: LLM Transfer
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-4)LlmAgentbookingAgent=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-5).name("Booker")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-6).description("Handles flight and hotel bookings.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-7).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-8)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-9)LlmAgentinfoAgent=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-10).name("Info")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-11).description("Provides general information and answers questions.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-12).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-13)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-14)// Define the coordinator agent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-15)LlmAgentcoordinator=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-16).name("Coordinator")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-17).model("gemini-2.0-flash")// Or your desired model
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-18).instruction("You are an assistant. Delegate booking tasks to Booker and info requests to Info.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-19).description("Main coordinator.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-20)// AutoFlow will be used by default (implicitly) because subAgents are present
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-21)// and transfer is not disallowed.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-22).subAgents(bookingAgent,infoAgent)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-23).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-24)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-25)// If coordinator receives "Book a flight", its LLM should generate:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-26)// FunctionCall.builder.name("transferToAgent").args(ImmutableMap.of("agent_name", "Booker")).build()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-11-27)// ADK framework then routes execution to bookingAgent.

```

#### c) Explicit Invocation (`AgentTool`)[¶](https://google.github.io/adk-docs/agents/multi-agents/#c-explicit-invocation-agenttool "Permanent link")
Allows an [`LlmAgent`](https://google.github.io/adk-docs/agents/llm-agents/) to treat another `BaseAgent` instance as a callable function or [Tool](https://google.github.io/adk-docs/tools/).
  * **Mechanism:** Wrap the target agent instance in `AgentTool` and include it in the parent `LlmAgent`'s `tools` list. `AgentTool` generates a corresponding function declaration for the LLM.
  * **Handling:** When the parent LLM generates a function call targeting the `AgentTool`, the framework executes `AgentTool.run_async`. This method runs the target agent, captures its final response, forwards any state/artifact changes back to the parent's context, and returns the response as the tool's result.
  * **Nature:** Synchronous (within the parent's flow), explicit, controlled invocation like any other tool.
  * **(Note:** `AgentTool` needs to be imported and used explicitly).


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_6)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_6)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-1)# Conceptual Setup: Agent as a Tool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-2)fromgoogle.adk.agentsimport LlmAgent, BaseAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-3)fromgoogle.adk.toolsimport agent_tool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-4)frompydanticimport BaseModel
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-5)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-6)# Define a target agent (could be LlmAgent or custom BaseAgent)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-7)classImageGeneratorAgent(BaseAgent): # Example custom agent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-8)  name: str = "ImageGen"
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-9)  description: str = "Generates an image based on a prompt."
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-10)  # ... internal logic ...
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-11)  async def_run_async_impl(self, ctx): # Simplified run logic
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-12)    prompt = ctx.session.state.get("image_prompt", "default prompt")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-13)    # ... generate image bytes ...
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-14)    image_bytes = b"..."
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-15)    yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-16)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-17)image_agent = ImageGeneratorAgent()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-18)image_tool = agent_tool.AgentTool(agent=image_agent) # Wrap the agent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-19)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-20)# Parent agent uses the AgentTool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-21)artist_agent = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-22)  name="Artist",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-23)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-24)  instruction="Create a prompt and use the ImageGen tool to generate the image.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-25)  tools=[image_tool] # Include the AgentTool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-26))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-27)# Artist LLM generates a prompt, then calls:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-28)# FunctionCall(name='ImageGen', args={'image_prompt': 'a cat wearing a hat'})
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-29)# Framework calls image_tool.run_async(...), which runs ImageGeneratorAgent.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-12-30)# The resulting image Part is returned to the Artist agent as the tool result.

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-1)// Conceptual Setup: Agent as a Tool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-2)importcom.google.adk.agents.BaseAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-3)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-4)importcom.google.adk.tools.AgentTool;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-5)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-6)// Example custom agent (could be LlmAgent or custom BaseAgent)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-7)publicclass ImageGeneratorAgentextendsBaseAgent{
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-8)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-9)publicImageGeneratorAgent(Stringname,Stringdescription){
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-10)super(name,description,List.of(),null,null);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-11)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-12)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-13)// ... internal logic ...
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-14)@Override
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-15)protectedFlowable<Event>runAsyncImpl(InvocationContextinvocationContext){// Simplified run logic
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-16)invocationContext.session().state().get("image_prompt");
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-17)// Generate image bytes
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-18)// ...
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-19)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-20)EventresponseEvent=Event.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-21).author(this.name())
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-22).content(Content.fromParts(Part.fromText("\b...")))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-23).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-24)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-25)returnFlowable.just(responseEvent);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-26)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-27)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-28)@Override
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-29)protectedFlowable<Event>runLiveImpl(InvocationContextinvocationContext){
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-30)returnnull;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-31)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-32)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-33)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-34)// Wrap the agent using AgentTool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-35)ImageGeneratorAgentimageAgent=newImageGeneratorAgent("image_agent","generates images");
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-36)AgentToolimageTool=AgentTool.create(imageAgent);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-37)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-38)// Parent agent uses the AgentTool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-39)LlmAgentartistAgent=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-40).name("Artist")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-41).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-42).instruction(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-43)"You are an artist. Create a detailed prompt for an image and then "+
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-44)"use the 'ImageGen' tool to generate the image. "+
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-45)"The 'ImageGen' tool expects a single string argument named 'request' "+
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-46)"containing the image prompt. The tool will return a JSON string in its "+
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-47)"'result' field, containing 'image_base64', 'mime_type', and 'status'."
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-48))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-49).description("An agent that can create images using a generation tool.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-50).tools(imageTool)// Include the AgentTool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-51).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-52)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-53)// Artist LLM generates a prompt, then calls:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-54)// FunctionCall(name='ImageGen', args={'imagePrompt': 'a cat wearing a hat'})
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-55)// Framework calls imageTool.runAsync(...), which runs ImageGeneratorAgent.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-13-56)// The resulting image Part is returned to the Artist agent as the tool result.

```

These primitives provide the flexibility to design multi-agent interactions ranging from tightly coupled sequential workflows to dynamic, LLM-driven delegation networks.
## 2. Common Multi-Agent Patterns using ADK Primitives[¶](https://google.github.io/adk-docs/agents/multi-agents/#2-common-multi-agent-patterns-using-adk-primitives "Permanent link")
By combining ADK's composition primitives, you can implement various established patterns for multi-agent collaboration.
### Coordinator/Dispatcher Pattern[¶](https://google.github.io/adk-docs/agents/multi-agents/#coordinatordispatcher-pattern "Permanent link")
  * **Structure:** A central [`LlmAgent`](https://google.github.io/adk-docs/agents/llm-agents/) (Coordinator) manages several specialized `sub_agents`.
  * **Goal:** Route incoming requests to the appropriate specialist agent.
  * **ADK Primitives Used:**
    * **Hierarchy:** Coordinator has specialists listed in `sub_agents`.
    * **Interaction:** Primarily uses **LLM-Driven Delegation** (requires clear `description`s on sub-agents and appropriate `instruction` on Coordinator) or **Explicit Invocation (`AgentTool`)** (Coordinator includes `AgentTool`-wrapped specialists in its `tools`).


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_7)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_7)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-1)# Conceptual Code: Coordinator using LLM Transfer
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-2)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-4)billing_agent = LlmAgent(name="Billing", description="Handles billing inquiries.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-5)support_agent = LlmAgent(name="Support", description="Handles technical support requests.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-7)coordinator = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-8)  name="HelpDeskCoordinator",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-9)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-10)  instruction="Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-11)  description="Main help desk router.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-12)  # allow_transfer=True is often implicit with sub_agents in AutoFlow
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-13)  sub_agents=[billing_agent, support_agent]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-14))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-15)# User asks "My payment failed" -> Coordinator's LLM should call transfer_to_agent(agent_name='Billing')
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-14-16)# User asks "I can't log in" -> Coordinator's LLM should call transfer_to_agent(agent_name='Support')

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-1)// Conceptual Code: Coordinator using LLM Transfer
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-4)LlmAgentbillingAgent=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-5).name("Billing")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-6).description("Handles billing inquiries and payment issues.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-7).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-8)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-9)LlmAgentsupportAgent=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-10).name("Support")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-11).description("Handles technical support requests and login problems.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-12).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-13)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-14)LlmAgentcoordinator=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-15).name("HelpDeskCoordinator")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-16).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-17).instruction("Route user requests: Use Billing agent for payment issues, Support agent for technical problems.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-18).description("Main help desk router.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-19).subAgents(billingAgent,supportAgent)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-20)// Agent transfer is implicit with sub agents in the Autoflow, unless specified
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-21)// using .disallowTransferToParent or disallowTransferToPeers
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-22).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-23)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-24)// User asks "My payment failed" -> Coordinator's LLM should call
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-25)// transferToAgent(agentName='Billing')
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-26)// User asks "I can't log in" -> Coordinator's LLM should call
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-15-27)// transferToAgent(agentName='Support')

```

### Sequential Pipeline Pattern[¶](https://google.github.io/adk-docs/agents/multi-agents/#sequential-pipeline-pattern "Permanent link")
  * **Structure:** A [`SequentialAgent`](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) contains `sub_agents` executed in a fixed order.
  * **Goal:** Implement a multi-step process where the output of one step feeds into the next.
  * **ADK Primitives Used:**
    * **Workflow:** `SequentialAgent` defines the order.
    * **Communication:** Primarily uses **Shared Session State**. Earlier agents write results (often via `output_key`), later agents read those results from `context.state`.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_8)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_8)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-1)# Conceptual Code: Sequential Data Pipeline
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-2)fromgoogle.adk.agentsimport SequentialAgent, LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-4)validator = LlmAgent(name="ValidateInput", instruction="Validate the input.", output_key="validation_status")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-5)processor = LlmAgent(name="ProcessData", instruction="Process data if {validation_status} is 'valid'.", output_key="result")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-6)reporter = LlmAgent(name="ReportResult", instruction="Report the result from {result}.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-7)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-8)data_pipeline = SequentialAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-9)  name="DataPipeline",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-10)  sub_agents=[validator, processor, reporter]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-11))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-12)# validator runs -> saves to state['validation_status']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-13)# processor runs -> reads state['validation_status'], saves to state['result']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-16-14)# reporter runs -> reads state['result']

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-1)// Conceptual Code: Sequential Data Pipeline
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-2)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-4)LlmAgentvalidator=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-5).name("ValidateInput")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-6).instruction("Validate the input")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-7).outputKey("validation_status")// Saves its main text output to session.state["validation_status"]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-8).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-9)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-10)LlmAgentprocessor=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-11).name("ProcessData")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-12).instruction("Process data if {validation_status} is 'valid'")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-13).outputKey("result")// Saves its main text output to session.state["result"]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-14).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-15)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-16)LlmAgentreporter=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-17).name("ReportResult")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-18).instruction("Report the result from {result}")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-19).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-20)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-21)SequentialAgentdataPipeline=SequentialAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-22).name("DataPipeline")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-23).subAgents(validator,processor,reporter)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-24).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-25)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-26)// validator runs -> saves to state['validation_status']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-27)// processor runs -> reads state['validation_status'], saves to state['result']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-17-28)// reporter runs -> reads state['result']

```

### Parallel Fan-Out/Gather Pattern[¶](https://google.github.io/adk-docs/agents/multi-agents/#parallel-fan-outgather-pattern "Permanent link")
  * **Structure:** A [`ParallelAgent`](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/) runs multiple `sub_agents` concurrently, often followed by a later agent (in a `SequentialAgent`) that aggregates results.
  * **Goal:** Execute independent tasks simultaneously to reduce latency, then combine their outputs.
  * **ADK Primitives Used:**
    * **Workflow:** `ParallelAgent` for concurrent execution (Fan-Out). Often nested within a `SequentialAgent` to handle the subsequent aggregation step (Gather).
    * **Communication:** Sub-agents write results to distinct keys in **Shared Session State**. The subsequent "Gather" agent reads multiple state keys.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_9)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_9)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-1)# Conceptual Code: Parallel Information Gathering
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-2)fromgoogle.adk.agentsimport SequentialAgent, ParallelAgent, LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-4)fetch_api1 = LlmAgent(name="API1Fetcher", instruction="Fetch data from API 1.", output_key="api1_data")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-5)fetch_api2 = LlmAgent(name="API2Fetcher", instruction="Fetch data from API 2.", output_key="api2_data")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-7)gather_concurrently = ParallelAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-8)  name="ConcurrentFetch",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-9)  sub_agents=[fetch_api1, fetch_api2]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-10))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-11)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-12)synthesizer = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-13)  name="Synthesizer",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-14)  instruction="Combine results from {api1_data} and {api2_data}."
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-15))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-16)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-17)overall_workflow = SequentialAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-18)  name="FetchAndSynthesize",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-19)  sub_agents=[gather_concurrently, synthesizer] # Run parallel fetch, then synthesize
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-20))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-21)# fetch_api1 and fetch_api2 run concurrently, saving to state.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-18-22)# synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-1)// Conceptual Code: Parallel Information Gathering
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-3)importcom.google.adk.agents.ParallelAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-4)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-5)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-6)LlmAgentfetchApi1=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-7).name("API1Fetcher")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-8).instruction("Fetch data from API 1.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-9).outputKey("api1_data")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-10).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-11)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-12)LlmAgentfetchApi2=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-13).name("API2Fetcher")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-14).instruction("Fetch data from API 2.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-15).outputKey("api2_data")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-16).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-17)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-18)ParallelAgentgatherConcurrently=ParallelAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-19).name("ConcurrentFetcher")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-20).subAgents(fetchApi2,fetchApi1)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-21).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-22)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-23)LlmAgentsynthesizer=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-24).name("Synthesizer")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-25).instruction("Combine results from {api1_data} and {api2_data}.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-26).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-27)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-28)SequentialAgentoverallWorfklow=SequentialAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-29).name("FetchAndSynthesize")// Run parallel fetch, then synthesize
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-30).subAgents(gatherConcurrently,synthesizer)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-31).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-32)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-33)// fetch_api1 and fetch_api2 run concurrently, saving to state.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-19-34)// synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].

```

### Hierarchical Task Decomposition[¶](https://google.github.io/adk-docs/agents/multi-agents/#hierarchical-task-decomposition "Permanent link")
  * **Structure:** A multi-level tree of agents where higher-level agents break down complex goals and delegate sub-tasks to lower-level agents.
  * **Goal:** Solve complex problems by recursively breaking them down into simpler, executable steps.
  * **ADK Primitives Used:**
    * **Hierarchy:** Multi-level `parent_agent`/`sub_agents` structure.
    * **Interaction:** Primarily **LLM-Driven Delegation** or **Explicit Invocation (`AgentTool`)** used by parent agents to assign tasks to subagents. Results are returned up the hierarchy (via tool responses or state).


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_10)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_10)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-1)# Conceptual Code: Hierarchical Research Task
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-2)fromgoogle.adk.agentsimport LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-3)fromgoogle.adk.toolsimport agent_tool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-5)# Low-level tool-like agents
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-6)web_searcher = LlmAgent(name="WebSearch", description="Performs web searches for facts.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-7)summarizer = LlmAgent(name="Summarizer", description="Summarizes text.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-8)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-9)# Mid-level agent combining tools
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-10)research_assistant = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-11)  name="ResearchAssistant",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-12)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-13)  description="Finds and summarizes information on a topic.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-14)  tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-15))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-16)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-17)# High-level agent delegating research
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-18)report_writer = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-19)  name="ReportWriter",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-20)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-21)  instruction="Write a report on topic X. Use the ResearchAssistant to gather information.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-22)  tools=[agent_tool.AgentTool(agent=research_assistant)]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-23)  # Alternatively, could use LLM Transfer if research_assistant is a sub_agent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-24))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-25)# User interacts with ReportWriter.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-26)# ReportWriter calls ResearchAssistant tool.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-27)# ResearchAssistant calls WebSearch and Summarizer tools.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-20-28)# Results flow back up.

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-1)// Conceptual Code: Hierarchical Research Task
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-3)importcom.google.adk.tools.AgentTool;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-5)// Low-level tool-like agents
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-6)LlmAgentwebSearcher=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-7).name("WebSearch")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-8).description("Performs web searches for facts.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-9).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-10)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-11)LlmAgentsummarizer=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-12).name("Summarizer")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-13).description("Summarizes text.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-14).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-15)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-16)// Mid-level agent combining tools
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-17)LlmAgentresearchAssistant=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-18).name("ResearchAssistant")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-19).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-20).description("Finds and summarizes information on a topic.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-21).tools(AgentTool.create(webSearcher),AgentTool.create(summarizer))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-22).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-23)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-24)// High-level agent delegating research
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-25)LlmAgentreportWriter=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-26).name("ReportWriter")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-27).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-28).instruction("Write a report on topic X. Use the ResearchAssistant to gather information.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-29).tools(AgentTool.create(researchAssistant))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-30)// Alternatively, could use LLM Transfer if research_assistant is a subAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-31).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-32)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-33)// User interacts with ReportWriter.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-34)// ReportWriter calls ResearchAssistant tool.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-35)// ResearchAssistant calls WebSearch and Summarizer tools.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-21-36)// Results flow back up.

```

### Review/Critique Pattern (Generator-Critic)[¶](https://google.github.io/adk-docs/agents/multi-agents/#reviewcritique-pattern-generator-critic "Permanent link")
  * **Structure:** Typically involves two agents within a [`SequentialAgent`](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/): a Generator and a Critic/Reviewer.
  * **Goal:** Improve the quality or validity of generated output by having a dedicated agent review it.
  * **ADK Primitives Used:**
    * **Workflow:** `SequentialAgent` ensures generation happens before review.
    * **Communication:** **Shared Session State** (Generator uses `output_key` to save output; Reviewer reads that state key). The Reviewer might save its feedback to another state key for subsequent steps.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_11)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_11)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-1)# Conceptual Code: Generator-Critic
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-2)fromgoogle.adk.agentsimport SequentialAgent, LlmAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-3)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-4)generator = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-5)  name="DraftWriter",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-6)  instruction="Write a short paragraph about subject X.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-7)  output_key="draft_text"
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-8))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-9)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-10)reviewer = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-11)  name="FactChecker",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-12)  instruction="Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-13)  output_key="review_status"
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-14))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-15)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-16)# Optional: Further steps based on review_status
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-17)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-18)review_pipeline = SequentialAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-19)  name="WriteAndReview",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-20)  sub_agents=[generator, reviewer]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-21))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-22)# generator runs -> saves draft to state['draft_text']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-22-23)# reviewer runs -> reads state['draft_text'], saves status to state['review_status']

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-1)// Conceptual Code: Generator-Critic
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-3)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-5)LlmAgentgenerator=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-6).name("DraftWriter")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-7).instruction("Write a short paragraph about subject X.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-8).outputKey("draft_text")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-9).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-10)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-11)LlmAgentreviewer=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-12).name("FactChecker")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-13).instruction("Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-14).outputKey("review_status")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-15).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-16)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-17)// Optional: Further steps based on review_status
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-18)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-19)SequentialAgentreviewPipeline=SequentialAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-20).name("WriteAndReview")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-21).subAgents(generator,reviewer)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-22).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-23)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-24)// generator runs -> saves draft to state['draft_text']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-23-25)// reviewer runs -> reads state['draft_text'], saves status to state['review_status']

```

### Iterative Refinement Pattern[¶](https://google.github.io/adk-docs/agents/multi-agents/#iterative-refinement-pattern "Permanent link")
  * **Structure:** Uses a [`LoopAgent`](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/) containing one or more agents that work on a task over multiple iterations.
  * **Goal:** Progressively improve a result (e.g., code, text, plan) stored in the session state until a quality threshold is met or a maximum number of iterations is reached.
  * **ADK Primitives Used:**
    * **Workflow:** `LoopAgent` manages the repetition.
    * **Communication:** **Shared Session State** is essential for agents to read the previous iteration's output and save the refined version.
    * **Termination:** The loop typically ends based on `max_iterations` or a dedicated checking agent setting `escalate=True` in the `Event Actions` when the result is satisfactory.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_12)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_12)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-1)# Conceptual Code: Iterative Code Refinement
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-2)fromgoogle.adk.agentsimport LoopAgent, LlmAgent, BaseAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-3)fromgoogle.adk.eventsimport Event, EventActions
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-4)fromgoogle.adk.agents.invocation_contextimport InvocationContext
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-5)fromtypingimport AsyncGenerator
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-6)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-7)# Agent to generate/refine code based on state['current_code'] and state['requirements']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-8)code_refiner = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-9)  name="CodeRefiner",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-10)  instruction="Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-11)  output_key="current_code" # Overwrites previous code in state
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-12))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-13)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-14)# Agent to check if the code meets quality standards
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-15)quality_checker = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-16)  name="QualityChecker",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-17)  instruction="Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-18)  output_key="quality_status"
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-19))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-20)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-21)# Custom agent to check the status and escalate if 'pass'
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-22)classCheckStatusAndEscalate(BaseAgent):
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-23)  async def_run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-24)    status = ctx.session.state.get("quality_status", "fail")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-25)    should_stop = (status == "pass")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-26)    yield Event(author=self.name, actions=EventActions(escalate=should_stop))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-27)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-28)refinement_loop = LoopAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-29)  name="CodeRefinementLoop",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-30)  max_iterations=5,
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-31)  sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-32))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-33)# Loop runs: Refiner -> Checker -> StopChecker
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-34)# State['current_code'] is updated each iteration.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-24-35)# Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-1)// Conceptual Code: Iterative Code Refinement
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-2)importcom.google.adk.agents.BaseAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-3)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-4)importcom.google.adk.agents.LoopAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-5)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-6)importcom.google.adk.events.EventActions;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-7)importcom.google.adk.agents.InvocationContext;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-8)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-9)importjava.util.List;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-10)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-11)// Agent to generate/refine code based on state['current_code'] and state['requirements']
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-12)LlmAgentcodeRefiner=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-13).name("CodeRefiner")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-14).instruction("Read state['current_code'] (if exists) and state['requirements']. Generate/refine Java code to meet requirements. Save to state['current_code'].")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-15).outputKey("current_code")// Overwrites previous code in state
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-16).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-17)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-18)// Agent to check if the code meets quality standards
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-19)LlmAgentqualityChecker=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-20).name("QualityChecker")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-21).instruction("Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-22).outputKey("quality_status")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-23).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-24)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-25)BaseAgentcheckStatusAndEscalate=newBaseAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-26)"StopChecker","Checks quality_status and escalates if 'pass'.",List.of(),null,null){
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-27)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-28)@Override
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-29)protectedFlowable<Event>runAsyncImpl(InvocationContextinvocationContext){
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-30)Stringstatus=(String)invocationContext.session().state().getOrDefault("quality_status","fail");
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-31)booleanshouldStop="pass".equals(status);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-32)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-33)EventActionsactions=EventActions.builder().escalate(shouldStop).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-34)Eventevent=Event.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-35).author(this.name())
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-36).actions(actions)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-37).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-38)returnFlowable.just(event);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-39)}
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-40)};
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-41)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-42)LoopAgentrefinementLoop=LoopAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-43).name("CodeRefinementLoop")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-44).maxIterations(5)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-45).subAgents(codeRefiner,qualityChecker,checkStatusAndEscalate)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-46).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-47)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-48)// Loop runs: Refiner -> Checker -> StopChecker
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-49)// State['current_code'] is updated each iteration.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-50)// Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-25-51)// iterations.

```

### Human-in-the-Loop Pattern[¶](https://google.github.io/adk-docs/agents/multi-agents/#human-in-the-loop-pattern "Permanent link")
  * **Structure:** Integrates human intervention points within an agent workflow.
  * **Goal:** Allow for human oversight, approval, correction, or tasks that AI cannot perform.
  * **ADK Primitives Used (Conceptual):**
    * **Interaction:** Can be implemented using a custom **Tool** that pauses execution and sends a request to an external system (e.g., a UI, ticketing system) waiting for human input. The tool then returns the human's response to the agent.
    * **Workflow:** Could use **LLM-Driven Delegation** (`transfer_to_agent`) targeting a conceptual "Human Agent" that triggers the external workflow, or use the custom tool within an `LlmAgent`.
    * **State/Callbacks:** State can hold task details for the human; callbacks can manage the interaction flow.
    * **Note:** ADK doesn't have a built-in "Human Agent" type, so this requires custom integration.


[Python](https://google.github.io/adk-docs/agents/multi-agents/#python_13)[Java](https://google.github.io/adk-docs/agents/multi-agents/#java_13)
```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-1)# Conceptual Code: Using a Tool for Human Approval
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-2)fromgoogle.adk.agentsimport LlmAgent, SequentialAgent
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-3)fromgoogle.adk.toolsimport FunctionTool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-4)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-5)# --- Assume external_approval_tool exists ---
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-6)# This tool would:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-7)# 1. Take details (e.g., request_id, amount, reason).
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-8)# 2. Send these details to a human review system (e.g., via API).
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-9)# 3. Poll or wait for the human response (approved/rejected).
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-10)# 4. Return the human's decision.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-11)# async def external_approval_tool(amount: float, reason: str) -> str: ...
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-12)approval_tool = FunctionTool(func=external_approval_tool)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-13)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-14)# Agent that prepares the request
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-15)prepare_request = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-16)  name="PrepareApproval",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-17)  instruction="Prepare the approval request details based on user input. Store amount and reason in state.",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-18)  # ... likely sets state['approval_amount'] and state['approval_reason'] ...
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-19))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-20)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-21)# Agent that calls the human approval tool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-22)request_approval = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-23)  name="RequestHumanApproval",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-24)  instruction="Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-25)  tools=[approval_tool],
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-26)  output_key="human_decision"
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-27))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-28)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-29)# Agent that proceeds based on human decision
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-30)process_decision = LlmAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-31)  name="ProcessDecision",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-32)  instruction="Check {human_decision}. If 'approved', proceed. If 'rejected', inform user."
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-33))
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-34)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-35)approval_workflow = SequentialAgent(
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-36)  name="HumanApprovalWorkflow",
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-37)  sub_agents=[prepare_request, request_approval, process_decision]
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-26-38))

```

```
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-1)// Conceptual Code: Using a Tool for Human Approval
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-2)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-3)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-4)importcom.google.adk.tools.FunctionTool;
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-5)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-6)// --- Assume external_approval_tool exists ---
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-7)// This tool would:
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-8)// 1. Take details (e.g., request_id, amount, reason).
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-9)// 2. Send these details to a human review system (e.g., via API).
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-10)// 3. Poll or wait for the human response (approved/rejected).
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-11)// 4. Return the human's decision.
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-12)// public boolean externalApprovalTool(float amount, String reason) { ... }
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-13)FunctionToolapprovalTool=FunctionTool.create(externalApprovalTool);
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-14)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-15)// Agent that prepares the request
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-16)LlmAgentprepareRequest=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-17).name("PrepareApproval")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-18).instruction("Prepare the approval request details based on user input. Store amount and reason in state.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-19)// ... likely sets state['approval_amount'] and state['approval_reason'] ...
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-20).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-21)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-22)// Agent that calls the human approval tool
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-23)LlmAgentrequestApproval=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-24).name("RequestHumanApproval")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-25).instruction("Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-26).tools(approvalTool)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-27).outputKey("human_decision")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-28).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-29)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-30)// Agent that proceeds based on human decision
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-31)LlmAgentprocessDecision=LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-32).name("ProcessDecision")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-33).instruction("Check {human_decision}. If 'approved', proceed. If 'rejected', inform user.")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-34).build();
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-35)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-36)SequentialAgentapprovalWorkflow=SequentialAgent.builder()
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-37).name("HumanApprovalWorkflow")
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-38).subAgents(prepareRequest,requestApproval,processDecision)
[](https://google.github.io/adk-docs/agents/multi-agents/#__codelineno-27-39).build();

```

These patterns provide starting points for structuring your multi-agent systems. You can mix and match them as needed to create the most effective architecture for your specific application.
Back to top
