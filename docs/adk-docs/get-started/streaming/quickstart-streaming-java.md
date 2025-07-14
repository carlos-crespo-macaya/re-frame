[ Skip to content ](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#adk-streaming-quickstart-java)
# Quickstart (Streaming / Java)[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#adk-streaming-quickstart-java "Permanent link")
This quickstart guide will walk you through the process of creating a basic agent and leveraging ADK Streaming with Java to facilitate low-latency, bidirectional voice interactions.
You'll begin by setting up your Java and Maven environment, structuring your project, and defining the necessary dependencies. Following this, you'll create a simple `ScienceTeacherAgent`, test its text-based streaming capabilities using the Dev UI, and then progress to enabling live audio communication, transforming your agent into an interactive voice-driven application.
## **Create your first agent**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#create-your-first-agent "Permanent link")
### **Prerequisites**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#prerequisites "Permanent link")
  * In this getting started guide, you will be programming in Java. Check if **Java** is installed on your machine. Ideally, you should be using Java 17 or more (you can check that by typing **java -version**)
  * You’ll also be using the **Maven** build tool for Java. So be sure to have [Maven installed](https://maven.apache.org/install.html) on your machine before going further (this is the case for Cloud Top or Cloud Shell, but not necessarily for your laptop).


### **Prepare the project structure**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#prepare-the-project-structure "Permanent link")
To get started with ADK Java, let’s create a Maven project with the following directory structure:
```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-0-1)adk-agents/
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-0-2)├── pom.xml
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-0-3)└── src/
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-0-4)  └── main/
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-0-5)    └── java/
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-0-6)      └── agents/
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-0-7)        └── ScienceTeacherAgent.java

```

Follow the instructions in [Installation](https://google.github.io/adk-docs/get-started/installation/) page to add `pom.xml` for using the ADK package.
Note
Feel free to use whichever name you like for the root directory of your project (instead of adk-agents)
### **Running a compilation**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#running-a-compilation "Permanent link")
Let’s see if Maven is happy with this build, by running a compilation (**mvn compile** command):
```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-1)$mvncompile
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-2)[INFO]Scanningforprojects...
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-3)[INFO]
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-4)[INFO]--------------------<adk-agents:adk-agents>--------------------
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-5)[INFO]Buildingadk-agents1.0-SNAPSHOT
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-6)[INFO]frompom.xml
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-7)[INFO]--------------------------------[jar]---------------------------------
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-8)[INFO]
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-9)[INFO]---resources:3.3.1:resources(default-resources)@adk-demo---
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-10)[INFO]skipnonexistingresourceDirectory/home/user/adk-demo/src/main/resources
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-11)[INFO]
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-12)[INFO]---compiler:3.13.0:compile(default-compile)@adk-demo---
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-13)[INFO]Nothingtocompile-allclassesareuptodate.
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-14)[INFO]------------------------------------------------------------------------
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-15)[INFO]BUILDSUCCESS
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-16)[INFO]------------------------------------------------------------------------
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-17)[INFO]Totaltime:1.347s
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-18)[INFO]Finishedat:2025-05-06T15:38:08Z
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-1-19)[INFO]------------------------------------------------------------------------

```

Looks like the project is set up properly for compilation!
### **Creating an agent**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#creating-an-agent "Permanent link")
Create the **ScienceTeacherAgent.java** file under the `src/main/java/agents/` directory with the following content:
```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-1)packagesamples.liveaudio;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-2)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-3)importcom.google.adk.agents.BaseAgent;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-4)importcom.google.adk.agents.LlmAgent;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-5)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-6)/** Science teacher agent. */
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-7)publicclass ScienceTeacherAgent{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-8)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-9)// Field expected by the Dev UI to load the agent dynamically
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-10)// (the agent must be initialized at declaration time)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-11)publicstaticBaseAgentROOT_AGENT=initAgent();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-12)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-13)publicstaticBaseAgentinitAgent(){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-14)returnLlmAgent.builder()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-15).name("science-app")
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-16).description("Science teacher agent")
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-17).model("gemini-2.0-flash-exp")
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-18).instruction("""
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-19)      You are a helpful science teacher that explains
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-20)      science concepts to kids and teenagers.
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-21)      """)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-22).build();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-23)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-2-24)}

```

Troubleshooting
The model `gemini-2.0-flash-exp` will be deprecated in the future. If you see any issues on using it, try using `gemini-2.0-flash-live-001` instead
We will use `Dev UI` to run this agent later. For the tool to automatically recognize the agent, its Java class has to comply with the following two rules:
  * The agent should be stored in a global **public static** variable named **ROOT_AGENT** of type **BaseAgent** and initialized at declaration time.
  * The agent definition has to be a **static** method so it can be loaded during the class initialization by the dynamic compiling classloader.


## **Run agent with Dev UI**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#run-agent-with-adk-web-server "Permanent link")
`Dev UI` is a web server where you can quickly run and test your agents for development purpose, without building your own UI application for the agents.
### **Define environment variables**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#define-environment-variables "Permanent link")
To run the server, you’ll need to export two environment variables:
  * a Gemini key that you can [get from AI Studio](https://ai.google.dev/gemini-api/docs/api-key),
  * a variable to specify we’re not using Vertex AI this time.


```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-3-1)exportGOOGLE_GENAI_USE_VERTEXAI=FALSE
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-3-2)exportGOOGLE_API_KEY=YOUR_API_KEY

```

### **Run Dev UI**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#run-dev-ui "Permanent link")
Run the following command from the terminal to launch the Dev UI.
terminal```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-4-1)mvn exec:java \
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-4-2)  -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-4-3)  -Dexec.args="--adk.agents.source-dir=src/main/java" \
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-4-4)  -Dexec.classpathScope="compile"

```

**Step 1:** Open the URL provided (usually `http://localhost:8080` or `http://127.0.0.1:8080`) directly in your browser.
**Step 2.** In the top-left corner of the UI, you can select your agent in the dropdown. Select "science-app".
Troubleshooting
If you do not see "science-app" in the dropdown menu, make sure you are running the `mvn` command at the location where your Java source code is located (usually `src/main/java`).
## Try Dev UI with text[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#try-dev-ui-with-text "Permanent link")
With your favorite browser, navigate to: <http://127.0.0.1:8080/>
You should see the following interface:
![Dev UI](https://google.github.io/adk-docs/assets/quickstart-streaming-devui.png)
Click the `Token Streaming` switch at the top right, and ask any questions for the science teacher such as `What's the electron?`. Then you should see the output text in streaming on the UI.
As we saw, you do not have to write any specific code in the agent itself for the text streaming capability. It is provided as an ADK Agent feature by default.
### Try with voice and video[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#try-with-voice-and-video "Permanent link")
To try with voice, reload the web browser, click the microphone button to enable the voice input, and ask the same question in voice. You will hear the answer in voice in real-time.
To try with video, reload the web browser, click the camera button to enable the video input, and ask questions like "What do you see?". The agent will answer what they see in the video input.
### Stop the tool[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#stop-the-tool "Permanent link")
Stop the tool by pressing `Ctrl-C` on the console.
## **Run agent with a custom live audio app**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#run-agent-with-live-audio "Permanent link")
Now, let's try audio streaming with the agent and a custom live audio application.
### **A Maven pom.xml build file for Live Audio**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#a-maven-pomxml-build-file-for-live-audio "Permanent link")
Replace your existing pom.xml with the following.
```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-1)<?xml version="1.0" encoding="UTF-8"?>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-2)<projectxmlns="http://maven.apache.org/POM/4.0.0"
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-3)xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-4)xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-5)<modelVersion>4.0.0</modelVersion>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-6)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-7)<groupId>com.google.adk.samples</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-8)<artifactId>google-adk-sample-live-audio</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-9)<version>0.1.0</version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-10)<name>GoogleADK-Sample-LiveAudio</name>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-11)<description>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-12)AsampleapplicationdemonstratingaliveaudioconversationusingADK,
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-13)runnableviasamples.liveaudio.LiveAudioRun.
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-14)</description>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-15)<packaging>jar</packaging>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-16)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-17)<properties>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-18)<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-19)<java.version>17</java.version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-20)<auto-value.version>1.11.0</auto-value.version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-21)<!-- Main class for exec-maven-plugin -->
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-22)<exec.mainClass>samples.liveaudio.LiveAudioRun</exec.mainClass>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-23)<google-adk.version>0.1.0</google-adk.version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-24)</properties>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-25)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-26)<dependencyManagement>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-27)<dependencies>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-28)<dependency>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-29)<groupId>com.google.cloud</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-30)<artifactId>libraries-bom</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-31)<version>26.53.0</version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-32)<type>pom</type>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-33)<scope>import</scope>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-34)</dependency>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-35)</dependencies>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-36)</dependencyManagement>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-37)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-38)<dependencies>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-39)<dependency>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-40)<groupId>com.google.adk</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-41)<artifactId>google-adk</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-42)<version>${google-adk.version}</version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-43)</dependency>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-44)<dependency>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-45)<groupId>commons-logging</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-46)<artifactId>commons-logging</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-47)<version>1.2</version><!-- Or use a property if defined in a parent POM -->
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-48)</dependency>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-49)</dependencies>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-50)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-51)<build>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-52)<plugins>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-53)<plugin>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-54)<groupId>org.apache.maven.plugins</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-55)<artifactId>maven-compiler-plugin</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-56)<version>3.13.0</version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-57)<configuration>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-58)<source>${java.version}</source>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-59)<target>${java.version}</target>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-60)<parameters>true</parameters>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-61)<annotationProcessorPaths>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-62)<path>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-63)<groupId>com.google.auto.value</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-64)<artifactId>auto-value</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-65)<version>${auto-value.version}</version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-66)</path>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-67)</annotationProcessorPaths>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-68)</configuration>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-69)</plugin>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-70)<plugin>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-71)<groupId>org.codehaus.mojo</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-72)<artifactId>build-helper-maven-plugin</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-73)<version>3.6.0</version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-74)<executions>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-75)<execution>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-76)<id>add-source</id>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-77)<phase>generate-sources</phase>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-78)<goals>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-79)<goal>add-source</goal>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-80)</goals>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-81)<configuration>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-82)<sources>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-83)<source>.</source>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-84)</sources>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-85)</configuration>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-86)</execution>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-87)</executions>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-88)</plugin>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-89)<plugin>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-90)<groupId>org.codehaus.mojo</groupId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-91)<artifactId>exec-maven-plugin</artifactId>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-92)<version>3.2.0</version>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-93)<configuration>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-94)<mainClass>${exec.mainClass}</mainClass>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-95)<classpathScope>runtime</classpathScope>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-96)</configuration>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-97)</plugin>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-98)</plugins>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-99)</build>
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-5-100)</project>

```

### **Creating Live Audio Run tool**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#creating-live-audio-run-tool "Permanent link")
Create the **LiveAudioRun.java** file under the `src/main/java/` directory with the following content. This tool runs the agent on it with live audio input and output.
```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-1)packagesamples.liveaudio;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-2)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-3)importcom.google.adk.agents.LiveRequestQueue;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-4)importcom.google.adk.agents.RunConfig;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-5)importcom.google.adk.events.Event;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-6)importcom.google.adk.runner.Runner;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-7)importcom.google.adk.sessions.InMemorySessionService;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-8)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-9)importcom.google.genai.types.Blob;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-10)importcom.google.genai.types.Modality;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-11)importcom.google.genai.types.PrebuiltVoiceConfig;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-12)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-13)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-14)importcom.google.genai.types.SpeechConfig;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-15)importcom.google.genai.types.VoiceConfig;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-16)importio.reactivex.rxjava3.core.Flowable;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-17)importjava.io.ByteArrayOutputStream;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-18)importjava.io.InputStream;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-19)importjava.net.URL;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-20)importjavax.sound.sampled.AudioFormat;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-21)importjavax.sound.sampled.AudioInputStream;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-22)importjavax.sound.sampled.AudioSystem;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-23)importjavax.sound.sampled.DataLine;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-24)importjavax.sound.sampled.LineUnavailableException;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-25)importjavax.sound.sampled.Mixer;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-26)importjavax.sound.sampled.SourceDataLine;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-27)importjavax.sound.sampled.TargetDataLine;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-28)importjava.util.UUID;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-29)importjava.util.concurrent.ExecutorService;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-30)importjava.util.concurrent.ConcurrentHashMap;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-31)importjava.util.concurrent.ConcurrentMap;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-32)importjava.util.concurrent.Executors;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-33)importjava.util.concurrent.Future;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-34)importjava.util.concurrent.TimeUnit;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-35)importjava.util.concurrent.atomic.AtomicBoolean;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-36)importagents.ScienceTeacherAgent;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-37)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-38)/** Main class to demonstrate running the {@link LiveAudioAgent} for a voice conversation. */
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-39)publicfinalclass LiveAudioRun{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-40)privatefinalStringuserId;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-41)privatefinalStringsessionId;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-42)privatefinalRunnerrunner;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-43)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-44)privatestaticfinaljavax.sound.sampled.AudioFormatMIC_AUDIO_FORMAT=
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-45)newjavax.sound.sampled.AudioFormat(16000.0f,16,1,true,false);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-46)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-47)privatestaticfinaljavax.sound.sampled.AudioFormatSPEAKER_AUDIO_FORMAT=
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-48)newjavax.sound.sampled.AudioFormat(24000.0f,16,1,true,false);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-49)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-50)privatestaticfinalintBUFFER_SIZE=4096;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-51)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-52)publicLiveAudioRun(){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-53)this.userId="test_user";
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-54)StringappName="LiveAudioApp";
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-55)this.sessionId=UUID.randomUUID().toString();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-56)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-57)InMemorySessionServicesessionService=newInMemorySessionService();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-58)this.runner=newRunner(ScienceTeacherAgent.ROOT_AGENT,appName,null,sessionService);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-59)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-60)ConcurrentMap<String,Object>initialState=newConcurrentHashMap<>();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-61)varunused=
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-62)sessionService.createSession(appName,userId,initialState,sessionId).blockingGet();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-63)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-64)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-65)privatevoidrunConversation()throwsException{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-66)System.out.println("Initializing microphone input and speaker output...");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-67)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-68)RunConfigrunConfig=
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-69)RunConfig.builder()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-70).setStreamingMode(RunConfig.StreamingMode.BIDI)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-71).setResponseModalities(ImmutableList.of(newModality("AUDIO")))
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-72).setSpeechConfig(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-73)SpeechConfig.builder()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-74).voiceConfig(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-75)VoiceConfig.builder()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-76).prebuiltVoiceConfig(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-77)PrebuiltVoiceConfig.builder().voiceName("Aoede").build())
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-78).build())
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-79).languageCode("en-US")
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-80).build())
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-81).build();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-82)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-83)LiveRequestQueueliveRequestQueue=newLiveRequestQueue();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-84)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-85)Flowable<Event>eventStream=
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-86)this.runner.runLive(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-87)runner.sessionService().createSession(userId,sessionId).blockingGet(),
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-88)liveRequestQueue,
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-89)runConfig);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-90)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-91)AtomicBooleanisRunning=newAtomicBoolean(true);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-92)AtomicBooleanconversationEnded=newAtomicBoolean(false);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-93)ExecutorServiceexecutorService=Executors.newFixedThreadPool(2);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-94)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-95)// Task for capturing microphone input
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-96)Future<?>microphoneTask=
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-97)executorService.submit(()->captureAndSendMicrophoneAudio(liveRequestQueue,isRunning));
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-98)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-99)// Task for processing agent responses and playing audio
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-100)Future<?>outputTask=
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-101)executorService.submit(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-102)()->{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-103)try{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-104)processAudioOutput(eventStream,isRunning,conversationEnded);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-105)}catch(Exceptione){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-106)System.err.println("Error processing audio output: "+e.getMessage());
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-107)e.printStackTrace();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-108)isRunning.set(false);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-109)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-110)});
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-111)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-112)// Wait for user to press Enter to stop the conversation
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-113)System.out.println("Conversation started. Press Enter to stop...");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-114)System.in.read();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-115)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-116)System.out.println("Ending conversation...");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-117)isRunning.set(false);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-118)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-119)try{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-120)// Give some time for ongoing processing to complete
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-121)microphoneTask.get(2,TimeUnit.SECONDS);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-122)outputTask.get(2,TimeUnit.SECONDS);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-123)}catch(Exceptione){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-124)System.out.println("Stopping tasks...");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-125)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-126)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-127)liveRequestQueue.close();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-128)executorService.shutdownNow();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-129)System.out.println("Conversation ended.");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-130)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-131)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-132)privatevoidcaptureAndSendMicrophoneAudio(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-133)LiveRequestQueueliveRequestQueue,AtomicBooleanisRunning){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-134)TargetDataLinemicLine=null;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-135)try{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-136)DataLine.Infoinfo=newDataLine.Info(TargetDataLine.class,MIC_AUDIO_FORMAT);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-137)if(!AudioSystem.isLineSupported(info)){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-138)System.err.println("Microphone line not supported!");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-139)return;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-140)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-141)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-142)micLine=(TargetDataLine)AudioSystem.getLine(info);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-143)micLine.open(MIC_AUDIO_FORMAT);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-144)micLine.start();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-145)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-146)System.out.println("Microphone initialized. Start speaking...");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-147)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-148)byte[]buffer=newbyte[BUFFER_SIZE];
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-149)intbytesRead;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-150)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-151)while(isRunning.get()){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-152)bytesRead=micLine.read(buffer,0,buffer.length);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-153)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-154)if(bytesRead>0){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-155)byte[]audioChunk=newbyte[bytesRead];
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-156)System.arraycopy(buffer,0,audioChunk,0,bytesRead);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-157)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-158)BlobaudioBlob=Blob.builder().data(audioChunk).mimeType("audio/pcm").build();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-159)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-160)liveRequestQueue.realtime(audioBlob);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-161)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-162)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-163)}catch(LineUnavailableExceptione){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-164)System.err.println("Error accessing microphone: "+e.getMessage());
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-165)e.printStackTrace();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-166)}finally{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-167)if(micLine!=null){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-168)micLine.stop();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-169)micLine.close();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-170)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-171)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-172)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-173)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-174)privatevoidprocessAudioOutput(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-175)Flowable<Event>eventStream,AtomicBooleanisRunning,AtomicBooleanconversationEnded){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-176)SourceDataLinespeakerLine=null;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-177)try{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-178)DataLine.Infoinfo=newDataLine.Info(SourceDataLine.class,SPEAKER_AUDIO_FORMAT);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-179)if(!AudioSystem.isLineSupported(info)){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-180)System.err.println("Speaker line not supported!");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-181)return;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-182)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-183)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-184)finalSourceDataLinefinalSpeakerLine=(SourceDataLine)AudioSystem.getLine(info);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-185)finalSpeakerLine.open(SPEAKER_AUDIO_FORMAT);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-186)finalSpeakerLine.start();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-187)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-188)System.out.println("Speaker initialized.");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-189)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-190)for(Eventevent:eventStream.blockingIterable()){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-191)if(!isRunning.get()){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-192)break;
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-193)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-194)event.content().ifPresent(content->content.parts().ifPresent(parts->parts.forEach(part->playAudioData(part,finalSpeakerLine))));
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-195)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-196)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-197)speakerLine=finalSpeakerLine;// Assign to outer variable for cleanup in finally block
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-198)}catch(LineUnavailableExceptione){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-199)System.err.println("Error accessing speaker: "+e.getMessage());
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-200)e.printStackTrace();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-201)}finally{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-202)if(speakerLine!=null){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-203)speakerLine.drain();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-204)speakerLine.stop();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-205)speakerLine.close();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-206)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-207)conversationEnded.set(true);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-208)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-209)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-210)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-211)privatevoidplayAudioData(Partpart,SourceDataLinespeakerLine){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-212)part.inlineData()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-213).ifPresent(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-214)inlineBlob->
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-215)inlineBlob
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-216).data()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-217).ifPresent(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-218)audioBytes->{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-219)if(audioBytes.length>0){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-220)System.out.printf(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-221)"Playing audio (%s): %d bytes%n",
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-222)inlineBlob.mimeType(),
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-223)audioBytes.length);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-224)speakerLine.write(audioBytes,0,audioBytes.length);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-225)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-226)}));
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-227)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-228)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-229)privatevoidprocessEvent(Eventevent,java.util.concurrent.atomic.AtomicBooleanaudioReceived){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-230)event
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-231).content()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-232).ifPresent(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-233)content->
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-234)content
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-235).parts()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-236).ifPresent(parts->parts.forEach(part->logReceivedAudioData(part,audioReceived))));
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-237)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-238)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-239)privatevoidlogReceivedAudioData(Partpart,AtomicBooleanaudioReceived){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-240)part.inlineData()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-241).ifPresent(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-242)inlineBlob->
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-243)inlineBlob
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-244).data()
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-245).ifPresent(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-246)audioBytes->{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-247)if(audioBytes.length>0){
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-248)System.out.printf(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-249)"  Audio (%s): received %d bytes.%n",
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-250)inlineBlob.mimeType(),
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-251)audioBytes.length);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-252)audioReceived.set(true);
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-253)}else{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-254)System.out.printf(
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-255)"  Audio (%s): received empty audio data.%n",
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-256)inlineBlob.mimeType());
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-257)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-258)}));
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-259)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-260)
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-261)publicstaticvoidmain(String[]args)throwsException{
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-262)LiveAudioRunliveAudioRun=newLiveAudioRun();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-263)liveAudioRun.runConversation();
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-264)System.out.println("Exiting Live Audio Run.");
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-265)}
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-6-266)}

```

### **Run the Live Audio Run tool**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#run-the-live-audio-run-tool "Permanent link")
To run Live Audio Run tool, use the following command on the `adk-agents` directory:
```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-7-1)mvn compile exec:java

```

Then you should see:
```
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-8-1)$ mvn compile exec:java
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-8-2)...
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-8-3)Initializing microphone input and speaker output...
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-8-4)Conversation started. Press Enter to stop...
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-8-5)Speaker initialized.
[](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#__codelineno-8-6)Microphone initialized. Start speaking...

```

With this message, the tool is ready to take voice input. Talk to the agent with a question like `What's the electron?`.
Caution
When you observe the agent keep speaking by itself and doesn't stop, try using earphones to suppress the echoing.
## **Summary**[¶](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming-java/#summary "Permanent link")
Streaming for ADK enables developers to create agents capable of low-latency, bidirectional voice and video communication, enhancing interactive experiences. The article demonstrates that text streaming is a built-in feature of ADK Agents, requiring no additional specific code, while also showcasing how to implement live audio conversations for real-time voice interaction with an agent. This allows for more natural and dynamic communication, as users can speak to and hear from the agent seamlessly.
Back to top
