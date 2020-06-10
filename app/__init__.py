from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_ldap import LDAP, login_required
from flask_login import LoginManager
from pyad import pyad, aduser, adobject, adgroup, addomain, adcontainer, adcomputer, adquery, adsearch
from app.pylib import win_user
import datetime
import sys
import os
global limiter


app = Flask(__name__)
Bootstrap(app=app)
app.config.from_object(Config)
app.config["head_menu"] = ["Home", "User_reg", "Systems", "Terms", "Contact", "Login"]
app.config["LDAP_HOST"] = win_user.ldap_server
app.config["LDAP_DOMAIN"] = win_user.topLevelDomain + "." + win_user.domainsuffix
limiter = Limiter(app, key_func=get_remote_address, default_limits=["60 per minute", "5 per second"],)
csrf = CSRFProtect(app)
csrf.init_app(app)
ldap = LDAP(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

today = datetime.date.today()
month = ""
day = ""
year = str(today.year)[-2:]
if len(str(today.month)) < 2:
    month = "0" + str(today.month)
else:
    month = str(today.month)
if len(str(today.day)) < 2:
    day = "0" + str(today.day)
else:
    day = str(today.day)
if app.config["ENABLE_LOG"]:
    log_name = "u_ex" + year + month + day+".txt"
    filename = str(os.path.abspath(os.getcwd())) + "\\app\\logs\\" + log_name
    try:
        sys.stdout = open(filename, 'a')
    except:
        sys.stdout = open(filename, 'w+')

cur_time = datetime.datetime.now()
cur_time_formatted = str(cur_time.hour) + ":" + str(cur_time.minute) + ":" + str(cur_time.second) # Using hh:mm:ss time format
cur_date_formatted = str(day) + "." + str(month) + "." + str(year) # Using dd.MM.yyyy date format
print(str("Date: " + cur_date_formatted) + "\tTime: " + str(cur_time_formatted) + "\tStarting flask server")




from app import routes