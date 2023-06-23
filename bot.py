import discord
from discord.ext import commands
import json
from mysql import connector

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

config = {}
with open("config.json", 'r') as configFile:
    config = json.load(configFile)

db_connect = connector.connect(
            host = config["db_host"],
            user = config["db_user"],
            password = config["db_pass"],
            database = config["db_name"],
            port = config["db_port"]
        )
db_cursor = db_connect.cursor()

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')


@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not cool')

@bot.command()
async def insert(ctx, name, quantity, type):
    


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')


bot.run(config["token"])
