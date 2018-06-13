import aiohttp
import discord

from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os

def check_folders():
    if not os.path.exists("data/UBCAniCogs/compare"):
        print("Creating data/UBCAniCogs/compare folder...")
        os.makedirs("data/UBCAniCogs/compare")

def check_files():
    f = "data/UBCAniCogs/compare/compare.json"
    if not dataIO.is_valid_json(f):
        print("Creating default compare.json...")
        dataIO.save_json(f, {})

class Compare:
    """Compares schedules between people who have uploaded their scheudle"""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/UBCAniCogs/compare/compare.json"
        self.config = dataIO.load_json(self.file_path)

    @commands.group(pass_context=True, no_pm=True)
    async def compare(self, ctx):
        """Comparison group of commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @compare.command(pass_context=True, no_pm=True)
    async def upload(self, ctx):
        message = ctx.message

        if not self.api_defined():
            return await self.bot.say("The API endpoint is not defined. Please define it via `>compare api <endpoint>`")

        author = message.author
        attachments = message.attachments

        if len(attachments) != 1:
            return await self.bot.say("An attached schedule file (.ics) was expected")

        attachment = attachments[0]

        if os.path.splitext(attachment["filename"])[1] != ".ics":
            return await self.bot.say("Please upload a valid .ics file")

        async with aiohttp.get(attachment["url"]) as resp:
            if resp.status != 200:
                return await self.bot.say("An unknown issue occurred, try again later!")
            calendar = await resp.text()

            payload = aiohttp.helpers.FormData()
            payload.add_field("user", author.id, content_type="text/plain")
            payload.add_field("data", calendar, filename="ical.ics", content_type="text/calendar")

            async with aiohttp.post("{}/upload".format(self.config["api"]), data=payload) as up:
                if up.status != 200:
                    return await self.bot.say("An unknown issue occurred, try again later!")

                return await self.bot.say("Your schedule has been successfully been uploaded!")


    @compare.command(pass_context=True, no_pm=True)
    async def same(self, ctx, user: discord.Member):
        if not self.api_defined():
            return await self.bot.say("The API endpoint is not defined. Please define it via `>compare api <endpoint>`")

        message = ctx.message
        author = message.author

        # Uncomment after proper testing
        # if author.id == user.id:
        #     return await self.bot.say("You're obvious going to be taking the same classes as yourself")

        async with aiohttp.post("{}/compare".format(self.config["api"]), data={'user': author.id, 'other': user.id}) as resp:
            result = await resp.json()

            if resp.status == 400:
                errors = result["errors"]
                if errors["user"] == author.id:
                    return await self.bot.say("Please first upload your schedule to the API by uploading your calendar file and including the comment `>compare upload`")
                elif errors["user"] == user.id:
                    return await self.bot.say("{} {}".format(user.mention, errors["message"]))
                else:
                    return await self.bot.say("An unknown issue occurred, try again later!")
            elif resp.status == 200:
                same = result["same"]
                await self.bot.say("Here are the classes that you have in common")
                return await self.bot.say(same.join('\n'))
            else:
                return await self.bot.say("An unknown issue occurred, try again later!")

    @compare.command(pass_context=True, no_pm=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def api(self, ctx, endpoint: str = None):
        if endpoint is not None:
            self.config["api"] = endpoint
            dataIO.save_json(self.file_path, self.config)
            await self.bot.say("API endpoint set to {}".format(endpoint))
        else:
            if not self.api_defined():
                await self.bot.say("The API endpoint is not defined. Please define it via `>compare api <endpoint>`")
            else:
                await self.bot.say("The current API endpoint is: {}".format(self.config["api"]))

    def api_defined(self):
        return "api" in self.config

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Compare(bot))
