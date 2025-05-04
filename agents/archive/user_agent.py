

class Phrasetext(Model):
    text: str

class RephraseText(Model):
    rephrase_content: str

@agent.on_event("startup")
async def handler(ctx: Context):
    """
    Send text for rephrasing on startup:
    """
    text = "Blockchain technology is revolutionizing various industries by providing secure, transparent, and decentralized solutions. It eliminates the need for intermediaries, reduces costs, and enhances efficiency. Many businesses are adopting blockchain to improve data integrity and streamline operations."
    await ctx.send("agent1qgrkw7ntkzyhjuj659wdyx2xl6330u85luxy6hjtnmp7tnh0q3cnwhmwnxr", Phrasetext(text=text))

@agent.on_message(model=RephraseText)
async def rephrase_text(ctx: Context, sender: str, msg: RephraseText):
    """
    Receive rephrase content from Rephrase agent:
    """
    ctx.logger.info(f"Rephrased text: {msg.rephrase_content}")
