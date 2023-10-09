from .usercommandmgmt import Usercommandmgmt
from redbot.core.bot import Red


def setup(bot: Red):
    await bot.add_cog(Usercommandmgmt(bot))
