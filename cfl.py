from discord.ext import commands


class CFL(commands.Cog):
  def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def !scores(self, ctx, *args):
        api = 'http://site.api.espn.com/apis/site/v2/sports/'
        cfl_scores = 'football/college-football/scoreboard'
        mlb_scores ='baseball/mlb/scoreboard'
        nfl_scores = 'football/nfl/scoreboard'
        response = requests.get(api).json()

        try:
            guess = await self.bot.wait_for('message', check=is_correct, timeout=30.0)
            if guess.content == answer:
                await ctx.channel.send('You are right')
            else:
                await ctx.channel.send('Oops. It was {}.'.format(answer))
        except asyncio.TimeoutError:
            return await ctx.channel.send('Sorry, you took too long it was {}.'.format(answer))
