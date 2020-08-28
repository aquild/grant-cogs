import discord
from redbot.core import commands, Config


class Verification(commands.Cog):
    """Verify new users"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=640477915129957944)

        # Default config
        self.config.register_guild(domains=["student.pps.net"], verified_role=None, trigger={"channel": None, "message": None})
        self.config.register_member()
    
    async def verify(self, member: discord.Member):
        pass
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
        if reaction.message.guild:
            guild_config = self.config.guild(reaction.message.guild)
            guild_trigger = guild_config.trigger()

            if reaction.message.id == guild_trigger["message"]:
                self.verify(member)

    @commands.group()
    @commands.guild_only()
    async def attachmentsuggestions(self, ctx):
        """Configure user verification"""
        pass

    @attachmentsuggestions.command()
    async def settriggers(self, ctx, channel: discord.TextChannel, message_id: str):
        """Set trigger message for verification"""

        message: discord.Message = await channel.fetch_message(message_id)
        self.config.guild(ctx.guild).trigger.set({"channel": channel.id, "message": message.id})
        await message.add_reaction('✅')

        ctx.send("Set trigger message")
