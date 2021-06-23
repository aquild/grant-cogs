import discord
from redbot.core import commands, Config

class Queries(commands.Cog):
    @commands.command(aliases=["search"])
    async def google(self, ctx: commands.Context, *args):
        await ctx.send(f"<https://google.com/?q={'+'.join(args)}>")

    @commands.command(aliases=["ddg"])
    async def duckduckgo(self, ctx: commands.Context, *args):
        await ctx.send(f"<https://duckduckgo.com/?q={'+'.join(args)}>")

    @commands.command(aliases=["wiki"])
    async def wikipedia(self, ctx: commands.Context, *args):
        await ctx.send(f"<https://en.wikipedia.org/w/index.php?search={'+'.join(args)}>")

    @commands.command(aliases=["wa"])
    async def wolframalpha(self, ctx: commands.Context, *args):
        await ctx.send(f"<https://www.wolframalpha.com/input/?i={'+'.join(args)}>")
