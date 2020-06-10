import ldap
from app.pylib import win_user
from flask_wtf import Form
from flask_login import UserMixin
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired
from pyad import *
import pythoncom

def get_ldap_connection():
    '''
    Initialize a ldap connection with ldap server.\n
    Arguments: None\n
    Returns a ldap connection.
    '''
    conn = ldap.initialize("ldap://" + win_user.ldap_server + ":389/")
    return conn

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
        return "<User ADUser=%s, username=%s, guid=%s>" %(self.u, self.username, self.guid)
    
    @staticmethod
    def try_login(username, password):
        '''
        Attemps to authenticate the user with the ldap/active directory server.\n
        Arguments:\n
        :param username: Username for the user <type:str>\n
        :param password: Password for the user <type:str>
        '''
        pyad.set_defaults(ldap_server=win_user.ldap_server, username=win_user.username, password=win_user.password)
        dn = aduser.ADUser.from_cn(username).dn
        conn = get_ldap_connection()
        conn.simple_bind_s(
            dn,
            password
        )
    
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