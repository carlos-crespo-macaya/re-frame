[ Skip to content ](https://google.github.io/adk-docs/tools/function-tools/#function-tools)
# Function tools[¶](https://google.github.io/adk-docs/tools/function-tools/#function-tools "Permanent link")
## What are function tools?[¶](https://google.github.io/adk-docs/tools/function-tools/#what-are-function-tools "Permanent link")
When out-of-the-box tools don't fully meet specific requirements, developers can create custom function tools. This allows for **tailored functionality** , such as connecting to proprietary databases or implementing unique algorithms.
_For example,_ a function tool, "myfinancetool", might be a function that calculates a specific financial metric. ADK also supports long running functions, so if that calculation takes a while, the agent can continue working on other tasks.
ADK offers several ways to create functions tools, each suited to different levels of complexity and control:
  1. Function Tool
  2. Long Running Function Tool
  3. Agents-as-a-Tool


## 1. Function Tool[¶](https://google.github.io/adk-docs/tools/function-tools/#1-function-tool "Permanent link")
Transforming a function into a tool is a straightforward way to integrate custom logic into your agents. In fact, when you assign a function to an agent’s tools list, the framework will automatically wrap it as a Function Tool for you. This approach offers flexibility and quick integration.
### Parameters[¶](https://google.github.io/adk-docs/tools/function-tools/#parameters "Permanent link")
Define your function parameters using standard **JSON-serializable types** (e.g., string, integer, list, dictionary). It's important to avoid setting default values for parameters, as the language model (LLM) does not currently support interpreting them.
### Return Type[¶](https://google.github.io/adk-docs/tools/function-tools/#return-type "Permanent link")
The preferred return type for a Function Tool is a **dictionary** in Python or **Map** in Java. This allows you to structure the response with key-value pairs, providing context and clarity to the LLM. If your function returns a type other than a dictionary, the framework automatically wraps it into a dictionary with a single key named **"result"**.
Strive to make your return values as descriptive as possible. _For example,_ instead of returning a numeric error code, return a dictionary with an "error_message" key containing a human-readable explanation. **Remember that the LLM** , not a piece of code, needs to understand the result. As a best practice, include a "status" key in your return dictionary to indicate the overall outcome (e.g., "success", "error", "pending"), providing the LLM with a clear signal about the operation's state.
### Docstring / Source code comments[¶](https://google.github.io/adk-docs/tools/function-tools/#docstring-source-code-comments "Permanent link")
The docstring (or comments above) your function serve as the tool's description and is sent to the LLM. Therefore, a well-written and comprehensive docstring is crucial for the LLM to understand how to use the tool effectively. Clearly explain the purpose of the function, the meaning of its parameters, and the expected return values.
Example
[Python](https://google.github.io/adk-docs/tools/function-tools/#python)[Java](https://google.github.io/adk-docs/tools/function-tools/#java)
This tool is a python function which obtains the Stock price of a given Stock ticker/ symbol.
_Note_ : You need to `pip install yfinance` library before using this tool.
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-2)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-6)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-8)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-13)# limitations under the License.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-14)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-15)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-16)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-17)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-18)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-19)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-20)importyfinanceasyf
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-21)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-22)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-23)APP_NAME = "stock_app"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-24)USER_ID = "1234"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-25)SESSION_ID = "session1234"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-26)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-27)defget_stock_price(symbol: str):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-28)"""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-29)  Retrieves the current stock price for a given symbol.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-30)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-31)  Args:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-32)    symbol (str): The stock symbol (e.g., "AAPL", "GOOG").
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-33)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-34)  Returns:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-35)    float: The current stock price, or None if an error occurs.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-36)  """
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-37)  try:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-38)    stock = yf.Ticker(symbol)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-39)    historical_data = stock.history(period="1d")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-40)    if not historical_data.empty:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-41)      current_price = historical_data['Close'].iloc[-1]
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-42)      return current_price
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-43)    else:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-44)      return None
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-45)  except Exception as e:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-46)    print(f"Error retrieving stock price for {symbol}: {e}")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-47)    return None
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-48)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-49)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-50)stock_price_agent = Agent(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-51)  model='gemini-2.0-flash',
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-52)  name='stock_agent',
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-53)  instruction= 'You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.',
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-54)  description='This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.',
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-55)  tools=[get_stock_price], # You can add Python functions directly to the tools list; they will be automatically wrapped as FunctionTools.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-56))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-57)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-58)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-59)# Session and Runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-60)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-61)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-62)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-63)  runner = Runner(agent=stock_price_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-64)  return session, runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-65)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-66)# Agent Interaction
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-67)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-68)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-69)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-70)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-71)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-72)  async for event in events:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-73)    if event.is_final_response():
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-74)      final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-75)      print("Agent Response: ", final_response)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-76)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-77)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-78)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-79)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-0-80)await call_agent_async("stock price of GOOG")

```

The return value from this tool will be wrapped into a dictionary.
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-1-1){"result":"$123"}

```

This tool retrieves the mocked value of a stock price.
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-2)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-3)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-4)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-5)importcom.google.adk.tools.Annotations.Schema;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-6)importcom.google.adk.tools.FunctionTool;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-7)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-8)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-9)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-10)importjava.util.HashMap;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-11)importjava.util.Map;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-12)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-13)publicclass StockPriceAgent{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-14)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-15)privatestaticfinalStringAPP_NAME="stock_agent";
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-16)privatestaticfinalStringUSER_ID="user1234";
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-17)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-18)// Mock data for various stocks functionality
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-19)// NOTE: This is a MOCK implementation. In a real Java application,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-20)// you would use a financial data API or library.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-21)privatestaticfinalMap<String,Double>mockStockPrices=newHashMap<>();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-22)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-23)static{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-24)mockStockPrices.put("GOOG",1.0);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-25)mockStockPrices.put("AAPL",1.0);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-26)mockStockPrices.put("MSFT",1.0);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-27)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-28)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-29)@Schema(description="Retrieves the current stock price for a given symbol.")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-30)publicstaticMap<String,Object>getStockPrice(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-31)@Schema(description="The stock symbol (e.g., \"AAPL\", \"GOOG\")",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-32)name="symbol")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-33)Stringsymbol){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-34)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-35)try{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-36)if(mockStockPrices.containsKey(symbol.toUpperCase())){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-37)doublecurrentPrice=mockStockPrices.get(symbol.toUpperCase());
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-38)System.out.println("Tool: Found price for "+symbol+": "+currentPrice);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-39)returnMap.of("symbol",symbol,"price",currentPrice);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-40)}else{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-41)returnMap.of("symbol",symbol,"error","No data found for symbol");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-42)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-43)}catch(Exceptione){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-44)returnMap.of("symbol",symbol,"error",e.getMessage());
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-45)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-46)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-47)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-48)publicstaticvoidcallAgent(Stringprompt){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-49)// Create the FunctionTool from the Java method
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-50)FunctionToolgetStockPriceTool=FunctionTool.create(StockPriceAgent.class,"getStockPrice");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-51)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-52)LlmAgentstockPriceAgent=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-53)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-54).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-55).name("stock_agent")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-56).instruction(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-57)"You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-58).description(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-59)"This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-60).tools(getStockPriceTool)// Add the Java FunctionTool
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-61).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-62)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-63)// Create an InMemoryRunner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-64)InMemoryRunnerrunner=newInMemoryRunner(stockPriceAgent,APP_NAME);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-65)// InMemoryRunner automatically creates a session service. Create a session using the service
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-66)Sessionsession=runner.sessionService().createSession(APP_NAME,USER_ID).blockingGet();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-67)ContentuserMessage=Content.fromParts(Part.fromText(prompt));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-68)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-69)// Run the agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-70)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-71)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-72)// Stream event response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-73)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-74)event->{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-75)if(event.finalResponse()){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-76)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-77)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-78)});
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-79)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-80)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-81)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-82)callAgent("stock price of GOOG");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-83)callAgent("What's the price of MSFT?");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-84)callAgent("Can you find the stock price for an unknown company XYZ?");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-85)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-2-86)}

```

The return value from this tool will be wrapped into a Map.
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-3-1)Forinput`GOOG`:{"symbol":"GOOG","price":"1.0"}

```

### Best Practices[¶](https://google.github.io/adk-docs/tools/function-tools/#best-practices "Permanent link")
While you have considerable flexibility in defining your function, remember that simplicity enhances usability for the LLM. Consider these guidelines:
  * **Fewer Parameters are Better:** Minimize the number of parameters to reduce complexity.
  * **Simple Data Types:** Favor primitive data types like `str` and `int` over custom classes whenever possible.
  * **Meaningful Names:** The function's name and parameter names significantly influence how the LLM interprets and utilizes the tool. Choose names that clearly reflect the function's purpose and the meaning of its inputs. Avoid generic names like `do_stuff()` or `beAgent()`.


## 2. Long Running Function Tool[¶](https://google.github.io/adk-docs/tools/function-tools/#2-long-running-function-tool "Permanent link")
Designed for tasks that require a significant amount of processing time without blocking the agent's execution. This tool is a subclass of `FunctionTool`.
When using a `LongRunningFunctionTool`, your function can initiate the long-running operation and optionally return an **initial result** ** (e.g. the long-running operation id). Once a long running function tool is invoked the agent runner will pause the agent run and let the agent client to decide whether to continue or wait until the long-running operation finishes. The agent client can query the progress of the long-running operation and send back an intermediate or final response. The agent can then continue with other tasks. An example is the human-in-the-loop scenario where the agent needs human approval before proceeding with a task.
### How it Works[¶](https://google.github.io/adk-docs/tools/function-tools/#how-it-works "Permanent link")
In Python, you wrap a function with `LongRunningFunctionTool`. In Java, you pass a Method name to `LongRunningFunctionTool.create()`.
  1. **Initiation:** When the LLM calls the tool, your function starts the long-running operation.
  2. **Initial Updates:** Your function should optionally return an initial result (e.g. the long-running operaiton id). The ADK framework takes the result and sends it back to the LLM packaged within a `FunctionResponse`. This allows the LLM to inform the user (e.g., status, percentage complete, messages). And then the agent run is ended / paused.
  3. **Continue or Wait:** After each agent run is completed. Agent client can query the progress of the long-running operation and decide whether to continue the agent run with an intermediate response (to update the progress) or wait until a final response is retrieved. Agent client should send the intermediate or final response back to the agent for the next run.
  4. **Framework Handling:** The ADK framework manages the execution. It sends the intermediate or final `FunctionResponse` sent by agent client to the LLM to generate a user friendly message.


### Creating the Tool[¶](https://google.github.io/adk-docs/tools/function-tools/#creating-the-tool "Permanent link")
Define your tool function and wrap it using the `LongRunningFunctionTool` class:
[Python](https://google.github.io/adk-docs/tools/function-tools/#python_1)[Java](https://google.github.io/adk-docs/tools/function-tools/#java_1)
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-1)# 1. Define the long running function
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-2)defask_for_approval(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-3)  purpose: str, amount: float
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-4)) -> dict[str, Any]:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-5)"""Ask for approval for the reimbursement."""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-6)  # create a ticket for the approval
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-7)  # Send a notification to the approver with the link of the ticket
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-8)  return {'status': 'pending', 'approver': 'Sean Zhou', 'purpose' : purpose, 'amount': amount, 'ticket-id': 'approval-ticket-1'}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-9)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-10)defreimburse(purpose: str, amount: float) -> str:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-11)"""Reimburse the amount of money to the employee."""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-12)  # send the reimbrusement request to payment vendor
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-13)  return {'status': 'ok'}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-14)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-15)# 2. Wrap the function with LongRunningFunctionTool
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-4-16)long_running_tool = LongRunningFunctionTool(func=ask_for_approval)

```

```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-2)importcom.google.adk.tools.LongRunningFunctionTool;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-3)importjava.util.HashMap;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-4)importjava.util.Map;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-5)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-6)publicclass ExampleLongRunningFunction{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-7)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-8)// Define your Long Running function.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-9)// Ask for approval for the reimbursement.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-10)publicstaticMap<String,Object>askForApproval(Stringpurpose,doubleamount){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-11)// Simulate creating a ticket and sending a notification
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-12)System.out.println(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-13)"Simulating ticket creation for purpose: "+purpose+", amount: "+amount);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-14)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-15)// Send a notification to the approver with the link of the ticket
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-16)Map<String,Object>result=newHashMap<>();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-17)result.put("status","pending");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-18)result.put("approver","Sean Zhou");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-19)result.put("purpose",purpose);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-20)result.put("amount",amount);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-21)result.put("ticket-id","approval-ticket-1");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-22)returnresult;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-23)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-24)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-25)publicstaticvoidmain(String[]args)throwsNoSuchMethodException{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-26)// Pass the method to LongRunningFunctionTool.create
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-27)LongRunningFunctionToolapproveTool=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-28)LongRunningFunctionTool.create(ExampleLongRunningFunction.class,"askForApproval");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-29)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-30)// Include the tool in the agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-31)LlmAgentapproverAgent=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-32)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-33)// ...
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-34).tools(approveTool)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-35).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-36)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-5-37)}

```

### Intermediate / Final result Updates[¶](https://google.github.io/adk-docs/tools/function-tools/#intermediate-final-result-updates "Permanent link")
Agent client received an event with long running function calls and check the status of the ticket. Then Agent client can send the intermediate or final response back to update the progress. The framework packages this value (even if it's None) into the content of the `FunctionResponse` sent back to the LLM.
Applies to only Java ADK
When passing `ToolContext` with Function Tools, ensure that one of the following is true:
  * The Schema is passed with the ToolContext parameter in the function signature, like:
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-6-1)@com.google.adk.tools.Annotations.Schema(name = "toolContext") ToolContext toolContext

```

OR
  * The following `-parameters` flag is set to the mvn compiler plugin


```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-1)<build>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-2)  <plugins>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-3)    <plugin>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-4)      <groupId>org.apache.maven.plugins</groupId>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-5)      <artifactId>maven-compiler-plugin</artifactId>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-6)      <version>3.14.0</version> <!-- or newer -->
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-7)      <configuration>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-8)        <compilerArgs>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-9)          <arg>-parameters</arg>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-10)        </compilerArgs>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-11)      </configuration>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-12)    </plugin>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-13)  </plugins>
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-7-14)</build>

```

This constraint is temporary and will be removed.
[Python](https://google.github.io/adk-docs/tools/function-tools/#python_2)[Java](https://google.github.io/adk-docs/tools/function-tools/#java_2)
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-1)# Agent Interaction
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-2)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-3)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-4)  defget_long_running_function_call(event: Event) -> types.FunctionCall:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-5)    # Get the long running function call from the event
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-6)    if not event.long_running_tool_ids or not event.content or not event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-7)      return
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-8)    for part in event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-9)      if (
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-10)        part
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-11)        and part.function_call
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-12)        and event.long_running_tool_ids
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-13)        and part.function_call.id in event.long_running_tool_ids
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-14)      ):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-15)        return part.function_call
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-16)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-17)  defget_function_response(event: Event, function_call_id: str) -> types.FunctionResponse:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-18)    # Get the function response for the fuction call with specified id.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-19)    if not event.content or not event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-20)      return
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-21)    for part in event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-22)      if (
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-23)        part
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-24)        and part.function_response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-25)        and part.function_response.id == function_call_id
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-26)      ):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-27)        return part.function_response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-28)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-29)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-30)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-31)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-32)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-33)  print("\nRunning agent...")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-34)  events_async = runner.run_async(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-35)    session_id=session.id, user_id=USER_ID, new_message=content
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-36)  )
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-37)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-38)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-39)  long_running_function_call, long_running_function_response, ticket_id = None, None, None
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-40)  async for event in events_async:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-41)    # Use helper to check for the specific auth request event
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-42)    if not long_running_function_call:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-43)      long_running_function_call = get_long_running_function_call(event)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-44)    else:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-45)      long_running_function_response = get_function_response(event, long_running_function_call.id)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-46)      if long_running_function_response:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-47)        ticket_id = long_running_function_response.response['ticket-id']
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-48)    if event.content and event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-49)      if text := ''.join(part.text or '' for part in event.content.parts):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-50)        print(f'[{event.author}]: {text}')
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-51)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-52)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-53)  if long_running_function_response:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-54)    # query the status of the correpsonding ticket via tciket_id
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-55)    # send back an intermediate / final response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-56)    updated_response = long_running_function_response.model_copy(deep=True)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-57)    updated_response.response = {'status': 'approved'}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-58)    async for event in runner.run_async(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-59)     session_id=session.id, user_id=USER_ID, new_message=types.Content(parts=[types.Part(function_response = updated_response)], role='user')
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-60)    ):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-61)      if event.content and event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-62)        if text := ''.join(part.text or '' for part in event.content.parts):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-8-63)          print(f'[{event.author}]: {text}')

```

```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-2)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-3)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-4)importcom.google.adk.runner.Runner;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-5)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-6)importcom.google.adk.tools.Annotations.Schema;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-7)importcom.google.adk.tools.LongRunningFunctionTool;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-8)importcom.google.adk.tools.ToolContext;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-9)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-10)importcom.google.common.collect.ImmutableMap;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-11)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-12)importcom.google.genai.types.FunctionCall;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-13)importcom.google.genai.types.FunctionResponse;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-14)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-15)importjava.util.Optional;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-16)importjava.util.UUID;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-17)importjava.util.concurrent.atomic.AtomicReference;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-18)importjava.util.stream.Collectors;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-19)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-20)publicclass LongRunningFunctionExample{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-21)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-22)privatestaticStringUSER_ID="user123";
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-23)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-24)@Schema(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-25)name="create_ticket_long_running",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-26)description="""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-27)     Creates a new support ticket with a specified urgency level.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-28)     Examples of urgency are 'high', 'medium', or 'low'.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-29)     The ticket creation is a long-running process, and its ID will be provided when ready.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-30)   """)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-31)publicstaticvoidcreateTicketAsync(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-32)@Schema(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-33)name="urgency",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-34)description=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-35)"The urgency level for the new ticket, such as 'high', 'medium', or 'low'.")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-36)Stringurgency,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-37)@Schema(name="toolContext")// Ensures ADK injection
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-38)ToolContexttoolContext){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-39)System.out.printf(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-40)"TOOL_EXEC: 'create_ticket_long_running' called with urgency: %s (Call ID: %s)%n",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-41)urgency,toolContext.functionCallId().orElse("N/A"));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-42)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-43)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-44)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-45)LlmAgentagent=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-46)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-47).name("ticket_agent")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-48).description("Agent for creating tickets via a long-running task.")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-49).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-50).tools(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-51)ImmutableList.of(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-52)LongRunningFunctionTool.create(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-53)LongRunningFunctionExample.class,"createTicketAsync")))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-54).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-55)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-56)Runnerrunner=newInMemoryRunner(agent);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-57)Sessionsession=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-58)runner.sessionService().createSession(agent.name(),USER_ID,null,null).blockingGet();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-59)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-60)// --- Turn 1: User requests ticket ---
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-61)System.out.println("\n--- Turn 1: User Request ---");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-62)ContentinitialUserMessage=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-63)Content.fromParts(Part.fromText("Create a high urgency ticket for me."));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-64)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-65)AtomicReference<String>funcCallIdRef=newAtomicReference<>();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-66)runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-67).runAsync(USER_ID,session.id(),initialUserMessage)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-68).blockingForEach(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-69)event->{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-70)printEventSummary(event,"T1");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-71)if(funcCallIdRef.get()==null){// Capture the first relevant function call ID
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-72)event.content().flatMap(Content::parts).orElse(ImmutableList.of()).stream()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-73).map(Part::functionCall)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-74).flatMap(Optional::stream)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-75).filter(fc->"create_ticket_long_running".equals(fc.name().orElse("")))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-76).findFirst()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-77).flatMap(FunctionCall::id)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-78).ifPresent(funcCallIdRef::set);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-79)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-80)});
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-81)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-82)if(funcCallIdRef.get()==null){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-83)System.out.println("ERROR: Tool 'create_ticket_long_running' not called in Turn 1.");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-84)return;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-85)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-86)System.out.println("ACTION: Captured FunctionCall ID: "+funcCallIdRef.get());
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-87)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-88)// --- Turn 2: App provides initial ticket_id (simulating async tool completion) ---
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-89)System.out.println("\n--- Turn 2: App provides ticket_id ---");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-90)StringticketId="TICKET-"+UUID.randomUUID().toString().substring(0,8).toUpperCase();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-91)FunctionResponseticketCreatedFuncResponse=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-92)FunctionResponse.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-93).name("create_ticket_long_running")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-94).id(funcCallIdRef.get())
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-95).response(ImmutableMap.of("ticket_id",ticketId))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-96).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-97)ContentappResponseWithTicketId=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-98)Content.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-99).parts(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-100)ImmutableList.of(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-101)Part.builder().functionResponse(ticketCreatedFuncResponse).build()))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-102).role("user")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-103).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-104)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-105)runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-106).runAsync(USER_ID,session.id(),appResponseWithTicketId)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-107).blockingForEach(event->printEventSummary(event,"T2"));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-108)System.out.println("ACTION: Sent ticket_id "+ticketId+" to agent.");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-109)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-110)// --- Turn 3: App provides ticket status update ---
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-111)System.out.println("\n--- Turn 3: App provides ticket status ---");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-112)FunctionResponseticketStatusFuncResponse=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-113)FunctionResponse.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-114).name("create_ticket_long_running")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-115).id(funcCallIdRef.get())
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-116).response(ImmutableMap.of("status","approved","ticket_id",ticketId))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-117).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-118)ContentappResponseWithStatus=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-119)Content.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-120).parts(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-121)ImmutableList.of(Part.builder().functionResponse(ticketStatusFuncResponse).build()))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-122).role("user")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-123).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-124)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-125)runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-126).runAsync(USER_ID,session.id(),appResponseWithStatus)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-127).blockingForEach(event->printEventSummary(event,"T3_FINAL"));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-128)System.out.println("Long running function completed successfully.");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-129)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-130)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-131)privatestaticvoidprintEventSummary(Eventevent,StringturnLabel){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-132)event
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-133).content()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-134).ifPresent(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-135)content->{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-136)Stringtext=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-137)content.parts().orElse(ImmutableList.of()).stream()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-138).map(part->part.text().orElse(""))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-139).filter(s->!s.isEmpty())
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-140).collect(Collectors.joining(" "));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-141)if(!text.isEmpty()){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-142)System.out.printf("[%s][%s_TEXT]: %s%n",turnLabel,event.author(),text);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-143)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-144)content.parts().orElse(ImmutableList.of()).stream()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-145).map(Part::functionCall)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-146).flatMap(Optional::stream)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-147).findFirst()// Assuming one function call per relevant event for simplicity
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-148).ifPresent(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-149)fc->
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-150)System.out.printf(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-151)"[%s][%s_CALL]: %s(%s) ID: %s%n",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-152)turnLabel,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-153)event.author(),
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-154)fc.name().orElse("N/A"),
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-155)fc.args().orElse(ImmutableMap.of()),
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-156)fc.id().orElse("N/A")));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-157)});
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-158)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-9-159)}

```

Python complete example: File Processing Simulation
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-2)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-6)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-8)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-13)# limitations under the License.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-14)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-15)importasyncio
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-16)fromtypingimport Any
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-17)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-18)fromgoogle.adk.eventsimport Event
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-19)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-20)fromgoogle.adk.toolsimport LongRunningFunctionTool
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-21)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-22)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-23)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-24)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-25)# 1. Define the long running function
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-26)defask_for_approval(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-27)  purpose: str, amount: float
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-28)) -> dict[str, Any]:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-29)"""Ask for approval for the reimbursement."""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-30)  # create a ticket for the approval
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-31)  # Send a notification to the approver with the link of the ticket
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-32)  return {'status': 'pending', 'approver': 'Sean Zhou', 'purpose' : purpose, 'amount': amount, 'ticket-id': 'approval-ticket-1'}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-33)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-34)defreimburse(purpose: str, amount: float) -> str:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-35)"""Reimburse the amount of money to the employee."""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-36)  # send the reimbrusement request to payment vendor
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-37)  return {'status': 'ok'}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-38)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-39)# 2. Wrap the function with LongRunningFunctionTool
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-40)long_running_tool = LongRunningFunctionTool(func=ask_for_approval)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-41)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-42)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-43)# 3. Use the tool in an Agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-44)file_processor_agent = Agent(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-45)  # Use a model compatible with function calling
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-46)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-47)  name='reimbursement_agent',
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-48)  instruction="""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-49)   You are an agent whose job is to handle the reimbursement process for
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-50)   the employees. If the amount is less than $100, you will automatically
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-51)   approve the reimbursement.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-52)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-53)   If the amount is greater than $100, you will
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-54)   ask for approval from the manager. If the manager approves, you will
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-55)   call reimburse() to reimburse the amount to the employee. If the manager
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-56)   rejects, you will inform the employee of the rejection.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-57)  """,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-58)  tools=[reimburse, long_running_tool]
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-59))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-60)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-61)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-62)APP_NAME = "human_in_the_loop"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-63)USER_ID = "1234"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-64)SESSION_ID = "session1234"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-65)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-66)# Session and Runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-67)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-68)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-69)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-70)  runner = Runner(agent=file_processor_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-71)  return session, runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-72)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-73)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-74)# Agent Interaction
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-75)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-76)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-77)  defget_long_running_function_call(event: Event) -> types.FunctionCall:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-78)    # Get the long running function call from the event
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-79)    if not event.long_running_tool_ids or not event.content or not event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-80)      return
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-81)    for part in event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-82)      if (
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-83)        part
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-84)        and part.function_call
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-85)        and event.long_running_tool_ids
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-86)        and part.function_call.id in event.long_running_tool_ids
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-87)      ):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-88)        return part.function_call
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-89)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-90)  defget_function_response(event: Event, function_call_id: str) -> types.FunctionResponse:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-91)    # Get the function response for the fuction call with specified id.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-92)    if not event.content or not event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-93)      return
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-94)    for part in event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-95)      if (
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-96)        part
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-97)        and part.function_response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-98)        and part.function_response.id == function_call_id
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-99)      ):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-100)        return part.function_response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-101)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-102)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-103)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-104)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-105)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-106)  print("\nRunning agent...")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-107)  events_async = runner.run_async(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-108)    session_id=session.id, user_id=USER_ID, new_message=content
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-109)  )
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-110)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-111)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-112)  long_running_function_call, long_running_function_response, ticket_id = None, None, None
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-113)  async for event in events_async:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-114)    # Use helper to check for the specific auth request event
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-115)    if not long_running_function_call:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-116)      long_running_function_call = get_long_running_function_call(event)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-117)    else:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-118)      long_running_function_response = get_function_response(event, long_running_function_call.id)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-119)      if long_running_function_response:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-120)        ticket_id = long_running_function_response.response['ticket-id']
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-121)    if event.content and event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-122)      if text := ''.join(part.text or '' for part in event.content.parts):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-123)        print(f'[{event.author}]: {text}')
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-124)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-125)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-126)  if long_running_function_response:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-127)    # query the status of the correpsonding ticket via tciket_id
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-128)    # send back an intermediate / final response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-129)    updated_response = long_running_function_response.model_copy(deep=True)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-130)    updated_response.response = {'status': 'approved'}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-131)    async for event in runner.run_async(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-132)     session_id=session.id, user_id=USER_ID, new_message=types.Content(parts=[types.Part(function_response = updated_response)], role='user')
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-133)    ):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-134)      if event.content and event.content.parts:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-135)        if text := ''.join(part.text or '' for part in event.content.parts):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-136)          print(f'[{event.author}]: {text}')
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-137)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-138)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-139)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-140)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-141)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-142)# reimbursement that doesn't require approval
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-143)# asyncio.run(call_agent_async("Please reimburse 50$ for meals"))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-144)await call_agent_async("Please reimburse 50$ for meals") # For Notebooks, uncomment this line and comment the above line
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-145)# reimbursement that requires approval
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-146)# asyncio.run(call_agent_async("Please reimburse 200$ for meals"))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-10-147)await call_agent_async("Please reimburse 200$ for meals") # For Notebooks, uncomment this line and comment the above line

```

#### Key aspects of this example[¶](https://google.github.io/adk-docs/tools/function-tools/#key-aspects-of-this-example "Permanent link")
  * **`LongRunningFunctionTool`**: Wraps the supplied method/function; the framework handles sending yielded updates and the final return value as sequential FunctionResponses.
  * **Agent instruction** : Directs the LLM to use the tool and understand the incoming FunctionResponse stream (progress vs. completion) for user updates.
  * **Final return** : The function returns the final result dictionary, which is sent in the concluding FunctionResponse to indicate completion.


## 3. Agent-as-a-Tool[¶](https://google.github.io/adk-docs/tools/function-tools/#3-agent-as-a-tool "Permanent link")
This powerful feature allows you to leverage the capabilities of other agents within your system by calling them as tools. The Agent-as-a-Tool enables you to invoke another agent to perform a specific task, effectively **delegating responsibility**. This is conceptually similar to creating a Python function that calls another agent and uses the agent's response as the function's return value.
### Key difference from sub-agents[¶](https://google.github.io/adk-docs/tools/function-tools/#key-difference-from-sub-agents "Permanent link")
It's important to distinguish an Agent-as-a-Tool from a Sub-Agent.
  * **Agent-as-a-Tool:** When Agent A calls Agent B as a tool (using Agent-as-a-Tool), Agent B's answer is **passed back** to Agent A, which then summarizes the answer and generates a response to the user. Agent A retains control and continues to handle future user input.
  * **Sub-agent:** When Agent A calls Agent B as a sub-agent, the responsibility of answering the user is completely **transferred to Agent B**. Agent A is effectively out of the loop. All subsequent user input will be answered by Agent B.


### Usage[¶](https://google.github.io/adk-docs/tools/function-tools/#usage "Permanent link")
To use an agent as a tool, wrap the agent with the AgentTool class.
[Python](https://google.github.io/adk-docs/tools/function-tools/#python_3)[Java](https://google.github.io/adk-docs/tools/function-tools/#java_3)
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-11-1)tools=[AgentTool(agent=agent_b)]

```

```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-12-1)AgentTool.create(agent)

```

### Customization[¶](https://google.github.io/adk-docs/tools/function-tools/#customization "Permanent link")
The `AgentTool` class provides the following attributes for customizing its behavior:
  * **skip_summarization: bool:** If set to True, the framework will **bypass the LLM-based summarization** of the tool agent's response. This can be useful when the tool's response is already well-formatted and requires no further processing.

Example
[Python](https://google.github.io/adk-docs/tools/function-tools/#python_4)[Java](https://google.github.io/adk-docs/tools/function-tools/#java_4)
```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-1)# Copyright 2025 Google LLC
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-2)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-3)# Licensed under the Apache License, Version 2.0 (the "License");
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-4)# you may not use this file except in compliance with the License.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-5)# You may obtain a copy of the License at
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-6)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-7)#   http://www.apache.org/licenses/LICENSE-2.0
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-8)#
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-9)# Unless required by applicable law or agreed to in writing, software
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-10)# distributed under the License is distributed on an "AS IS" BASIS,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-11)# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-12)# See the License for the specific language governing permissions and
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-13)# limitations under the License.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-14)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-15)fromgoogle.adk.agentsimport Agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-16)fromgoogle.adk.runnersimport Runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-17)fromgoogle.adk.sessionsimport InMemorySessionService
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-18)fromgoogle.adk.tools.agent_toolimport AgentTool
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-19)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-20)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-21)APP_NAME="summary_agent"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-22)USER_ID="user1234"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-23)SESSION_ID="1234"
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-24)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-25)summary_agent = Agent(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-26)  model="gemini-2.0-flash",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-27)  name="summary_agent",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-28)  instruction="""You are an expert summarizer. Please read the following text and provide a concise summary.""",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-29)  description="Agent to summarize text",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-30))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-31)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-32)root_agent = Agent(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-33)  model='gemini-2.0-flash',
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-34)  name='root_agent',
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-35)  instruction="""You are a helpful assistant. When the user provides a text, use the 'summarize' tool to generate a summary. Always forward the user's message exactly as received to the 'summarize' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.""",
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-36)  tools=[AgentTool(agent=summary_agent)]
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-37))
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-38)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-39)# Session and Runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-40)async defsetup_session_and_runner():
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-41)  session_service = InMemorySessionService()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-42)  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-43)  runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-44)  return session, runner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-45)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-46)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-47)# Agent Interaction
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-48)async defcall_agent_async(query):
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-49)  content = types.Content(role='user', parts=[types.Part(text=query)])
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-50)  session, runner = await setup_session_and_runner()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-51)  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-52)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-53)  async for event in events:
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-54)    if event.is_final_response():
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-55)      final_response = event.content.parts[0].text
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-56)      print("Agent Response: ", final_response)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-57)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-58)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-59)long_text = """Quantum computing represents a fundamentally different approach to computation,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-60)leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-61)that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-62)being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-63)meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-64)interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-65)as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-66)faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages."""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-67)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-68)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-69)# Note: In Colab, you can directly use 'await' at the top level.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-70)# If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-13-71)await call_agent_async(long_text)

```

```
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-1)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-2)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-3)importcom.google.adk.runner.InMemoryRunner;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-4)importcom.google.adk.sessions.Session;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-5)importcom.google.adk.tools.AgentTool;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-6)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-7)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-8)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-9)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-10)publicclass AgentToolCustomization{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-11)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-12)privatestaticfinalStringAPP_NAME="summary_agent";
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-13)privatestaticfinalStringUSER_ID="user1234";
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-14)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-15)publicstaticvoidinitAgentAndRun(Stringprompt){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-16)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-17)LlmAgentsummaryAgent=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-18)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-19).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-20).name("summaryAgent")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-21).instruction(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-22)"You are an expert summarizer. Please read the following text and provide a concise summary.")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-23).description("Agent to summarize text")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-24).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-25)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-26)// Define root_agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-27)LlmAgentrootAgent=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-28)LlmAgent.builder()
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-29).model("gemini-2.0-flash")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-30).name("rootAgent")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-31).instruction(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-32)"You are a helpful assistant. When the user provides a text, always use the 'summaryAgent' tool to generate a summary. Always forward the user's message exactly as received to the 'summaryAgent' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-33).description("Assistant agent")
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-34).tools(AgentTool.create(summaryAgent,true))// Set skipSummarization to true
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-35).build();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-36)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-37)// Create an InMemoryRunner
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-38)InMemoryRunnerrunner=newInMemoryRunner(rootAgent,APP_NAME);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-39)// InMemoryRunner automatically creates a session service. Create a session using the service
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-40)Sessionsession=runner.sessionService().createSession(APP_NAME,USER_ID).blockingGet();
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-41)ContentuserMessage=Content.fromParts(Part.fromText(prompt));
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-42)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-43)// Run the agent
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-44)Flowable<Event>eventStream=runner.runAsync(USER_ID,session.id(),userMessage);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-45)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-46)// Stream event response
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-47)eventStream.blockingForEach(
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-48)event->{
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-49)if(event.finalResponse()){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-50)System.out.println(event.stringifyContent());
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-51)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-52)});
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-53)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-54)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-55)publicstaticvoidmain(String[]args){
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-56)StringlongText=
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-57)"""
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-58)      Quantum computing represents a fundamentally different approach to computation,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-59)      leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-60)      that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-61)      being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled,
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-62)      meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-63)      interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-64)      as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-65)      faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.""";
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-66)
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-67)initAgentAndRun(longText);
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-68)}
[](https://google.github.io/adk-docs/tools/function-tools/#__codelineno-14-69)}

```

### How it works[¶](https://google.github.io/adk-docs/tools/function-tools/#how-it-works_1 "Permanent link")
  1. When the `main_agent` receives the long text, its instruction tells it to use the 'summarize' tool for long texts.
  2. The framework recognizes 'summarize' as an `AgentTool` that wraps the `summary_agent`.
  3. Behind the scenes, the `main_agent` will call the `summary_agent` with the long text as input.
  4. The `summary_agent` will process the text according to its instruction and generate a summary.
  5. **The response from the`summary_agent` is then passed back to the `main_agent`.**
  6. The `main_agent` can then take the summary and formulate its final response to the user (e.g., "Here's a summary of the text: ...")


Back to top
