import os
import json
import requests
from typing import Any
from dotenv import load_dotenv

load_dotenv()

ASI1_URL = "https://api.asi1.ai/v1/chat/completions"
ASI1_MODEL = os.getenv("ASI1_MODEL", "asi1-mini")
ASI1_API_KEY = os.getenv("ASI1_API_KEY", "YOUR_ASI1_API_KEY")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ASI1_API_KEY}",
}

if ASI1_API_KEY is None or ASI1_API_KEY == "YOUR_ASI1_API_KEY":
    raise ValueError(
        "You need to provide an ASI1 API key. Get one at https://asi1.ai/"
    )

def get_completion(
    context: str,
    prompt: str,
    response_schema: dict[str, Any] | None = None,
    max_tokens: int = MAX_TOKENS,
) -> str:
    # ASI1 API is OpenAI-compatible, but may not support response_schema
    messages = []
    if context:
        messages.append({"role": "system", "content": context})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": ASI1_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if response_schema is not None:
        # If ASI1 supports response_format, add it here. Otherwise, ignore.
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": response_schema.get("title", "output"),
                "strict": False,
                "schema": response_schema,
            },
        }

    try:
        response = requests.post(
            ASI1_URL,
            headers=HEADERS,
            data=json.dumps(payload),
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        # ASI1 returns choices[0].message.content (OpenAI-compatible)
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred: {e}"
