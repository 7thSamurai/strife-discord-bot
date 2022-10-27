#!/usr/bin/env python3

import discord
from discord.ext import commands
from config import config
import asyncio

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, help_command=None)

@bot.event
async def on_command_error(ctx, error):
    print('ERROR: ', error)
    await ctx.send(error)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

async def load_extensions():
    bot_extensions = [
        'modules.help',
        'modules.moderation',
        'modules.anti_spam',
        'modules.misc',
        'modules.status',
        'modules.fun',
        'modules.crypto',
        'modules.space',
    ]

    for extension in bot_extensions:
        print(f'[i] Loading {extension}...')
        await bot.load_extension(extension)

async def main():
    async with bot:
        # Load the extensions
        await load_extensions()
        print(f'[i] modules loaded!')

        # Start the bot
        await bot.start(config.TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
