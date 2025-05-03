import asyncio
from uagents import Agent, Context
from pydantic import BaseModel
from agents.memory_bank_agent import StoreMessage, GetMessage

# Agent configuration
AGENT_NAME = "caller_agent"
AGENT_SEED = "caller_agent secret phrase"
AGENT_PORT = 8004
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"

# Create the agent
caller_agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)

MEMORY_BANK_ADDRESS = "memory_bank_agent"
REPLY_TIMEOUT = 5  # seconds

async def main():
    # Start the agent in the background
    async with caller_agent:
        await asyncio.sleep(1)  # Give agent time to start

        # a. Send StoreMessage
        store_msg = StoreMessage(key="greeting", value="Hello, world!")
        try:
            reply = await asyncio.wait_for(
                caller_agent.send(MEMORY_BANK_ADDRESS, store_msg, return_response=True),
                timeout=REPLY_TIMEOUT
            )
            print(f"StoreMessage reply: {reply}")
        except asyncio.TimeoutError:
            print("StoreMessage reply: timeout")

        # b. Send GetMessage
        get_msg = GetMessage(key="greeting")
        try:
            reply = await asyncio.wait_for(
                caller_agent.send(MEMORY_BANK_ADDRESS, get_msg, return_response=True),
                timeout=REPLY_TIMEOUT
            )
            print(f"GetMessage reply: {reply}")
        except asyncio.TimeoutError:
            print("GetMessage reply: timeout")

if __name__ == "__main__":
    asyncio.run(main())