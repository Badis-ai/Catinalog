import discord
from discord.ext import commands
import os, asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Slash commands synced.")

async def load_extensions():
    for file in os.listdir("./commands"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"commands.{file[:-3]}")
                print(f"Loaded extension: commands.{file[:-3]}")
            except Exception as e:
                print(f"Failed to load extension commands.{file[:-3]}: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())