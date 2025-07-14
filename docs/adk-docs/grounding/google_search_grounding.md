[ Skip to content ](https://google.github.io/adk-docs/grounding/google_search_grounding/#understanding-google-search-grounding)
# Understanding Google Search Grounding[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#understanding-google-search-grounding "Permanent link")
[Google Search Grounding tool](https://google.github.io/adk-docs/tools/built-in-tools/#google-search) is a powerful feature in the Agent Development Kit (ADK) that enables AI agents to access real-time, authoritative information from the web. By connecting your agents to Google Search, you can provide users with up-to-date answers backed by reliable sources.
This feature is particularly valuable for queries requiring current information like weather updates, news events, stock prices, or any facts that may have changed since the model's training data cutoff. When your agent determines that external information is needed, it automatically performs web searches and incorporates the results into its response with proper attribution.
## What You'll Learn[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#what-youll-learn "Permanent link")
In this guide, you'll discover:
  * **Quick Setup** : How to create and run a Google Search-enabled agent from scratch
  * **Grounding Architecture** : The data flow and technical process behind web grounding
  * **Response Structure** : How to interpret grounded responses and their metadata
  * **Best Practices** : Guidelines for displaying search results and citations to users


### Additional resource[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#additional-resource "Permanent link")
As an additional resource, [Gemini Fullstack Agent Development Kit (ADK) Quickstart](https://github.com/google/adk-samples/tree/main/python/agents/gemini-fullstack) has [a great practical use of the Google Search grounding](https://github.com/google/adk-samples/blob/main/python/agents/gemini-fullstack/app/agent.py) as a full stack application example.
## Google Search Grounding Quickstart[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#google-search-grounding-quickstart "Permanent link")
This quickstart guides you through creating an ADK agent with Google Search grounding feature. This quickstart assumes a local IDE (VS Code or PyCharm, etc.) with Python 3.9+ and terminal access.
### 1. Set up Environment & Install ADK[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#venv-install "Permanent link")
Create & Activate Virtual Environment:
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-0-1)# Create
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-0-2)python-mvenv.venv
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-0-3)
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-0-4)# Activate (each new terminal)
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-0-5)# macOS/Linux: source .venv/bin/activate
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-0-6)# Windows CMD: .venv\Scripts\activate.bat
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-0-7)# Windows PowerShell: .venv\Scripts\Activate.ps1

```

Install ADK:
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-1-1)pipinstallgoogle-adk==1.4.2

```

### 2. Create Agent Project[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#create-agent-project "Permanent link")
Under a project directory, run the following commands:
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-1)# Step 1: Create a new directory for your agent
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-2)mkdirgoogle_search_agent
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-3)
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-4)# Step 2: Create __init__.py for the agent
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-5)echo"from . import agent">google_search_agent/__init__.py
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-6)
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-7)# Step 3: Create an agent.py (the agent definition) and .env (Gemini authentication config)
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-2-8)touchgoogle_search_agent/agent.py.env

```

#### Edit `agent.py`[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#edit-agentpy "Permanent link")
Copy and paste the following code into `agent.py`:
google_search_agent/agent.py```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-1)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-2)fromgoogle.adk.toolsimport google_search
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-3)
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-4)root_agent = Agent(
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-5)  name="google_search_agent",
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-6)  model="gemini-2.5-flash",
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-7)  instruction="Answer questions using Google Search when needed. Always cite sources.",
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-8)  description="Professional search assistant with Google Search capabilities",
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-9)  tools=[google_search]
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-3-10))

```

Now you would have the following directory structure:
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-4-1)my_project/
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-4-2)  google_search_agent/
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-4-3)    __init__.py
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-4-4)    agent.py
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-4-5)  .env

```

### 3. Choose a platform[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#choose-a-platform "Permanent link")
To run the agent, you need to select a platform that the agent will use for calling the Gemini model. Choose one from Google AI Studio or Vertex AI:
[Gemini - Google AI Studio](https://google.github.io/adk-docs/grounding/google_search_grounding/#gemini---google-ai-studio)[Gemini - Google Cloud Vertex AI](https://google.github.io/adk-docs/grounding/google_search_grounding/#gemini---google-cloud-vertex-ai)
  1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
  2. When using Python, open the **`.env`**file and copy-paste the following code.
.env```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-5-1)GOOGLE_GENAI_USE_VERTEXAI=FALSE
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-5-2)GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE

```

  3. Replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with your actual `API KEY`.


  1. You need an existing [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) account and a project.
     * Set up a [Google Cloud project](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
     * Set up the [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
     * Authenticate to Google Cloud, from the terminal by running `gcloud auth login`.
     * [Enable the Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
  2. When using Python, open the **`.env`**file and copy-paste the following code and update the project ID and location.
.env```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-6-1)GOOGLE_GENAI_USE_VERTEXAI=TRUE
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-6-2)GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-6-3)GOOGLE_CLOUD_LOCATION=LOCATION

```



### 4. Run Your Agent[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#run-your-agent "Permanent link")
There are multiple ways to interact with your agent:
[Dev UI (adk web)](https://google.github.io/adk-docs/grounding/google_search_grounding/#dev-ui-adk-web)[Terminal (adk run)](https://google.github.io/adk-docs/grounding/google_search_grounding/#terminal-adk-run)
Run the following command to launch the **dev UI**.
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-7-1)adkweb

```

Note for Windows users
When hitting the `_make_subprocess_transport NotImplementedError`, consider using `adk web --no-reload` instead.
**Step 1:** Open the URL provided (usually `http://localhost:8000` or `http://127.0.0.1:8000`) directly in your browser.
**Step 2.** In the top-left corner of the UI, you can select your agent in the dropdown. Select "google_search_agent".
Troubleshooting
If you do not see "google_search_agent" in the dropdown menu, make sure you are running `adk web` in the **parent folder** of your agent folder (i.e. the parent folder of google_search_agent).
**Step 3.** Now you can chat with your agent using the textbox.
Run the following command, to chat with your Weather agent.
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-8-1)adk run google_search_agent

```

To exit, use Cmd/Ctrl+C.
### 📝 Example prompts to try[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#example-prompts-to-try "Permanent link")
With those questions, you can confirm that the agent is actually calling Google Search to get the latest weather and time.
  * What is the weather in New York?
  * What is the time in New York?
  * What is the weather in Paris?
  * What is the time in Paris?


![Try the agent with adk web](https://google.github.io/adk-docs/assets/google_search_grd_adk_web.png)
You've successfully created and interacted with your Google Search agent using ADK!
## How grounding with Google Search works[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#how-grounding-with-google-search-works "Permanent link")
Grounding is the process that connects your agent to real-time information from the web, allowing it to generate more accurate and current responses. When a user's prompt requires information that the model was not trained on, or that is time-sensitive, the agent's underlying Large Language Model intelligently decides to invoke the google_search tool to find the relevant facts
### **Data Flow Diagram**[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#data-flow-diagram "Permanent link")
This diagram illustrates the step-by-step process of how a user query results in a grounded response.
![](https://google.github.io/adk-docs/assets/google_search_grd_dataflow.png)
### **Detailed Description**[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#detailed-description "Permanent link")
The grounding agent uses the data flow described in the diagram to retrieve, process, and incorporate external information into the final answer presented to the user.
  1. **User Query** : An end-user interacts with your agent by asking a question or giving a command.
  2. **ADK Orchestration** : The Agent Development Kit orchestrates the agent's behavior and passes the user's message to the core of your agent.
  3. **LLM Analysis and Tool-Calling** : The agent's LLM (e.g., a Gemini model) analyzes the prompt. If it determines that external, up-to-date information is required, it triggers the grounding mechanism by calling the google_search tool. This is ideal for answering queries about recent news, weather, or facts not present in the model's training data.
  4. **Grounding Service Interaction** : The google_search tool interacts with an internal grounding service that formulates and sends one or more queries to the Google Search Index.
  5. **Context Injection** : The grounding service retrieves the relevant web pages and snippets. It then integrates these search results into the model's context before the final response is generated. This crucial step allows the model to "reason" over factual, real-time data.
  6. **Grounded Response Generation** : The LLM, now informed by the fresh search results, generates a response that incorporates the retrieved information.
  7. **Response Presentation with Sources** : The ADK receives the final grounded response, which includes the necessary source URLs and groundingMetadata, and presents it to the user with attribution. This allows end-users to verify the information and builds trust in the agent's answers.


### Understanding grounding with Google Search response[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#understanding-grounding-with-google-search-response "Permanent link")
When the agent uses Google Search to ground a response, it returns a detailed set of information that includes not only the final text answer but also the sources it used to generate that answer. This metadata is crucial for verifying the response and for providing attribution to the original sources.
#### **Example of a Grounded Response**[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#example-of-a-grounded-response "Permanent link")
The following is an example of the content object returned by the model after a grounded query.
**Final Answer Text:**
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-9-1)"Yes, Inter Miami won their last game in the FIFA Club World Cup. They defeated FC Porto 2-1 in their second group stage match. Their first game in the tournament was a 0-0 draw against Al Ahly FC. Inter Miami is scheduled to play their third group stage match against Palmeiras on Monday, June 23, 2025."

```

**Grounding Metadata Snippet:**
```
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-1)"groundingMetadata":{
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-2)"groundingChunks":[
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-3){"web":{"title":"mlssoccer.com","uri":"..."}},
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-4){"web":{"title":"intermiamicf.com","uri":"..."}},
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-5){"web":{"title":"mlssoccer.com","uri":"..."}}
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-6)],
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-7)"groundingSupports":[
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-8){
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-9)"groundingChunkIndices":[0,1],
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-10)"segment":{
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-11)"startIndex":65,
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-12)"endIndex":126,
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-13)"text":"They defeated FC Porto 2-1 in their second group stage match."
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-14)}
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-15)},
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-16){
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-17)"groundingChunkIndices":[1],
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-18)"segment":{
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-19)"startIndex":127,
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-20)"endIndex":196,
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-21)"text":"Their first game in the tournament was a 0-0 draw against Al Ahly FC."
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-22)}
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-23)},
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-24){
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-25)"groundingChunkIndices":[0,2],
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-26)"segment":{
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-27)"startIndex":197,
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-28)"endIndex":303,
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-29)"text":"Inter Miami is scheduled to play their third group stage match against Palmeiras on Monday, June 23, 2025."
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-30)}
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-31)}
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-32)],
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-33)"searchEntryPoint":{...}
[](https://google.github.io/adk-docs/grounding/google_search_grounding/#__codelineno-10-34)}

```

#### **How to Interpret the Response**[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#how-to-interpret-the-response "Permanent link")
The metadata provides a link between the text generated by the model and the sources that support it. Here is a step-by-step breakdown:
  1. **groundingChunks** : This is a list of the web pages the model consulted. Each chunk contains the title of the webpage and a uri that links to the source.
  2. **groundingSupports** : This list connects specific sentences in the final answer back to the groundingChunks.
  3. **segment** : This object identifies a specific portion of the final text answer, defined by its startIndex, endIndex, and the text itself.
  4. **groundingChunkIndices** : This array contains the index numbers that correspond to the sources listed in the groundingChunks. For example, the sentence "They defeated FC Porto 2-1..." is supported by information from groundingChunks at index 0 and 1 (both from mlssoccer.com and intermiamicf.com).


### How to display grounding responses with Google Search[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#how-to-display-grounding-responses-with-google-search "Permanent link")
A critical part of using grounding is to correctly display the information, including citations and search suggestions, to the end-user. This builds trust and allows users to verify the information.
![Responnses from Google Search](https://google.github.io/adk-docs/assets/google_search_grd_resp.png)
#### **Displaying Search Suggestions**[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#displaying-search-suggestions "Permanent link")
The `searchEntryPoint` object in the `groundingMetadata` contains pre-formatted HTML for displaying search query suggestions. As seen in the example image, these are typically rendered as clickable chips that allow the user to explore related topics.
**Rendered HTML from searchEntryPoint:** The metadata provides the necessary HTML and CSS to render the search suggestions bar, which includes the Google logo and chips for related queries like "When is the next FIFA Club World Cup" and "Inter Miami FIFA Club World Cup history". Integrating this HTML directly into your application's front end will display the suggestions as intended.
For more information, consult [using Google Search Suggestions](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions) in Vertex AI documentation.
## Summary[¶](https://google.github.io/adk-docs/grounding/google_search_grounding/#summary "Permanent link")
Google Search Grounding transforms AI agents from static knowledge repositories into dynamic, web-connected assistants capable of providing real-time, accurate information. By integrating this feature into your ADK agents, you enable them to:
  * Access current information beyond their training data
  * Provide source attribution for transparency and trust
  * Deliver comprehensive answers with verifiable facts
  * Enhance user experience with relevant search suggestions


The grounding process seamlessly connects user queries to Google's vast search index, enriching responses with up-to-date context while maintaining the conversational flow. With proper implementation and display of grounded responses, your agents become powerful tools for information discovery and decision-making.
Back to top
