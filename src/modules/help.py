import discord
from discord.ext import commands
from modules import Args
from config import config

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        args = Args(ctx.message.content)
        embed = None

        if not args.check(0):
            embed = discord.Embed(
                title='Help',
                description=f'Use `{config.PREFIX}help <category>` to get information about that category\'s commands.',
                color=config.COLOR
            )

            desc = ''

            for cog in self.bot.cogs:
                if cog.lower() in ['help', 'antispam', 'status']:
                    continue
                # Only display the moderation stuff in the private bot channel
                elif cog.lower() == 'moderation' and ctx.message.channel.id != config.BOT_CHANNEL:
                    continue

                desc += f'`{cog}'
                desc += ' '*(10 - len(cog))
                desc+=f'`{self.bot.cogs[cog].__doc__}'

            embed.add_field(name='Categories', value=desc, inline=False)

        else:
            # Only display the moderation stuff in the private bot channel
            if args[0].lower() != 'moderation' or ctx.message.channel.id == config.BOT_CHANNEL:
                for cog in self.bot.cogs:
                    if cog.lower() == args[0].lower():
                        embed = discord.Embed(
                            title=f'{cog} - Commands',
                            description = self.bot.cogs[cog].__doc__,
                            color=config.COLOR
                        )

                        for command in self.bot.get_cog(cog).get_commands():
                            if not command.hidden:
                                embed.add_field(name=f'{config.PREFIX}{command.name}', value=command.help, inline=False)

                        break

        if embed:
            await ctx.message.channel.send(embed=embed)
        else:
            await ctx.message.channel.send('Invalid Category!')

async def setup(bot):
    await bot.add_cog(Help(bot))
