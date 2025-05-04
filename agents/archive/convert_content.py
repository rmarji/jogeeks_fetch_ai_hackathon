
import requests
import json
from uagents import Agent, Context
from openai import OpenAI

class Phrasetext(Model):
    text: str

class RephraseText(Model):
    rephrase_content: str

def query_openai_chat(prompt: str) -> str:
    """
    Sends a chat request to OpenAI's API and retrieves the response.
    Args:
        prompt (str): The input prompt/question formatted for the model.
    Returns:
        str: The response from the OpenAI chat model.
    """
    try:
        client = OpenAI(api_key="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")  # Replace with your API key
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Rephrase the following text while maintaining its meaning."},
                {"role": "user", "content": prompt},
            ]
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error querying OpenAI API: {str(e)}"

@agent.on_message(model=Phrasetext)
async def rephrase_text(ctx: Context, sender: str, msg: Phrasetext):
    """
    Handles text rephrasing on startup:
    1. Gets user input.
    2. Logs the input text.
    3. Sends text to OpenAI.
    4. Logs and displays the rephrased text.
    5. Handles any errors.
    """
    
    try:
        text = msg.text
        rephrased_text = query_openai_chat(text)
        ctx.logger.info(f"Rephrased text: {rephrased_text}")
        await ctx.send(sender, RephraseText(rephrase_content=rephrased_text))
    except Exception as e:
        ctx.logger.error(f"Exception: {str(e)}")
        print(f"Error: {str(e)}")
