import discord
import asyncio
import requests
import json
from discord.ext import commands

class Trebek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trebek(self, ctx):
        api = 'https://jservice.io/api/random'
        response = requests.get(api).json()
        question = response[0]['question']
        answer = response[0]['answer']

        await ctx.send(question)
        def is_correct(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        try:
            guess = await self.bot.wait_for('message', check=is_correct, timeout=30.0)
            if guess.content == answer:
                await ctx.channel.send('You are right')
            else:
                await ctx.channel.send('Oops. It was {}.'.format(answer))
        except asyncio.TimeoutError:
            return await ctx.channel.send('Sorry, you took too long it was {}.'.format(answer))

