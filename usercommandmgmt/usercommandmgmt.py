from redbot.core import commands
import .configurable as configurable
import .commanddatahandler as cmd_data_handler

#configurable variables
command_moderation = False



class Usercommandmgmt(commands.Cog):
    """My custom cog"""

    @commands.command()
    async def testcomm(self, ctx):
        """This does stuff!"""
        # Your code will go here
        await ctx.send(ctx.message.content.replace("testcomm ", "", 1))

    @commands.command()
    async def newcomm(self, ctx):
        """
        Creates a new redbot CustomCommands, after going thru the necessary process of checking if a user is 
        allowed to make more commands and a moderator evaluation of the proposed command
        """

        #the non-command portion of the message
        proposed_comm = ctx.message.content.replace("newcomm ", "", 1)

        #regardless of the case, inform user about status of their command
        #first, checks if user is allowed to create any more commands. If not, command creation is cancelled. 


        #if check is passed, the command is submitted to a specified moderation channel for evaluation
        if ModEvaluate(proposed_comm) == False: 
            await ctx.message.author.send("Sorry, your requested command was deemed inappopriate by moderator")

        #if evaluation is passed, command is created



        await ctx.message.author.send("Command successfully created")


    def EnforceUserCmdLimit(user):
        """
        returns true if the current number commands owned by the user is less than the highest amount allowed by any of their roles.
        """

    def ModEvaluate(proposed_msg):
            """
            posts the proposed command in the specified channel, and waits for a moderator's reaction to either 
            reject or accept the command. Will  return true if command_moderation is set to False or command
            passes moderator evalutaion. False if it is rejected by a moderator.           
            Note: proposed_msg is the proposed command
            """
            if configurable.command_moderation == False:
                return True
            else:
                #submits command for evaluation and awaits response
                pass 



    