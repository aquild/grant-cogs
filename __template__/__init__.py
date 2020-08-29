from .cog import Cog


def setup(bot):
    bot.add_cog(Cog(bot))