# NOTE: To run this agent, use: python -m agents.alert_agent from the project root.
import os
from datetime import datetime
from typing import Optional

import aiohttp
from pydantic import BaseModel, Field
from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import (
    ChatMessage, ChatAcknowledgement, TextContent, chat_protocol_spec
)
from uagents import Protocol

from .message_models import AlertMsg, AckMsg

# Webhook URL for sending alerts
WEBHOOK_URL = "https://arootah.app.n8n.cloud/webhook-test/alert_agent"

# Agent configuration
AGENT_SEED = "dubai-habibi"
AGENT_PORT = 8003
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"

# Create the agent
alert_agent = Agent(
    name="alert-agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)
# Add endpoint to silence "Agent won’t be reachable" warning
alert_agent.add_endpoint("http://127.0.0.1:8100")

# Create chat protocol instance
chat_proto = Protocol(spec=chat_protocol_spec)
#alert_agent.include(chat_proto, publish_manifest=True)


@alert_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the alert agent on startup.
    """
    ctx.logger.info(f"Alert Agent started with address: {alert_agent.address}")


@alert_agent.on_message(model=AlertMsg)
async def handle_alert(ctx: Context, sender: str, msg: AlertMsg):
    """
    Handle incoming alert messages and forward them to the webhook.
    """
    ctx.logger.info(f"Received alert from {sender} for {msg.symbol} at price ${msg.price:.2f}")

    # Prepare the payload
    payload = {
        "symbol": msg.symbol,
        "price": msg.price,
        "timestamp": msg.timestamp.isoformat()
    }

    # Send to webhook
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=payload) as response:
                if response.status == 200:
                    ctx.logger.info(f"Successfully sent alert for {msg.symbol} to webhook")
                else:
                    ctx.logger.error(f"Failed to send alert to webhook. Status: {response.status}")
                    ctx.logger.error(await response.text())
    except Exception as e:
        ctx.logger.error(f"Error sending alert to webhook: {e}")
# Send acknowledgement
    await ctx.send(sender, AckMsg(detail="Alert processed"))


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle incoming chat messages and forward them to the webhook.
    """
    ctx.logger.info(f"Received chat message from {sender}")

    for item in msg.content:
        if isinstance(item, TextContent):
            ctx.logger.info(f"Processing text content: {item.text}")
            
            # Prepare the payload
            payload = {
                "message": item.text
            }

            # Send to webhook
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(WEBHOOK_URL, json=payload) as response:
                        if response.status == 200:
                            ctx.logger.info("Successfully sent chat message to webhook")
                        else:
                            ctx.logger.error(f"Failed to send chat message to webhook. Status: {response.status}")
                            ctx.logger.error(await response.text())
            except Exception as e:
                ctx.logger.error(f"Error sending chat message to webhook: {e}")
    
    # Send acknowledgement
    ack = ChatAcknowledgement(msg_id=msg.msg_id)
    await ctx.send(sender, ack)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_chat_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """
    Handle chat acknowledgements.
    """
    ctx.logger.info(f"Received acknowledgement for message {msg.msg_id} from {sender}")


if __name__ == "__main__":
    # Run the agent and send test messages to itself
    import asyncio
    
    async def send_test_messages(ctx):
        # Wait for agent to fully start
        await asyncio.sleep(1)
        
        # Create a test alert using AlertMsg
        test_alert = AlertMsg(
            symbol="BTC",
            price=45000.0
        )
        
        # Send the alert to ourselves to demonstrate the functionality
        await ctx.send(alert_agent.address, test_alert)
        ctx.logger.info(f"Sent test alert for {test_alert.symbol} at price ${test_alert.price:.2f}")
        
        # Wait a moment before sending the next test
        await asyncio.sleep(1)
        
        # Create and send a test ChatMessage
        text_content = TextContent(text="BTC 46000.0")
        chat_message = ChatMessage(content=[text_content])
        
        await ctx.send(alert_agent.address, chat_message)
        ctx.logger.info("Sent test chat message")
    
    # Run the agent and schedule test messages after the event loop starts
    if __name__ == "__main__":
        alert_agent.run()