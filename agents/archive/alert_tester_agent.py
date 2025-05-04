# NOTE: To run this agent, use: python -m agents.alert_tester_agent from the project root.
import asyncio
from datetime import datetime
from uagents import Agent, Context
from pydantic import BaseModel
from datetime import datetime

class AlertMsg(BaseModel):
    symbol: str
    price: float
    timestamp: datetime = None

class AckMsg(BaseModel):
    detail: str


# The address of alert_agent is deterministic from its seed
ALERT_AGENT_SEED = "dubai-habibi"
ALERT_AGENT_ADDRESS = Agent(seed=ALERT_AGENT_SEED).address

# Create the tester agent
tester_agent = Agent(name="alert_tester")


@tester_agent.on_event("startup")
async def send_alert(ctx: Context):
    # Wait a moment to ensure agent is ready
    await asyncio.sleep(1)
    # Construct a demo alert message
    alert = AlertMsg(symbol="ETH", price=3500.0)
    ctx.logger.info(f"Sending AlertMsg to alert_agent at {ALERT_AGENT_ADDRESS}: {alert}")
    # Send the message and await a response (if any)
    await ctx.send(ALERT_AGENT_ADDRESS, alert)

@tester_agent.on_message(model=AckMsg)
async def handle_ack(ctx: Context, sender: str, message: AckMsg):
    ctx.logger.info(f"Received acknowledgement: {message.detail}")
    print("Received acknowledgement:", message.detail)
    await ctx.stop()

if __name__ == "__main__":
    tester_agent.run()