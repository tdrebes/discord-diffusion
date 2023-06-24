import configparser
import json
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.message import Message


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, game_name):
        self.config = configparser.ConfigParser()
        self.config.read_file(open('bot_config.ini'))
        intents = discord.Intents.default()
        intents.message_content = True
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents, activity=discord.Game(name=game_name))
        self.add_events()
        self.add_commands()      

    def add_events(self):
        @self.event
        async def on_ready():
            print(f'Logged in as {self.user}')

        @self.event
        async def on_message(msg: Message):
            if msg.author == self.user:
                return

            print(f'{msg.guild}/{msg.author}: {msg.content}')

            await self.process_commands(msg)

    def add_commands(self):
        @self.command(name="history", pass_context=True)
        async def history(ctx: Context):
            history = await self.fetch_history(ctx, 10)
            await ctx.message.reply(json.dumps(history))

    async def fetch_history(self, ctx: Context, limit: int):
        messages = {}
        async for msg in ctx.channel.history(limit=limit):
            if (msg.author.id == self.user.id):
                continue

            if msg.author.id not in messages:
                messages[msg.author.id] = []

            if not isinstance(messages[msg.author.id], list):
                messages[msg.author.id] = []

            messages[msg.author.id].append(msg.content)

        return messages

bot = DiscordBot(command_prefix='$', game_name='Artifact')
bot.run(token=bot.config.get('Discord', 'Token'))
