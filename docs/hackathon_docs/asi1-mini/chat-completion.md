---
id: asi1-mini-chat-completion
title: Chat Completion with ASI-1 Mini
sidebar_label: Chat Completion
---

# Chat Completion with ASI-1 Mini

The Chat Completion API is the primary way to interact with ASI-1 Mini. This guide provides detailed information on how to use the API effectively, with examples and best practices.

## Overview

The Chat Completion API allows you to have conversational interactions with ASI-1 Mini. You provide a series of messages representing a conversation, and the model generates a response that continues the conversation in a natural way.

What sets ASI-1 Mini apart from other LLMs is its agentic capabilities - it can reason through complex problems, maintain context across long conversations, and execute multi-step tasks autonomously.

## Endpoint

```
POST https://api.asi1.ai/v1/chat/completions
```

## Request Format

A basic chat completion request includes the model name, a list of messages, and optional parameters to control the generation:

```json
{
  "model": "asi1-mini",
  "messages": [
    {
      "role": "user",
      "content": "Your message here"
    }
  ],
  "temperature": 0,
  "stream": false,
  "max_tokens": 500
}
```

### Required Parameters

- `model`: Currently, only "asi1-mini" is available.
- `messages`: An array of message objects representing the conversation history.

### Optional Parameters

- `temperature`: Controls randomness in the response. Range is 0-2, with lower values producing more deterministic outputs. Default is 1.0.
- `stream`: When set to `true`, the API will stream the response as it's generated. Default is `false`.
- `max_tokens`: The maximum number of tokens to generate. Default varies based on the model.

## Message Roles

Each message in the conversation has a `role` and `content`. The available roles are:

- `system`: Used to set the behavior or context for the assistant. System messages help guide the model's behavior.
- `user`: Represents messages from the user.
- `assistant`: Represents previous responses from the assistant.

## Basic Example

Here's a simple example of a chat completion request and response:

### Request

```python
import requests
import json

url = "https://api.asi1.ai/v1/chat/completions"

payload = json.dumps({
  "model": "asi1-mini",
  "messages": [
    {
      "role": "user",
      "content": "Hi, tell me about giraffes"
    }
  ],
  "temperature": 0,
  "stream": False,
  "max_tokens": 500
})

headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer YOUR_API_KEY'  # Replace with your actual API key
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

### Response

```json
{
  "id": "id_comqjiusZjAoyuXlh",
  "object": "chat.completion",
  "model": "asi1-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Giraffes are fascinating creatures known for their towering height and distinctive long necks. They are the tallest land animals, with heights ranging from 14 to 19 feet (4.3 to 5.8 meters). Males, called bulls, are typically taller and heavier than females (cows). Their long necks allow them to reach leaves, flowers, and fruits high up in trees, especially from their preferred food source, the acacia tree.\n\nThese animals are native to Africa and are commonly found in savannas, grasslands, and open woodlands. Giraffes live in loose social groups, often mingling with other herbivores like zebras and antelopes. They are generally peaceful but can defend themselves with powerful kicks if threatened by predators such as lions or hyenas.\n\nOne of the most unique traits of giraffes is their spotted coat pattern, which is unique to each individual, much like a human fingerprint. They also have a specialized cardiovascular system to manage blood flow due to their height—especially when lowering their heads to drink water. Giraffes only need to drink water occasionally, as they obtain most of their moisture from the plants they consume.\n\nTheir social behavior and communication are also intriguing. Giraffes communicate using low-frequency sounds that are often inaudible to human ears. Additionally, they engage in a behavior called \"necking,\" where males swing their necks to compete for dominance or mates."
      },
      "finish_reason": "stop",
      "stop_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 435,
    "completion_tokens": 391,
    "total_tokens": 826
  }
}
```

## Multi-turn Conversations

ASI-1 Mini excels at maintaining context across multiple turns of conversation. To create a multi-turn conversation, include previous messages in the `messages` array:

```python
payload = json.dumps({
  "model": "asi1-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert in Web3 technologies and decentralized systems."
    },
    {
      "role": "user",
      "content": "What is a blockchain?"
    },
    {
      "role": "assistant",
      "content": "A blockchain is a distributed, immutable ledger that records transactions across many computers. It's the underlying technology behind cryptocurrencies like Bitcoin, but its applications extend far beyond digital currencies. Each 'block' contains a set of transactions, and once verified, it's linked to the previous block, forming a chain. This design makes the data extremely difficult to alter retroactively, providing security and transparency."
    },
    {
      "role": "user",
      "content": "How does this relate to Web3?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 500
})
```

## Streaming Responses

For more interactive applications, you can stream the response as it's being generated:

```python
import requests
import json

url = "https://api.asi1.ai/v1/chat/completions"

payload = json.dumps({
  "model": "asi1-mini",
  "messages": [
    {
      "role": "user",
      "content": "Explain the concept of decentralized AI"
    }
  ],
  "temperature": 0.7,
  "stream": True,
  "max_tokens": 500
})

headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer YOUR_API_KEY'
}

response = requests.request("POST", url, headers=headers, data=payload, stream=True)

for line in response.iter_lines():
    if line:
        line_text = line.decode('utf-8')
        if line_text.startswith('data: '):
            data_str = line_text[6:]  # Remove 'data: ' prefix
            if data_str == '[DONE]':
                break
            try:
                data = json.loads(data_str)
                if 'choices' in data and len(data['choices']) > 0:
                    delta = data['choices'][0].get('delta', {})
                    if 'content' in delta:
                        print(delta['content'], end='', flush=True)
            except json.JSONDecodeError:
                pass
```

When streaming is enabled, you'll receive a series of server-sent events (SSE), each containing a small piece of the response. The stream is terminated with a `data: [DONE]` message.

## Accessing Model Thoughts

A unique feature of ASI-1 Mini is the ability to access the model's "thoughts" during generation when streaming is enabled. These thoughts provide insight into the model's reasoning process:

```python
for line in response.iter_lines():
    if line:
        line_text = line.decode('utf-8')
        if line_text.startswith('data: '):
            data_str = line_text[6:]  # Remove 'data: ' prefix
            if data_str == '[DONE]':
                break
            try:
                data = json.loads(data_str)
                if 'thought' in data:
                    print(f"Thought: {data['thought']}")
                elif 'choices' in data and len(data['choices']) > 0:
                    delta = data['choices'][0].get('delta', {})
                    if 'content' in delta:
                        print(f"Content: {delta['content']}", end='', flush=True)
            except json.JSONDecodeError:
                pass
```

## Best Practices

### System Messages

Use system messages to guide the model's behavior. For example:

```json
{
  "role": "system",
  "content": "You are an AI assistant specialized in blockchain technology. Provide concise, accurate information and use examples where appropriate."
}
```

### Managing Context Length

ASI-1 Mini has a limited context window. To manage long conversations:

1. Summarize previous turns when necessary
2. Remove less relevant messages from the history
3. Focus on the most recent and relevant context

### Controlling Response Style

Use the temperature parameter to control the creativity of responses:

- Lower temperature (0.2-0.5): More deterministic, factual responses
- Medium temperature (0.5-0.8): Balanced creativity and coherence
- Higher temperature (0.8-1.0): More creative, diverse responses

### Error Handling

Implement robust error handling in your application:

```python
try:
    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()  # Raise an exception for 4XX/5XX responses
    result = response.json()
    # Process the result
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    # Handle specific status codes if needed
except requests.exceptions.ConnectionError as conn_err:
    print(f"Connection error occurred: {conn_err}")
except requests.exceptions.Timeout as timeout_err:
    print(f"Timeout error occurred: {timeout_err}")
except requests.exceptions.RequestException as req_err:
    print(f"An error occurred: {req_err}")
except json.JSONDecodeError as json_err:
    print(f"JSON decode error: {json_err}")
```

## Advanced Use Cases

ASI-1 Mini's agentic capabilities make it particularly well-suited for:

1. **Multi-step reasoning tasks**: Problems that require breaking down into steps
2. **Autonomous agents**: Creating AI assistants that can plan and execute tasks
3. **Web3 integrations**: Interacting with blockchain data and smart contracts
4. **Context-aware applications**: Systems that need to maintain state and adapt to changing information

## Conclusion

The Chat Completion API provides a powerful interface to ASI-1 Mini's capabilities. By understanding how to structure your requests and leverage the model's agentic reasoning, you can build sophisticated applications that go beyond simple text generation.

For more information, refer to the [API Reference](../asi1-mini/api-reference.md) documentation. 