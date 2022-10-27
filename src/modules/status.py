import discord, datetime, holidays, random
from dateutil.easter import easter
from discord.ext import commands, tasks
from config import config

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(hours=1)
    async def status_tick(self):
        """ Routinely updates status
        """
        holiday = self.get_holiday()
        name = holiday if holiday else random.choice(config.STATUS)

        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name)
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.status_tick.start()

    def get_holiday(self):
        """ Checks if it's a holiday, returning the proper greeting if so, otherwise returns None
        """
        today = datetime.date.today()
        h = holidays.US(years=today.year)

        # Oddball cases
        if h.get(datetime.date.today()) == "Thanksgiving":
            return 'Happy Thanksgiving!'
        elif today == easter(today.year):
            return 'Happy Easter!'

        elif today == datetime.date(today.year, 1, 1): return 'Happy New Year\'s Day!'
        elif today == datetime.date(today.year, 7, 4): return 'Happy Independence Day!'
        elif today == datetime.date(today.year, 12, 24): return 'Merry Christmas Eve!'
        elif today == datetime.date(today.year, 12, 25): return 'Merry Christmas!'
        elif today == datetime.date(today.year, 12, 31): return 'Happy New Year\'s Eve!'

        return None

async def setup(bot):
    await bot.add_cog(Status(bot))
