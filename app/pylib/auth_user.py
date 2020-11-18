import ldap
import pythoncom
from app.pylib.ad_settings import get_ad_settings
from flask_login import UserMixin
from pyad import *

def get_ldap_connection():
    '''
    Initialize a ldap connection with ldap server.\n
    Arguments: None\n
    Returns a ldap connection.\n
    get_ldap_connection() -> LDAPObject
    '''
    conn = ldap.initialize("ldap://" + get_ad_settings()['ldap_server'] + ":389/")
    return conn

def is_web_admin(user):
    '''
    Checks if a user object from AD is part of the `web admin` group.\n
    Parameters:\n
    :user (pyad.aduser.ADUser): User object to check. <type:pyad.aduser.ADUser>\n
    is_web_admin(`user`) -> bool
    '''
    r = False
    if type(user) is not pyad.aduser.ADUser:
        r = False
    g = adgroup.ADGroup.from_cn("Web Admin").get_members()
    for m in g:
        if user.guid_str == m.guid_str and user.dn == m.dn:
            r = True
    domain_admins = adgroup.ADGroup.from_cn("Domain Admins").get_members(True)
    for m in domain_admins:
        if user.guid_str == m.guid_str and user.dn == m.dn:
            r = True
    return r

def is_admin(user):
    '''
    Checks if a user object from AD is part of the `Administrators` group.\n
    Parameters:\n
    :user (pyad.aduser.ADUser): User object to check.\n
    is_admin(`user`) -> bool
    '''
    r = False
    if type(user) is not pyad.aduser.ADUser:
        r = False
    g = adgroup.ADGroup.from_cn("Admins").get_members()
    for m in g:
        if user.guid_str == m.guid_str and user.dn == m.dn:
            r = True
    domain_admins = adgroup.ADGroup.from_cn("Domain Admins").get_members(True)
    for m in domain_admins:
        if user.guid_str == m.guid_str and user.dn == m.dn:
            r = True
    return r

def get_images(images=[]):
    '''
    Returns the portrait images of the user in a dict.\n
    Parameters:\n
    :images (list): List of strings from `get_attribute(\'wbemPath\', True)` from an ADUser object.\n
    get_images(`images`) -> dict{int: str}
    '''
    i = {}
    if len(images) == 0:
        return None
    for image in images:
        img = image.split(':')
        i[int(img[0])] = img[1]
    return i

class User(UserMixin):
    '''
    User object, inheriting from flask_login.UserMixin to use as a user object for `flask_login`.
    Methods:\n
    `__init__(self, username)` -> User\n
    `get_id(self)` -> str\n
    `get(id)` -> User\n
    staticsmethod(s):\n
    `try_login(username, password)` -> None || Error\n
    `try_admin_login(username, password)` -> None || Error
    '''
    def __init__(self, username):
        '''
        Initialize a User to use for `flask_login`.
        Paramerters:\n
        :username (str): Username for the User object.\n
        __init__(`self`, `username`) -> User
        '''
        print("Searching ad for user: " + str(username))
        if username is None or username=="":
            return None
        self.u = aduser.ADUser.from_cn(username)
        self.guid = self.u.get_attribute('objectGUID', False).tobytes().hex()
        self.username = self.u.get_attribute('cn', False)
        self.is_web_admin = is_web_admin(self.u)
        self.is_admin = is_admin(self.u)
        self.image = get_images(self.u.get_attribute('wbemPath', True))

    def __repr___(self):
        '''
        Represent a User with a string.\n
        To string / str method for representing a user.\n
        __repr__(`self`) -> str
        '''
        return '<User %s>' % self.username

    def __str__(self):
        '''
        To string method for the User class.\n
        __str__(`self`) -> str
        '''
        return "<User ADUser=%s, username=%s, guid=%s, is_web_admin=%s, is_admin=%s>" % (self.u, self.username, self.guid, self.is_web_admin, self.is_admin)
    
    @staticmethod
    def try_login(username, password):
        '''
        Attemps to authenticate the user with the ldap/active directory server.\n
        Parameters:\n
        :username (str): Username for the user\n
        :password (str): Password for the user\n
        try_login(`username`, `password`) -> None || Error
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
        '''
        Attempts to authenticate the user as an admin with the ldap/active directory server.\n
        Parameters:\n
        :username (str): Username for the user\n
        :password (str): Password for the user\n
        try_admin_login(`username`, `password`) -> None || Error
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
    
    def get_id(self):
        '''
        Return \'cn\' of a User.\n
        get_id(`self`) -> str
        '''
        return str(self.username)

    def get(id):
        '''
        Return a user by username\n
        Arguments:\n
        :id str: Username of the user
        get(`id`) -> User
        '''
        return User(username=id)