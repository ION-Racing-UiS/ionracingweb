import pywin32_system32
import win32api
from pyad import pyad, aduser, adobject, adgroup, addomain, adcontainer, adcomputer, adquery, adsearch
from app.pylib.ad_settings import get_ad_settings
import os
import re
from pathlib import Path
import datetime
import json

ad_settings = get_ad_settings()

ldap_server = ad_settings["ldap_server"] # Fully qualified domain name of the ldap server
username = ad_settings["username"] # Account operations account
password = ad_settings["password"] # Password for the account above
topLevelDomain = ad_settings["topLevelDomain"] # Top level domain name
homeDrive = ad_settings["homeDrive"] # User home drive letter
profileDirectoryPrefix = ad_settings["profileDirectoryPrefix"] # UNC Share path for profiles
homeDirectoryPrefix = ad_settings["homeDirectoryPrefix"] # Suffix to access the profile directory from homeDrive
scriptPath = ad_settings["scriptPath"] # path to script in \\<servername>\sysvol\<topLevelDomain>\scripts
physicalDeliveryOfficeName = ad_settings["physicalDeliveryOfficeName"] # Office name
company = ad_settings["company"] # Official Company name
userdomain = ad_settings["userdomain"] # Just your domain name, ie. google, not google.com
base_ou = ad_settings["base_ou"]
usergroup = ad_settings["usergroup"]
domainsuffix = ad_settings["domainsuffix"] # What top level domain you have, ie. .com, .net, .eu, dk, .no, .se
ous = ad_settings["ous"] # Organizational units list for the wtf form <type:list> of <type:tuple> or <type:str> and <type:str>
path = ad_settings["path"] # Absolute path to this file within the filesystem.
user_groups = ad_settings["user_groups"] # Group name for users so that they can be local admins
user_groups_d = ad_settings["user_groups_d"] # Dict of groups names for users, works better than the list

def create_user_settings(user_input):
    '''
    Returns a dict with the correct user settings for the domain\n
    Arguments:\n
    :param user_input: dict with the user data for user registration <type:dict>\n
    :keys    \"fname\", \"lname\", \"email\", \"passw\", \"department\", \"role\": <types:str>\n
    :values first name, last name, email, password, department, role <types:str>
    '''
    vdate = datetime.datetime.now() + datetime.timedelta(weeks=4*6) # Add half a year to create a new team group
    try:
        ou = adcontainer.ADContainer.from_cn("Teams")
        u_group = adgroup.ADGroup.create(str(vdate.year), ou, True, "GLOBAL")
        user_groups.append(u_group)
    except:
        u_group = adgroup.ADGroup.from_cn(str(vdate.year))
        user_groups.append(u_group)
        
    fname = user_input["fname"]
    lname = user_input["lname"]
    email = user_input["email"]
    passw = user_input["passw"]
    dept = user_input["department"]
    role = user_input["role"]
    if dept.lower() == 'it':
        dept = "IT"
    else:
        dept = dept[0].upper() + dept[1:].lower()
    sAMAccountName = get_username(fname, lname)
    userPrincipalName = get_userPrincipalName(sAMAccountName)
    year = u_group.get_attribute("cn", False)
    return {
        'company': company,
        'department': json.dumps({year: dept}),
        'description': json.dumps({year: role}),
        'displayName': get_name(fname, lname),
        'givenName': capitalize(fname),
        'homeDirectory': str(homeDirectoryPrefix + sAMAccountName),
        'homeDrive': homeDrive,
        'mail': email,
        'physicalDeliveryOfficeName': physicalDeliveryOfficeName,
        'profilePath': str(profileDirectoryPrefix + sAMAccountName),
        'sn': lname,
        'scriptPath': scriptPath,
        'userPrincipalName': userPrincipalName,
        'sAMAccountName': sAMAccountName,
        'title': json.dumps({year: role}),
        'c': user_input["c"],
        'st': user_input["st"],
        'postalCode': user_input["postalCode"],
        'l': user_input["l"],
        'streetAddress': user_input["streetAddress"]
    } # 'cn' and 'name' keys have been removed as they cause exceptions when being updated.

def create_user(user_settings, password): # Deprecated function
    '''
    Create a Windows Active Directory user with data supplied from a dict and password, q is the adquery object.\n
    Arguments:\n
    :param user_settings: User settings created by create_user_setting(user_data) <type:dict>\n
    :param password: Password for the user to be registerd <type:str>
    '''
    ou_arg = str("OU=" + user_settings["department"] + ",DC=" + userdomain + ",DC=" + domainsuffix)
    dept = user_settings["department"].upper()
    '''q = adquery.ADQuery()
    q.execute_query(
        attributes=["distinguishedName", "ou", "cn"], 
        where_clause="ou = '{}'".format(dept),
        base_dn=""
        )
    ou_arg = q.get_single_result().get("distinguishedName")'''
    pyad.set_defaults(ldap_server=ldap_server, username=username, password=password)
    ou = adcontainer.ADContainer.from_dn(ou_arg)
    name = user_settings["sAMAccountName"]
    user = aduser.ADUser.create(
        name,
        ou,
        password,
        user_settings
    )
    user.set_user_account_control_setting("DONT_EXPIRE_PASSWD", True)
    return user

def update_attributes(sAMAccountName, user_settings, password=None):
    '''
    Sets password for a user password if given.
    Set/update attributes of a selected user <sAMAccountName>, 
    given a dict of ldap attributes with values.
    Returns a list of the set attributes\n
    Arguments:\n
    :param aAMAccountName: Username as in sAMAccountName <type:str>\n
    :param user_settings: Dict of the usersettings <type:dict(str:str)>\n
    :param password: Password to set for the user <type:str>
    '''
    try:
        if (sAMAccountName is None or type(sAMAccountName) is not str) and (user_settings is None or type(user_settings) is not dict):
            return ["No or incorrect sAMAccountName and user_settings given: sAMAccountName: " + str(sAMAccountName) + ", user_settings: " + str(user_settings)]
        elif sAMAccountName is None or type(sAMAccountName) is not str:
            return ["No or incorrect sAMAccountName given, got: "  + str(sAMAccountName)]
        elif user_settings is None or type(user_settings) is not dict:
            return ["No or incorrect user_settings given, got: " + str(user_settings)]
    except:
        return str(["An error occoured when trying to check input"])
    #print("Input arguments are of valid types")
    user = aduser.ADUser.from_cn(str(sAMAccountName))
    if type(password) is str and password is not None:
        user.set_password(password)
        #pyad.set_defaults(ldap_server=ldap_server, username=sAMAccountName, password=password)
    user.set_user_account_control_setting("DONT_EXPIRE_PASSWD", True)
    for key in user_settings.keys():
        #print(str(key))
        user.update_attribute(str(key), str(user_settings[key]))
    set_attributes = []
    for key in user_settings.keys():
        set_attributes.append(str(str(key) + ": " + str(user.get_attribute(str(key)))))
    #pyad.set_defaults(ldap_server=ldap_server, username=username, password=password)
    return set_attributes

def join_group(sAMAccountName, group_cn=user_groups_d):
    '''
    Joins user <sAMAccountName> to a given <group_cn> and returns what groups 
    the user belongs to.\n
    Arguments:\n
    :param sAMAccountName: Username as is sAMAccountName <type:str>\n
    :param group_cn: Common Name of the group you want the user added to <type:str>
    '''
    try:
        if (sAMAccountName is None or type(sAMAccountName) is not str) and (group_cn is None or type(group_cn) is not dict):
            return ["No or incorrect sAMAccountName and group_cn given: sAMAccountName: " + str(sAMAccountName) + ", group_cn: " + str(group_cn)]
        elif sAMAccountName is None or type(sAMAccountName) is not str:
            return ["No or incorrect sAMAccountName given, got: "  + str(sAMAccountName)]
    except:
        return str(["An error occoured when trying to check input"])
    #print("Input arguments are of valid types")
    user_groups = []
    user = aduser.ADUser.from_cn(sAMAccountName)
    if type(group_cn) == (type(None) or  None):
        for g in sorted(user.get_attribute('memberOf')):
            user_groups.append(str(adgroup.ADGroup.from_dn(str(g)).cn))
        return user_groups
    if type(group_cn) is list:
        #user = aduser.ADUser.from_cn(sAMAccountName)
        for i in range(len(group_cn)):
            g = adgroup.ADGroup.from_cn(str(group_cn[i]))
            user.add_to_group(g)
    elif type(group_cn) is dict:
        for v in group_cn.values():
            g = adgroup.ADGroup.from_cn(str(v))
            try:
                user.add_to_group(g)
            except:
                g.add_members([user])
    else:
        group = adgroup.ADGroup.from_cn(group_cn)
        group.add_members([user])
    for group in sorted(user.get_attribute('memberOf')):
        user_groups.append(str(adgroup.ADGroup.from_dn(str(group)).cn))
    return user_groups
    
def get_username(first_name, last_name):
    '''
    Get username for a user based on first and last name\n
    get_username(\"Neil\", \"Peart\")
    returns n.peart\n
    Arguments:\n
    :param first_name: first name of the user <type:str>\n
    :param last_name:  last name of the user  <type:str>
    '''
    return str(first_name.replace(" ", ".").lower() + "." + last_name.replace(" ", ".").lower())

def get_userPrincipalName(username, topLevelDomain=topLevelDomain):
    '''
    Get userPrincipalName for a user based on username and domain.
    get_userPrincipalName(\"g.lee\", \"rush.com\") 
    returns g.lee@rush.com\n
    Arguments:\n
    :param username: username of the user <type:str>\n
    :param topLevelDomain:   domain of the user   <type:str>
    '''
    return str(username + "@" + topLevelDomain)

def capitalize(string):
    '''
    Capitalize first letter of any input string.\n
    capitalize(\"alex\") returns \"Alex\"
    capitalize(\"Alex\") returns \"Alex\"\n
    Arguments:\n
    :param string: string to capitalize <type:str>
    '''
    return str(string[0].upper() + string[1:])

def get_name(first_name, last_name):
    '''
    Assemble and capitalize first and last names into a full name/common name.\n
    get_name(\"geddy\", \"lee\") returns \"Geddy Lee\"
    Arguments:\n
    :param first_name: first name <type:str>
    :param last_name:  last name  <type:str>
    '''
    return str(capitalize(first_name) + " " + capitalize(last_name))

def get_last_index_of(string, charachter=" "):
    '''
    Returns the last index of a specific charachter by looping backwards through a string.\n
    Arguments:\n
    :param string: string that you want to find the index in <type:str>\n
    :param charachter: the charachter you you want to find the last index of <type:chr|str>
    '''
    for i in range(len(string)-1, 0, -1):
        if string[i] == " ":
            return i
    else:
        return None

def split_name(name, index):
    '''
    Returns a tupple of two strings by splitting the string at a given index.
    I.e split_name(\"Alex Lifeson\", 4) will return (\"Alex\", \"Lifeson\")\n
    Arguments:\n
    :param name: Name or string to split at the given index <type:str>\n
    :param index: Index of where to split <name> at <type:int>
    '''
    return name[:index], name[index + 1:]

def loop_addomain(adomain="DC=" + userdomain + ",DC=" + domainsuffix):
    '''
    Gets the domain from the Domain Controller to get its children and runs 'loop_domain_children()'\n
    Arguments:\n
    :param adomain: DistinguishedName of the domain <type:str>
    '''
    try: 
        domain = addomain.ADDomain.from_dn(adomain)
    except:
        return "Unable to get domain from Domain Controller."
    domain_children = domain.get_children()
    return loop_domain_children(domain_children)

def loop_domain_children(domain_children):
    '''
    Uses recursion to loop through children of the domain object.\n
    Arguments:\n
    :param domain_children: Collection of domain_children in the from of a list <type:List>[<type:adobjects>]
    '''
    users = []
    for child in domain_children:
        if type(child) is pyad.adcontainer.ADContainer:
            loop = loop_domain_children(child.get_children())
            #print(type(loop))
            if type(loop) is not type(None) and type(loop) is list:
                for l in loop:
                    users.append(l)
        elif type(child) is pyad.aduser.ADUser:
            users.append(child.name)
    if len(users) > 0:
        return users

def level_list(l):
    '''
    Loop trough a list with possible nested list and return a single level list.\n
    Arguments:\n
    :param l: list with possible nested lists inside <type:list>
    '''
    e = []
    for i in l:
        if type(i) is list:
            entries = level_list(i)
            for entry in entries:
                e.append(entry)
        elif type(i) is str:
            e.append(i)
    
def name_check(name):
    '''
    Check name of a new user with current users and objects in AD\n
    Arguments:\n
    :param name: Name of new user <type:str>
    '''
    usernames = loop_addomain()
    g = adgroup.ADGroup.from_cn(usergroup).get_members()
    for user in g:
        if user.get_attribute("cn", False).lower() == name.lower():
            return False
    #print(str(usernames))
    if name in usernames:
        return False
    else:
        return True
    

if __name__=="__main__":
    if len(os.sys.argv) == 6:
        pyad.set_defaults(ldap_server=ldap_server, username=username, password=password)
        user_data = {
            'name': os.sys.argv[1],
            'passw': os.sys.argv[2],
            'department': os.sys.argv[3],
            'role': os.sys.argv[4],
            'email': os.sys.argv[5]
        }
        #print(user_data['name'])
        user_data['fname'], user_data['lname'] = split_name(user_data['name'], get_last_index_of(user_data['name'], charachter=" "))
        user_settings = create_user_settings(user_data)
        sAMAccountName = get_username(user_data['fname'], user_data['lname'])
        ou = adcontainer.ADContainer.from_dn(str("OU=" + user_data["department"].upper() + ", DC=" + userdomain.upper() + ", DC=" + domainsuffix.upper()))
        #print(str(ou))
        user = aduser.ADUser.create(sAMAccountName, ou, user_data["passw"])
        user = aduser.ADUser.from_cn(sAMAccountName)
        group = adgroup.ADGroup.from_cn(user_groups)
        group.add_members([user])
        #print(str(user))
        user.set_user_account_control_setting("DONT_EXPIRE_PASSWD", True)
        for key in user_settings.keys():
            #print(str(key))
            user.update_attribute(str(key), str(user_settings[key]))
        #print(str(user_data))
        #print(str(user_settings))
    elif len(os.sys.argv) == 3:
        # Simpler version to create a user account with only 2 arguments (Username and department)
        pyad.set_defaults(ldap_server=ldap_server, username=username, password=None)
        name = os.sys.argv[1]
        fname, lname = split_name(name, get_last_index_of(name, charachter=" "))
        sAMAccountName = get_username(fname, lname)
        department = os.sys.argv[2]
        ou = adcontainer.ADContainer.from_dn(str("OU=" + department.upper() + ",DC=" + userdomain.upper() + ",DC=" + domainsuffix.upper()))
        #print(str(ou))
        user = aduser.ADUser.create(sAMAccountName, ou, None)
        #print(str(user))
        group = adgroup.ADGroup.from_cn(user_groups)
        group.add_members([user])
    elif len(os.sys.argv) == 2:
        res = name_check(os.sys.argv[-1])
        print("Username: %s is available %b" % (os.sys.argv[-1], res))
    else:
        print("Usage: win_user.py \"First_name Last_name\" \"Password\" \"Department\" \"Role\" \"Mail\"\nOr: win_user.py \"First_name Last_name\" \"Department\"")