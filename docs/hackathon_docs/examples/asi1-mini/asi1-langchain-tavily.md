---
id: asi-langchain-tavily
title: ASI1-mini LangChain & Tavily Search Integration Guide
---

# ASI1-mini LangChain & Tavily Search Integration Guide

This guide demonstrates how to integrate the ASI1-mini API with LangChain and leverage the Tavily Search tool to process search queries in a streamlined manner. The project is encapsulated in a single file that implements a custom LangChain `LLM` and integrates it with an agent chain to combine API responses with dynamic search results.

## Overview

This project showcases an integration system built on the following key components:

- **Custom LLM Integration:**  
  Implements a custom LangChain `LLM` that sends user prompts to the ASI1-mini API using a defined JSON payload.

- **Tavily Search Tool:**  
  Uses the Tavily Search API to fetch search results, which are then incorporated into the agent chain to enhance the response.

- **Agent Chain Execution:**  
  Sets up an agent chain that processes search queries, calls the ASI1-mini API, and returns a combined result.

- **Environment-Based Configuration:**  
  Manages API keys and sensitive configurations through environment variables loaded from a `.env` file.

## Prerequisites

Before running this project, ensure you have the following:

- **Python:** Version 3.8 or higher.
- **Required Python Packages:**
  ```bash
  pip install requests pydantic python-dotenv langchain
  ```
- **Environment Variables:**
    - A valid API key for ASI1. Obtain your API Key [here](https://asi1.ai/dashboard/api-keys).
    - A valid API key for Tavily. Obtain your API Key [here](https://app.tavily.com/home#).

    Create a `.env` file in the project directory with the following keys:
    `ASI_LLM_KEY=<asi1-api_key>`
    `TAVILY_API_KEY=<tavily_api_key>`

## Project Structure
  The entire integration is contained within a single file:

`ASI_Langchain.py`  # Contains the custom LLM class and the search handler integration

## Script Breakdown

__1. Importing Required Libraries__

The script begins by importing the necessary modules:
    - **os**: To get environment variables.
    - **requests:** To perform HTTP requests to the ASI-1 Mini API.
    - **typing:** For getting Python types.
    - **pydantic:** To define pydantic data models required by Langchain.
    - **langchain:** Imports required by Langchain.
    - **langchain_community:** Imports required to use the TavilySearch tool.

```python
import os
import requests
from typing import Optional, List
from pydantic import Field
from langchain.llms.base import LLM
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from dotenv import load_dotenv
```

__2. Defining the ASI-1 Mini LLM Class__

Defines a custom LangChain LLM that sends prompts to the ASI1-mini API. It supports parameters such as temperature, fun mode, and web search, and handles API responses by extracting the relevant message content.

```python
class ASI1MINI(LLM):
    api_key: str = Field(...)
    api_url: str = Field(...)
    model: str = Field(default="asi1-mini")
    temperature: float = Field(default=0.7)
    fun_mode: bool = Field(default=False)
    web_search: bool = Field(default=False)
    enable_stream: bool = Field(default=False)
    max_tokens: int = Field(default=1024)

    @property
    def _llm_type(self) -> str:
        return "custom_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "fun_mode": self.fun_mode,
            "web_search": self.web_search,
            "stream": self.enable_stream,
            "max_tokens": self.max_tokens,
        }
        if stop:
            payload["stop"] = stop

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        return (
            response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )


```

__3. Initializing the Agent__

The agent is defined in the `custom_search_handler` function.

```python
def custom_search_handler(data):
    """
    Uses LangChain to process a search query with the custom LLM.
    Expects a JSON payload with the key "search_query" and returns the result.
    """
    search_query = data.get("search_query")
    if not search_query:
        return {"error": "Missing search query"}

    custom_api_key = os.getenv("ASI_LLM_KEY")
    custom_api_url = "https://api.asi1.ai/v1/chat/completions"
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    print("1: ", custom_api_key)
    print("2: ", custom_api_url)
    print("3: ", tavily_api_key)

    if not custom_api_key or not custom_api_url or not tavily_api_key:
        return {"error": "Missing API keys"}

    try:
        # Initialize your custom LLM
        llm = ASI1MINI(api_key=custom_api_key, api_url=custom_api_url, temperature=0.7)
        # Initialize the Tavily search tool
        search = TavilySearchAPIWrapper()
        tavily_tool = TavilySearchResults(
            api_wrapper=search, tavily_api_key=tavily_api_key
        )

        # Initialize the agent with your custom LLM and Tavily search tool
        agent_chain = initialize_agent(
            [tavily_tool],
            llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )
        # Run the agent chain with the search query
        result = agent_chain.invoke({"input": search_query})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
```

# Running the System

__1. Activate Your Virtual Environment:__

```bash
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

__2. Run the Script:__

```bash
python ASI_Langchain.py
```

# Sample Outputs
1. **Factual question known by the LLM(Does not use the Tavily tool)**

    **Input:** `How tall is the Eiffel tower?`

    **Final Output:** 
    ```bash
    {'result': 'The Eiffel Tower is approximately 330 meters (1,083 feet) tall, including its antennas.'}
    ```



2. **Current news not known by the LLM (Uses the Tavily tool)**

    **Input:** `Nvidia company news?`

    ** Final Output:** 
    ```bash
    {'result': "Here are some recent updates on NVIDIA:\n1. **GTC 2025 Announcement**: NVIDIA’s premier AI conference will take place from March 17-21, 2025, in San Jose, California, featuring advancements in agentic AI and RTX AI tools.\n2. **New Product Launch**: The NVIDIA GeForce RTX 5070 Ti, built on the Blackwell architecture, is now available, boosting generative AI content creation and creative workflows.\n3. **AI Platform Advancements**: NVIDIA has unveiled the Rubin AI platform, set for 2026, and introduced the largest publicly available AI model for genomic data using DGX Cloud.\n4. **Stock Performance**: After a 27% decline over three weeks, Nvidia stock is attempting a rebound, supported by positive analyst reports.\nFor more details, you can visit NVIDIA's official newsroom or recent financial updates."}
    ```

# Troubleshooting

1. **Environment Variables**

Ensure that both `ASI_LLM_KEY` and `TAVILY_API_KEY` are correctly defined in your `.env` file.

Missing or incorrect API keys will lead to errors.
API Connectivity

Verify that the ASI1-mini API endpoint (https://api.asi1.ai/v1/chat/completions) is accessible.

Confirm that the Tavily Search API is operational and that your API key is valid.

# Debugging
The code includes debug print statements (e.g., printing API responses) to help trace issues with API calls or response handling.
Review the console output to diagnose any problems during execution.


# Benefits of This Integration
1. **Seamless API Communication:**

    Directly integrates with the ASI1-mini API via a custom LangChain LLM.

2. **Enhanced Search Capabilities:**

    Enriches responses by combining LLM outputs with real-time search results using Tavily Search.

3. **Configurable Parameters:**

    Offers flexibility through parameters like temperature, fun mode, and maximum tokens.

4. **Simplified Deployment:**

    The single-file integration simplifies setup and deployment, making it easy to incorporate into larger projects.

# Additional Resources

- **ASI1-mini API Documentation**(https://docs.asi1.ai)
- **LangChain GitHub Repository**(https://python.langchain.com/docs/introduction/)
- **Tavily Search Tool Documentation**(https://docs.tavily.com/welcome)



## GitHub Repository

For the complete code, visit the [ASI1 Chat System Repository](https://github.com/abhifetch/ASI-1_mini_Langchain).

:::note
**Note:** You can learn more about ASI1 Mini APIs [__here__](https://docs.asi1.ai/docs/).
::: 