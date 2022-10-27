import discord, datetime
from discord.ext import commands, tasks
from re import match
from config import config
from db import db
import asyncio
from modules import Args, get_user, get_time, get_reason, check_for_role, check_for_owner, send_embed_dm

class Moderation(commands.Cog):
    """ Commands for moderation
    """

    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=1)
    async def punishment_tick(self):
        expired = db.get_expired()
        guild = self.bot.get_guild(config.GUILD)
        bans = await guild.bans()

        # TODO: See about deleted users
        for punishment in expired:
            if punishment['type'] == 'mute':
                member = guild.get_member(punishment['id'])
                if not member:
                    db.remove_mute(punishment['id'], self.bot.user.id, 'Mute expired')
                    continue

                # If the user doesn't have the role (I.e. it got manually deleted), just remove the database-entry silently
                has_role = config.MUTED_ROLE in [role.id for role in member.roles]
                if not has_role:
                    db.remove_mute(member.id, self.bot.user.id, 'Mute expired')
                    continue

                muted_role = guild.get_role(config.MUTED_ROLE)
                await member.remove_roles(muted_role, reason='Mute expired')
                db.remove_mute(member.id, self.bot.user.id, 'Mute expired')

                embed = discord.Embed(
                    title='Midgar',
                    description=config.UNMUTE_MSG,
                    color=config.COLOR
                )

                embed.add_field(
                    name='Reason',
                    value='Mute expired'
                )

                await send_embed_dm(member, embed=embed)

            elif punishment['type'] == 'ban':
                member = await self.bot.fetch_user(punishment['id']);

                # If the user isn't banned (I.e. they were manually unbanned), just remove the database-entry silently
                if not punishment['id'] in [ban.user.id for ban in await guild.bans()]:
                    db.remove_ban(member.id, self.bot.user.id, 'Ban expired')
                    continue

                await member.unban(reason='Ban expired')
                db.remove_ban(member.id, self.bot.user.id, 'Ban expired')

                embed = discord.Embed(
                    title='Midgar',
                    description=config.UNBAN_MSG,
                    color=config.COLOR
                )

                embed.add_field(
                    name='Reason',
                    value='Ban expired'
                )

                await send_embed_dm(member, embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(1)
        self.punishment_tick.start()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if db.get_mute(member.id) != None:
            await member.add_roles(
                member.guild.get_role(config.MUTED_ROLE),
                reason='Mute due to rejoining'
            )

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def whois(self, ctx):
        """ Queries information on a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)

        name = f'{member.name}#{member.discriminator}'
        embed = discord.Embed(
            title='Whois:',
            color=config.COLOR
        )

        info = {
            'Nickname': member.nick,
            'Username': name,
            'Created': member.created_at.strftime('%m/%d/%Y %H:%M:%S'),
            'Joined': member.joined_at.strftime('%m/%d/%Y %H:%M:%S'),
            'Premium Since': ('None' if not member.premium_since else member.premium_since.strftime('%m/%d/%Y %H:%M:%S')),
            'Roles': [role.name for role in member.roles],
            'Guild Permissions': member.guild_permissions,
            'Punishments Received': db.get_num(member.id),
            'Bot': member.bot,
            'Mention': member.mention
        }

        for name, value in info.items():
            embed.add_field(name=name, value=value, inline=False)

        embed.set_author(name=member.name, icon_url=member.avatar.url)
        embed.set_footer(text=f'User ID: {member.id}')

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def mute(self, ctx):
        """ Mutes a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)
        endtime = await get_time(ctx, args)
        reason = await get_reason(ctx, args)

        await check_for_owner(ctx, member)
        await check_for_role(ctx, member, config.MOD_ROLE, 'muted')

        # Add the role
        muted_role = ctx.message.guild.get_role(config.MUTED_ROLE)
        await member.add_roles(muted_role, reason='Muted by mod')
        db.add_mute(member.id, endtime, ctx.message.author.id, reason)

        embed = discord.Embed(
            title='Midgar',
            description=config.MUTE_MSG,
            color=config.COLOR
        )

        await send_embed_dm(member, embed)
        await ctx.message.channel.send(f'Successfully muted {member.mention}.', allowed_mentions = discord.AllowedMentions(users=False))

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def unmute(self, ctx):
        """ Unmutes a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)
        reason = await get_reason(ctx, args, 1)

        if db.get_mute(member.id):
            db.remove_mute(member.id, ctx.message.author.id, reason)

        # Make sure that the user is actually muted
        has_role = config.MUTED_ROLE in [role.id for role in member.roles]
        if not has_role:
            ctx.message.channel.send(f'The user {member.mention} isn\'t muted.', allowed_mentions = discord.AllowedMentions(users=False))
            return

        # Remove the role
        muted_role = ctx.message.guild.get_role(config.MUTED_ROLE)
        await member.remove_roles(muted_role, reason='Unmuted by mod')

        embed = discord.Embed(
            title='Midgar',
            description=config.UNMUTE_MSG,
            color=config.COLOR
        )

        embed.add_field(
            name='Reason',
            value=reason
        )

        await send_embed_dm(member, embed)
        await ctx.message.channel.send(f'Successfully unmuted {member.mention}.', allowed_mentions = discord.AllowedMentions(users=False))

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def warn(self, ctx):
        """ Warns a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)
        reason = await get_reason(ctx, args, 1)

        await check_for_owner(ctx, member)
        await check_for_role(ctx, member, config.MOD_ROLE, 'warned')
        db.add_warn(member.id, ctx.message.author.id, reason)

        embed = discord.Embed(
            title='Midgar',
            description=config.WARN_MSG,
            color=config.COLOR
        )

        embed.add_field(
            name='Reason',
            value=reason
        )

        file = discord.File(config.WARN_IMG, filename='image.jpg')
        embed.set_image(url='attachment://image.jpg')

        await send_embed_dm(member, embed, file)
        await ctx.message.channel.send(f'Successfully warned {member.mention}.', allowed_mentions = discord.AllowedMentions(users=False))

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def kick(self, ctx):
        """ Kicks a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)
        reason = await get_reason(ctx, args, 1)

        await check_for_owner(ctx, member)
        await check_for_role(ctx, member, config.MOD_ROLE, 'kicked')

        await member.kick(reason='Kicked by mod')
        db.add_kick(member.id, ctx.message.author.id, reason)

        embed = discord.Embed(
            title='Midgar',
            description=config.KICK_MSG,
            color=config.COLOR
        )

        embed.add_field(
            name='Reason',
            value=reason
        )

        await send_embed_dm(member, embed)
        await ctx.message.channel.send(f'Successfully kicked {member.mention}.', allowed_mentions = discord.AllowedMentions(users=False))

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def ban(self, ctx):
        """ Bans a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args, ignore_errors=True)
        endtime = await get_time(ctx, args)
        reason = await get_reason(ctx, args)

        # Check if the target user is not in the guild
        not_in_guild = member == None
        if not_in_guild:
            member = await self.bot.fetch_user(args[0])

        await check_for_owner(ctx, member)

        if not not_in_guild:
            await check_for_role(ctx, member, config.MOD_ROLE, 'banned')
            await member.ban(reason='Banned by mod')
        else:
            await ctx.guild.ban(member)

        db.add_ban(member.id, endtime, ctx.message.author.id, reason)

        if not not_in_guild:
            embed = discord.Embed(
                title='Midgar',
                description=config.BAN_MSG,
                color=config.COLOR
            )

            await send_embed_dm(member, embed)

        await ctx.message.channel.send(f'Successfully banned {member.mention}.', allowed_mentions = discord.AllowedMentions(users=False))

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def unban(self, ctx):
        """ Unbans a user
        """
        args = Args(ctx.message.content)
        reason = await get_reason(ctx, args, 1)

        # Make sure that the argument is in valid ID form
        if not args.check(0, '^[0-9]*$'):
            await ctx.message.channel.send('Please supply a valid ID.')
            return

        member = await self.bot.fetch_user(args[0]);
        if db.get_ban(member.id):
            db.remove_ban(member.id, ctx.message.author.id, reason)

        banned = member.id in [ban.user.id for ban in await ctx.guild.bans()]
        if banned:
            ctx.message.channel.send(f'The user {member.mention} isn\'t banned.', allowed_mentions = discord.AllowedMentions(users=False))
            return

        embed = discord.Embed(
            title='Midgar',
            description=config.UNBAN_MSG,
            color=config.COLOR
        )

        embed.add_field(
            name='Reason',
            value=reason
        )

        await send_embed_dm(member, embed)
        await ctx.message.channel.send(f'Successfully unbanned {member.mention}.', allowed_mentions = discord.AllowedMentions(users=False))

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def purge(self, ctx):
        """ Deletes all messages by a certain member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args, ignore_errors=True)

        # Check if the target user is not in the guild
        not_in_guild = member == None
        if not_in_guild:
            member = await self.bot.fetch_user(args[0])

        await check_for_owner(ctx, member)

        if not not_in_guild:
            await check_for_role(ctx, member, config.MOD_ROLE, 'purged')

        await ctx.message.channel.send('Purging...')

        # Purge the messages
        for channel in ctx.message.guild.channels:
            if channel.type == discord.ChannelType.text:
                await channel.purge(check=(lambda m: m.author.id == member.id))

        await ctx.message.channel.send(f'Successfully purged {member.mention}. Rerun if any messages remain.', allowed_mentions = discord.AllowedMentions(users=False))

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def log(self, ctx):
        """ Gets the moderation log of a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)

        embed = discord.Embed(
            title=f'{member.name}#{member.discriminator}',
            color=config.COLOR
        )

        log = db.get_user_log(member.id)

        if not len(log):
            embed.add_field(name='Error', value='No log entries for requested user.')
        else:
            for entry in log:
                if entry['type'] == 'warn' or entry['type'] == 'kick' or \
                   entry['type'] == 'unmute' or entry['type'] == 'unban':
                    embed.add_field(
                        name=entry["type"].capitalize(),
                        value=(
                            f'Time: {entry["time"].strftime("%m/%d/%Y %H:%M:%S")}\n' + \
                            f'Reason: {entry["reason"]}\n' + \
                            f'Mod: <@{entry["mod"]}>'
                        ),
                        inline=False
                    )

                else:
                    # Round off the microseconds
                    dur = entry['end'] - entry['time']
                    if dur.microseconds >= 500000:
                        dur += datetime.timedelta(seconds=1)
                    dur -= datetime.timedelta(microseconds=dur.microseconds)

                    embed.add_field(
                        name=entry["type"].capitalize(),
                        value=(
                            f'Time: {entry["time"].strftime("%m/%d/%Y %H:%M:%S")}\n' + \
                            f'Reason: {entry["reason"]}\n' + \
                            f'Duration: {str(dur)} ' + \
                            f'(Until {entry["end"].strftime("%m/%d/%Y %H:%M:%S")})\n' + \
                            f'Mod: <@{entry["mod"]}>'
                        ),
                        inline=False
                    )

        embed.set_author(name=member.name, icon_url=member.avatar.url)
        await ctx.message.channel.send(embed=embed)

    #@commands.command()
    #@commands.has_role(config.MOD_ROLE)
    #async def modlog(self, ctx):
    #    pass

    @commands.command()
    @commands.has_role(config.MOD_ROLE)
    async def clearlog(self, ctx):
        """ Clears the moderation log of a member
        """
        args = Args(ctx.message.content)
        member = await get_user(ctx, args)

        db.remove_log(member.id)
        await ctx.message.channel.send(f'Successfully cleared log of {member.mention}.', allowed_mentions = discord.AllowedMentions(users=False))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
