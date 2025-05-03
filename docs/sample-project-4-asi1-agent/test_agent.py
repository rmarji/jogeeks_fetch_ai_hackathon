import asyncio
from datetime import datetime
from uuid import uuid4

from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
)

# Address of the running ASI1 agent (update if needed)
ASI1_AGENT_ADDRESS = "agent1q0rn642gqe9d5rehad3w9wpcygzjeaf280ktfxsyrmljgzel6yy7sxzc6f9"  # Replace with your ASI1 agent's address

# Create a test agent
test_agent = Agent(
    name="asi1-test-client",
    seed="asi1-test-client-seed",
    port=8006,
    endpoint="http://localhost:8006/submit",
)

# Handler for ChatMessage responses from the ASI1 agent
@test_agent.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    print(f"Received ChatMessage from ASI1 agent:")
    for item in msg.content:
        if isinstance(item, TextContent):
            print(f"\n{item.text}\n")
    await asyncio.sleep(1)

# Handler for ChatAcknowledgement
@test_agent.on_message(model=ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    print(f"Received ChatAcknowledgement from {sender} for message {msg.acknowledged_msg_id}")

@test_agent.on_event("startup")
async def send_test_chat(ctx: Context):
    # Send a ChatMessage to the ASI1 agent on startup
    chat_msg = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text="What is agentic AI?")]
    )
    await ctx.send(ASI1_AGENT_ADDRESS, chat_msg)

if __name__ == "__main__":
    test_agent.run()
