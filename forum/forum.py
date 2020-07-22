from redbot.core import Config, commands

class Forum(commands.Cog):
    """Forum games"""

    def __init__(self, bot):
        defaults = dict(last_count=0, contributors=dict(), last_contributor=None)

        self.bot = bot
        self.config = Config.get_conf(self, 738678076)
        self.config.register_guild(**defaults)

    @commands.guild_only()
    @commands.command()
    async def count(self, ctx, value: int):
        """Continues the count"""
        settings = self.config.guild(ctx.guild)
        last_count = await settings.last_count()
        last_contributor = await settings.last_contributor()

        if last_count + 1 != value:
            return await ctx.send("Learn to count; the current number is {}.".format(last_count))

        if ctx.author.id != last_contributor:
            await settings.last_count.set(value)

            async with settings.contributors() as contributors:
                if ctx.author.id not in contributors:
                    contributors[ctx.author.id] = []

                contributors[ctx.author.id].append(value)

            await settings.last_contributor.set(ctx.author.id)

            return await ctx.send("We're now at {}.".format(value))

        return await ctx.send("Let someone else continue the count.")


    @commands.guild_only()
    @commands.command()
    async def countinfo(self, ctx):
        """Gives the current value"""
        settings = self.config.guild(ctx.guild)

        contributors = await settings.contributors()
        if ctx.author.id in contributors:
            contributions = contributors[ctx.author.id]
            if len(contributions) == 0:
                message = "You have made no contributions; get counting!"
            else:
                message = "You've counted {} number{}: {}".format(len(contributions), "" if len(contributions) == 1 else "s", ", ".join(map(str, contributions)))
        else:
            message = "You have made no contributions; get counting!"

        return await ctx.send("We are now at {}.\n{}".format(await settings.last_count(), message))
