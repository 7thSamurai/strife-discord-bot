import discord, requests, datetime
from discord.ext import commands
from config import config

class Crypto(commands.Cog):
    """ Cryptocurrency related stuff
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def crypto(self, ctx, symbol):
        """ Gets the price of any coin from it's symbol
        """
        symbol = symbol.upper()
        if not await self.get_crypto_info(ctx, symbol):
            await ctx.message.channel.send(f'Invalid currency symbol "{symbol}"')

    @commands.command()
    async def bitcoin(self, ctx):
        """ Gets the price of Bitcoin
        """
        await self.get_crypto_info(ctx, 'BTC')

    @commands.command()
    async def eth(self, ctx):
        """ Gets the price of Ethereum
        """
        await self.get_crypto_info(ctx, 'ETH')

    @commands.command()
    async def monero(self, ctx):
        """ Gets the price of Monero
        """
        await self.get_crypto_info(ctx, 'XMR')

    @commands.command()
    async def doge(self, ctx):
        """ Gets the price of Dogecoin
        """
        await self.get_crypto_info(ctx, 'DOGE')

    @commands.command()
    async def shib(self, ctx):
        """ Gets the price of Shiba Inu
        """
        await self.get_crypto_info(ctx, 'SHIB')

    async def get_crypto_info(self, ctx, symbol):
        """ Fetches information about a cryptocurrency based off of it's symbol
        """
        date = datetime.datetime.now().strftime("%m/%d/%Y")

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': config.COIN_MARKET_CAP_KEY,
        }

        params = {
            'symbol': symbol,
        }

        # Grab the data
        try:
            session = requests.Session()
            session.headers.update(headers)
            data = session.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest', params=params).json()
            data = data['data'][symbol]

            info = session.get(' https://pro-api.coinmarketcap.com/v1/cryptocurrency/info', params=params).json()
            info = info['data'][symbol]
        except:
            return False

        embed = discord.Embed(color=config.COLOR)

        if data["quote"]["USD"]["price"] >= 0.01:
            embed.add_field(name='Price', value=f'${data["quote"]["USD"]["price"]:,.2f} USD', inline=False)
        else:
            embed.add_field(name='Price', value=f'${data["quote"]["USD"]["price"]:.8f} USD', inline=False)

        embed.add_field(name='Change over last 1h', value=f'{data["quote"]["USD"]["percent_change_1h"]:+.2f}%', inline=False)
        embed.add_field(name='Change over last 24h', value=f'{data["quote"]["USD"]["percent_change_24h"]:+.2f}%', inline=False)
        embed.add_field(name='Change over last 7d', value=f'{data["quote"]["USD"]["percent_change_7d"]:+.2f}%', inline=False)
        embed.add_field(name='Market Cap', value=f'${data["quote"]["USD"]["market_cap"]:,.2f} USD', inline=False)
        embed.add_field(name='Circulating Supply', value=f'{data["circulating_supply"]:,} {symbol}', inline=False)
        embed.add_field(name='Total Supply', value=f'{data["total_supply"]:,} {symbol}', inline=False)

        if data["max_supply"]:
            embed.add_field(name='Max Supply', value=f'{data["max_supply"]:,} {symbol}', inline=False)

        embed.set_author(name=f'Price of {info["name"]}', icon_url=info['logo'])
        embed.set_footer(text=date)

        await ctx.message.channel.send(embed=embed)
        return True

async def setup(bot):
    await bot.add_cog(Crypto(bot))
