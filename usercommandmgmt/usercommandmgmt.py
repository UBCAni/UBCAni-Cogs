from redbot.core import Config, checks, commands, data_manager
from .configurable import *
from .commanddatahandler import *
import inspect
import sys
from .commanddatahandler import Database
import os


#imports customcomm class
path = inspect.getfile(commands).replace("\core\commands\__init__.py", "")
path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(inspect.getfile(commands)))), "cogs\customcom")
sys.path.insert(1, path)

from customcom import CustomCommands, CommandObj


class Usercommandmgmt(CustomCommands):
    """My custom cog"""
    
    def __init__(self, bot):
        super().__init__(bot)
        saveFile = os.path.join(data_manager.cog_data_path(cog_instance=self), "user commands.json")
        if not os.path.isfile(saveFile):
            with open(saveFile, "w+") as f:
                empty = dict()
                json.dump(empty, f)

        self.activeDb = Database(saveFile)


    # def createDbInstance(self, path):
    #     if not os.path.isfile(path):
    #         with open(path, "w+") as f:
    #             empty = dict()
    #             json.dump(empty, f)

    #     activeDb = Database(path)
    
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

            #marks command as created by admin in database, exempted from count
            self.activeDb.SaveToDb(command, text, True)

        #normal per-role allowance check and moderation process if user isnt an admin
        else:
            #checks if user has any capacity left to make commands based on their allowance
            if self.EnforceUserCmdLimit(ctx.message.author) == False:
                await ctx.send("Sorry, you have already created the maximum number of commands allowed by your role")
                return
            #regardless of the case, inform user about status of their command
            await ctx.send("Command request submitted")

            #if check is passed, the command is submitted to a specified moderation channel for evaluation
            if self.ModEvaluate(text) == False: 
                await ctx.send("Sorry, your requested command was deemed inappopriate by moderator")
                return

            await ctx.invoke(self.cc_create_simple, command=command, text=text)

            #marks command as created by non-admin; counted as normal
            self.activeDb.SaveToDb(command, text, False)
            

    def GetHighestUserCommAllowance(self, member):
        """
        returns the highest number of custom commands permitted by the user's roles
        """
        #all of the given user's roles
        usr_roles = member.roles

        #the user's roles that confer different command allowances
        rel_usr_roles = [0]

        for cmd in self.activeDb.loaded_cmd_data:
            allowance = role_cmd_limits.get(cmd)

            if allowance != None:
                rel_usr_roles.append(allowance)

        return max(rel_usr_roles)   

    def ModEvaluate(self, proposed_msg):
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

    def EnforceUserCmdLimit(self, member):
        """
        returns true if the current number commands owned by the user is less than the highest amount allowed by any of their roles.
        """
        return self.activeDb.GetUserCommQuantity(member.id) < Usercommandmgmt.GetHighestUserCommAllowance(member)





    