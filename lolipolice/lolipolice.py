from discord.ext import commands
from random import choice

image_links = [
    "https://cdn.discordapp.com/attachments/400776422383288320/405812501830303744/fMew1oA.gif",
    "https://cdn.discordapp.com/attachments/400776422383288320/405812501234843671/Kcj6K6R.gif",
    "https://cdn.discordapp.com/attachments/400776422383288320/405812501234843671/Kcj6K6R.gif",
    "https://cdn.discordapp.com/attachments/400776422383288320/405587460521852938/Oujznpw.gif"
]

class LoliPolice:
    """Gallery for lolipolice"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lolipolice")
    async def _lolipolice(self):
        return await self.bot.say(choice(image_links))

def setup(bot):
    bot.add_cog(LoliPolice(bot))
