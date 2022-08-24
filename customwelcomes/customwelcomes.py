from redbot.core import commands, Config, data_manager
from redbot.core.bot import Red
import discord
import os
import sys
import aiohttp
import io
from PIL import Image, ImageChops, ImageOps

class CustomWelcomes(commands.Cog):
    """My custom cog"""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 169234992, force_registration=True)


        default_guild = {
            "welcome_msg_channel": 802078699582521374,
            "toggle_msg": True,
            "toggle_img": False,
            "randomise_msg": False,
            "randomise_img": False,
            "def_welcome_msg": "Welcome to UBC chinese cartoon club {USER}", 
            "mandatory_msg_frag": "Make sure to check <#244434657414873090> and <#892612995891466270>! Feel free to DM an exec if you have any questions!"
        }

        self.config.register_guild(**default_guild)
        self.data_dir = data_manager.cog_data_path(cog_instance=self)
        self.img_dir = os.path.join(self.data_dir, "welcome_imgs")

        self.session = aiohttp.ClientSession()
        # a header to successfully download user avatars for use
        self.headers = {"User-agent": "Mozilla/5.0"}

        # create folder to hold welcome images
        try:
            os.mkdir(os.path.join(self.data_dir, "welcome_imgs"))
        except OSError as error: 
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = discord.utils.get(guild.channels, id= await self.config.guild(guild).get_attr("welcome_msg_channel")())

        is_sending_msg = await self.config.guild(guild).get_attr("toggle_msg")()
        is_sending_img = await self.config.guild(guild).get_attr("toggle_img")()

        is_randomising_msg = await self.config.guild(guild).get_attr("randomise_msg")()
        is_randomising_img = await self.config.guild(guild).get_attr("randomise_img")()

        #if true, process welcome message and send
        welcome_msg = ""
        if is_sending_msg:
            if is_randomising_msg:
                welcome_msg = str(await self.get_random_welcome_msg(member))
            else:
                welcome_msg = str(await self.get_welcome_msg(member))

            mandatory  =await self.config.guild(guild).get_attr("mandatory_msg_frag")()
            welcome_msg = welcome_msg.replace("{USER}", member.mention) + ". " + str(mandatory)


        #if true, process welcome img and send
        if is_sending_img:
            if is_randomising_img:
                custom_img = await self.generate_random_welcome_img(member)
            else:
                custom_img = await self.generate_welcome_img(member)



        #provides appropriate response according to settings
        if is_sending_msg and is_sending_img:
            img_format = "{}.png"
            welcome_img_path = os.path.join(self.img_dir, img_format)
            await channel.send(welcome_msg, file=discord.File(custom_img, filename = "output.png"))

        elif not is_sending_msg and is_sending_img:
            img_format = "{}.png"
            welcome_img_path = os.path.join(self.img_dir, img_format)
            await channel.send(file=discord.File(custom_img, filename = "output.png"))

        elif is_sending_msg and not is_sending_img:
            await channel.send(welcome_msg, filename = "output.png")

        elif not is_sending_msg and not is_sending_img:
            # do nothing
            pass
        

    ### TOGGLE & UTLITY COMMANDS ###
    @commands.group(aliases=["welcomecfg"])
    @commands.guild_only()
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

    @greetsettings.group(name="togglerandommsg")
    async def togglewelmsg(self, ctx):
        """Call this to toggle random welcome message on and off"""
        value = await self.config.guild(ctx.author.guild).get_attr("randomise_msg")()

        #invert valuue
        value = not value

        #change value
        await self.config.guild(ctx.author.guild).toggle_msg.set(value)

        await ctx.send("Sending custom message set to " + str(await self.config.guild(ctx.author.guild).get_attr("randomise_msg")()))

    @greetsettings.group(name="togglerandomimg")
    async def togglewelmsg(self, ctx):
        """Call this to toggle random welcome message on and off"""
        value = await self.config.guild(ctx.author.guild).get_attr("randomise_img")()

        #invert valuue
        value = not value

        #change value
        await self.config.guild(ctx.author.guild).toggle_msg.set(value)

        await ctx.send("Sending custom message set to " + str(await self.config.guild(ctx.author.guild).get_attr("randomise_img")()))

    @greetsettings.group(name="currrentgreet")
    async def get_current_greeting(self, ctx):
        await ctx.send("Current Message is: "+ str(await self.config.guild(ctx.author.guild).get_attr("def_welcome_msg")()))
        await ctx.send("Mandatory Message Fragment: " + str(await self.config.guild(ctx.author.guild).get_attr("mandatory_msg_frag")()))
        base_img_path = os.path.join(self.data_dir, "default.png")  
        await ctx.send("Current template image is: ", file=discord.File(base_img_path))

    ### SET MESSAGE & PICTURE COMMANDS ###
    @commands.group(aliases=["welcomeset"])
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
    async def set_image(self, ctx):
        """Sets the image to be sent when a user joins the server. This must be set before any welcome image is sent. Please only attach 1 image, make it fit into the template provided"""
        image = None
        if len(ctx.message.attachments) == 1:
            image = ctx.message.attachments[0]
        else:
            await ctx.reply("You need to attach exactly 1 image in the message that uses this command")
            return

        base_img_path = os.path.join(self.data_dir, "default.png")
        await image.save(base_img_path)

        await ctx.reply("Welcome Image base set to: ", file=discord.File(base_img_path))

    @greetcontent.group(name="template")
    async def get_tempate(self, ctx):
        """responds to command with the template for the welcome image so users can create their own easier"""
        await ctx.reply("Here is the template file!", file=discord.File(os.path.join(os.path.dirname(os.path.realpath(__file__)), "welcome_template.png")))

    ### CUSTOM WELCOME PICTURE GENERATION ###
    async def generate_welcome_img(self, user):
        """creates an image for the specific player using their avatar and saves it to the custom image folder, then returns the path to that image"""
        base = Image.open(os.path.join(self.data_dir, "default.png"))
        mask = Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "MASK.png"))

        #get avatar from User
        avatar: bytes

        try:
            async with self.session.get(str(user.avatar_url), headers = self.headers) as webp:
                avatar = await webp.read()
        except aiohttp.ClientResponseError:
            pass

        with Image.open(io.BytesIO(avatar)) as retrieved_avatar:
            if not retrieved_avatar:
                return
            else:
                #base = base.resize((1193, 671), 2)
                retrieved_avatar = retrieved_avatar.resize((325,325), 1)
                base.paste(retrieved_avatar, (434,0), mask)
                generated = io.BytesIO()
                base.save(generated, format="png")
                generated.seek(0)
                return generated
            

        #usr = "{}.png"
        #gen_image_path = os.path.join(self.img_dir, usr.format(user.id))
        #print(user.avatar_url)
        #await user.avatar.save(gen_image_path)
        #retrieved_avatar = Image.open(gen_image_path)

        #base.paste(retrieved_avatar, (0,0))
        #base.save(gen_image_path)

    def generate_random_welcome_img(self, user):
        pass

    ### CUSTOM WELCOME MESSAGE GENERATION ###
    async def get_welcome_msg(self, author):
        msg =  await self.config.guild(author.guild).get_attr("def_welcome_msg")()
        return msg

    def get_random_welcome_msg(self, author):
        pass


#   @commands.command()
#   async def mycom(self, ctx):
#       """This does stuff!"""
#       # Your code will go here
#       await ctx.send(await self.config.guild(ctx.guild).get_attr(FIRST_RUN)())