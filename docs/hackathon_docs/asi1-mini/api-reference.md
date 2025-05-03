---
id: asi1-mini-api-reference
title: ASI-1 Mini API Reference
sidebar_label: API Reference
---

# ASI-1 Mini API Reference

This API Reference describes the RESTful and streaming interfaces of the ASI-1 Mini platform.

## Introduction

ASI-1 Mini provides a powerful API that allows developers to integrate advanced agentic AI capabilities into their applications. The API is designed to be easy to use while providing access to the full range of ASI-1 Mini's capabilities.

## OpenAI Compatibility

Where possible, the ASI-1 Mini API conforms to the OpenAI API specification. This means that users can often plug the ASI-1 Mini API into existing code that uses the OpenAI API with minimal changes.

## Authorization

API keys can be created from your account when you log into ASI-1. Authorization is done by adding the following header into your requests:

```
Authorization: Bearer <api token>
```

Remember your API key is a secret, do not share it with anyone. If you need to revoke access for a particular key, simply log into your account and delete it from your profile.

## Base URL

All API requests should be made to the following base URL:

```
https://api.asi1.ai/v1
```

## Endpoints

### Chat Completions

```
POST /chat/completions
```

Creates a model response for the given chat conversation.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | ID of the model to use. Currently, only "asi1-mini" is available. |
| messages | array | Yes | An array of message objects representing the conversation history. |
| temperature | number | No | What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Default is 1.0. |
| stream | boolean | No | If set to true, partial message deltas will be sent as they become available. Default is false. |
| max_tokens | integer | No | The maximum number of tokens that can be generated in the chat completion. This can be used to control costs for text generated via API. |

#### Message Object

Each message in the `messages` array should have the following structure:

| Field | Type | Description |
|-------|------|-------------|
| role | string | The role of the message author. Must be one of "system", "user", or "assistant". |
| content | string | The content of the message. |

#### Example Request

```json
{
  "model": "asi1-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant specialized in Web3 technologies."
    },
    {
      "role": "user",
      "content": "Explain the concept of decentralized AI."
    }
  ],
  "temperature": 0.7,
  "stream": false,
  "max_tokens": 500
}
```

#### Response Format

The API returns a JSON object with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| id | string | The completion request ID. |
| model | string | The name of the model being used. |
| thought | string | (Optional) The thoughts that were generated as part of the chat completion request. Only present when streaming is enabled. |
| choices | array | An array of completion choices. |
| usage | object | (Optional) Information about token usage. |

#### Choice Object

Each choice in the `choices` array has the following structure:

| Field | Type | Description |
|-------|------|-------------|
| index | integer | The index of the choice in the array. |
| delta | object | (When streaming) Contains the incremental content being streamed. |
| finish_reason | string | The reason the model stopped generating text. Can be "stop", "length", etc. |
| stop_reason | string | Additional information about why generation stopped. |

#### Example Response (Non-streaming)

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
        "content": "Decentralized AI refers to artificial intelligence systems that operate on distributed networks rather than centralized servers. This approach aligns with Web3 principles by removing central points of control and enabling more democratic access to AI capabilities..."
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

#### Streaming Responses

When `stream` is set to `true`, the API will send a series of server-sent events (SSE) with partial completions as they become available. Each event is prefixed with `data: ` and contains a JSON object with incremental updates.

The stream is terminated with a `data: [DONE]` message.

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid API key)
- 422: Unprocessable Entity (valid parameters but request cannot be processed)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

Error responses include a JSON object with an `error` field containing details about the error.

## Rate Limits

API usage is subject to rate limits based on your account tier. If you exceed these limits, you'll receive a 429 status code. The response headers include information about your current rate limit status.

## Best Practices

- Store your API key securely and never expose it in client-side code.
- Implement proper error handling to gracefully handle API errors.
- For long-running conversations, consider maintaining context on your side to reduce token usage.
- Use streaming for more responsive user interfaces when generating longer responses.

For more detailed examples of how to use the API, see the [Chat Completion](../asi1-mini/chat-completion.md) guide. 