import discord
from redbot.core import commands, Config


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1111111111)