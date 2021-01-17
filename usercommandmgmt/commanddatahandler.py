#manages the custom command data stored in command_data.json

import json 

#working database
#to be performant, load this opon the cog being loaded, and save to database when the cog is unloaded or bot shuts down
loaded_cmd_data = {}

def AddCommandEntry(cmd_name, user_id):
    """
    adds the name of a new command, and the ID of the user that created it
    """
    n_entry = {cmd_name, user_id}
    loaded_cmd_data.update(n_entry)

def RemoveCommandEntry(cmd_name):
    """
    removes a command entry
    """
    del loaded_cmd_data[cmd_name]


def LoadDatabase():
    """
    loads the database to loaded_cmd_data
    """
    rawD = open('command_data.json')
    loaded_cmd_data = json.load(rawD ,)

    rawD.close()


def SaveDatabase():
    """
    saves loaded_cmd_data to command_data.json
    """
    with open('command_data.json', 'w') as outfile:
        json.dump(loaded_cmd_data, outfile)

    outfile.close()

def getUserCommQuantity(user_id):
    """
    returns how many commands are owned by the user who owns the given ID. If user does not exist in database, returns zero.
    """
    cmd_count = 0
    for command, owner in loaded_cmd_data.keys:
        if user_id == owner:
            cmd_count += 1

    return cmd_count


def BelomgsToUser(cmd_name, user_id):
    """
    returns true if the name of the given command belongs to the user who owns the given ID, false otherwise. Will also
    return false if the command does not exist.
    """

    if CommExists(cmd_name) == False:
        return False

    return loaded_cmd_data[cmd_name] == user_id

def CommExists(cmd_name):
    """
    returns true if the given command name exists in the database
    """
    for cmd in loaded_cmd_data:
        if cmd == cmd_name:
            return True

    return False







