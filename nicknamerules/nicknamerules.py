import discord
from redbot.core import commands, Config
import string


class NicknameRules(commands.Cog):
    """Nickname Rule Enforcement"""

    def __init__(self, bot, verification: commands.Cog):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=273062, force_registration=True)
        self.verification_config = Config.get_conf(verification, identifier=273062, force_registration=True)

        # Default config
        self.config.register_global(enabled=False)
        self.config.register_member(whitelisted=False)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if (
            before.display_name != after.display_name
            and await self.config.enabled()
            and not await self.config.member(after).whitelisted()
        ):
            user_name = await self.verification_config.user(after).name()

            if not user_name[0].lower() in after.display_name.lower():
                await after.edit(nick=user_name[0][:32])

                embed = discord.Embed(
                    title="Invalid Nickname",
                    description=(
                        "To ensure a safe environment, your nickname must include your real first name.\n"
                        "You can still use your psuedonym by including your name elsewhere."
                    ),
                )
                embed.set_author(name=after.guild.name, icon_url=after.guild.icon_url)

                await after.send(embed=embed)

                # Return to prevent uneccessary nick change
                return

            cleaned_nick = after.display_name.lstrip(string.punctuation + string.whitespace)
            if after.display_name != cleaned_nick:
                await after.edit(nick=cleaned_nick)


    @commands.group()
    async def nicknamerules(self, ctx):
        """Nickname Rules Configuration"""
        pass

    @nicknamerules.command()
    @commands.admin()
    async def setenabled(self, ctx, enabled: bool):
        await self.config.enabled.set(enabled)

        await ctx.send(f"{('Disabled', 'Enabled')[enabled]} nickname rule enforcement.")

    @nicknamerules.command()
    @commands.admin()
    async def setwhitelisted(self, ctx, whitelisted: bool, *members: discord.Member):
        for member in members:
            await self.config.member(member).whitelisted.set(whitelisted)

        await ctx.send(
            f"Successfully {('unwhitelisted', 'whitelisted')[whitelisted]} members."
        )
