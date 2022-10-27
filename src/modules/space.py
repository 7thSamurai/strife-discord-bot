import discord, requests, datetime
from discord.ext import commands
from modules import BotException
from config import config

class Space(commands.Cog):
    """ Outer-space related stuff
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nasa(self, ctx):
        """ Fetches NASA's Astronomy Picture of the Day
        """
        try:
            r = requests.get('https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY').json()
            image = r['url']
            desc = r['explanation']
        except:
            await ctx.message.channel.send('Error fetching data.')
            raise BotException

        embed = discord.Embed(
            title='Astronomy Picture of the Day',
            description=desc,
            color=config.COLOR
        )

        date = datetime.datetime.now().strftime("%m/%d/%Y")

        embed.set_author(name='NASA', icon_url='https://static.wikia.nocookie.net/logopedia/images/e/e5/NASA_logo.svg/revision/latest/scale-to-width-down/250?cb=20210622024945')
        embed.set_image(url=image)
        embed.set_footer(text=date)

        await ctx.message.channel.send(embed=embed)

    @commands.command()
    async def iss(self, ctx):
        """ Fetches information about the International Space Station
        """
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        iss_now = requests.get('http://api.open-notify.org/iss-now.json').json()
        astros = requests.get('http://api.open-notify.org/astros.json').json()

        iss_pos = f'{iss_now["iss_position"]["latitude"]}, {iss_now["iss_position"]["longitude"]}'
        people = []

        # Get the names of the people onboard the ISS
        for person in astros['people']:
            if person['craft'] == 'ISS':
                people.append(person['name'])

        embed = discord.Embed(
            title='ISS Info',
            color=config.COLOR
        )

        embed.add_field(name='Current location of the ISS', value=iss_pos, inline=False)
        embed.add_field(name=f'Humans onboard the ISS ({len(people)}):', value='\n'.join(people), inline=False)
        embed.set_image(url='http://www.businessforum.com/nasa01.JPEG') # TODO
        embed.set_footer(text=date)

        await ctx.message.channel.send(embed=embed)

    @commands.command()
    async def humans(self, ctx):
        """ Generates a list of the current humans in space
        """
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        data = requests.get('http://api.open-notify.org/astros.json').json()

        crafts = {}

        # Get the names of the people in space
        for person in data['people']:
            if person['craft'] in crafts:
                crafts[person['craft']].append(person['name'])
            else:
                crafts[person['craft']] = [person['name']]

        embed = discord.Embed(
            title='Humans in Space',
            color=config.COLOR
        )

        for craft in crafts:
            embed.add_field(name=f'Humans onboard the {craft} ({len(crafts[craft])}):', value='\n'.join(crafts[craft]), inline=False)

        embed.set_footer(text=date)
        await ctx.message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Space(bot))
