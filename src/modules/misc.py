import discord, datetime
from discord.ext import commands, tasks
from config import config
from modules import Args, get_user, send_embed_dm

class Misc(commands.Cog):
    """ Miscellaneous stuff
    """

    def __init__(self, bot):
        self.bot = bot
        self.start = datetime.datetime.utcnow()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title='Welcome!',
            description=f'Welcome to Midgar {member.mention}!',
            color=config.COLOR
        )

        # Send a message in the welcome channel
        channel = self.bot.get_channel(config.WELCOME_CHANNEL)
        await channel.send(embed=embed)

        # Send a DM
        embed = discord.Embed(
            title='Midgar',
            description=config.WELCOME_MSG,
            color=config.COLOR
        )

        await send_embed_dm(member, embed=embed)

    @commands.command()
    async def avatar(self, ctx):
        """ Grabs a member's avatar
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)

        await ctx.message.channel.send(member.avatar.url)

    @commands.command()
    async def membercount(self, ctx):
        """ Gets the current number of server members
        """
        msg = f'There are currently {ctx.message.guild.member_count} members.'
        if ctx.message.guild.member_count < 100:
            msg += ' Let\'s try to make that number higher!'

        await ctx.message.channel.send(msg)

    @commands.command()
    async def serverinfo(self, ctx):
        """ Queries server info
        """
        embed = discord.Embed(
            title='Server Info',
            color=config.COLOR
        )

        embed.add_field(name='Description', value=ctx.message.guild.description, inline=False)
        embed.add_field(name='Created At', value=ctx.message.guild.created_at.strftime('%m/%d/%Y'), inline=False)
        embed.add_field(name='Number of Members', value=ctx.message.guild.member_count, inline=False)
        embed.add_field(name='Owner', value=f'The mighty {ctx.message.guild.owner.mention}', inline=False)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)

        await ctx.message.channel.send(embed=embed)

    @commands.command()
    async def botinfo(self, ctx):
        """ Queries Bot info
        """
        embed = discord.Embed(
            title='Bot Info',
            color=config.COLOR
        )

        info = await self.bot.application_info()

        embed.add_field(name='Description', value=info.description, inline=False)
        embed.add_field(name='Created At', value=self.bot.user.created_at.strftime('%m/%d/%Y'), inline=False)
        embed.add_field(name='Creator', value=f'The fantastic {info.owner.mention}', inline=False)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        await ctx.message.channel.send(embed=embed)

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def uptime(self, ctx):
        """ Gets the uptime of the bot
        """
        uptime = datetime.datetime.utcnow() - self.start

        await ctx.message.channel.send(f'Uptime: {str(uptime)} (Since {self.start.strftime("%m/%d/%Y %H:%M:%S")})')

async def setup(bot):
    await bot.add_cog(Misc(bot))
