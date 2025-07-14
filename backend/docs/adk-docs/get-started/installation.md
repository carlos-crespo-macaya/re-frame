[ Skip to content ](https://google.github.io/adk-docs/get-started/installation/#installing-adk)
# Installing ADK[¶](https://google.github.io/adk-docs/get-started/installation/#installing-adk "Permanent link")
[Python](https://google.github.io/adk-docs/get-started/installation/#python)[Java](https://google.github.io/adk-docs/get-started/installation/#java)
## Create & activate virtual environment[¶](https://google.github.io/adk-docs/get-started/installation/#create-activate-virtual-environment "Permanent link")
We recommend creating a virtual Python environment using [venv](https://docs.python.org/3/library/venv.html):
```
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-0-1)python-mvenv.venv

```

Now, you can activate the virtual environment using the appropriate command for your operating system and environment:
```
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-1)# Mac / Linux
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-2)source .venv/bin/activate
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-3)
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-4)# Windows CMD:
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-5).venv\Scripts\activate.bat
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-6)
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-7)# Windows PowerShell:
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-1-8).venv\Scripts\Activate.ps1

```

### Install ADK[¶](https://google.github.io/adk-docs/get-started/installation/#install-adk "Permanent link")
```
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-2-1)pipinstallgoogle-adk

```

(Optional) Verify your installation:
```
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-3-1)pipshowgoogle-adk

```

You can either use maven or gradle to add the `google-adk` and `google-adk-dev` package.
`google-adk` is the core Java ADK library. Java ADK also comes with a pluggable example SpringBoot server to run your agents seamlessly. This optional package is present as part of `google-adk-dev`.
If you are using maven, add the following to your `pom.xml`:
pom.xml```
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-1)<dependencies>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-2)<!-- The ADK Core dependency -->
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-3)<dependency>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-4)<groupId>com.google.adk</groupId>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-5)<artifactId>google-adk</artifactId>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-6)<version>0.1.0</version>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-7)</dependency>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-8)
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-9)<!-- The ADK Dev Web UI to debug your agent (Optional) -->
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-10)<dependency>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-11)<groupId>com.google.adk</groupId>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-12)<artifactId>google-adk-dev</artifactId>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-13)<version>0.1.0</version>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-14)</dependency>
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-4-15)</dependencies>

```

Here's a [complete pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml) file for reference.
If you are using gradle, add the dependency to your build.gradle:
build.gradle```
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-5-1)dependencies {
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-5-2)  implementation 'com.google.adk:google-adk:0.1.0'
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-5-3)  implementation 'com.google.adk:google-adk-dev:0.1.0'
[](https://google.github.io/adk-docs/get-started/installation/#__codelineno-5-4)}

```

## Next steps[¶](https://google.github.io/adk-docs/get-started/installation/#next-steps "Permanent link")
  * Try creating your first agent with the [**Quickstart**](https://google.github.io/adk-docs/get-started/quickstart/)


Back to top
