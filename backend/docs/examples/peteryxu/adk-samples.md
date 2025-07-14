[Skip to content](https://github.com/peteryxu/adk-samples#start-of-content)
You signed in with another tab or window. [Reload](https://github.com/peteryxu/adk-samples) to refresh your session. You signed out in another tab or window. [Reload](https://github.com/peteryxu/adk-samples) to refresh your session. You switched accounts on another tab or window. [Reload](https://github.com/peteryxu/adk-samples) to refresh your session. Dismiss alert
{{ message }}
[ peteryxu ](https://github.com/peteryxu) / **[adk-samples](https://github.com/peteryxu/adk-samples) ** Public
forked from [google/adk-samples](https://github.com/google/adk-samples)
  * [ Notifications ](https://github.com/login?return_to=%2Fpeteryxu%2Fadk-samples) You must be signed in to change notification settings
  * [ Fork 0 ](https://github.com/login?return_to=%2Fpeteryxu%2Fadk-samples)
  * [ Star  0 ](https://github.com/login?return_to=%2Fpeteryxu%2Fadk-samples)


A collection of sample agents built with Agent Development (ADK)
[google.github.io/adk-docs/](https://google.github.io/adk-docs/ "https://google.github.io/adk-docs/")
### License
[ Apache-2.0 license ](https://github.com/peteryxu/adk-samples/blob/main/LICENSE)
[ 0 stars ](https://github.com/peteryxu/adk-samples/stargazers) [ 987 forks ](https://github.com/peteryxu/adk-samples/forks) [ Branches ](https://github.com/peteryxu/adk-samples/branches) [ Tags ](https://github.com/peteryxu/adk-samples/tags) [ Activity ](https://github.com/peteryxu/adk-samples/activity)
[ Star  ](https://github.com/login?return_to=%2Fpeteryxu%2Fadk-samples)
[ Notifications ](https://github.com/login?return_to=%2Fpeteryxu%2Fadk-samples) You must be signed in to change notification settings
# peteryxu/adk-samples
main
[**1** Branch](https://github.com/peteryxu/adk-samples/branches)[**0** Tags](https://github.com/peteryxu/adk-samples/tags)
[](https://github.com/peteryxu/adk-samples/branches)[](https://github.com/peteryxu/adk-samples/tags)
Go to file
Code
Open more actions menu
This branch is [251 commits behind](https://github.com/peteryxu/adk-samples/compare/main...google%3Aadk-samples%3Amain) google/adk-samples:main.
## Folders and files
Name| Name| Last commit message| Last commit date
---|---|---|---
## Latest commit
[![turanbulmus](https://avatars.githubusercontent.com/u/124069046?v=4&size=40)](https://github.com/turanbulmus)[turanbulmus](https://github.com/peteryxu/adk-samples/commits?author=turanbulmus)[Merge pull request](https://github.com/peteryxu/adk-samples/commit/71b6655915269a182e4cc6fd0c2168f3e89cd103) [google#9](https://github.com/google/adk-samples/pull/9) [from mstyer-google/main](https://github.com/peteryxu/adk-samples/commit/71b6655915269a182e4cc6fd0c2168f3e89cd103)Open commit detailsApr 11, 2025[71b6655](https://github.com/peteryxu/adk-samples/commit/71b6655915269a182e4cc6fd0c2168f3e89cd103) · Apr 11, 2025
## History
[6 Commits](https://github.com/peteryxu/adk-samples/commits/main/)Open commit details[](https://github.com/peteryxu/adk-samples/commits/main/)
[agents](https://github.com/peteryxu/adk-samples/tree/main/agents "agents")| [agents](https://github.com/peteryxu/adk-samples/tree/main/agents "agents")| [Minor fixes:](https://github.com/peteryxu/adk-samples/commit/6e8ccf3de2f58f5db14a53d13fbd59b6bfe22210 "Minor fixes:
* \[data-science, fomc-research\] Fix test_deployment.py scripts
* \[travel-concierge\] Improved planning and booking agent stability; Increased eval tries to 4 for better chances of succeeding
* \[customer-service\] updating customer service agent readme
* \[RAG\] Add llama-index requirement to RAG agent.")| Apr 10, 2025
[CONTRIBUTING.md](https://github.com/peteryxu/adk-samples/blob/main/CONTRIBUTING.md "CONTRIBUTING.md")| [CONTRIBUTING.md](https://github.com/peteryxu/adk-samples/blob/main/CONTRIBUTING.md "CONTRIBUTING.md")| [initial commit with readmes](https://github.com/peteryxu/adk-samples/commit/070312d68d1210afee6a6b76bdd9a4e9572a3a11 "initial commit with readmes")| Apr 8, 2025
[LICENSE](https://github.com/peteryxu/adk-samples/blob/main/LICENSE "LICENSE")| [LICENSE](https://github.com/peteryxu/adk-samples/blob/main/LICENSE "LICENSE")| [initial commit with readmes](https://github.com/peteryxu/adk-samples/commit/070312d68d1210afee6a6b76bdd9a4e9572a3a11 "initial commit with readmes")| Apr 8, 2025
[README.md](https://github.com/peteryxu/adk-samples/blob/main/README.md "README.md")| [README.md](https://github.com/peteryxu/adk-samples/blob/main/README.md "README.md")| [fixing links to documentation](https://github.com/peteryxu/adk-samples/commit/effa3dc9b067dd0ed636f6e0cd2a6ef96c95c230 "fixing links to documentation")| Apr 9, 2025
View all files
## Repository files navigation
# Agent Development Kit (ADK) Samples
[](https://github.com/peteryxu/adk-samples#agent-development-kit-adk-samples)
[![License](https://camo.githubusercontent.com/5ce2e21e84680df1ab24807babebc3417d27d66e0826a350eb04ab57f4c8f3e5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4170616368655f322e302d626c75652e737667)](https://github.com/peteryxu/adk-samples/blob/main/LICENSE)
[![Agent Development Kit Logo](https://github.com/google/adk-docs/raw/main/docs/assets/agent-development-kit.png)](https://github.com/google/adk-docs/blob/main/docs/assets/agent-development-kit.png)
Welcome to the Sample Agents repository! This collection provides ready-to-use agents built on top of the [Agent Development Kit](https://github.com/google/adk-python), designed to accelerate your development process. These agents cover a range of common use cases and complexities, from simple conversational bots to complex multi-agent workflows.
## ✨ What are Sample Agents?
[](https://github.com/peteryxu/adk-samples#-what-are-sample-agents)
A Sample Agent is a functional starting point for a foundational agent designed for common application scenarios. It comes pre-packaged with core logic (like different agents using different tools, evaluation, human in the loop) relevant to a specific use case or industry. While functional, a Sample Agent typically requires customization (e.g., adjusting specific responses or integrating with external systems) to be fully operational. Each agent includes instructions on how it can be customized.
## 🚀 Getting Started
[](https://github.com/peteryxu/adk-samples#-getting-started)
Follow these steps to set up and run the sample agents:
  1. **Prerequisites:**
     * **Install the ADK Samples:** Ensure you have the Agent Development Kit installed and configured. Follow the [ADK Installation Guide](https://google.github.io/adk-docs/get-started/installation/).
     * **Set Up Environment Variables:** Each agent example relies on a `.env` file for configuration (like API keys, Google Cloud project IDs, and location). This keeps secrets out of the code.
       * You will need to create a `.env` file in each agent's directory you wish to run (usually by copying the provided `.env.example`).
       * Setting up these variables, especially obtaining Google Cloud credentials, requires careful steps. Refer to the **Environment Setup** section in the [ADK Installation Guide](https://google.github.io/adk-docs/get-started/installation/) for detailed instructions.
     * **Google Cloud Project (Recommended):** While some agents might run locally with just an API key, most leverage Google Cloud services like Vertex AI and BigQuery. A configured Google Cloud project is highly recommended. See the [ADK Quickstart](https://google.github.io/adk-docs/get-started/quickstart/) for setup details.
  2. **Clone this repository:** You can install the ADK samples via cloning it from the public repository by
```
git clone https://github.com/google/adk-samples.git
cd adk-samples
```

  3. **Explore the Agents:**


  * Navigate to the `agents/` directory.
  * The `agents/README.md` provides an overview and categorization of the available agents.
  * Browse the subdirectories. Each contains a specific sample agent with its own `README.md`.


  1. **Run an Agent:**
     * Choose an agent from the `agents/` directory.
     * Navigate into that agent's specific directory (e.g., `cd agents/llm-auditor`).
     * Follow the instructions in _that agent's_ `README.md` file for specific setup (like installing dependencies via `poetry install`) and running the agent.
Browse the folders in this repository. Each agent and tool have its own `README.md` file with detailed instructions.


**Notes:**
  * These agents have been built and tested using [Google models](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) on Vertex AI. You can test these samples with other models as well. Please refer to [ADK Tutorials](https://google.github.io/adk-docs/agents/models/) to use other models for these samples.


## 🧱 Repository Structure
[](https://github.com/peteryxu/adk-samples#-repository-structure)
```
.
├── agents         # Contains individual agent samples
│  ├── agent1       # Specific agent directory
│  │  └── README.md    # Agent-specific instructions
│  ├── agent2
│  │  └── README.md
│  ├── ...
│  └── README.md      # Overview and categorization of agents
└── README.md        # This file (Repository overview)
```

## ℹ️ Getting help
[](https://github.com/peteryxu/adk-samples#ℹ️-getting-help)
If you have any questions or if you found any problems with this repository, please report through [GitHub issues](https://github.com/google/adk-samples/issues).
## 🤝 Contributing
[](https://github.com/peteryxu/adk-samples#-contributing)
We welcome contributions from the community! Whether it's bug reports, feature requests, documentation improvements, or code contributions, please see our [**Contributing Guidelines**](https://github.com/google/adk-samples/blob/main/CONTRIBUTING.md) to get started.
## 📄 License
[](https://github.com/peteryxu/adk-samples#-license)
This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/google/adk-samples/blob/main/LICENSE) file for details.
## Disclaimers
[](https://github.com/peteryxu/adk-samples#disclaimers)
This is not an officially supported Google product. This project is not eligible for the [Google Open Source Software Vulnerability Rewards Program](https://bughunters.google.com/open-source-security).
This project is intended for demonstration purposes only. It is not intended for use in a production environment.
## About
A collection of sample agents built with Agent Development (ADK)
[google.github.io/adk-docs/](https://google.github.io/adk-docs/ "https://google.github.io/adk-docs/")
### Resources
[ Readme ](https://github.com/peteryxu/adk-samples#readme-ov-file)
### License
[ Apache-2.0 license ](https://github.com/peteryxu/adk-samples#Apache-2.0-1-ov-file)
###  Uh oh!
There was an error while loading. [Please reload this page](https://github.com/peteryxu/adk-samples).
[ Activity](https://github.com/peteryxu/adk-samples/activity)
### Stars
[ **0** stars](https://github.com/peteryxu/adk-samples/stargazers)
### Watchers
[ **0** watching](https://github.com/peteryxu/adk-samples/watchers)
### Forks
[ **0** forks](https://github.com/peteryxu/adk-samples/forks)
[ Report repository ](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fpeteryxu%2Fadk-samples&report=peteryxu+%28user%29)
##  [Releases](https://github.com/peteryxu/adk-samples/releases)
No releases published
##  [Packages 0](https://github.com/users/peteryxu/packages?repo_name=adk-samples)
No packages published
## Languages
  * Python 93.5%
  * HTML 5.2%
  * Shell 1.3%


You can’t perform that action at this time.
