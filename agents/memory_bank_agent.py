from uagents import Agent, Context, Model
from pydantic import BaseModel

# Message schema for storing a key-value pair
class StoreMessage(BaseModel):
    key: str
    value: str

# Message schema for retrieving a value by key
class GetMessage(BaseModel):
    key: str

# In-memory key-value store
memory_bank = {}

# Create the agent
memory_bank_agent = Agent(
    name="memory_bank_agent",
    seed="memory_bank_agent secret phrase",
    endpoint=None,
)

@memory_bank_agent.on_message(model=StoreMessage)
async def handle_store_message(ctx: Context, sender: str, msg: StoreMessage):
    memory_bank[msg.key] = msg.value
    await ctx.send(sender, "Stored.")

@memory_bank_agent.on_message(model=GetMessage)
async def handle_get_message(ctx: Context, sender: str, msg: GetMessage):
    value = memory_bank.get(msg.key)
    if value is not None:
        await ctx.send(sender, value)
    else:
        await ctx.send(sender, "Key not found")

if __name__ == "__main__":
    memory_bank_agent.run()