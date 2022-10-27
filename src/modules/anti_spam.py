import discord, datetime
from discord.ext import commands
from config import config
from db import db

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.last_messages = []
        self.violations = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        # Make sure that the message isn't written by this or any other bots
        # And check that it isn't a mod (They get a pass)
        if message.author.bot or config.MOD_ROLE in message.author.roles:
            return

        # Record the new message
        self.last_messages.append({
            'author': message.author.id,
            'channel': message.channel.id,
            'created': message.created_at,
            'content': message.clean_content # FIXME?
        })

        # Scan messages to try to determine if they're spam
        if len(self.last_messages) >= 5:
            await self.detect_spam()

        # Clear out the older messages
        if len(self.last_messages) >= 6:
            self.last_messages.pop(0)

    def get_violations(self, author):
        """ Updates and returns the number of violations that a user has committed
        """
        now = datetime.datetime.now()

        if author in self.violations:
            # Drop any violations that are older than a hour
            self.violations[author] = [time for time in self.violations[author] if (now - time) <= datetime.timedelta(hours=1)]

            # Add the new violation
            self.violations[author].append(now)
        else:
            # Add the new violation
            self.violations[author] = [now]

        return len(self.violations[author])

    async def punish_spammer(self, author_id):
        """ Warns or mutes a spammer depending on the number of offenses
        """
        channel_id = [message['channel'] for message in self.last_messages if message['author'] == author_id][-1]

        # Flush out the last messages
        self.last_messages = []

        guild = self.bot.get_guild(config.GUILD)
        muted_role = guild.get_role(config.MUTED_ROLE)
        author = await guild.fetch_member(author_id)
        channel = self.bot.get_channel(channel_id)

        num = self.get_violations(author_id)

        # Warn after one violation
        if num == 1:
            await channel.send(f'Warning: Member {author.mention} will been spam-muted after one more offense.') # FIXME?
        # Mute after two violations
        else:
            minutes = 5 if num == 2 else 60
            endtime = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)  

            await author.add_roles(muted_role, reason='Spamming')
            await channel.send(f'The member {author.mention} has been spam-muted for {minutes} minutes.') # FIXME?
            db.add_mute(author.id, endtime, self.bot.user.id, 'Spamming')

    async def detect_spam(self):
        """ Attempts to detect possible spam in the most recent messages
        """
        scores = {message['author']: 0 for message in self.last_messages}

        # Calculate a score for each user on how likely that they were spamming
        for author in set(message['author'] for message in self.last_messages):
            # Check the number of messages that were posted by the user
            count = [message['author'] for message in self.last_messages].count(author)
            if count >= 5:
                scores[author] += 1

            # Check how many duplicate messages were posted by the user
            messages = [message['content'] for message in self.last_messages if message['author'] == author]
            for message in messages:
                count = messages.count(message)

                if count >= 5:
                    scores[author] += 1
                    break

            # Check message length
            for message in messages:
                if len(message) > 400:
                    scores[author] += 1
                    break

            # Check how fast the messages were posted
            created = [message['created'] for message in self.last_messages if message['author'] == author]
            if (created[-1] - created[0]).total_seconds() <= 5:
                scores[author] += 1

        # Evaluate each user to see if their score was high enough for action to be taken
        for author, score in scores.items():
            if score / 4 >= 0.6: # FIXME
                await self.punish_spammer(author)


async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
