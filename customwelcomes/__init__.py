from .customwelcomes import CustomWelcomes
from redbot.core.bot import Red


def setup(bot: Red):
    bot.add_cog(CustomWelcomes(bot))