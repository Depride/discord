import discord
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # 환경변수에서 토큰 불러오기

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

client.run(TOKEN)
