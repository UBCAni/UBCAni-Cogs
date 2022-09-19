from redbot.core import commands, Config, data_manager, checks
from redbot.core.bot import Red
import discord
import os
import sys
import aiohttp
import io
import pickle


class EventManager(commands.Cog):
    '''a cog for managing events'''
    def __init__(self, bot):
        self.bot = bot	
        self.config = Config.get_conf(self, 867664587, force_registration=True)
        default_guild = {}
        self.config.register_guild(**default_guild)
        self.data_dir = data_manager.cog_data_path(cog_instance=self)
        self.event_dir = os.path.join(self.data_dir, "events")
        self.current_event = None



