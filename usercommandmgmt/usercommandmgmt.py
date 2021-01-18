from redbot.core import Config, checks, commands
from .configurable import *
from .commanddatahandler import *
import inspect
import sys


#imports customcomm class
sys.path.insert(1, inspect.getfile(commands).replace("\core\commands\__init__.py", "\cogs\customcom"))

from customcom import CustomCommands


class Usercommandmgmt(CustomCommands):
    """My custom cog"""

    
    # def __init__(self, bot):
    #     self.bot = bot

    

    @commands.command()
    async def testcomm(self, ctx):
        """This does stuff!"""
        
        pass

    
    @commands.group(aliases=["cc"])
    @commands.guild_only()
    async def customcom(self, ctx: commands.Context):
        """Base command for Custom Commands management."""
        pass
    

    @customcom.group(name="create", aliases=["add"], invoke_without_command=True)
    async def cc_create(self, ctx: commands.Context, command: str.lower, *, text: str):
        """Create custom commands.

        If a type is not specified, a simple CC will be created.
        CCs can be enhanced with arguments, see the guide
        [here](https://docs.discord.red/en/stable/cog_customcom.html).
        """

        #overrides the mod process and limit check if user is an admin
        if ctx.message.author.top_role.permissions.administrator:
            await ctx.send("Admin request detected. Bypassing checks")
            #custom command is created and the entry is added to the database
            await ctx.invoke(self.cc_create_simple, command=command, text=text)
            AddCommandEntry(command, ctx.message.author.id)

        #normal per-role allowance check and moderation process if user isnt an admin
        else:
            #checks if user has any capacity left to make commands based on their allowance
            if self.EnforceUserCmdLimit(ctx.message.author):
                await ctx.message.author.send("Sorry, you have already created the maximum number of commands allowed by your role")
                return
            #regardless of the case, inform user about status of their command
            await ctx.send("Command request submitted")

            #if check is passed, the command is submitted to a specified moderation channel for evaluation
            if ModEvaluate(text) == False: 
                await ctx.message.author.send("Sorry, your requested command was deemed inappopriate by moderator")
                return

            await ctx.invoke(self.cc_create_simple, command=command, text=text)
            AddCommandEntry(command, ctx.message.author.id)

    @staticmethod
    def GetHighestUserCommAllowance(member):
        """
        returns the highest number of custom commands permitted by the user's roles
        """
        #all of the given user's roles
        usr_roles = member.roles

        #the user's roles that confer different command allowances
        rel_usr_roles = [0]

        for cmd in loaded_cmd_data:
            allowance = role_cmd_limits.get(cmd)

            if allowance != None:
                rel_usr_roles.append(allowance)

        return max(rel_usr_roles)   

    @staticmethod
    def ModEvaluate(proposed_msg):
        """
        posts the proposed command in the specified channel, and waits for a moderator's reaction to either 
        reject or accept the command. Will  return true if command_moderation is set to False or command
        passes moderator evalutaion. False if it is rejected by a moderator.           
        Note: proposed_msg is the proposed command
        """
        if command_moderation == False:
            return True
        else:        
            #submits command for evaluation and awaits response; TODO
            pass    

    @staticmethod
    def EnforceUserCmdLimit(member):
        """
        returns true if the current number commands owned by the user is less than the highest amount allowed by any of their roles.
        """
        return getUserCommQuantity(member.id) < Usercommandmgmt.GetHighestUserCommAllowance(member)

    '''
    @commands.command()
    async def newcomm(self, ctx):
        """
        Creates a new redbot CustomCommand, after going thru the necessary process of checking if a user is 
        allowed to make more commands and a moderator evaluation of the proposed command
        """

        #the non-command portion of the message
        comm_data = ctx.message.content.split()
        comm_name = comm_data[1]
        comm_msg = " ".join(comm_data[2:])



        #regardless of the case, inform user about status of their command
        #first, checks if user is allowed to create any more commands. If not, command creation is cancelled. 
        if EnforceUserCmdLimit(ctx.message.author):
            await ctx.message.author.send("Sorry, you have already created the maximum number of commands allowed by your role")
            return
        #if check is passed, the command is submitted to a specified moderation channel for evaluation
        if ModEvaluate(comm_msg) == False: 
            await ctx.message.author.send("Sorry, your requested command was deemed inappopriate by moderator")
            return

        #if evaluation is passed, custom command is created and the entry is added to the database
        cc = self.bot.get_cog("CustomCommands")
        await ctx.invoke(CustomCommands.cc_create, ctx = cc, command = "no_u", text = "no you")
        AddCommandEntry(comm_name, ctx.message.author.id)


        await ctx.message.author.send("Command successfully created")
    '''




    