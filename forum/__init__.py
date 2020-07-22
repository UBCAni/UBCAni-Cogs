from .forum import Forum

def setup(bot):
    bot.add_cog(Forum(bot))
