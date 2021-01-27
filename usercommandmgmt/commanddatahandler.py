#manages the custom command data stored in command_data.json

import json 
import os

class Database:
    '''database object; stores info for custom commands'''
    def __init__(self, directory):
        super().__init__()
        self.dir = directory
        self.loaded_cmd_data = {"db": []}

        self.ReadFromDB()


    def ReadFromDB(self):
        '''
        reads from the database
        '''
        try:
            with open(self.dir, "r") as f:
                self.loaded_cmd_data = json.load(f)
        except IOError:
            self.loaded_cmd_data = {}

    def SaveToDb(self, cmd_name, cmd_owner, is_admin):
        '''
        saves a command's info to the database
        '''
        n_entry = {cmd_name : [{
                   "cmd_owner": cmd_owner,
                   "admin-made": is_admin
        }]}
        self.loaded_cmd_data["db"].append(n_entry)
        with open(self.dir, 'w') as outfile:
            json.dump(self.loaded_cmd_data, outfile)

    def DeleteFromDb(self, cmd_name):
        '''
        removes an entry from the list of command data and updates the database
        '''
        if not self.CommExists(cmd_name):
            return

        remove_index = 0
        for cmd in self.loaded_cmd_data["db"]:
            if list(cmd.items())[0][0] == cmd_name:
                break
            remove_index += 1
            
        self.loaded_cmd_data["db"].pop(remove_index)
        with open(self.dir, 'w') as outfile:
            json.dump(self.loaded_cmd_data, outfile)

    def GetUserCommQuantity(self, user_id):
        """
        returns how many commands are owned by the user who owns the given ID. If user does not exist in database, returns zero.
        """
        cmd_count = 0
        for command in self.loaded_cmd_data["db"]:
            if list(command.items())[0][1][0]['cmd_owner'] == user_id and list(command.items())[0][1][0]["admin-made"] == False:
                cmd_count += 1

        return cmd_count

    def CommExists(self, cmd_name):
        """
        returns true if the given command name exists in the database
        """
        for cmd in self.loaded_cmd_data["db"]:
            if list(cmd.items())[0][0] == cmd_name:
                return True

        return False

    def GetComm(self, cmd_name):
        """
        returns the database entry for the given cmd_name, if it exists
        """
        for cmd in self.loaded_cmd_data["db"]:
            if list(cmd.items())[0][0] == cmd_name:
                return cmd

        return None
    
    def BelongsToUser(self, cmd_name, user_id):
        """
        returns true if the name of the given command belongs to the user who owns the given ID, false otherwise. Will also
        return false if the command does not exist.
        """

        if self.CommExists(cmd_name) == False:
            return False

        return list(self.GetComm(cmd_name).items())[0][1][0]['cmd_owner'] == user_id

    






