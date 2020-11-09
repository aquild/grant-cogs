import discord
from redbot.core import commands, Config

import requests
from json import JSONDecodeError


class MinecraftWhitelist(commands.Cog):
    """Minecraft Whitelist"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=273062, force_registration=True)

        # Default config
        self.config.register_guild(api_base=None, api_token=None, whitelist_role=[])
        self.config.register_member(username=None)

    @commands.command()
    @commands.guild_only()
    async def mcwhitelist(self, ctx: commands.Context, username: str):
        """Whitelist yourself on the Minecraft server"""
        guild_config = self.config.guild(ctx.guild)
        member_config = self.config.member(ctx.author)

        # Check if user has permission
        if not (await guild_config.whitelist_role()) in [
            role.id for role in ctx.author.roles
        ]:
            return await ctx.send("Lacking required role.")

        # Check if configured
        if not await guild_config.api_base():
            return await ctx.send(
                "Minecraft Whitelist is not configured correctly. Message a staff member for help."
            )

        # Request parameters
        api_base = await guild_config.api_base()
        headers = {"X-Api-Token": await guild_config.api_token() or ""}

        # Unwhitelist previous name
        if await member_config.username():
            res = requests.post(
                f"{api_base}/command/run",
                headers=headers,
                json={"command": f"whitelist remove {await member_config.username()}"},
            )
            try:
                if res.json()["errored"]:
                    return await ctx.send(
                        "Failed to whitelist name. Message a staff member for help."
                    )
            except JSONDecodeError:
                return await ctx.send(
                    "Failed to whitelist name. Message a staff member for help."
                )

        # Set New Username
        await member_config.username.set(username)

        # Whitelist and set new name
        res = requests.post(
            f"{api_base}/command/run",
            headers=headers,
            json={"command": f"whitelist add {username}"},
        )
        try:
            if res.json()["errored"]:
                return await ctx.send(
                    "Failed to whitelist name. Message a staff member for help."
                )
        except JSONDecodeError:
            return await ctx.send(
                "Failed to whitelist name. Message a staff member for help."
            )

        await ctx.send("Successfully updated whitelisted name.")

    @commands.group()
    @commands.guild_only()
    async def mclookup(self, ctx):
        """Lookup Minecraft Name/Discord Member pairs"""
        pass

    @mclookup.command()
    async def getminecraft(self, ctx: commands.Context, member: discord.Member):
        """Lookup Minecraft username"""
        member_config = self.config.member(member)

        await ctx.send(
            f"{member.mention}'s Minecraft username: '{await member_config.username()}'"
        )

    @mclookup.command()
    async def getdiscord(self, ctx: commands.Context, name: str):
        """Lookup Discord username"""
        members = await self.config.all_members(ctx.guild)
        for user_id, data in members.items():
            if data["username"].lower() == name.lower():
                return await ctx.send(
                    f"{name}'s Discord name: {ctx.guild.get_member(user_id).mention}"
                )

        await ctx.send(f"Nobody was found with the username {name}")

    @commands.group()
    @commands.guild_only()
    @commands.admin()
    async def mcwhitelistset(self, ctx):
        """Minecraft Whitelist Configuration"""
        pass

    @mcwhitelistset.command()
    async def serverapi(self, ctx: commands.Context, api_base: str, api_token: str):
        """Set Minecraft Server API (Respite)"""
        guild_config = self.config.guild(ctx.guild)
        await guild_config.api_base.set(api_base)
        await guild_config.api_token.set(api_token)

        await ctx.message.delete()
        await ctx.send(
            f"Set Minecraft server API settings (using Respite). *Message deleted for security*"
        )

    @mcwhitelistset.command()
    async def whitelistrole(self, ctx: commands.Context, role: discord.Role):
        """Set Necessary Role for Whitelisting"""
        guild_config = self.config.guild(ctx.guild)
        await guild_config.whitelist_role.set(role.id)

        await ctx.send(f"Set whitelisted role.")
