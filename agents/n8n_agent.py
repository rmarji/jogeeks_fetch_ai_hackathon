import asyncio
import aiohttp
import json
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, Optional
from enum import Enum

from uagents import Agent, Context, Model, Protocol
from uagents.experimental.quota import QuotaProtocol, RateLimit

# Import the chat protocol components
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

import os

# Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "https://arootah.app.n8n.cloud/webhook/alert_agent")

# Create the agent with a unique seed
agent = Agent(
    name="n8n_chat_agent",
    seed=os.getenv("AGENT_SEED", "your_unique_seed_phrase"),
)

# Set up the quota protocol to limit requests
quota_proto = QuotaProtocol(
    storage_reference=agent.storage,
    name="N8n-Webhook-Protocol",
    version="0.1.1",
    default_rate_limit=RateLimit(window_size_minutes=60, max_requests=30),
)

# Create chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# Helper function to create text chat responses
def create_text_chat(text: str, end_session: bool = True) -> ChatMessage:
    """Create a formatted chat message response"""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )

# Helper function to call the n8n webhook
async def call_webhook(payload: Dict[str, Any]) -> str:
    """
    Call an n8n webhook with the given payload and return just the text response.
    
    Args:
        payload: The data to send to the webhook
    
    Returns:
        The text response from the webhook
    """
    async with aiohttp.ClientSession() as session:
        headers = {"Content-Type": "application/json"}
        
        try:
            async with session.post(N8N_WEBHOOK_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    # Parse the JSON response
                    raw_response = await response.json()
                    
                    # Extract the output text directly for your specific case
                    if isinstance(raw_response, dict) and 'output' in raw_response:
                        return raw_response['output']
                    
                    # Return raw response as string if we can't extract the output
                    return str(raw_response)
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP Error {response.status}: {error_text}")
        except Exception as e:
            raise Exception(f"Failed to call webhook: {str(e)}")

# Handler for incoming chat messages
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Process incoming chat messages and forward to n8n webhook"""
    ctx.logger.info(f"Got a message from {sender}")
    
    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id),
    )
    
    # Process message content
    message_text = None
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
        elif isinstance(item, TextContent):
            ctx.logger.info(f"Got a message from {sender}: {item.text}")
            message_text = item.text
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")
    
    if message_text:
        try:
            # Create the payload for n8n webhook
            payload = {
                "message": message_text,
                "sender": sender,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call the n8n webhook and get the text response directly
            response_text = await call_webhook(payload)
            
            # Send the response back to the sender
            await ctx.send(sender, create_text_chat(response_text))
            
        except Exception as e:
            error_message = f"Error processing your request: {str(e)}"
            ctx.logger.error(f"Error in handle_message: {str(e)}")
            await ctx.send(sender, create_text_chat(error_message))

# Handle acknowledgements
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    ctx.logger.info(
        f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}"
    )

# Health check functionality
def agent_is_healthy() -> bool:
    """Check if the agent can connect to the n8n webhook"""
    try:
        import asyncio
        asyncio.run(call_webhook({"health_check": True}))
        return True
    except Exception:
        return False

class HealthCheck(Model):
    """Health check request model"""
    pass

class HealthStatus(str, Enum):
    """Health status enum"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class AgentHealth(Model):
    """Health response model"""
    agent_name: str
    status: HealthStatus

# Health protocol
health_protocol = QuotaProtocol(
    storage_reference=agent.storage, 
    name="HealthProtocol", 
    version="0.1.0"
)

@health_protocol.on_message(HealthCheck, replies={AgentHealth})
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    """Handle health check requests"""
    status = HealthStatus.UNHEALTHY
    try:
        if agent_is_healthy():
            status = HealthStatus.HEALTHY
    except Exception as e:
        ctx.logger.error(e)
    finally:
        await ctx.send(
            sender, 
            AgentHealth(agent_name="n8n_chat_agent", status=status)
        )

# Include all protocols
agent.include(quota_proto, publish_manifest=True)
agent.include(chat_proto, publish_manifest=True)
agent.include(health_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()