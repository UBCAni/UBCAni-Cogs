from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
import os
import requests

def check_folders():
    if not os.path.exists("data/UBCAniCogs/mailchimp"):
        print("Creating data/UBCAniCogs/mailchimp folder...")
        os.makedirs("data/UBCAniCogs/mailchimp")

def check_files():
    f = "data/UBCAniCogs/mailchimp/mailchimp.json"
    if not dataIO.is_valid_json(f):
        print("Creating default mailchimp.json...")
        dataIO.save_json(f, {})

class Mailchimp:
    """Mailchimp integrates with our mailing service"""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/UBCAniCogs/mailchimp/mailchimp.json"
        self.data = dataIO.load_json(self.file_path)

    @commands.group(pass_context=True, no_pm=True)
    async def mailchimp(self, ctx):
        """Mailchimp group of commands"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @mailchimp.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def key(self, ctx, key : str):
        """Sets the API key for mailchimp"""
        server = ctx.message.server
        self.data[server.id] = key
        dataIO.save_json(self.file_path, self.data)
        await self.bot.delete_message(ctx.message)
        await self.bot.say("API key successfully set")

    @commands.command(pass_context=True, no_pm=True)
    async def newsletter(self, ctx):
        server = ctx.message.server
        if server.id not in self.data or not self.data[server.id]:
            return await self.bot.say("The API key is not set for this server!")

        key = self.data[server.id]
        payload = {"count": 1, "sort_field": "send_time", "sort_dir": "DESC"}
        url = "https://us7.api.mailchimp.com/3.0/campaigns"
        headers = {"Authorization": f"apikey {key}"}

        r = requests.get(url, params=payload, headers=headers)

        if r.status_code == 200:
            await self.bot.say(r.json()["campaigns"][0]["long_archive_url"])
        else:
            await self.bot.say("There was an issue with using the mailchimp API")

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Mailchimp(bot))
