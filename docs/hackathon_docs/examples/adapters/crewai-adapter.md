---
id: crewai-adapter-example
title: CrewAI Adapter Example
---

# CrewAI Adapter for uAgents

This example demonstrates how to integrate a **CrewAI multi-agent system** with the **uAgents ecosystem** using the uAgents Adapter package. CrewAI allows you to create collaborative teams of AI agents working together to accomplish complex tasks.

## Overview

The CrewAI adapter enables:

- Creating specialized agent teams with distinct roles and responsibilities
- Orchestrating complex workflows between different AI agents
- Exposing CrewAI teams as uAgents for seamless communication with the broader agent ecosystem
- Deploying CrewAI applications to the Agentverse network

## Trip Planner Example

Let's look at a real-world example of a trip planning system with multiple specialized agents working together to create a complete travel itinerary. We'll compare the standard CrewAI implementation with the uAgents-integrated version.

### Standard CrewAI Implementation

First, let's look at how a standard CrewAI system is implemented without uAgents integration:

```python
# Standard main.py
from textwrap import dedent

from crewai import Crew
from dotenv import load_dotenv

from trip_agents import TripAgents
from trip_tasks import TripTasks

load_dotenv()


class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        self.date_range = date_range

    def run(self):
        agents = TripAgents()
        tasks = TripTasks()

        city_selector_agent = agents.city_selection_agent()
        local_expert_agent = agents.local_expert()
        travel_concierge_agent = agents.travel_concierge()

        identify_task = tasks.identify_task(
            city_selector_agent,
            self.origin,
            self.cities,
            self.interests,
            self.date_range,
        )
        gather_task = tasks.gather_task(local_expert_agent, self.origin, self.interests, self.date_range)
        plan_task = tasks.plan_task(travel_concierge_agent, self.origin, self.interests, self.date_range)

        crew = Crew(
            agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
            tasks=[identify_task, gather_task, plan_task],
            verbose=True,
        )

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    print("## Welcome to Trip Planner Crew")
    print("-------------------------------")
    location = input(
        dedent("""
      From where will you be traveling from?
    """)
    )
    cities = input(
        dedent("""
      What are the cities options you are interested in visiting?
    """)
    )
    date_range = input(
        dedent("""
      What is the date range you are interested in traveling?
    """)
    )
    interests = input(
        dedent("""
      What are some of your high level interests and hobbies?
    """)
    )

    trip_crew = TripCrew(location, cities, date_range, interests)
    result = trip_crew.run()
    print("\n\n########################")
    print("## Here is you Trip Plan")
    print("########################\n")
    print(result)
```

### uAgents Integration

Now, let's see how we can integrate this same CrewAI system with uAgents to enable network communication:

```python
#!/usr/bin/env python3
"""Trip Planner script using CrewAI adapter for uAgents."""

import os

from crewai import Crew
from dotenv import load_dotenv
from uagents_adapter.crewai import CrewAIRegisterTool

from trip_agents import TripAgents
from trip_tasks import TripTasks


class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        self.date_range = date_range

    def run(self):
        agents = TripAgents()
        tasks = TripTasks()

        city_selector_agent = agents.city_selection_agent()
        local_expert_agent = agents.local_expert()
        travel_concierge_agent = agents.travel_concierge()

        identify_task = tasks.identify_task(
            city_selector_agent,
            self.origin,
            self.cities,
            self.interests,
            self.date_range,
        )
        gather_task = tasks.gather_task(local_expert_agent, self.origin, self.interests, self.date_range)
        plan_task = tasks.plan_task(travel_concierge_agent, self.origin, self.interests, self.date_range)

        crew = Crew(
            agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
            tasks=[identify_task, gather_task, plan_task],
            verbose=True,
        )

        result = crew.kickoff()
        return result

    def kickoff(self, inputs=None):
        """
        Compatibility method for uAgents integration.
        Accepts a dictionary of inputs and calls run() with them.
        """
        if inputs:
            self.origin = inputs.get("origin", self.origin)
            self.cities = inputs.get("cities", self.cities)
            self.date_range = inputs.get("date_range", self.date_range)
            self.interests = inputs.get("interests", self.interests)

        return self.run()


def main():
    """Main function to demonstrate Trip Planner with CrewAI adapter."""

    # Load API key from environment
    load_dotenv()
    api_key = os.getenv("AGENTVERSE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: AGENTVERSE_API_KEY not found in environment")
        return

    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found in environment")
        return

    # Set OpenAI API key in environment
    os.environ["OPENAI_API_KEY"] = openai_api_key

    # Create an instance of TripCrew with default empty values
    trip_crew = TripCrew("", "", "", "")

    # Create tool for registering the crew with Agentverse
    register_tool = CrewAIRegisterTool()

    # Define parameters schema for the trip planner
    query_params = {
        "origin": {"type": "str", "required": True},
        "cities": {"type": "str", "required": True},
        "date_range": {"type": "str", "required": True},
        "interests": {"type": "str", "required": True},
    }

    # Register the crew with parameter schema
    result = register_tool.run(
        tool_input={
            "crew_obj": trip_crew,
            "name": "Trip Planner Crew AI Agent adapters",
            "port": 8080,
            "description": "A CrewAI agent that helps plan trips based on preferences",
            "api_token": api_key,
            "mailbox": True,
            "query_params": query_params,
            "example_query": "Plan a trip from New York to Paris in June, I'm interested in art and history other than museums.",
        }
    )

    # Get the agent address from the result
    if isinstance(result, dict) and "address" in result:
        result["address"]

    print(f"\nCrewAI agent registration result: {result}")

    # Keep the program running
    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
```

## Key Differences in uAgents Integration

When integrating a CrewAI system with uAgents, there are several important differences:

1. **CrewAIRegisterTool**: 
   - Uses the specialized `CrewAIRegisterTool` instead of the generic `UAgentRegisterTool`.
   - This tool is specifically designed to handle CrewAI's collaborative agent structure.

2. **Kickoff Method**: 
   - The `TripCrew` class has an additional `kickoff` method that serves as an adapter between uAgents messages and the CrewAI system.
   - It extracts parameters from the input dictionary and passes them to the actual execution method.

3. **Parameter Schema**:
   - A `query_params` schema is defined to validate and structure inputs to the CrewAI system.
   - This allows for better error handling and client guidance when using the agent.

4. **Example Query**:
   - An example query is provided to help users understand the expected input format.
   - This improves usability when interacting with the agent through chat protocols.

## Specialized Agents in the Trip Planner

The trip planning system uses three specialized agents, defined in `trip_agents.py`:

1. **City Selection Agent**: Analyzes client preferences to select the optimal city to visit
2. **Local Expert**: Identifies authentic local experiences and hidden gems
3. **Travel Concierge**: Creates detailed itineraries and plans logistics

Each agent is assigned specific tasks through the `trip_tasks.py` file:

1. **Identify Task**: Determines the best city based on client preferences
2. **Gather Task**: Collects detailed information about activities and attractions
3. **Plan Task**: Creates a comprehensive itinerary with transportation details

## Interacting with the Trip Planner

Once registered as a uAgent, you can interact with the CrewAI trip planner using any uAgent client:

```python
from datetime import datetime, timezone
from uuid import uuid4
from uagents import Agent, Protocol, Context

#import the necessary components from the chat protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
# Initialise agent2
agent2 = Agent(name="client_agent",
               port = 8082,
               mailbox=True,
               seed="client agent testing seed"
               )

# Initialize the chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

langgraph_agent_address = "agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t"

# Startup Handler - Print agent details
@agent2.on_event("startup")
async def startup_handler(ctx: Context):
    # Print agent details
    ctx.logger.info(f"My name is {ctx.agent.name} and my address is {ctx.agent.address}")

    # Send initial message to agent2
    initial_message = ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text="Plan a trip for me from london to paris starting on 22nd of April 2025 and I am interested in a mountains beaches and history")]
    )
    await ctx.send(langgraph_agent_address, initial_message)

# Message Handler - Process received messages and send acknowledgements
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    for item in msg.content:
        if isinstance(item, TextContent):
            # Log received message
            ctx.logger.info(f"Received message from {sender}: {item.text}")
            
            # Send acknowledgment
            ack = ChatAcknowledgement(
                timestamp=datetime.now(timezone.utc),
                acknowledged_msg_id=msg.msg_id
            )
            await ctx.send(sender, ack)
            

# Acknowledgement Handler - Process received acknowledgements
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")

# Include the protocol in the agent to enable the chat functionality
# This allows the agent to send/receive messages and handle acknowledgements using the chat protocol
agent2.include(chat_proto, publish_manifest=True)

if __name__ == '__main__':
    agent2.run()
```

## Benefits of the uAgents Integration

Integrating CrewAI with uAgents provides several significant advantages:

- **Network Communication**: Enables remote access to your CrewAI system over networks
- **Structured Inputs**: Validates inputs through a defined parameter schema
- **Persistent Mailbox**: Allows asynchronous communication with message storage
- **Agentverse Integration**: Makes your CrewAI system discoverable in the agent ecosystem
- **NL Processing**: Optional AI agent integration for processing natural language queries

## Getting Started

1. Clone the [Trip Planner repository](https://github.com/abhifetch/crewai-example/tree/main/trip_planner)

2. Install dependencies:
   ```bash
   pip install uagents==0.22.3 "crewai[tools]"==0.105.0 uagents-adapter==0.1.0 python-dotenv==1.0.0 langchain_openai==0.2.13
   ```
   
   Or use the provided requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```
   OPENAI_API_KEY=your_openai_key
   AGENTVERSE_API_KEY=your_agentverse_key
   AGENT_SEED=your_agent_seed_phrase
   ```

4. Run the CrewAI trip planner with uAgents adapter:
   ```bash
   cd crewai-example/trip_planner
   python main_uagents.py
   ```

5. In a separate terminal, run a client agent to interact with it:
   ```bash
   cd crewai-example
   python client_agent.py
   ```

## Expected Outputs

When running the examples, you should expect to see outputs similar to these:

### Standard CrewAI (`main.py`)

```
## Welcome to Trip Planner Crew
-------------------------------
From where will you be traveling from?
> New York

What are the cities options you are interested in visiting?
> Paris, Rome, Barcelona

What is the date range you are interested in traveling?
> June 10-20, 2023

What are some of your high level interests and hobbies?
> Food, art, architecture, and history

[City Selection Specialist] I'll analyze which city would be the best fit based on the traveler's preferences...

Working on: Analyze the traveler's preferences and determine which city from the options would be the best fit...

[... search and reasoning details ...]

########################
## Here is you Trip Plan
########################

# PARIS: 3-DAY FOOD & ART JOURNEY
*A curated itinerary for experiencing the best of Parisian cuisine and artistic treasures*

## RECOMMENDED ACCOMMODATIONS
Le Marais district or Saint-Germain-des-Prés would be ideal locations, offering central positioning with charming atmosphere and proximity to key attractions.

[... detailed itinerary continues ...]
```

### uAgents Integration (`main_uagents.py`)

First terminal:
```
(venv) abhi@Fetchs-MacBook-Pro test examples % python3 trip_planner/main_uagents.py
INFO:     [Trip Planner Crew AI Agent adapters]: Starting agent with address: agent1q2sgs58jzw70e8vvsrlx8k3yukdqc9gwkhp8p7q6tslcxhy0eqtxyq4fv07
INFO:     [Trip Planner Crew AI Agent adapters]: Agent 'Trip Planner Crew AI Agent adapters' started with address: agent1q2sgs58jzw70e8vvsrlx8k3yukdqc9gwkhp8p7q6tslcxhy0eqtxyq4fv07
INFO:     [Trip Planner Crew AI Agent adapters]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8080&address=agent1q2sgs58jzw70e8vvsrlx8k3yukdqc9gwkhp8p7q6tslcxhy0eqtxyq4fv07
INFO:     [Trip Planner Crew AI Agent adapters]: Starting server on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     [Trip Planner Crew AI Agent adapters]: Starting mailbox client for https://agentverse.ai
INFO:     [Trip Planner Crew AI Agent adapters]: Mailbox access token acquired
Connecting agent 'Trip Planner Crew AI Agent adapters' to Agentverse...
INFO:     [mailbox]: Successfully registered as mailbox agent in Agentverse
Successfully connected agent 'Trip Planner Crew AI Agent adapters' to Agentverse
Updating agent 'Trip Planner Crew AI Agent adapters' README on Agentverse...
Successfully updated agent 'Trip Planner Crew AI Agent adapters' README on Agentverse

CrewAI agent registration result: Agent 'Trip Planner Crew AI Agent adapters' registered with address: agent1q2sgs58jzw70e8vvsrlx8k3yukdqc9gwkhp8p7q6tslcxhy0eqtxyq4fv07 with mailbox (Parameters: origin, cities, date_range, interests)
INFO:     [mailbox]: Successfully registered as mailbox agent in Agentverse
INFO:     [Trip Planner Crew AI Agent adapters]: Got a message from agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [Trip Planner Crew AI Agent adapters]: Received message model digest: timestamp=datetime.datetime(2025, 4, 21, 10, 13, 39, 989489, tzinfo=datetime.timezone.utc) msg_id=UUID('7930acf1-b16e-4b20-896b-7d801763eaa6') content=[TextContent(type='text', text='Plan a trip for me from london to paris starting on 22nd of April 2025 and I am interested in a mountains beaches and history')]
INFO:     [Trip Planner Crew AI Agent adapters]: Got a text message from agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49: Plan a trip for me from london to paris starting on 22nd of April 2025 and I am interested in a mountains beaches and history
INFO:     [Trip Planner Crew AI Agent adapters]: Using crew object: <__main__.TripCrew object at 0x12c1f79d0>
INFO:     [Trip Planner Crew AI Agent adapters]: Extracting parameters using keys: ['origin', 'cities', 'date_range', 'interests']
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:     [Trip Planner Crew AI Agent adapters]: Extracted parameters: {'origin': 'london', 'cities': 'paris', 'date_range': '22nd of April 2025', 'interests': 'mountains beaches and history'}
INFO:     [Trip Planner Crew AI Agent adapters]: Running crew with extracted parameters
╭─────────────────────────────────────────────────────── Crew Execution Started ───────────────────────────────────────────────────────╮
│                                                                                                                                      │
│  Crew Execution Started                                                                                                              │
│  Name: crew                                                                                                                          │
│  ID: 1462f3ae-5ce4-4ea3-b1af-5639aac04dd2                                                                                            │
│                                                                                                                                      │
│                                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

🚀 Crew: crew
└── 📋 Task: c181e31b-6b7f-4471-ab8f-fa5f06078365
       Status: Executing Task...
[... crew execution continues ...]
```

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/adapters/crewai.png" alt="crewai-adapter" style={{ width: '100%', maxWidth: '1000px' }} />
</div>

### Client Agent (`client_agent.py`)

Second terminal:
```
(venv) abhi@Fetchs-MacBook-Pro crewai-example % python3 trip_planner/client_agent.py 
INFO:     [client_agent]: Starting agent with address: agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [client_agent]: My name is client_agent and my address is agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [client_agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8082&address=agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [client_agent]: Starting server on http://0.0.0.0:8082 (Press CTRL+C to quit)
INFO:     [client_agent]: Starting mailbox client for https://agentverse.ai
INFO:     [client_agent]: Manifest published successfully: AgentChatProtocol
INFO:     [client_agent]: Mailbox access token acquired
INFO:     [client_agent]: Received acknowledgement from agent1q2sgs58jzw70e8vvsrlx8k3yukdqc9gwkhp8p7q6tslcxhy0eqtxyq4fv07 for message: 7930acf1-b16e-4b20-896b-7d801763eaa6
INFO:     [uagents.registration]: Registration on Almanac API successful
INFO:     [uagents.registration]: Almanac contract registration is up to date!

[... detailed itinerary continues ...]
```

This example demonstrates how uAgents adapters can bring collaborative AI agent systems into a networked environment, making complex workflows accessible through standardized messaging protocols. 