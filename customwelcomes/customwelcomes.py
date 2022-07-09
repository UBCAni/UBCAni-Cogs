from redbot.core import commands, Config
from redbot.core.bot import Red
import discord

class CustomWelcomes(commands.Cog):
    """My custom cog"""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 169234992, force_registration=True)


        default_guild = {
            "welcome_msg_channel": 802078699582521374,
            "toggle_msg": True,
            "toggle_img": False
        }

        self.config.register_guild(**default_guild)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = discord.utils.get(guild.channels, id= await self.config.guild(guild).get_attr("welcome_msg_channel")())
        await channel.send("test message")

    ### UTLITY COMMANDS ###
    @commands.command()
    async def setwelcomech(self, ctx):
        """Call this in the channel where you want to display welcomes"""
        # Your code will go here
        await self.config.guild(ctx.author.guild).welcome_msg_channel.set(ctx.channel.id)
        await ctx.send("New welcome channel is: " + ctx.channel.name)

    @commands.command()
    async def getwelcomestatus(self, ctx):
        """Call this in the channel where you want to display welcomes"""
        # Your code will go here
        channel = discord.utils.get(ctx.author.guild.channels, id= await self.config.guild(ctx.author.guild).get_attr("welcome_msg_channel")())
        await ctx.send("Current welcome channel is: " + channel.name)
        await ctx.send("Sending custom message: " + str(await self.config.guild(ctx.author.guild).get_attr("toggle_msg")()))
        await ctx.send("Sending custom image: "+ str(await self.config.guild(ctx.author.guild).get_attr("toggle_img")()))

    @commands.command()
    async def togglewelmsg(self, ctx):
        """Call this to toggle welcome message on and off"""
        value = await self.config.guild(ctx.author.guild).get_attr("toggle_msg")()

        #invert valuue
        value = not value

        #change value
        await self.config.guild(ctx.author.guild).toggle_msg.set(value)

        await ctx.send("Sending custom message set to " + str(await self.config.guild(ctx.author.guild).get_attr("toggle_msg")()))

    @commands.command()
    async def togglewelimg(self, ctx):
        """Call this to toggle welcome image on and off"""
        value = await self.config.guild(ctx.author.guild).get_attr("toggle_img")()

        #invert valuue
        value = not value

        #change value
        await self.config.guild(ctx.author.guild).toggle_img.set(value)

        await ctx.send("Sending custom image set to "+ str(await self.config.guild(ctx.author.guild).get_attr("toggle_img")()))

#   @commands.command()
#   async def mycom(self, ctx):
#       """This does stuff!"""
#       # Your code will go here
#       await ctx.send(await self.config.guild(ctx.guild).get_attr(FIRST_RUN)())