from json import dump, load, JSONDecodeError
from tkinter.filedialog import asksaveasfile, askopenfilename
from sys import exit
from getpass import getpass
from pathlib import Path
import os
import tkinter as tk

__author__ = "Truls Skadberg (Scadic)"
__copyright__ = "Copyright 2020, Scadic"
__credits__ = "Truls Skadberg (Scadic)"

__version__ = "1.0.0"
__maintainer__ = "Truls Skadberg (Scadic)"
__email__ = "trulshskadberg@gmail.com"
__status__ = "Prototype"

def get_input(promt="", t=str):
    '''
    Gets input from `input` and evaluates if the data is of the correct type.
    If not it will ask again until it is of the correct type.\n
    Parameters:\n
    :prompt (str): The string which is sent to `input`'s prompt.
    :t (class): The class of the return value. Only single classes i.e. <type:str>, <type:int>...\n
    get_input(`prompt`, `t`) -> t(`get_input(prompt)`)
    '''
    if t == None or type(t) is None:
        print("Cannot use None as the type as it is not callable, use a suitable type for your data!")
        return None
    while True and t != None:
        i = input(promt)
        try:
            i = t(i)
        except ValueError as e:
            print("Unable to parse the value to the type %s, please try again." % str(t))
        except TypeError as e:
            print("Unable to call %s because %s" % (t, e))
        if type(i) is t:
            break
    return i

def prompts():
    '''
    Uses `get_input` and `getpass` to request data from the user to setup parameters for ServerSettings.\n
    prompts() -> dict{str: str}
    '''
    return {
        "ldap_server": get_input("LDAP Server FQDN. <Servername>.<domain>.<tld>: ", str),
        "username": get_input("Username (cn of the user) to user for AD manipulation: ", str),
        "password":  getpass("Password for the user: "),
        "topLevelDomain": get_input("Top level domain of the domain of AD. <domain>.<tld>: ", str),
        "homeDrive": get_input("Home drive the useraccounts will use. i.e. 'H:': ", str),
        "profileDeliveryPrefix": get_input("Path prefix for user profiles in a UNC format. \\\\<Servername>\\<share>\\", str),
        "homeDirectoryPrefix": get_input("Path prefix for user home directories in a UNC format. \\\\<Servername>\\<share>\\", str),
        "scriptPath": get_input("Path to the script name which is located in \\\\<Servername>\\sysvol\\<domain>.<tld>\\scripts\\", str),
        "physicalDeliveryOfficeName": get_input("Office name or code: ", str),
        "company": get_input("Name of company/organization: ", str),
        "userdomain": get_input("NETBIOS name of the domain, usually equal to <domain>: ", str),
        "base_ou": get_input("Base OU's cn of where all the departments and groups are located, best practice is to use <domain> as the 'cn' or an abbreviation of it.: ", str),
        "usergroup": get_input("Group where all none default users are located, recommended is to use '<domain> Users': ", str),
        "domainsuffix": get_input("Top level domain. <domain>.<tld>: ", str),
        "path": str(Path(__file__).absolute()),
        "user_groups": [get_input("Group where all none default users are located, recommended is to use '<domain> Users': ", str)],
        "user_groups_d": {1: get_input("Group where all none default users are located, recommended is to use '<domain> Users': ", str)},
        "db_user": get_input("Username to use to connect to MySQL DB: ", str),
        "db_pwd": getpass("Password to use to connect to MySQL DB: ", str),
        "db_host": get_input("Host of the DB: ", str),
        "db_db": get_input("DB to connect to: ", str),
        "db_port": get_input("Port on which to connect to MySQL DB, usually 3306: ", str)
    }

class ServerSettings():
    '''
    ServerSettings which holds a dict loaded from a JSON file or user input.
    It also has the keys as attributes for their corressponding values.
    '''
    def __init__(self, json_settings_file="", new=False):
        '''
        Tries to use the supplied path to a json settings file to load settings for the server.
        If it encounters errors or no files, you may be prompted for input or the program may exit.\n
        Parameters:\n
        :json_settings_file (str): Full path to the settings json file.\n
        :new (bool): True or False depending if you want to create new settings or not.
        __init__(`self`, `json_settings_file`, `new`) -> ServerSettings
        '''
        root = tk.Tk()
        root.withdraw()
        if json_settings_file == "" or not os.path.exists(json_settings_file) or new:
            if new:
                print("Creating new ServerSettings...")
                self.settings = prompts()
                self.__setattrs__()
                self.__save_settings__()
            elif not os.path.exists(json_settings_file):
                print("Cannot find the server settings file!\n \
                \rFile may have been deleted or you do not have access to the file.\
                    \rPlease either stop the server or input the required data to start the application.")
                self.__load_settings__()
            if not hasattr(self, "settings"):
                print("No settings!\nPlease remember where your server settings file is located!")
                self.settings = prompts()
                self.__setattrs__()
                self.__save_settings__()
        elif os.path.exists(json_settings_file):
            with open(json_settings_file) as f:
                try:
                    self.settings = load(f)
                    self.__setattrs__()
                except JSONDecodeError as e:
                    print("Error Unable to decode JSON data!\n%s" + str(e))
                    exit(1)
                self.print_settings()

    def print_settings(self):
        '''
        Prints the settings in an ServerSettings instance. 
        Password will only be printed with '*' representing any type of character.
        '''
        print("Loading Server Settings...")
        print("{")
        for k, v in self.settings.items():
            if k == "password" or "pwd" in k:
                print("\t%s:\t" % k + "*"*len(v))
            else:
                print("\t%s:\t%s" % (k, v))
        print("}")

    def __setattrs__(self):
        '''
        Loop through `self.settings` and set them as attributes.
        If there is no `settings` attribute it will return {}.\n
        __setattrs__(`self`) -> dict{'str': 'str'}
        '''
        if hasattr(self, "settings"):
            for k, v in self.settings.items():
                self.__setattr__(k, v)
            return self.settings
        else:
            return {}

    def __save_settings__(self):
        '''
        Method for saving the contents of `self.settings` to a json file.
        And returns the filename of where the json file\n
        __save_settings__(`self`) -> str
        '''
        f = asksaveasfile(mode="w", filetypes=[('JSON', '*.json')], defaultextension=('JSON', '*.json'))
        if not f:
            print("File save cancelled!")
            return ""
        dump(self.settings, f, indent=2)
        return str(f.name)

    def __load_settings__(self):
        '''
        Method for loading a json file.
        Returns the loaded settings in a dict.\n
        __load_settings__(`self`) -> dict{'str': 'str'}
        '''
        f = askopenfilename()
        if not f:
            print("No File Loaded!\nRequesting User Input!")
            self.settings = prompts()
            a = self.__setattrs__()
            r = self.__save_settings__()
            return r
        else:
            with open(f, 'r') as reader:
                try:
                    self.settings = load(reader)
                    self.__setattrs__()
                except JSONDecodeError as e:
                    print("Unable to decode JSON data!")
                    self.settings = prompts()
                    self.__setattrs__()
                    self.__save_settings__()
                self.print_settings()
                reader.close()
            return self.settings