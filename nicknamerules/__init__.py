from .nicknamerules import NicknameRules


def setup(bot):
    if bot.get_cog("Verification"):
        verification = bot.get_cog("Verification")
        bot.add_cog(NicknameRules(bot, verification))