from redbot.core import Config, checks, commands
import json
import urllib.request

class Mailchimp(commands.Cog):
    """Mailchimp integrates with our mailing service"""

    def __init__(self, bot):
        defaults = dict(api_key="")

        self.bot = bot
        self.config = Config.get_conf(self, 623215216)
        self.config.register_guild(**defaults)


    @commands.group(autohelp=True)
    @commands.guild_only()
    async def mailchimp(self, ctx):
        """Mailchimp group of commands"""
        pass

    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    @mailchimp.command()
    async def key(self, ctx, key : str):
        """Sets the API key for mailchimp"""
        await self.config.guild(ctx.guild).api_key.set(key)
        await ctx.message.delete()
        await ctx.send("API key successfully set")

    @commands.guild_only()
    @commands.command()
    async def newsletter(self, ctx):
        """The last newsletter sent"""
        settings = self.config.guild(ctx.guild)
        key = await settings.api_key()
        if len(key) == 0:
            return await ctx.send("The API key is not set for this server!")

        payload = {"count": 1, "sort_field": "send_time", "sort_dir": "DESC", "status": "sent", "type": "regular"}
        url = "https://us7.api.mailchimp.com/3.0/campaigns"
        headers = {"Authorization": f"apikey {key}", "Content-Type": "application/json" }

        r = urllib.request.Request(url=url, data=json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(r) as f:
            data = json.loads(f.read().decode())

        if f.status == 200:
            await ctx.send("The last newsletter sent was: {}".format(data['long_archive_url']))
        else:
            await ctx.send("There was an issue with using the mailchimp API")
