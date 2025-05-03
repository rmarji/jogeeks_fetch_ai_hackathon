---
id: asi1-mini-language-tutor
title: AI Language Tutor with ASI-1 Mini
---

# Building an AI Language Tutor uAgent with ASI-1 Mini

This guide explains how to create a simple uAgent that serves as an AI language tutor using the ASI-1 Mini API. The agent accepts a user query and returns language learning assistance—such as translation, grammar correction, or pronunciation tips—based on the provided prompt.

## Overview

### Purpose

This project demonstrates how to integrate ASI-1 Mini, Fetch.ai's Web3-native large language model, into a uAgent. The agent, named __AI_Language_Tutor__, is designed to:

    - Call the __ASI-1 Mini API__ with a prompt tailored for language learning.
    - Provide translation, grammar correction, or pronunciation tips based on user input.
    - Log the response upon agent startup.


## Prerequisites

Before running this project, ensure you have:

    - Python 3.11 installed.
    - uAgents library installed. If not already installed, use:
    ```
    pip install uagents
    ```
    - Requests library installed:
    ```
    pip install requests
    ```
    - A valid API key for ASI-1 Mini. Get your API Key [here](https://asi1.ai/dashboard/api-keys).

## Script Breakdown

__1. Importing Required Libraries__

The script begins by importing the necessary modules:

    - **requests:** To perform HTTP requests to the ASI-1 Mini API.
    - **json:** For handling JSON responses and potential JSON decode errors.
    - **uagents:** To create the uAgent and manage events.
    - **Context:** Provides access to the agent's runtime context, including logging.

```python
import requests
import json
from uagents import Agent, Context
```

__2. Initializing the uAgent__

An instance of the uAgent is created with a name, port, and endpoint. 

```python
agent = Agent(
    name="AI_Language_Tutor",
    port=8000,  # You can change this to any available port
    endpoint="http://localhost:8000/submit"
)
```

__3. Defining the ASI-1 Mini API Helper Function__

The function `get_language_help` constructs a custom prompt and sends a POST request to the ASI-1 Mini API. Based on the user's query and target language, it asks the API to either translate, correct grammar, or offer pronunciation tips.

```python
def get_language_help(query: str, target_language: str = "Spanish") -> str:
    url = "https://api.asi1.ai/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer <Your_ASI1_Mini_API_Key>'  # Replace with your API Key
    }

    prompt = f"""You are an AI language tutor. Help the user with their language learning request:

    - If they ask for a **translation**, provide it in {target_language}.
    - If they provide a sentence, **correct any grammar mistakes**.
    - If they ask for pronunciation tips, explain how to say it.

    User request: "{query}"
    """

    payload = {
        "model": "asi1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 0
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        return f"API Request Error: {str(e)}"

    except json.JSONDecodeError:
        return "API Error: Unable to parse JSON response"
```

__4. Startup Event Handler__

The agent registers an `on_event("startup")` handler. When the agent starts, it:

    - Logs a sample query.
    - Calls the `get_language_help` function with an example query.
    - Logs the returned response from the ASI-1 Mini API.

```python
@agent.on_event("startup")
async def language_tutor_demo(ctx: Context):
    query = "How do you say 'Good morning' in French?"  # Example query
    ctx.logger.info(f"User query: {query}")
    response = get_language_help(query, target_language="French")
    ctx.logger.info(f"🌍 AI Tutor Response: {response}")
```

__5. Running the Agent__

The script concludes by running the agent, which starts the server and registers the startup handler.

```python
if __name__ == "__main__":
    agent.run()
```

## Running the Agent

__1. Activate Your Virtual Environment:__

```bash
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

__2. Run the Script:__

```bash
python my_language_tutor.py
```

__3. Expected Output:__ 

Upon startup, you should see log messages similar to:

```
INFO: [AI_Language_Tutor]: Starting agent with address: agent1...
INFO: [AI_Language_Tutor]: User query: How do you say 'Good morning' in French?
INFO: [AI_Language_Tutor]: 🌍 AI Tutor Response: Bonjour (Good morning/Good day).
```

## GitHub Repository

For the complete code and additional examples, visit the [ASI-1-Mini-simple-Examples](https://github.com/abhifetch/ASI-1-Mini-simple-Examples/blob/main/language_tutor.py) repository.

:::note
**Note:** You can learn more about ASI-1 Mini APIs [__here__](https://docs.asi1.ai/docs/).
::: 