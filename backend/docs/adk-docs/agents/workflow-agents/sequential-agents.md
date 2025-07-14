[ Skip to content ](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#sequential-agents)
# Sequential agents[¶](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#sequential-agents "Permanent link")
## The `SequentialAgent`[¶](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#the-sequentialagent "Permanent link")
The `SequentialAgent` is a [workflow agent](https://google.github.io/adk-docs/agents/workflow-agents/) that executes its sub-agents in the order they are specified in the list.
Use the `SequentialAgent` when you want the execution to occur in a fixed, strict order.
### Example[¶](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#example "Permanent link")
  * You want to build an agent that can summarize any webpage, using two tools: `Get Page Contents` and `Summarize Page`. Because the agent must always call `Get Page Contents` before calling `Summarize Page` (you can't summarize from nothing!), you should build your agent using a `SequentialAgent`.


As with other [workflow agents](https://google.github.io/adk-docs/agents/workflow-agents/), the `SequentialAgent` is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are concerned only with their execution (i.e. in sequence), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.
### How it works[¶](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#how-it-works "Permanent link")
When the `SequentialAgent`'s `Run Async` method is called, it performs the following actions:
  1. **Iteration:** It iterates through the sub agents list in the order they were provided.
  2. **Sub-Agent Execution:** For each sub-agent in the list, it calls the sub-agent's `Run Async` method.


![Sequential Agent](https://google.github.io/adk-docs/assets/sequential-agent.png)
### Full Example: Code Development Pipeline[¶](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#full-example-code-development-pipeline "Permanent link")
Consider a simplified code development pipeline:
  * **Code Writer Agent:** An LLM Agent that generates initial code based on a specification.
  * **Code Reviewer Agent:** An LLM Agent that reviews the generated code for errors, style issues, and adherence to best practices. It receives the output of the Code Writer Agent.
  * **Code Refactorer Agent:** An LLM Agent that takes the reviewed code (and the reviewer's comments) and refactors it to improve quality and address issues.


A `SequentialAgent` is perfect for this:
```
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-0-1)SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])

```

This ensures the code is written, _then_ reviewed, and _finally_ refactored, in a strict, dependable order. **The output from each sub-agent is passed to the next by storing them in state via[Output Key](https://google.github.io/adk-docs/agents/llm-agents/#structuring-data-input_schema-output_schema-output_key)**.
Code
[Python](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#python)[Java](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#java)
```
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-1)# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-2)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-3)# --- 1. Define Sub-Agents for Each Pipeline Stage ---
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-4)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-5)# Code Writer Agent
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-6)# Takes the initial specification (from user query) and writes code.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-7)code_writer_agent = LlmAgent(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-8)  name="CodeWriterAgent",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-9)  model=GEMINI_MODEL,
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-10)  # Change 3: Improved instruction
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-11)  instruction="""You are a Python Code Generator.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-12)Based *only* on the user's request, write Python code that fulfills the requirement.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-13)Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```).
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-14)Do not add any other text before or after the code block.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-15)""",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-16)  description="Writes initial Python code based on a specification.",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-17)  output_key="generated_code" # Stores output in state['generated_code']
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-18))
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-19)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-20)# Code Reviewer Agent
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-21)# Takes the code generated by the previous agent (read from state) and provides feedback.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-22)code_reviewer_agent = LlmAgent(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-23)  name="CodeReviewerAgent",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-24)  model=GEMINI_MODEL,
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-25)  # Change 3: Improved instruction, correctly using state key injection
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-26)  instruction="""You are an expert Python Code Reviewer.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-27)  Your task is to provide constructive feedback on the provided code.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-28)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-29)  **Code to Review:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-30)  ```python
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-31){generated_code}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-32)  ```
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-33)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-34)**Review Criteria:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-35)1. **Correctness:** Does the code work as intended? Are there logic errors?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-36)2. **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-37)3. **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-38)4. **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-39)5. **Best Practices:** Does the code follow common Python best practices?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-40)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-41)**Output:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-42)Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-43)If the code is excellent and requires no changes, simply state: "No major issues found."
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-44)Output *only* the review comments or the "No major issues" statement.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-45)""",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-46)  description="Reviews code and provides feedback.",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-47)  output_key="review_comments", # Stores output in state['review_comments']
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-48))
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-49)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-50)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-51)# Code Refactorer Agent
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-52)# Takes the original code and the review comments (read from state) and refactors the code.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-53)code_refactorer_agent = LlmAgent(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-54)  name="CodeRefactorerAgent",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-55)  model=GEMINI_MODEL,
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-56)  # Change 3: Improved instruction, correctly using state key injection
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-57)  instruction="""You are a Python Code Refactoring AI.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-58)Your goal is to improve the given Python code based on the provided review comments.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-59)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-60) **Original Code:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-61) ```python
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-62){generated_code}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-63) ```
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-64)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-65) **Review Comments:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-66){review_comments}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-67)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-68)**Task:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-69)Carefully apply the suggestions from the review comments to refactor the original code.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-70)If the review comments state "No major issues found," return the original code unchanged.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-71)Ensure the final code is complete, functional, and includes necessary imports and docstrings.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-72)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-73)**Output:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-74)Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```).
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-75)Do not add any other text before or after the code block.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-76)""",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-77)  description="Refactors code based on review comments.",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-78)  output_key="refactored_code", # Stores output in state['refactored_code']
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-79))
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-80)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-81)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-82)# --- 2. Create the SequentialAgent ---
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-83)# This agent orchestrates the pipeline by running the sub_agents in order.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-84)code_pipeline_agent = SequentialAgent(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-85)  name="CodePipelineAgent",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-86)  sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-87)  description="Executes a sequence of code writing, reviewing, and refactoring.",
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-88)  # The agents will run in the order provided: Writer -> Reviewer -> Refactorer
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-89))
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-90)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-91)# For ADK tools compatibility, the root agent must be named `root_agent`
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-1-92)root_agent = code_pipeline_agent

```

```
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-2)importcom.google.adk.agents.SequentialAgent;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-3)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-4)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-5)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-6)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-7)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-8)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-9)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-10)publicclass SequentialAgentExample{
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-11)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-12)privatestaticfinalStringAPP_NAME="CodePipelineAgent";
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-13)privatestaticfinalStringUSER_ID="test_user_456";
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-14)privatestaticfinalStringMODEL_NAME="gemini-2.0-flash";
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-15)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-16)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-17)SequentialAgentExamplesequentialAgentExample=newSequentialAgentExample();
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-18)sequentialAgentExample.runAgent(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-19)"Write a Java function to calculate the factorial of a number.");
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-20)}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-21)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-22)publicvoidrunAgent(Stringprompt){
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-23)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-24)LlmAgentcodeWriterAgent=
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-25)LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-26).model(MODEL_NAME)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-27).name("CodeWriterAgent")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-28).description("Writes initial Java code based on a specification.")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-29).instruction(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-30)"""
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-31)        You are a Java Code Generator.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-32)        Based *only* on the user's request, write Java code that fulfills the requirement.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-33)        Output *only* the complete Java code block, enclosed in triple backticks (```java ... ```).
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-34)        Do not add any other text before or after the code block.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-35)        """)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-36).outputKey("generated_code")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-37).build();
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-38)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-39)LlmAgentcodeReviewerAgent=
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-40)LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-41).model(MODEL_NAME)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-42).name("CodeReviewerAgent")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-43).description("Reviews code and provides feedback.")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-44).instruction(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-45)"""
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-46)          You are an expert Java Code Reviewer.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-47)          Your task is to provide constructive feedback on the provided code.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-48)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-49)          **Code to Review:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-50)      ```java
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-51)          {generated_code}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-52)      ```
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-53)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-54)          **Review Criteria:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-55)          1. **Correctness:** Does the code work as intended? Are there logic errors?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-56)          2. **Readability:** Is the code clear and easy to understand? Follows Java style guidelines?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-57)          3. **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-58)          4. **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-59)          5. **Best Practices:** Does the code follow common Java best practices?
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-60)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-61)          **Output:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-62)          Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-63)          If the code is excellent and requires no changes, simply state: "No major issues found."
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-64)          Output *only* the review comments or the "No major issues" statement.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-65)        """)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-66).outputKey("review_comments")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-67).build();
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-68)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-69)LlmAgentcodeRefactorerAgent=
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-70)LlmAgent.builder()
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-71).model(MODEL_NAME)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-72).name("CodeRefactorerAgent")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-73).description("Refactors code based on review comments.")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-74).instruction(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-75)"""
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-76)        You are a Java Code Refactoring AI.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-77)        Your goal is to improve the given Java code based on the provided review comments.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-78)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-79)         **Original Code:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-80)     ```java
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-81)         {generated_code}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-82)     ```
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-83)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-84)         **Review Comments:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-85)         {review_comments}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-86)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-87)        **Task:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-88)        Carefully apply the suggestions from the review comments to refactor the original code.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-89)        If the review comments state "No major issues found," return the original code unchanged.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-90)        Ensure the final code is complete, functional, and includes necessary imports and docstrings.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-91)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-92)        **Output:**
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-93)        Output *only* the final, refactored Java code block, enclosed in triple backticks (```java ... ```).
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-94)        Do not add any other text before or after the code block.
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-95)        """)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-96).outputKey("refactored_code")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-97).build();
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-98)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-99)SequentialAgentcodePipelineAgent=
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-100)SequentialAgent.builder()
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-101).name(APP_NAME)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-102).description("Executes a sequence of code writing, reviewing, and refactoring.")
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-103)// The agents will run in the order provided: Writer -> Reviewer -> Refactorer
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-104).subAgents(codeWriterAgent,codeReviewerAgent,codeRefactorerAgent)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-105).build();
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-106)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-107)// Create an InMemoryRunner
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-108)InMemoryRunnerrunner=newInMemoryRunner(codePipelineAgent,APP_NAME);
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-109)// InMemoryRunner automatically creates a session service. Create a session using the service
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-110)Sessionsession=runner.sessionService().createSession(APP_NAME,USER_ID).blockingGet();
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-111)ContentuserMessage=Content.fromParts(Part.fromText(prompt));
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-112)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-113)// Run the agent
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-114)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-115)
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-116)// Stream event response
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-117)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-118)event->{
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-119)if(event.finalResponse()){
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-120)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-121)}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-122)});
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-123)}
[](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#__codelineno-2-124)}

```

Back to top
