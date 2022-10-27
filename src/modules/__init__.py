from re import match, sub
import datetime

class Args:
    def __init__(self, command):
        self.args = command.split()[1:] # Get rid of command

    def __getitem__(self, pos):
        return self.args[pos]

    def __setitem__(self, pos, val):
        self.args[pos] = val

    def check(self, pos, re=''):
        """ Checks if pos is in args and if re matches, if supplied
        """
        if len(self.args) >= pos + 1 and \
            ((not re) or
            (re and match(re, self.args[pos]))):
            return True
        else:
            return False

class BotException(Exception):
    pass

async def get_user(ctx, args, pos=0, ignore_errors=False):
    # Check if a mention was supplied, and extract the ID if so
    if args.check(pos):
        m = match(r'^<.{1,2}[0-9]*>$', args[pos])
        if m:
            args[pos] = sub(r'[^0-9]', '', m.group())

    # Make sure that the argument is in valid ID form
    if not args.check(pos, '^[0-9]*$'):
        await ctx.message.channel.send('Please supply a valid mention or ID.')
        raise BotException

    try:
        member = await ctx.guild.fetch_member(args[pos])
    except:
        if not ignore_errors:
            await ctx.message.channel.send('Could not fetch member.')
            raise BotException
        else:
            return None

    return member

async def get_time(ctx, args, pos=1):
    # Make sure an argument was supplied
    if not args.check(pos):
        await ctx.message.channel.send('Please supply a valid time. Available units: **m**(inute), **h**(our), **d**(ay), **w**(eek),  or **perma**(nent)')

    # Check to see if a permanent duration of time was supplied
    if args[pos].lower() == 'perma':
        return datetime.datetime.utcnow() + datetime.timedelta(minutes=999999999)

    # Make sure the string matches proper form
    m = match(r'^[0-9]*[mhdw]$', args[pos])
    if not m:
        await ctx.message.channel.send('Please supply a valid time. Available units: **m**(inute), **h**(our), **d**(ay), **w**(eek), or **perma**(nent)')

    # Extract the amount of time and the unit of time
    amount = int(sub(r'[^0-9]', '', m.group()))
    unit = sub(r'[^mhdw]', '', m.group())

    # Minutes per unit
    time_to_min = {
        'm': 1,
        'h': 60,
        'd': 60*24,
        'w': 60*24*7
    }

    # Convert the time to minutes, and make sure its non-zero
    time = amount * time_to_min[unit]
    if not time:
        await ctx.message.channel.send('Please supply a non-zero value for the time.')
        raise BotException

    return datetime.datetime.utcnow() + datetime.timedelta(minutes=time)

async def get_reason(ctx, args, pos=2):
    if not args.check(pos):
        await ctx.message.channel.send('No reason specified.')
        raise BotException

    return ' '.join(args[pos:])

async def check_for_role(ctx, member, role, action):
    if role in [r.id for r in member.roles]:
        await ctx.message.channel.send(f'The user {member.mention} can not be targeted to be {action}.', allowed_mentions = discord.AllowedMentions(users=False))
        raise BotException

async def check_for_owner(ctx, member):
    info = await ctx.bot.application_info()
    if member.id == info.owner.id:
        await ctx.message.channel.send('You dare try to turn me against my very own master and creator? Human fool...')
        raise BotException

async def send_embed_dm(member, embed, file=None):
    try:
        await member.send(embed=embed, file=file)
    except:
        pass
