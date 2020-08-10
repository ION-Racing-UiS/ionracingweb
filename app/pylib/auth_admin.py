import ldap
from app.pylib.ad_settings import get_ad_settings
from flask_login import UserMixin
from pyad import *
import pythoncom

def get_ldap_connection():
    '''
    Initialize a ldap connection with ldap server.\n
    Arguments: None\n
    Returns a ldap connection.
    '''
    conn = ldap.initialize("ldap://" + get_ad_settings()["ldap_server"] + ":389")
    return conn

def is_web_admin(user):
    '''
    Checks if a user object from AD is part of the `web admin` group.\n
    Arguments:\n
    :param user: User object to check. <type:pyad.aduser.ADUser>
    '''
    if type(user) is not pyad.aduser.ADUser:
        return False
    g = adgroup.ADGroup.from_cn("web admin").get_members()
    for m in g:
        if user.guid_str == m.guid_str and user.dn == m.dn:
            return True
    return False

def is_admin(user):
    '''
    Checks if a user object from AD is part of the `Administrators` group.\n
    Arguments:\n
    :param user: User object to check. <type:pyad.aduser.ADUser>
    '''
    if type(user) is not pyad.aduser.ADUser:
        return False
    g = adgroup.ADGroup.from_cn("Administrators").get_members()
    for m in g:
        if user.guid_str == m.guid_str and user.dn == m.dn:
            return True
    return False


class Admin(UserMixin):
    '''
    Admin object, inheriting from flask_login.UserMixin to use as a admin object for `flask_login`.
    Methods:\n
    `__init__(self, username)`\n
    `get(id)`\n
    staticmethod(s):\n
    `try_login(username, password)`
    '''
    def __init__(self, username):
        '''
        Initialize an Admin to use for `flask_login`.
        Arguments:\n
        :param username: Username for the Admin object. <type:str>
        '''
        print("Searching ad for admin: " + str(username))
        if username is None or username=="" or not is_web_admin(username):
            return None
        self.u = aduser.ADUser.from_cn(username)
        self.guid = self.u.get_attribute('objectGUID')[0].tobytes().hex()
        self.username = self.u.get_attribute('cn')[0]
        self.is_web_admin = is_web_admin(self.u)
        self.is_admin = is_admin(self.u)

    def __repr__(self):
        '''
        Represent an admin with a string.\n
        To string / str method for representing an admin.
        '''
        return '<Admin %s>' % self.username

    def __str__(self):
        '''
        To string method for the Admin class.
        '''
        return "<Admin ADUser=%s, username=%s, guid=%s>" %(self.u, self.username, self.guid)

    @staticmethod
    def try_login(username, password):
        '''
        Attemps to authenticate the admin with the ldap/active directory server.\n
        Arguments:\n
        :param username: Username for the admin <type:str>\n
        :param password: Password for the admin <type:str>
        '''
        ad_settings = get_ad_settings()
        pyad.set_defaults(ldap_server=ad_settings['ldap_server'], username=ad_settings['username'], password=ad_settings['password'])
        u = aduser.ADUser.from_cn(username)
        if is_web_admin(u) or is_admin(u):
            dn = u.dn
            conn = get_ldap_connection()
            conn.simple_bind_s(
                dn,
                password
            )
        else:
            raise ldap.INVALID_CREDENTIALS("You do not have the required privileges required to access this area.")