import discord
import asyncio
import os
from dotenv import load_dotenv

async def test_discord_simple():
    # Load environment variables
    load_dotenv(override=True)
    token = os.getenv('DISCORD_TOKEN')
    
    print(f"Testing token: {token[:20]}...")
    
    try:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            print(f"SUCCESS: Connected as {client.user}")
            await client.close()
        
        @client.event
        async def on_error(event, *args, **kwargs):
            print(f"ERROR in {event}: {args}")
            await client.close()
        
        print("Starting Discord connection...")
        await client.start(token)
        
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_discord_simple())
