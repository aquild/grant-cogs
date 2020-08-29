import discord
from redbot.core import commands, Config


class Cog(commands.Cog):
    """<Cog Name>"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=273062)