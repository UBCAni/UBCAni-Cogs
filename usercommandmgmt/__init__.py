from .usercommandmgmt import Usercommandmgmt
from redbot.core.bot import Red


def setup(bot: Red):
    bot.add_cog(Usercommandmgmt(bot))