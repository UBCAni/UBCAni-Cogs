from redbot.core import Config, checks, commands, data_manager
from .configurable import *
from .commanddatahandler import *
import discord
from discord.utils import get
import inspect
import sys
import os
from redbot.cogs.customcom import CustomCommands
from redbot.cogs.customcom.customcom import (
    CustomCommands,
    CommandObj,
    NotFound,
    ArgParseError,
    CommandNotEdited,
)


class Usercommandmgmt(CustomCommands):
    """Custom user command limit enforcements for user"""

    def __init__(self, bot):
        super().__init__(bot)
        save_file = os.path.join(
            data_manager.cog_data_path(cog_instance=self), "user commands.json"
        )

        config_file = os.path.join(
            data_manager.cog_data_path(cog_instance=self), "config.json"
        )

        if not os.path.isfile(save_file):
            with open(save_file, "w+") as f:
                empty = {"db": []}
                json.dump(empty, f, indent=2)

        if not os.path.isfile(config_file):
            with open(config_file, "w+") as f:
                default = {
                    "role_cmd_limits": [
                        {"Tier 1 Simp": 1, "Tier 2 Simp": 3, "Tier 3 Simp": 5}
                    ],
                    "command_moderation": True,
                    "mod_channel_name": "usercommandmgmt-admin-approval",
                    "number_of_mod_reacts_needed": 2,
                }
                json.dump(default, f, indent=2)

        self.config = Config(config_file)
        self.activeDb = Database(save_file)
        intents = discord.Intents.default()
        intents.reactions = True
        self.create_command_queue = {}

    # cc commmands
    @commands.group(aliases=["cc"])
    @commands.guild_only()
    async def customcom(self, ctx: commands.Context):
        """Base command for Custom Commands management."""
        pass

    @customcom.group(name="create", aliases=["add", "new"], invoke_without_command=True)
    async def cc_create(self, ctx: commands.Context, command: str.lower, *, text: str):
        """Create custom commands.

        If a type is not specified, a simple CC will be created.
        CCs can be enhanced with arguments, see the guide
        [here](https://docs.discord.red/en/stable/cog_customcom.html).
        """

        # overrides the mod process and limit check if user is an admin
        if ctx.message.author.top_role.permissions.administrator:
            await ctx.send("Admin request detected. Bypassing checks")
            # custom command is created and the entry is added to the database
            try:
                await ctx.invoke(self.cc_create_simple, command=command, text=text)
            except:
                await ctx.send("something went wrong; could not add command")
                return
            # marks command as created by admin in database, exempted from count
            self.activeDb.save_to_db(
                command, ctx.message.author.id, True, ctx.message.guild.id
            )
        # normal per-role allowance check and moderation process if user isnt an admin
        else:
            # checks if user has any capacity left to make commands based on their allowance
            if not self.enforce_user_cmd_limit(
                ctx.message.author, ctx.message.guild.id
            ):
                await ctx.send(
                    "Sorry, you have already created the maximum number of commands allowed by your role"
                )
                return
            # inform user about status of their command
            if self.config.is_mod_enabled:
                await self.submit_for_approval(ctx, command, text)
                await ctx.send("Command request submitted")
            else:
                try:
                    await ctx.invoke(self.cc_create_simple, command=command, text=text)
                except:
                    await ctx.send("something went wrong; could not add command")
                    return
                # marks command as created by non-admin; counted as normal
                self.activeDb.save_to_db(
                    command, ctx.message.author.id, False, ctx.message.guild.id
                )

    @customcom.command(name="delete", aliases=["del", "remove"])
    async def cc_delete(self, ctx, command: str.lower):
        """Delete a custom command.

        Example:
            - `[p]customcom delete yourcommand`

        **Arguments:**

        - `<command>` The custom command to delete.
        """
        # if user is admin, allows them to delete any command
        if ctx.message.author.top_role.permissions.administrator:
            try:
                await ctx.send("Admin Override.")
                await self.commandobj.delete(ctx=ctx, command=command)
            except NotFound:
                await ctx.send("That command doesn't exist.")
                return
            self.activeDb.delete_from_db(command)
            await ctx.send("Custom command successfully deleted.")
        # if user isnt an admin, only allows them to delete their own commands
        else:
            if not self.activeDb.belongs_to_user(command, ctx.message.author.id):
                await ctx.send("Hey, that's not yours.")
                return

            try:
                await self.commandobj.delete(ctx=ctx, command=command)
            except NotFound:
                await ctx.send("That command doesn't exist.")
                return
            self.activeDb.delete_from_db(command)
            await ctx.send("Custom command successfully deleted.")

    @customcom.command(name="edit")
    async def cc_edit(self, ctx, command: str.lower, *, text: str = None):
        """Edit a custom command.

        Example:
            - `[p]customcom edit yourcommand Text you want`

        **Arguments:**

        - `<command>` The custom command to edit.
        - `<text>` The new text to return when executing the command.
        """
        if ctx.message.author.top_role.permissions.administrator:
            await ctx.send("Admin Override.")

            try:
                await self.commandobj.edit(ctx=ctx, command=command, response=text)
                await ctx.send("Custom command successfully edited.")
            except NotFound:
                await ctx.send(
                    "That command doesn't exist. Use" + ctx.clean_prefix + " to add it."
                )
            except ArgParseError as e:
                await ctx.send(e.args[0])
            except CommandNotEdited:
                pass
        else:
            # blocks a user from editing a command that isnt theirs
            if not self.activeDb.belongs_to_user(command, ctx.message.author.id):
                await ctx.send("Hey, that's not yours.")
                return

            try:
                await self.commandobj.edit(ctx=ctx, command=command, response=text)
                await ctx.send("Custom command successfully edited.")
            except NotFound:
                await ctx.send(
                    (
                        "That command doesn't exist. Use"
                        + ctx.clean_prefix
                        + " to add it."
                    )
                )
            except ArgParseError as e:
                await ctx.send(e.args[0])
            except CommandNotEdited:
                pass

    async def submit_for_approval(self, ctx, command, text):
        """
        posts the proposed command in the specified channel, and waits for a moderator's reaction to either
        reject or accept the command.
        """
        # create message to submit for mod approval
        MESSAGE_TEMPLATE = """Sender: {author}
        Proposed Command: {command}
        {text}
        {jump_url}
        """

        message_to_submit = MESSAGE_TEMPLATE.format(
            author=ctx.author.name,
            command=command,
            text=text,
            jump_url=ctx.message.jump_url,
        )

        # finds the channel to send this message to: the moderator one; specified in configurable.py
        mod_channel = self.find_channel_by_name(
            self.config.get_mod_channel_name, ctx.message.guild.channels
        )
        # submit proposed command and relavant info to specified moderation channel
        msg = await mod_channel.send(message_to_submit)
        # adds reacts
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        self.create_command_queue.append([msg, ctx, command, text])
        self.create_command_queue[msg] = [ctx, command, text]

    # reaction listener
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        listens for reacts on the mod channel
        """
        channel = self.bot.get_channel(payload.channel_id)

        if self.config.get_mod_channel_name == channel.name:
            if payload.emoji.name == "✅" or payload.emoji.name == "❌":
                message = await channel.fetch_message(payload.message_id)
                reaction = get(message.reactions, emoji=payload.emoji.name)
                if reaction and reaction.count >= 1 + self.config.get_reacts_needed:
                    req_data = self.create_command_queue.get(message)
                    # find the command data in queue, if none then do nothing
                    if req_data == None:
                        return
                    else:
                        if payload.emoji.name == "✅":
                            is_created = False
                            try:
                                await req_data[0].invoke(
                                    self.cc_create_simple,
                                    command=req_data[1],
                                    text=req_data[2],
                                )
                                is_created = True
                            except:
                                req_data[0].message.author.send(
                                    "command approved, but an error occured in creating it. Please try again"
                                )
                            if is_created:
                                self.activeDb.save_to_db(
                                    req_data[1],
                                    req_data[0].message.author.id,
                                    False,
                                    req_data[0].message.guild.id,
                                )

                                MESSAGE_TEMPLATE = """command successfully created!: 
                                You can now use >: {command}
                                """

                                can_use_alert = MESSAGE_TEMPLATE.format(
                                    command=req_data[2]
                                )
                                await req_data[0].message.author.send(can_use_alert)

                        elif payload.emoji.name == "❌":
                            await req_data[0].message.author.send(
                                "Sorry, your proposed command was deemed inappropriate by the moderators"
                            )

                        self.create_command_queue.pop(message)

    # utility commands for users
    @commands.command()
    async def command_count(self, ctx):
        """
        gets the number of commands created by the caller of this command
        """
        currently_used = self.activeDb.get_user_comm_quantity(
            ctx.message.author.id, ctx.message.guild.id
        )
        current_max = self.get_highest_user_comm_allowance(ctx.message.author)

        MESSAGE_TEMPLATE = """You have assigned {currrent_amt} out of {max_amt} commands available to you"""

        msg = MESSAGE_TEMPLATE.format(currrent_amt=currently_used, max_amt=current_max)

        await ctx.send(msg)

    # utility commands for moderators
    @checks.mod_or_permissions(administrator=True)
    @commands.command()
    async def togglemoderation(self, ctx):
        """
        sets command_moderation to false if true, and vice versa
        """

    @checks.mod_or_permissions(administrator=True)
    @commands.command()
    async def setmodchannel(self, ctx):
        """
        sets command_moderation to false if true, and vice versa
        """

    @checks.mod_or_permissions(administrator=True)
    @commands.command()
    async def setapprovalreq(self, ctx):
        """
        sets command_moderation to false if true, and vice versa. Number must be > 1, otherwise does nothing and alerts user
        """

    @checks.mod_or_permissions(administrator=True)
    @commands.command()
    async def addallowancedrole(self, ctx):
        """
        adds a new allowance setting for a role in the dictionary with the given allowance, if it doesn't already exist. Allowance must be >= 1
        """

    @checks.mod_or_permissions(administrator=True)
    @commands.command()
    async def removeallowancedrole(self, ctx):
        """
        removes an allowance setting for a role in the dictionary, if it exists
        """

    @checks.mod_or_permissions(administrator=True)
    @commands.command()
    async def changeroleallowance(self, ctx):
        """
        changes role allowance to the given number for the given role. Must be greater or equal to 1
        """

    # helper functions
    def enforce_user_cmd_limit(self, member, server):
        """
        returns true if the current number commands owned by the user is less than the highest amount allowed by any of their roles.
        """
        return self.activeDb.get_user_comm_quantity(
            member.id, server_id=server
        ) < self.get_highest_user_comm_allowance(member)

    def get_highest_user_comm_allowance(self, member):
        """
        returns the highest number of custom commands permitted by the user's roles
        """
        # all of the given user's roles
        usr_roles = member.roles
        # the user's roles that confer different command allowances
        rel_usr_roles = [0]
        for cmd in usr_roles:
            allowance = self.config.get_role_list.get(cmd.name, 0)
            if allowance != 0:
                rel_usr_roles.append(allowance)

        return max(rel_usr_roles)

    def find_channel_by_name(self, channel_name, channel_List):

        """
        finds the discord channel in the list with the given name, and returns it. Will return none if a channel can't be found
        """

        for i in channel_List:
            if i.name == channel_name:
                return i

        return None

    def find_command_req_data(self, msg):
        """
        finds the given command request data from the queue by matching its message with the given one
        """
        for req in self.create_command_queue:
            if msg == req[0]:
                return req
        return None
