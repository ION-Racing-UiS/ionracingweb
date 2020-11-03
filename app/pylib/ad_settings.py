import datetime
from pathlib import Path
from pyad import adgroup, adcontainer

ldap_server = "ION-S1.DEV.IONRACING.NO"
username = "Administrator"
password = "1998"
topLevelDomain = "DEV.IONRACING.NO"
homeDrive = "H:"
profileDirectoryPrefix = "\\\\ION-S1\\$profiles\\"
homeDirectoryPrefix = "\\\\ION-S1\\$home\\"
scriptPath = ""
physicalDeliveryOfficeName = "KE D-121"
company = "ION Racing UiS"
userdomain = "DEV"
base_ou = "IONRacing"
usergroup = "ION Users"
domainsuffix = "IONRACING.NO"
path = (str(Path(__file__).absolute()))
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

db_user = "ionracing"
db_pwd = "1998"
db_host = "k122-189.ux.uis.no"
db_db = "ionracing"
db_port = 3306
