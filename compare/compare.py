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
        """Upload a new schedule to the server"""
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
            await self.bot.delete_message(message)
            if resp.status != 200:
                return await self.bot.say(await resp.text())
            calendar = await resp.text()

            payload = aiohttp.helpers.FormData()
            payload.add_field("user", author.id, content_type="text/plain")
            payload.add_field("data", calendar, filename="ical.ics", content_type="text/calendar")

            async with aiohttp.post("{}/upload".format(self.config["api"]), data=payload) as up:
                if up.status != 200:
                    return await self.bot.say(await resp.text())

                return await self.bot.say("Your schedule has been successfully been uploaded!")


    @compare.command(pass_context=True, no_pm=True)
    async def same(self, ctx, user: discord.Member):
        """Check what classes you share with someone else"""
        if not self.api_defined():
            return await self.bot.say("The API endpoint is not defined. Please define it via `>compare api <endpoint>`")

        message = ctx.message
        author = message.author

        async with aiohttp.post("{}/same".format(self.config["api"]), data={'user': author.id, 'other': user.id}) as resp:
            result = await resp.json()

            if resp.status == 400:
                errors = result["errors"]
                if errors["user"] == author.id:
                    return await self.bot.say("Please first upload your schedule to the API by uploading your calendar file and including the comment `>compare upload`")
                elif errors["user"] == user.id:
                    return await self.bot.say("{} {}".format(user.mention, errors["message"]))
                else:
                    return await self.bot.say(await resp.text())
            elif resp.status == 200:
                same = result["result"]
                if len(same) == 0:
                    return await self.bot.say("You have no classes in common :aquacry:")

                await self.bot.say("Here are the classes that you have in common:")
                return await self.bot.say('\n'.join(same))
            else:
                return await self.bot.say(await resp.text())

    @compare.command(pass_context=True, no_pm=True)
    async def free(self, ctx, weekday: int, user: discord.Member):
        """Checks which free blocks you share with someone on a day of the week"""
        if not self.api_defined():
            return await self.bot.say("The API endpoint is not defined. Please define it via `>compare api <endpoint>`")

        message = ctx.message
        author = message.author

        if weekday == 1: weekday_name = "Monday"
        elif weekday == 2: weekday_name = "Tuesday"
        elif weekday == 3: weekday_name = "Wednesday"
        elif weekday == 4: weekday_name = "Thursday"
        elif weekday == 5: weekday_name = "Friday"
        else: return await self.bot.say("Please specify the weekday as a number from 1-5 (starting from Monday)")


        async with aiohttp.post("{}/free".format(self.config["api"]), data={'user': author.id, 'other': user.id, 'weekday': weekday}) as resp:
            result = await resp.json()

            if resp.status == 400:
                errors = result["errors"]
                if "user" in errors:
                    if errors["user"] == author.id:
                        return await self.bot.say("Please first upload your schedule to the API by uploading your calendar file and including the comment `>compare upload`")
                    elif errors["user"] == user.id:
                        return await self.bot.say("{} {}".format(user.mention, errors["message"]))

                if "message" in errors:
                    return await self.bot.say(errors["message"])

                return await self.bot.say(await resp.text())
            elif resp.status == 200:
                start = result["start"]
                end = result["end"]
                blocks = result["blocks"]
                if start == "00:00:00" and end == "23:59:59":
                    return await self.bot.say("Neither of you have classes today; find a time to meetup!")

                if len(blocks) == 0:
                    return await self.bot.say("There are no hour-long free blocks between your schedules. Try meeting before {} or after {}".format(start, end))

                await self.bot.say("Here are some times that might work for you:")
                await self.bot.say('\n'.join(blocks))
                return await self.bot.say("Also, you can try find a time before {} or after {}".format(start, end))
            else:
                return await self.bot.say(await resp.text())

    @compare.command(pass_context=True, no_pm=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def api(self, ctx, endpoint: str = None):
        """Update the API endpoint"""
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
