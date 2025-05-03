---
id: asi-mini-example
title: ASI-1 Mini Examples
---

# ASI1-Mini Example Repositories

Below is a **brief overview** of various open-source repositories demonstrating how to integrate and use **ASI1-Mini** in different scenarios, from simple scripts to advanced multi-agent systems.


## 1. ASI-1-Mini-simple-Examples
**GitHub**: [ASI-1-Mini-simple-Examples](https://github.com/abhifetch/ASI-1-Mini-simple-Examples)  
A **collection of simple agents** built with the uAgents framework. Each script focuses on a specialized task (language tutor, LeetCode solver, fun fact generator, etc.) and is powered by **ASI1-Mini**.


## 2. langchain-asi
**GitHub**: [langchain-asi integration](https://github.com/rajashekarcs2023/langchain-asi)  
A **lightweight integration package** connecting ASI1’s API with LangChain. Ideal if you want to easily swap out other LLM providers for **ASI1-Mini** while retaining multi-turn conversations, agent support, system messages, and more.


## 3. ASI-1_mini_Langchain
**GitHub**: [ASI-1_mini_Langchain and tavily](https://github.com/abhifetch/ASI-1_mini_Langchain)  
Shows a **custom LLM integration** with LangChain and **Tavily Search**. Learn how to build a custom LangChain `LLM` class that calls the ASI1-Mini API and fetches external information for more sophisticated query handling.

## 4. DeFI-Agent-Starter
**GitHub**: [DeFI-Agent-Starter](https://github.com/RoyceBraden/DeFI-Agent-Starter)  
A **multi-agent** system focusing on **DeFi (Decentralized Finance)** use cases. It leverages **AgentVerse** and ASI1-Mini to determine whether to hold or sell a crypto asset based on Fear and Greed Index and sentiment analysis.

## 5. ASI1-Mini-Chat-System
**GitHub**: [ASI1-Mini-Chat-System](https://github.com/abhifetch/ASI1-Mini-Chat-System)  
A **modular, agent-based chat system** powered by uAgents. It features a **Client Agent** and a **Server Agent** that communicate in real time, with queries relayed to the ASI1 API for intelligent responses.

## Getting Started

1. **Clone any repository** that fits your interests.  
2. **Install dependencies** and create a `.env` file (or set environment variables) with your `ASI1_API_KEY`.  Get your API Key [here](https://asi1.ai/dashboard/api-keys).
3. **Run the sample scripts** or follow the instructions in each repo’s README.  
4. **Experiment & Customize** – tweak prompts, add tools, or integrate more data sources.

:::note
**Note:** You can learn more about ASI-1 Mini APIs [__here__](https://docs.asi1.ai/docs/).
:::

With **ASI1-Mini**, you can rapidly build anything from simple chatbots to complex, multi-agent DeFi applications.