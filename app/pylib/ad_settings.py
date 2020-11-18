import datetime
from pathlib import Path
from pyad import adgroup, adcontainer
from app.pylib.settings import ServerSettings

s = ServerSettings()

ldap_server = s.ldap_server
username = s.username
password = s.password
topLevelDomain = s.topLevelDomain
homeDrive = s.homeDrive
profileDirectoryPrefix = s.profileDirectoryPrefix
homeDirectoryPrefix = s.homeDirectoryPrefix
scriptPath = s.scriptPath
physicalDeliveryOfficeName = s.physicalDeliveryOfficeName
company = s.company
userdomain = s.userdomain
base_ou = s.base_ou
usergroup = s.usergroup
domainsuffix = s.domainsuffix
path = s.path
user_groups = [usergroup, str((datetime.datetime.now() + datetime.timedelta(weeks=4*6)).year)]
user_groups_d = {1: usergroup, 2: str((datetime.datetime.now() + datetime.timedelta(weeks=4*6)).year)}

def get_ous():
    '''
    Queries ad for all departments int the `base_ou` and returns a list of tuples for use with FlaskForm.\n
    get_ous() -> tuple(str, str)
    '''
    p = adcontainer.ADContainer.from_cn(base_ou).get_children()
    ous = []
    for c in p:
        if type(c) is adcontainer.ADContainer:
            if c.cn.lower() == "it":
                ous.append((c.cn, c.cn.upper()))
            elif c.cn.lower() != "teams":
                ous.append((c.cn, c.cn[0].upper()+c.cn[1:].lower()))
    return ous

ous = get_ous()

def get_teams():
    '''
    Queries ad for all teams in `Teams` and returns a list of type:tuples for use with FlaskForm.\n
    get_teams() -> tuple(str, str)
    '''
    t = adcontainer.ADContainer.from_cn("Teams").get_children()
    teams = []
    for g in t:
        if type(g) is adgroup.ADGroup:
            teams.append((g.cn, g.cn[0].upper()+g.cn[1:].lower()))
    return teams

def get_groups():
    '''
    Queries ad for all groups in the base OU and returns a list of type:pyad.adgroup.ADGroup for use with group management.\n
    get_groups() -> list[pyad.adgroup.ADGroup]
    '''
    ou = adcontainer.ADContainer.from_cn(base_ou).get_children()
    g = []
    for c in ou:
        if type(c) is adgroup.ADGroup:
            g.append(c)
    return g

def get_ad_settings():
    return {
        'ldap_server': ldap_server,
        'username': username,
        'password': password,
        'topLevelDomain': topLevelDomain,
        'homeDrive': homeDrive,
        'profileDirectoryPrefix': profileDirectoryPrefix,
        'homeDirectoryPrefix': homeDirectoryPrefix,
        'scriptPath': scriptPath,
        'physicalDeliveryOfficeName': physicalDeliveryOfficeName,
        'company': company,
        'userdomain': userdomain,
		'usergroup': usergroup,
        'base_ou': base_ou,
        'domainsuffix': domainsuffix,
        'ous': ous,
        'path': path,
        'user_groups': user_groups,
        'user_groups_d': user_groups_d
    }

db_user = s.db_user
db_pwd = s.db_pwd
db_host = s.db_host
db_db = s.db_db
db_port = int(s.db_port) or 3306
