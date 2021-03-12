import discord
from redbot.core import checks, Config, commands, bot

unique_identifier = 33731329013491435756377863810138753385554083940397


class ReactionRoles(commands.Cog):
    def __init__(self, bot: bot.Red):
        super().__init__()  # not actually sure what this does exactly
        self.bot = bot
        self.conf = Config.get_conf(self, identifier=unique_identifier)

    @commands.command
    @checks.admin_or_permissions(manage_guild=True)
    async def createmenu(self, ctx: commands.Context):
        await ctx.send("At your service")
