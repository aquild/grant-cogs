from .mcwhitelist import MinecraftWhitelist


def setup(bot):
    bot.add_cog(MinecraftWhitelist())