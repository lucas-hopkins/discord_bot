import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from trebek import Trebek

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user} is connected to the following guild: \n'
          f'{guild.name}(id: {guild.id})'
    )

@bot.command()
async def please(ctx):
  await ctx.send('just give me a chance!')

bot.add_cog(Trebek(bot))
bot.run(TOKEN)

