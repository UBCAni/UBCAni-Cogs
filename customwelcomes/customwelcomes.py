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

        #if true, process welcome message and send
        if await self.config.guild(guild).get_attr("toggle_msg")():
            pass

        #if true, process welcome img and send
        if await self.config.guild(guild).get_attr("toggle_img")():
            pass

        await channel.send("test message")

    ### TOGGLE & UTLITY COMMANDS ###
    @commands.group(aliases=["welcomecfg"])
    async def greetsettings(self, ctx: commands.Context):
        """Base command for configuring the customised welcome."""
        pass

    @greetsettings.group(name="setch")
    async def setwelcomech(self, ctx):
        """Call this in the channel where you want to display welcomes"""
        # Your code will go here
        await self.config.guild(ctx.author.guild).welcome_msg_channel.set(ctx.channel.id)
        await ctx.send("New welcome channel is: " + ctx.channel.name)

    @greetsettings.group(name="getstatus")
    async def getwelcomestatus(self, ctx):
        """Call this in the channel where you want to display welcomes"""
        # Your code will go here
        channel = discord.utils.get(ctx.author.guild.channels, id= await self.config.guild(ctx.author.guild).get_attr("welcome_msg_channel")())
        await ctx.send("Current welcome channel is: " + channel.name)
        await ctx.send("Sending custom message: " + str(await self.config.guild(ctx.author.guild).get_attr("toggle_msg")()))
        await ctx.send("Sending custom image: "+ str(await self.config.guild(ctx.author.guild).get_attr("toggle_img")()))

    @greetsettings.group(name="togglemsg")
    async def togglewelmsg(self, ctx):
        """Call this to toggle welcome message on and off"""
        value = await self.config.guild(ctx.author.guild).get_attr("toggle_msg")()

        #invert valuue
        value = not value

        #change value
        await self.config.guild(ctx.author.guild).toggle_msg.set(value)

        await ctx.send("Sending custom message set to " + str(await self.config.guild(ctx.author.guild).get_attr("toggle_msg")()))

    @greetsettings.group(name="toggleimg")
    async def togglewelimg(self, ctx):
        """Call this to toggle welcome image on and off"""
        value = await self.config.guild(ctx.author.guild).get_attr("toggle_img")()

        #invert valuue
        value = not value

        #change value
        await self.config.guild(ctx.author.guild).toggle_img.set(value)

        await ctx.send("Sending custom image set to "+ str(await self.config.guild(ctx.author.guild).get_attr("toggle_img")()))

    ### SET MESSAGE & PICTURE COMMANDS ###
    @commands.group(aliases=["welcomesetset"])
    async def greetcontent(self, ctx: commands.Context):
        """Base command for configuring the image/text used for customised welcome."""
        pass

    @greetcontent.group(name="settxt")
    async def set_text(self, ctx, txt):
        """Sets the message to be sent when a user joins the server. This must be set before any welcome message is sent"""
        await self.config.guild(ctx.author.guild).def_welcome_msg.set(txt)
        new_welcome_message = "New welcome message is : {}"
        await ctx.send(new_welcome_message.format(await self.config.guild(ctx.author.guild).get_attr("def_welcome_msg")()))

    @greetcontent.group(name="setimg")
    async def set_text(self, ctx):
        """Sets the image to be sent when a user joins the server. This must be set before any welcome image is sent. Please only attach 1 image, make it fit into the template provided"""

    @greetcontent.group(name="template")
    async def get_tempate(self, ctx):
        """responds to command with the template for the welcome image so users can create their own easier"""
        await ctx.respond("Here is the template file!", file=Discord.File("UBCANI_welcome_template.png"))


    ### CUSTOM WELCOME PICTURE GENERATION ###
    def get_welcome_img(self):
        pass

    ### CUSTOM WELCOME MESSAGE GENERATION ###
    def get_welcome_msg(self):
        pass
    



#   @commands.command()
#   async def mycom(self, ctx):
#       """This does stuff!"""
#       # Your code will go here
#       await ctx.send(await self.config.guild(ctx.guild).get_attr(FIRST_RUN)())