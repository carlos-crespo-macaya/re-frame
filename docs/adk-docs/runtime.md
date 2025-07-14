[ Skip to content ](https://google.github.io/adk-docs/runtime/#runtime)
# Runtime[¶](https://google.github.io/adk-docs/runtime/#runtime "Permanent link")
## What is runtime?[¶](https://google.github.io/adk-docs/runtime/#what-is-runtime "Permanent link")
The ADK Runtime is the underlying engine that powers your agent application during user interactions. It's the system that takes your defined agents, tools, and callbacks and orchestrates their execution in response to user input, managing the flow of information, state changes, and interactions with external services like LLMs or storage.
Think of the Runtime as the **"engine"** of your agentic application. You define the parts (agents, tools), and the Runtime handles how they connect and run together to fulfill a user's request.
## Core Idea: The Event Loop[¶](https://google.github.io/adk-docs/runtime/#core-idea-the-event-loop "Permanent link")
At its heart, the ADK Runtime operates on an **Event Loop**. This loop facilitates a back-and-forth communication between the `Runner` component and your defined "Execution Logic" (which includes your Agents, the LLM calls they make, Callbacks, and Tools).
![intro_components.png](https://google.github.io/adk-docs/assets/event-loop.png)
In simple terms:
  1. The `Runner` receives a user query and asks the main `Agent` to start processing.
  2. The `Agent` (and its associated logic) runs until it has something to report (like a response, a request to use a tool, or a state change) – it then **yields** or **emits** an `Event`.
  3. The `Runner` receives this `Event`, processes any associated actions (like saving state changes via `Services`), and forwards the event onwards (e.g., to the user interface).
  4. Only _after_ the `Runner` has processed the event does the `Agent`'s logic **resume** from where it paused, now potentially seeing the effects of the changes committed by the Runner.
  5. This cycle repeats until the agent has no more events to yield for the current user query.


This event-driven loop is the fundamental pattern governing how ADK executes your agent code.
## The Heartbeat: The Event Loop - Inner workings[¶](https://google.github.io/adk-docs/runtime/#the-heartbeat-the-event-loop-inner-workings "Permanent link")
The Event Loop is the core operational pattern defining the interaction between the `Runner` and your custom code (Agents, Tools, Callbacks, collectively referred to as "Execution Logic" or "Logic Components" in the design document). It establishes a clear division of responsibilities:
Note
The specific method names and parameter names may vary slightly by SDK language (e.g., `agent_to_run.runAsync(...)` in Java, `agent_to_run.run_async(...)` in Python). Refer to the language-specific API documentation for details.
### Runner's Role (Orchestrator)[¶](https://google.github.io/adk-docs/runtime/#runners-role-orchestrator "Permanent link")
The `Runner` acts as the central coordinator for a single user invocation. Its responsibilities in the loop are:
  1. **Initiation:** Receives the end user's query (`new_message`) and typically appends it to the session history via the `SessionService`.
  2. **Kick-off:** Starts the event generation process by calling the main agent's execution method (e.g., `agent_to_run.run_async(...)`).
  3. **Receive & Process:** Waits for the agent logic to `yield` or `emit` an `Event`. Upon receiving an event, the Runner **promptly processes** it. This involves:
     * Using configured `Services` (`SessionService`, `ArtifactService`, `MemoryService`) to commit changes indicated in `event.actions` (like `state_delta`, `artifact_delta`).
     * Performing other internal bookkeeping.
  4. **Yield Upstream:** Forwards the processed event onwards (e.g., to the calling application or UI for rendering).
  5. **Iterate:** Signals the agent logic that processing is complete for the yielded event, allowing it to resume and generate the _next_ event.


_Conceptual Runner Loop:_
[Python](https://google.github.io/adk-docs/runtime/#python)[Java](https://google.github.io/adk-docs/runtime/#java)
```
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-1)# Simplified view of Runner's main loop logic
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-2)defrun(new_query, ...) -> Generator[Event]:
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-3)  # 1. Append new_query to session event history (via SessionService)
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-4)  session_service.append_event(session, Event(author='user', content=new_query))
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-5)
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-6)  # 2. Kick off event loop by calling the agent
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-7)  agent_event_generator = agent_to_run.run_async(context)
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-8)
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-9)  async for event in agent_event_generator:
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-10)    # 3. Process the generated event and commit changes
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-11)    session_service.append_event(session, event) # Commits state/artifact deltas etc.
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-12)    # memory_service.update_memory(...) # If applicable
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-13)    # artifact_service might have already been called via context during agent run
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-14)
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-15)    # 4. Yield event for upstream processing (e.g., UI rendering)
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-16)    yield event
[](https://google.github.io/adk-docs/runtime/#__codelineno-0-17)    # Runner implicitly signals agent generator can continue after yielding

```

```
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-1)// Simplified conceptual view of the Runner's main loop logic in Java.
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-2)publicFlowable<Event>runConceptual(
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-3)Sessionsession,
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-4)InvocationContextinvocationContext,
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-5)ContentnewQuery
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-6)){
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-7)
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-8)// 1. Append new_query to session event history (via SessionService)
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-9)// ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-10)sessionService.appendEvent(session,userEvent).blockingGet();
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-11)
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-12)// 2. Kick off event stream by calling the agent
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-13)Flowable<Event>agentEventStream=agentToRun.runAsync(invocationContext);
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-14)
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-15)// 3. Process each generated event, commit changes, and "yield" or "emit"
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-16)returnagentEventStream.map(event->{
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-17)// This mutates the session object (adds event, applies stateDelta).
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-18)// The return value of appendEvent (a Single<Event>) is conceptually
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-19)// just the event itself after processing.
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-20)sessionService.appendEvent(session,event).blockingGet();// Simplified blocking call
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-21)
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-22)// memory_service.update_memory(...) // If applicable - conceptual
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-23)// artifact_service might have already been called via context during agent run
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-24)
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-25)// 4. "Yield" event for upstream processing
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-26)//  In RxJava, returning the event in map effectively yields it to the next operator or subscriber.
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-27)returnevent;
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-28)});
[](https://google.github.io/adk-docs/runtime/#__codelineno-1-29)}

```

### Execution Logic's Role (Agent, Tool, Callback)[¶](https://google.github.io/adk-docs/runtime/#execution-logics-role-agent-tool-callback "Permanent link")
Your code within agents, tools, and callbacks is responsible for the actual computation and decision-making. Its interaction with the loop involves:
  1. **Execute:** Runs its logic based on the current `InvocationContext`, including the session state _as it was when execution resumed_.
  2. **Yield:** When the logic needs to communicate (send a message, call a tool, report a state change), it constructs an `Event` containing the relevant content and actions, and then `yield`s this event back to the `Runner`.
  3. **Pause:** Crucially, execution of the agent logic **pauses immediately** after the `yield` statement (or `return` in RxJava). It waits for the `Runner` to complete step 3 (processing and committing).
  4. **Resume:** _Only after_ the `Runner` has processed the yielded event does the agent logic resume execution from the statement immediately following the `yield`.
  5. **See Updated State:** Upon resumption, the agent logic can now reliably access the session state (`ctx.session.state`) reflecting the changes that were committed by the `Runner` from the _previously yielded_ event.


_Conceptual Execution Logic:_
[Python](https://google.github.io/adk-docs/runtime/#python_1)[Java](https://google.github.io/adk-docs/runtime/#java_1)
```
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-1)# Simplified view of logic inside Agent.run_async, callbacks, or tools
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-2)
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-3)# ... previous code runs based on current state ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-4)
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-5)# 1. Determine a change or output is needed, construct the event
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-6)# Example: Updating state
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-7)update_data = {'field_1': 'value_2'}
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-8)event_with_state_change = Event(
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-9)  author=self.name,
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-10)  actions=EventActions(state_delta=update_data),
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-11)  content=types.Content(parts=[types.Part(text="State updated.")])
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-12)  # ... other event fields ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-13))
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-14)
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-15)# 2. Yield the event to the Runner for processing & commit
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-16)yield event_with_state_change
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-17)# <<<<<<<<<<<< EXECUTION PAUSES HERE >>>>>>>>>>>>
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-18)
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-19)# <<<<<<<<<<<< RUNNER PROCESSES & COMMITS THE EVENT >>>>>>>>>>>>
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-20)
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-21)# 3. Resume execution ONLY after Runner is done processing the above event.
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-22)# Now, the state committed by the Runner is reliably reflected.
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-23)# Subsequent code can safely assume the change from the yielded event happened.
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-24)val = ctx.session.state['field_1']
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-25)# here `val` is guaranteed to be "value_2" (assuming Runner committed successfully)
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-26)print(f"Resumed execution. Value of field_1 is now: {val}")
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-27)
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-28)# ... subsequent code continues ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-2-29)# Maybe yield another event later...

```

```
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-1)// Simplified view of logic inside Agent.runAsync, callbacks, or tools
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-2)// ... previous code runs based on current state ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-3)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-4)// 1. Determine a change or output is needed, construct the event
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-5)// Example: Updating state
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-6)ConcurrentMap<String,Object>updateData=newConcurrentHashMap<>();
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-7)updateData.put("field_1","value_2");
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-8)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-9)EventActionsactions=EventActions.builder().stateDelta(updateData).build();
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-10)ContenteventContent=Content.builder().parts(Part.fromText("State updated.")).build();
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-11)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-12)EventeventWithStateChange=Event.builder()
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-13).author(self.name())
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-14).actions(actions)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-15).content(Optional.of(eventContent))
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-16)// ... other event fields ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-17).build();
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-18)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-19)// 2. "Yield" the event. In RxJava, this means emitting it into the stream.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-20)//  The Runner (or upstream consumer) will subscribe to this Flowable.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-21)//  When the Runner receives this event, it will process it (e.g., call sessionService.appendEvent).
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-22)//  The 'appendEvent' in Java ADK mutates the 'Session' object held within 'ctx' (InvocationContext).
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-23)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-24)// <<<<<<<<<<<< CONCEPTUAL PAUSE POINT >>>>>>>>>>>>
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-25)// In RxJava, the emission of 'eventWithStateChange' happens, and then the stream
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-26)// might continue with a 'flatMap' or 'concatMap' operator that represents
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-27)// the logic *after* the Runner has processed this event.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-28)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-29)// To model the "resume execution ONLY after Runner is done processing":
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-30)// The Runner's `appendEvent` is usually an async operation itself (returns Single<Event>).
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-31)// The agent's flow needs to be structured such that subsequent logic
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-32)// that depends on the committed state runs *after* that `appendEvent` completes.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-33)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-34)// This is how the Runner typically orchestrates it:
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-35)// Runner:
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-36)//  agent.runAsync(ctx)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-37)//   .concatMapEager(eventFromAgent ->
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-38)//     sessionService.appendEvent(ctx.session(), eventFromAgent) // This updates ctx.session().state()
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-39)//       .toFlowable() // Emits the event after it's processed
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-40)//   )
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-41)//   .subscribe(processedEvent -> { /* UI renders processedEvent */ });
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-42)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-43)// So, within the agent's own logic, if it needs to do something *after* an event it yielded
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-44)// has been processed and its state changes are reflected in ctx.session().state(),
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-45)// that subsequent logic would typically be in another step of its reactive chain.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-46)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-47)// For this conceptual example, we'll emit the event, and then simulate the "resume"
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-48)// as a subsequent operation in the Flowable chain.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-49)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-50)returnFlowable.just(eventWithStateChange)// Step 2: Yield the event
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-51).concatMap(yieldedEvent->{
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-52)// <<<<<<<<<<<< RUNNER CONCEPTUALLY PROCESSES & COMMITS THE EVENT >>>>>>>>>>>>
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-53)// At this point, in a real runner, ctx.session().appendEvent(yieldedEvent) would have been called
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-54)// by the Runner, and ctx.session().state() would be updated.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-55)// Since we are *inside* the agent's conceptual logic trying to model this,
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-56)// we assume the Runner's action has implicitly updated our 'ctx.session()'.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-57)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-58)// 3. Resume execution.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-59)// Now, the state committed by the Runner (via sessionService.appendEvent)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-60)// is reliably reflected in ctx.session().state().
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-61)Objectval=ctx.session().state().get("field_1");
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-62)// here `val` is guaranteed to be "value_2" because the `sessionService.appendEvent`
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-63)// called by the Runner would have updated the session state within the `ctx` object.
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-64)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-65)System.out.println("Resumed execution. Value of field_1 is now: "+val);
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-66)
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-67)// ... subsequent code continues ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-3-68)// If this subsequent code needs to yield another event, it would do so here.

```

This cooperative yield/pause/resume cycle between the `Runner` and your Execution Logic, mediated by `Event` objects, forms the core of the ADK Runtime.
## Key components of the Runtime[¶](https://google.github.io/adk-docs/runtime/#REDACTED "Permanent link")
Several components work together within the ADK Runtime to execute an agent invocation. Understanding their roles clarifies how the event loop functions:
  1. ### `Runner`[¶](https://google.github.io/adk-docs/runtime/#runner "Permanent link")
     * **Role:** The main entry point and orchestrator for a single user query (`run_async`).
     * **Function:** Manages the overall Event Loop, receives events yielded by the Execution Logic, coordinates with Services to process and commit event actions (state/artifact changes), and forwards processed events upstream (e.g., to the UI). It essentially drives the conversation turn by turn based on yielded events. (Defined in `google.adk.runners.runner`).
  2. ### Execution Logic Components[¶](https://google.github.io/adk-docs/runtime/#execution-logic-components "Permanent link")
     * **Role:** The parts containing your custom code and the core agent capabilities.
     * **Components:**
     * `Agent` (`BaseAgent`, `LlmAgent`, etc.): Your primary logic units that process information and decide on actions. They implement the `_run_async_impl` method which yields events.
     * `Tools` (`BaseTool`, `FunctionTool`, `AgentTool`, etc.): External functions or capabilities used by agents (often `LlmAgent`) to interact with the outside world or perform specific tasks. They execute and return results, which are then wrapped in events.
     * `Callbacks` (Functions): User-defined functions attached to agents (e.g., `before_agent_callback`, `after_model_callback`) that hook into specific points in the execution flow, potentially modifying behavior or state, whose effects are captured in events.
     * **Function:** Perform the actual thinking, calculation, or external interaction. They communicate their results or needs by **yielding`Event` objects** and pausing until the Runner processes them.
  3. ### `Event`[¶](https://google.github.io/adk-docs/runtime/#event "Permanent link")
     * **Role:** The message passed back and forth between the `Runner` and the Execution Logic.
     * **Function:** Represents an atomic occurrence (user input, agent text, tool call/result, state change request, control signal). It carries both the content of the occurrence and the intended side effects (`actions` like `state_delta`).
  4. ### `Services`[¶](https://google.github.io/adk-docs/runtime/#services "Permanent link")
     * **Role:** Backend components responsible for managing persistent or shared resources. Used primarily by the `Runner` during event processing.
     * **Components:**
     * `SessionService` (`BaseSessionService`, `InMemorySessionService`, etc.): Manages `Session` objects, including saving/loading them, applying `state_delta` to the session state, and appending events to the `event history`.
     * `ArtifactService` (`BaseArtifactService`, `InMemoryArtifactService`, `GcsArtifactService`, etc.): Manages the storage and retrieval of binary artifact data. Although `save_artifact` is called via context during execution logic, the `artifact_delta` in the event confirms the action for the Runner/SessionService.
     * `MemoryService` (`BaseMemoryService`, etc.): (Optional) Manages long-term semantic memory across sessions for a user.
     * **Function:** Provide the persistence layer. The `Runner` interacts with them to ensure changes signaled by `event.actions` are reliably stored _before_ the Execution Logic resumes.
  5. ### `Session`[¶](https://google.github.io/adk-docs/runtime/#session "Permanent link")
     * **Role:** A data container holding the state and history for _one specific conversation_ between a user and the application.
     * **Function:** Stores the current `state` dictionary, the list of all past `events` (`event history`), and references to associated artifacts. It's the primary record of the interaction, managed by the `SessionService`.
  6. ### `Invocation`[¶](https://google.github.io/adk-docs/runtime/#invocation "Permanent link")
     * **Role:** A conceptual term representing everything that happens in response to a _single_ user query, from the moment the `Runner` receives it until the agent logic finishes yielding events for that query.
     * **Function:** An invocation might involve multiple agent runs (if using agent transfer or `AgentTool`), multiple LLM calls, tool executions, and callback executions, all tied together by a single `invocation_id` within the `InvocationContext`.


These players interact continuously through the Event Loop to process a user's request.
## How It Works: A Simplified Invocation[¶](https://google.github.io/adk-docs/runtime/#how-it-works-a-simplified-invocation "Permanent link")
Let's trace a simplified flow for a typical user query that involves an LLM agent calling a tool:
![intro_components.png](https://google.github.io/adk-docs/assets/invocation-flow.png)
### Step-by-Step Breakdown[¶](https://google.github.io/adk-docs/runtime/#step-by-step-breakdown "Permanent link")
  1. **User Input:** The User sends a query (e.g., "What's the capital of France?").
  2. **Runner Starts:** `Runner.run_async` begins. It interacts with the `SessionService` to load the relevant `Session` and adds the user query as the first `Event` to the session history. An `InvocationContext` (`ctx`) is prepared.
  3. **Agent Execution:** The `Runner` calls `agent.run_async(ctx)` on the designated root agent (e.g., an `LlmAgent`).
  4. **LLM Call (Example):** The `Agent_Llm` determines it needs information, perhaps by calling a tool. It prepares a request for the `LLM`. Let's assume the LLM decides to call `MyTool`.
  5. **Yield FunctionCall Event:** The `Agent_Llm` receives the `FunctionCall` response from the LLM, wraps it in an `Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))`, and `yields` or `emits` this event.
  6. **Agent Pauses:** The `Agent_Llm`'s execution pauses immediately after the `yield`.
  7. **Runner Processes:** The `Runner` receives the FunctionCall event. It passes it to the `SessionService` to record it in the history. The `Runner` then yields the event upstream to the `User` (or application).
  8. **Agent Resumes:** The `Runner` signals that the event is processed, and `Agent_Llm` resumes execution.
  9. **Tool Execution:** The `Agent_Llm`'s internal flow now proceeds to execute the requested `MyTool`. It calls `tool.run_async(...)`.
  10. **Tool Returns Result:** `MyTool` executes and returns its result (e.g., `{'result': 'Paris'}`).
  11. **Yield FunctionResponse Event:** The agent (`Agent_Llm`) wraps the tool result into an `Event` containing a `FunctionResponse` part (e.g., `Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))`). This event might also contain `actions` if the tool modified state (`state_delta`) or saved artifacts (`artifact_delta`). The agent `yield`s this event.
  12. **Agent Pauses:** `Agent_Llm` pauses again.
  13. **Runner Processes:** `Runner` receives the FunctionResponse event. It passes it to `SessionService` which applies any `state_delta`/`artifact_delta` and adds the event to history. `Runner` yields the event upstream.
  14. **Agent Resumes:** `Agent_Llm` resumes, now knowing the tool result and any state changes are committed.
  15. **Final LLM Call (Example):** `Agent_Llm` sends the tool result back to the `LLM` to generate a natural language response.
  16. **Yield Final Text Event:** `Agent_Llm` receives the final text from the `LLM`, wraps it in an `Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))`, and `yield`s it.
  17. **Agent Pauses:** `Agent_Llm` pauses.
  18. **Runner Processes:** `Runner` receives the final text event, passes it to `SessionService` for history, and yields it upstream to the `User`. This is likely marked as the `is_final_response()`.
  19. **Agent Resumes & Finishes:** `Agent_Llm` resumes. Having completed its task for this invocation, its `run_async` generator finishes.
  20. **Runner Completes:** The `Runner` sees the agent's generator is exhausted and finishes its loop for this invocation.


This yield/pause/process/resume cycle ensures that state changes are consistently applied and that the execution logic always operates on the most recently committed state after yielding an event.
## Important Runtime Behaviors[¶](https://google.github.io/adk-docs/runtime/#important-runtime-behaviors "Permanent link")
Understanding a few key aspects of how the ADK Runtime handles state, streaming, and asynchronous operations is crucial for building predictable and efficient agents.
### State Updates & Commitment Timing[¶](https://google.github.io/adk-docs/runtime/#state-updates-commitment-timing "Permanent link")
  * **The Rule:** When your code (in an agent, tool, or callback) modifies the session state (e.g., `context.state['my_key'] = 'new_value'`), this change is initially recorded locally within the current `InvocationContext`. The change is only **guaranteed to be persisted** (saved by the `SessionService`) _after_ the `Event` carrying the corresponding `state_delta` in its `actions` has been `yield`-ed by your code and subsequently processed by the `Runner`.
  * **Implication:** Code that runs _after_ resuming from a `yield` can reliably assume that the state changes signaled in the _yielded event_ have been committed.


[Python](https://google.github.io/adk-docs/runtime/#python_2)[Java](https://google.github.io/adk-docs/runtime/#java_2)
```
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-1)# Inside agent logic (conceptual)
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-2)
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-3)# 1. Modify state
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-4)ctx.session.state['status'] = 'processing'
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-5)event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-6)
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-7)# 2. Yield event with the delta
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-8)yield event1
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-9)# --- PAUSE --- Runner processes event1, SessionService commits 'status' = 'processing' ---
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-10)
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-11)# 3. Resume execution
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-12)# Now it's safe to rely on the committed state
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-13)current_status = ctx.session.state['status'] # Guaranteed to be 'processing'
[](https://google.github.io/adk-docs/runtime/#__codelineno-4-14)print(f"Status after resuming: {current_status}")

```

```
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-1)// Inside agent logic (conceptual)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-2)// ... previous code runs based on current state ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-3)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-4)// 1. Prepare state modification and construct the event
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-5)ConcurrentHashMap<String,Object>stateChanges=newConcurrentHashMap<>();
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-6)stateChanges.put("status","processing");
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-7)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-8)EventActionsactions=EventActions.builder().stateDelta(stateChanges).build();
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-9)Contentcontent=Content.builder().parts(Part.fromText("Status update: processing")).build();
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-10)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-11)Eventevent1=Event.builder()
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-12).actions(actions)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-13)// ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-14).build();
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-15)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-16)// 2. Yield event with the delta
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-17)returnFlowable.just(event1)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-18).map(
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-19)emittedEvent->{
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-20)// --- CONCEPTUAL PAUSE & RUNNER PROCESSING ---
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-21)// 3. Resume execution (conceptually)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-22)// Now it's safe to rely on the committed state.
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-23)StringcurrentStatus=(String)ctx.session().state().get("status");
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-24)System.out.println("Status after resuming (inside agent logic): "+currentStatus);// Guaranteed to be 'processing'
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-25)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-26)// The event itself (event1) is passed on.
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-27)// If subsequent logic within this agent step produced *another* event,
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-28)// you'd use concatMap to emit that new event.
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-29)returnemittedEvent;
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-30)});
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-31)
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-32)// ... subsequent agent logic might involve further reactive operators
[](https://google.github.io/adk-docs/runtime/#__codelineno-5-33)// or emitting more events based on the now-updated `ctx.session().state()`.

```

### "Dirty Reads" of Session State[¶](https://google.github.io/adk-docs/runtime/#dirty-reads-of-session-state "Permanent link")
  * **Definition:** While commitment happens _after_ the yield, code running _later within the same invocation_ , but _before_ the state-changing event is actually yielded and processed, **can often see the local, uncommitted changes**. This is sometimes called a "dirty read".
  * **Example:**


[Python](https://google.github.io/adk-docs/runtime/#python_3)[Java](https://google.github.io/adk-docs/runtime/#java_3)
```
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-1)# Code in before_agent_callback
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-2)callback_context.state['field_1'] = 'value_1'
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-3)# State is locally set to 'value_1', but not yet committed by Runner
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-4)
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-5)# ... agent runs ...
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-6)
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-7)# Code in a tool called later *within the same invocation*
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-8)# Readable (dirty read), but 'value_1' isn't guaranteed persistent yet.
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-9)val = tool_context.state['field_1'] # 'val' will likely be 'value_1' here
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-10)print(f"Dirty read value in tool: {val}")
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-11)
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-12)# Assume the event carrying the state_delta={'field_1': 'value_1'}
[](https://google.github.io/adk-docs/runtime/#__codelineno-6-13)# is yielded *after* this tool runs and is processed by the Runner.

```

```
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-1)// Modify state - Code in BeforeAgentCallback
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-2)// AND stages this change in callbackContext.eventActions().stateDelta().
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-3)callbackContext.state().put("field_1","value_1");
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-4)
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-5)// --- agent runs ... ---
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-6)
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-7)// --- Code in a tool called later *within the same invocation* ---
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-8)// Readable (dirty read), but 'value_1' isn't guaranteed persistent yet.
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-9)Objectval=toolContext.state().get("field_1");// 'val' will likely be 'value_1' here
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-10)System.out.println("Dirty read value in tool: "+val);
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-11)// Assume the event carrying the state_delta={'field_1': 'value_1'}
[](https://google.github.io/adk-docs/runtime/#__codelineno-7-12)// is yielded *after* this tool runs and is processed by the Runner.

```

  * **Implications:**
  * **Benefit:** Allows different parts of your logic within a single complex step (e.g., multiple callbacks or tool calls before the next LLM turn) to coordinate using state without waiting for a full yield/commit cycle.
  * **Caveat:** Relying heavily on dirty reads for critical logic can be risky. If the invocation fails _before_ the event carrying the `state_delta` is yielded and processed by the `Runner`, the uncommitted state change will be lost. For critical state transitions, ensure they are associated with an event that gets successfully processed.


### Streaming vs. Non-Streaming Output (`partial=True`)[¶](https://google.github.io/adk-docs/runtime/#streaming-vs-non-streaming-output-partialtrue "Permanent link")
This primarily relates to how responses from the LLM are handled, especially when using streaming generation APIs.
  * **Streaming:** The LLM generates its response token-by-token or in small chunks.
  * The framework (often within `BaseLlmFlow`) yields multiple `Event` objects for a single conceptual response. Most of these events will have `partial=True`.
  * The `Runner`, upon receiving an event with `partial=True`, typically **forwards it immediately** upstream (for UI display) but **skips processing its`actions`** (like `state_delta`).
  * Eventually, the framework yields a final event for that response, marked as non-partial (`partial=False` or implicitly via `turn_complete=True`).
  * The `Runner` **fully processes only this final event** , committing any associated `state_delta` or `artifact_delta`.
  * **Non-Streaming:** The LLM generates the entire response at once. The framework yields a single event marked as non-partial, which the `Runner` processes fully.
  * **Why it Matters:** Ensures that state changes are applied atomically and only once based on the _complete_ response from the LLM, while still allowing the UI to display text progressively as it's generated.


## Async is Primary (`run_async`)[¶](https://google.github.io/adk-docs/runtime/#async-is-primary-run_async "Permanent link")
  * **Core Design:** The ADK Runtime is fundamentally built on asynchronous libraries (like Python's `asyncio` and Java's `RxJava`) to handle concurrent operations (like waiting for LLM responses or tool executions) efficiently without blocking.
  * **Main Entry Point:** `Runner.run_async` is the primary method for executing agent invocations. All core runnable components (Agents, specific flows) use `asynchronous` methods internally.
  * **Synchronous Convenience (`run`):** A synchronous `Runner.run` method exists mainly for convenience (e.g., in simple scripts or testing environments). However, internally, `Runner.run` typically just calls `Runner.run_async` and manages the async event loop execution for you.
  * **Developer Experience:** We recommend designing your applications (e.g., web servers using ADK) to be asynchronous for best performance. In Python, this means using `asyncio`; in Java, leverage `RxJava`'s reactive programming model.
  * **Sync Callbacks/Tools:** The ADK framework supports both asynchronous and synchronous functions for tools and callbacks.
    * **Blocking I/O:** For long-running synchronous I/O operations, the framework attempts to prevent stalls. Python ADK may use asyncio.to_thread, while Java ADK often relies on appropriate RxJava schedulers or wrappers for blocking calls.
    * **CPU-Bound Work:** Purely CPU-intensive synchronous tasks will still block their execution thread in both environments.


Understanding these behaviors helps you write more robust ADK applications and debug issues related to state consistency, streaming updates, and asynchronous execution.
Back to top
