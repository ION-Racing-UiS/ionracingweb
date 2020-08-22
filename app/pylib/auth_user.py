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
    conn = ldap.initialize("ldap://" + get_ad_settings()['ldap_server'] + ":389/")
    return conn

def is_web_admin(user):
    '''
    Checks if a user object from AD is part of the `web admin` group.\n
    Arguments:\n
    :param user: User object to check. <type:pyad.aduser.ADUser>
    '''
    if type(user) is not pyad.aduser.ADUser:
        return False
    g = adgroup.ADGroup.from_cn("Web Admin").get_members()
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
    g = adgroup.ADGroup.from_cn("Admins").get_members()
    for m in g:
        if user.guid_str == m.guid_str and user.dn == m.dn:
            return True
    return False

class User(UserMixin):
    '''
    User object, inheriting from flask_login.UserMixin to use as a user object for `flask_login`.
    Methods:\n
    `__init__(self, username)`\n
    `get_id(self)`\n
    `get(id)`\n
    staticsmethod(s):\n
    `try_login(username, password)`
    '''
    def __init__(self, username):
        '''
        Initialize a User to use for `flask_login`.
        Arguments:\n
        :param username: Username for the User object. <type:str>
        '''
        print("Searching ad for user: " + str(username))
        if username is None or username=="":
            return None
        self.u = aduser.ADUser.from_cn(username)
        self.guid = self.u.get_attribute('objectGUID')[0].tobytes().hex()
        self.username = self.u.get_attribute('cn')[0]
        self.is_web_admin = is_web_admin(self.u)
        self.is_admin = is_admin(self.u)

    def __repr___(self):
        '''
        Represent a User with a string.\n
        To string / str method for representing a user.
        '''
        return '<User %s>' % self.username

    def __str__(self):
        '''
        To string method for the User class.
        '''
        return "<User ADUser=%s, username=%s, guid=%s, is_web_admin=%s, is_admin=%s>" % (self.u, self.username, self.guid, self.is_web_admin, self.is_admin)
    
    @staticmethod
    def try_login(username, password):
        '''
        Attemps to authenticate the user with the ldap/active directory server.\n
        Arguments:\n
        :param username: Username for the user <type:str>\n
        :param password: Password for the user <type:str>
        '''
        ad_settings = get_ad_settings()
        pyad.set_defaults(ldap_server=ad_settings['ldap_server'], username=ad_settings['username'], password=ad_settings['password'])
        dn = aduser.ADUser.from_cn(username).dn
        conn = get_ldap_connection()
        conn.simple_bind_s(
            dn,
            password
        )

    @staticmethod
    def try_admin_login(username, password):
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
    
    def get_id(self):
        '''
        Return \'cn\' of a User.
        '''
        return str(self.username)

    def get(id):
        '''
        Return a user by username\n
        Arguments:\n
        :param id: Username of the user <type:str>
        '''
        return User(username=id)