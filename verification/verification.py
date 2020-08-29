import discord
from redbot.core import commands, Config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import traceback

import os
from dotenv import load_dotenv

load_dotenv()


class Verification(commands.Cog):
    """Verify new users"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=273062)

        # Default config
        self.config.register_global(
            sendgrid_key=os.getenv("SENDGRID_KEY"), from_email=None
        )
        self.config.register_guild(
            domains=[],
            verified_roles=[],
            trigger={"channel": None, "message": None},
        )
        self.config.register_user(email=None, verification_code=None, name=tuple())

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: discord.RawReactionActionEvent):
        if not event.guild_id:
            return

        guild_config = self.config.guild_from_id(event.guild_id)
        guild_trigger = await guild_config.trigger()

        if event.message_id == guild_trigger["message"]:

            embed = discord.Embed(
                title="Verification",
                description=(
                    "In order to join we need to verify that you really are a student.\n"
                    "To start verification, use the !verifyemail command like this:\n"
                    "`!verifyemail <your student email>`\n"
                    "You'll get an email with a code and instructions to verify."
                ),
            )
            guild: discord.Guild = self.bot.get_guild(event.guild_id)
            user = self.bot.get_user(event.user_id)
            embed.set_author(name=guild.name, icon_url=guild.icon_url)

            await user.send(embed=embed)

    @commands.command()
    @commands.dm_only()
    async def verifyemail(self, ctx, email: str):
        """Send verification email"""

        user_config = self.config.user(ctx.author)
        await user_config.email.set(email)
        verification_code = "".join([str(n) for n in random.choices(range(10), k=6)])
        await user_config.verification_code.set(verification_code)

        message = Mail(
            from_email=await self.config.from_email(),
            to_emails=email,
            subject="Grant Discord Email Verification",
            html_content=f'<!DOCTYPE html><html><body style="min-height: 600px; padding: 2em 0; text-align: center"><h3>Grant Discord Verification Code</h3><h1 style="font-size: 4rem; margin: 1rem">{verification_code}</h1></body></html>',
        )
        try:
            sg = SendGridAPIClient(await self.config.sendgrid_key())
            sg.send(message)
            await ctx.send(
                (
                    "Sent verification email...\n"
                    "Once you've recieved the email use the !verify command like this to complete your verification:\n"
                    "`!verify <your verification code> <your first name> <your last name>`"
                )
            )
        except Exception as e:
            traceback.print_exc()
            await ctx.send(
                "There was an error sending the email. DM a staff member to verify manually."
            )

    @commands.command()
    @commands.dm_only()
    async def verify(
        self,
        ctx: commands.Context,
        verification_code: str,
        first_name: str,
        last_name: str,
    ):
        """Verify user"""

        user_config = self.config.user(ctx.author)

        if await user_config.name():
            await ctx.send(
                "Name already set, contact a staff member to change it manually."
            )
        else:
            await user_config.name.set((first_name, last_name))

        correct = await user_config.verification_code() == verification_code
        if not correct:
            return await ctx.send("Verification code is incorrect.")

        verification_code = "".join([str(n) for n in random.choices(range(10), k=6)])
        await user_config.verification_code.set(verification_code)

        for guild in self.bot.guilds:
            guild_config = self.config.guild(guild)

            if (await user_config.email()).split("@")[
                1
            ] in await guild_config.domains():
                member: discord.Member = guild.get_member(ctx.author.id)
                if member:
                    await member.add_roles(
                        *[
                            guild.get_role(role)
                            for role in await guild_config.verified_roles()
                        ]
                    )
                    await member.edit(nick=first_name)
                    await ctx.send(f"Verified in server: {guild.name}.")
            else:
                await ctx.send(
                    (
                        f"Failed to verify in server {guild.name} due to an invalid email domain.\n"
                        f"Valid email domains: {', '.join(await guild_config.domains())}"
                    )
                )

    @commands.command(aliases=["getinfo"])
    async def verificationinfo(self, ctx, user: discord.User):
        """Get information about a verified user"""
        user_config = self.config.user(user)
        name = await user_config.name()
        email = await user_config.email()

        embed = discord.Embed(title="User Info")
        embed.set_author(
            name=ctx.guild.get_member(user.id).nick if ctx.guild else user.name,
            icon_url=user.avatar_url,
        )
        if name:
            embed.add_field(name="First Name", value=name[0])
            embed.add_field(name="Last Name", value=name[1])
        if email:
            embed.add_field(name="Email", value=email)

        await ctx.send(embed=embed)

    @commands.command()
    async def manualverify(
        self, ctx, user: discord.User, email: str, first_name: str, last_name: str
    ):
        """Manually verify a user"""

        user_config = self.config.user(user)
        await user_config.email.set(email)
        await user_config.name.set((first_name, last_name))

        await ctx.send("Manually updated user information.")

    @commands.group()
    async def verificationset(self, ctx):
        """Configure user verification"""
        pass

    @verificationset.command()
    @commands.guild_only()
    async def setdomains(self, ctx, *domains: str):
        """Set domains for verification"""
        await self.config.guild(ctx.guild).domains.set(domains)

        await ctx.send("Set verified domains.")

    @verificationset.command()
    @commands.guild_only()
    async def settrigger(self, ctx, channel: discord.TextChannel, message_id: str):
        """Set trigger message for verification"""

        if not await self.config.sendgrid_key():
            return await ctx.send("There is no SendGrid key set for verification.")

        message: discord.Message = await channel.fetch_message(message_id)
        await self.config.guild(ctx.guild).trigger.set(
            {"channel": channel.id, "message": message.id}
        )
        await message.add_reaction("✅")

        await ctx.send("Set trigger message.")

    @verificationset.command()
    @commands.guild_only()
    async def setverifiedroles(self, ctx, *roles: discord.Role):
        """Set role for verification"""
        await self.config.guild(ctx.guild).verified_roles.set(
            [role.id for role in roles]
        )

        await ctx.send("Set verified role(s).")

    @verificationset.command()
    async def setfromemail(self, ctx, from_email: str):
        await self.config.from_email.set(from_email)
        await ctx.send("Set from email.")

    @verificationset.command()
    async def setsendgridkey(self, ctx: commands.Context, key: str):
        await self.config.sendgrid_key.set(key)
        await ctx.send("Set SendGrid key.")
        await ctx.message.delete()
