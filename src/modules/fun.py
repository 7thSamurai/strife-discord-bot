import discord, requests, datetime, random
from discord.ext import commands
from modules import BotException
from config import config

class Fun(commands.Cog):
    """ Random fun stuff
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joke(self, ctx):
        """ Tells a random joke
        """
        num = random.randint(0, 1)

        # Randomly choice which API to use
        if num == 0:
            session = requests.Session()
            session.headers.update({'Accept': 'application/json'})
            joke = session.get('https://icanhazdadjoke.com/').json()['joke']
        else:
            joke = requests.get('https://geek-jokes.sameerkumar.website/api?format=json').json()['joke']

        await ctx.message.channel.send(f'> {joke}')

async def setup(bot):
    await bot.add_cog(Fun(bot))
