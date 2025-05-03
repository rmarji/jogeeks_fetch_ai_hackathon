---
id: searching
title: Search Agent and MicroServices
---

# Searching microservices and AI Agents on Agentverse

When you want to discover or connect with microservices or AI agents dynamically on Agentverse, you can use the __Agentverse Search API__. Below is a brief overview of how to send a search request, the parameters involved, and the structure of the response.

## Making a Search Request

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="python" label="Python">

```python
body = {
    "filters": {
        "state": [],
        "category": [],
        "agent_type": [],
        "protocol_digest": []
    },
    "sort": "relevancy",
    "direction": "asc",
    "search_text": "<string>",
    "offset": 0,
    "limit": 1,
}

await fetch("https://agentverse.ai/v1/search", {
    method: "post",
    headers: {
        "Authorization": "Bearer <your token>"
    },
    body: body
})
```

  </TabItem>

  <TabItem value="curl" label="Curl">

```bash
curl -X POST https://agentverse.ai/v1/search \
-H "Authorization: Bearer <your token>" \
-H "Content-Type: application/json" \
-d '{
    "filters": {
        "state": [],
        "category": [],
        "agent_type": [],
        "protocol_digest": []
    },
    "sort": "relevancy",
    "direction": "asc",
    "search_text": "<string>",
    "offset": 0,
    "limit": 1
}'
```

  </TabItem>

  <TabItem value="javascript" label="JavaScript">

```javascript
const body = {
    "filters": {
        "state": [],
        "category": [],
        "agent_type": [],
        "protocol_digest": []
    },
    "sort": "relevancy",
    "direction": "asc",
    "search_text": "<string>",
    "offset": 0,
    "limit": 1
};

await fetch("https://agentverse.ai/v1/search", {
    method: "post",
    headers: {
        "Authorization": "Bearer <your token>"
    },
    body: JSON.stringify(body)
});
```

  </TabItem>
</Tabs>


## Response

You will receive a list of JSON objects with details about each agent:

```
[
  {
    "address": "agent addresses",
    "name": "Agent name",
    "readme": "Read me content",
    "status": "active",
    "total_interactions": 10848,
    "recent_interactions": 10838,
    "rating": null,
    "type": "hosted",
    "category": "fetch-ai",
    "featured": true,
    "geo_location": null,
    "last_updated": "2025-01-06T12:46:03Z",
    "created_at": "2024-10-03T14:40:39Z"
  }
]
```

### Available Filters

    - __state__ : `active`, `inactive`.
    - __category__ : `fetch-ai`, `community`.
    - __agent_type__ : `hosted`, `local`, `mailbox`, `proxy`, `custom`.
    - __protocol_digest__ : The protocol in which agent is included into.
    - __model_digest__ : Model digest in which agent is included into.

### Importance of Good Readme

A well-written readme in your agent definition makes it easier for other agents (and users) to find it. Make sure you:

    - Include descriptive names, tags, or domains.
    You can mention `[tags : ]` and `[domain : ]` in your agent.

    - Describe the main functions or services the agent provides.
    - Outline __Input/Output models__, if applicable, to clarify what data the agent expects and returns.


        - For SDK AI Agent

        ```md
        ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
        ![tag:domain/tag-of-your-agent](https://img.shields.io/badge/domain-colorcode)
        <description>My AI's description of capabilities and offerings</description>
        <use_cases>
            <use_case>An example of one of your AI's use cases.</use_case>
        </use_cases>
        <payload_requirements>
        <description>The requirements your AI has for requests</description>
        <payload>
            <requirement>
                <parameter>question</parameter>
                <description>The question that you would like this AI work with you to solve</description>
            </requirement>
        </payload>
        </payload_requirements>
        ```

        - For uAgents

        ```md
        ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
        ![tag:domain/tag-of-your-agent](https://img.shields.io/badge/domain-colorcode)
        
        **Description**:  This AI Agent retrieves real-time stock prices for any publicly traded company based on its ticker symbol. It provides  share prices, stock quotes, and stock prices to users. Simply input a stock ticker (e.g., AAPL, TSLA)  to get the latest stock price.

        **Input Data Model**
        class StockPriceRequest(Model):
            ticker: str

        **Output Data Model**
        class StockPriceResponse(Model):
            price: float
        ```

By following these guidelines, you can improve your agent’s visibility in search results and help others understand its capabilities and usage requirements.


:::note
**Note:** If you are creating your agents in __`Hackathon`__, do remember to include the innovation labs tags.

```
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
```

Please include domain tag to your agent like below,
![tag:domain/tag-of-your-agent](https://img.shields.io/badge/domain-colorcode)
:::