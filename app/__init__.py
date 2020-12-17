from flask import Flask, g 
from config import Config
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_ldap import LDAP, login_required
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from pyad import pyad, aduser, adobject, adgroup, addomain, adcontainer, adcomputer, adquery, adsearch
from app.pylib import win_user
import datetime
import sys
import os
global limiter


app = Flask(__name__)
Bootstrap(app=app)
app.config.from_object(Config)
app.config["head_menu"] = ["Home", "Sponsor", "User_reg", "Systems", "Terms", "Contact", "Login"]
app.config["LDAP_HOST"] = win_user.ldap_server
app.config["LDAP_DOMAIN"] = win_user.topLevelDomain + "." + win_user.domainsuffix
limiter = Limiter(app, key_func=get_remote_address, default_limits=["60 per minute", "5 per second"],)
csrf = CSRFProtect(app)
csrf.init_app(app)
ldap = LDAP(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
carimages = UploadSet('carimages', IMAGES, default_dest=lambda  x: 'SecretKey')
configure_uploads(app, carimages)
patch_request_class(app)

app.config["sponsors"] = {
        "main" : [
            {
                "id" : 0,
                "name" : "J.B Ugland Holding AS",
                "url" : "https://www.google.com/",
                "text" : """ J.B. Ugland Holding AS was established 18th of September 2000 and 
                    is the parent company of all the J.B. Ugland-companies. 
                    The company is located in Sørlandets Teknologipark in Grimstad (Norway) where Johan 
                    Benad Ugland is the owner and his son, Johan Martin Ugland, is the chief 
                    executive officer. Their vision is “Pride in developing”, an expression 
                    that promotes big ambitions and versatile engagement in the local community. 
                    Therefore, J.B. Ugland Holding AS wishes to contribute to development that creates 
                    long-lasting and sustainable changes. That’s whay the company ownes businesses within 
                    numerous business areas, such as construction, civil engineering, shipping, investments and renewable 
                    energy. In Addition, the company is also committed to the community and are engaged in several local initiatives that contributes 
                    to growth and wellbeing in their local community in Grimstad. The Ugland family and the JBU-companies continues a thousand year old tradition related to three main businesses. 
                    These businesses are related to farming, trading and shipping. The Storegra farm in Grimstad is therefore an important part of the family`s history and origins back to the 1200`s. 
                    Johan Benad Ugland took over the family farm in 1973 and has since then had a strong focus on locally resources and a good anchoring in the production chain. """,
                "image" : 'images/MECA_ALT.svg',
                "alt" : "MECA",
            },
            { 
                "id" : 1,
                "name" : "J.B Ugland Holding AS",
                "url" : "https://www.google.com/",
                "text" : """ J.B. Ugland Holding AS was established 18th of September 2000 and 
                    is the parent company of all the J.B. Ugland-companies. 
                    The company is located in Sørlandets Teknologipark in Grimstad (Norway) where Johan 
                    Benad Ugland is the owner and his son, Johan Martin Ugland, is the chief 
                    executive officer. Their vision is “Pride in developing”, an expression 
                    that promotes big ambitions and versatile engagement in the local community. 
                    Therefore, J.B. Ugland Holding AS wishes to contribute to development that creates 
                    long-lasting and sustainable changes. That’s whay the company ownes businesses within 
                    numerous business areas, such as construction, civil engineering, shipping, investments and renewable 
                    energy. In Addition, the company is also committed to the community and are engaged in several local initiatives that contributes 
                    to growth and wellbeing in their local community in Grimstad. The Ugland family and the JBU-companies continues a thousand year old tradition related to three main businesses. 
                    These businesses are related to farming, trading and shipping. The Storegra farm in Grimstad is therefore an important part of the family`s history and origins back to the 1200`s. 
                    Johan Benad Ugland took over the family farm in 1973 and has since then had a strong focus on locally resources and a good anchoring in the production chain. """,
                "image" : 'images/MECA_ALT.svg',
                "alt" : "MECA",
            },
        ],
        "platinum" : [
            {
                "id" : 0,
                "name" : "molstad modell&form",
                "url" : "https://www.molstad.no/",
                "text" : """ J.B. Ugland Holding AS was established 18th of September 2000 and is the parent company of all the J.B. Ugland-companies. The company is located in Sørlandets Teknologipark in Grimstad (Norway) where Johan Benad Ugland is the owner and his son, Johan Martin Ugland, is the chief executive officer. Their vision is “Pride in developing”, an expression that promotes big ambitions and versatile engagement in the 
                    local community. Therefore, J.B. Ugland Holding AS wishes to contribute 
                    to development that... """,
                "image" : 'images/Molstad.svg',
                "alt" : "Molstad",
            },
            {
                "id" : 1,
                "name" : "NITO",
                "url" : "https://www.nito.no/",
                "text" : """ J.B. Ugland Holding AS was established 18th of September 2000 and is the parent company of all the J.B. Ugland-companies. The company is located in Sørlandets Teknologipark in Grimstad (Norway) where Johan Benad Ugland is the owner and his son, Johan Martin Ugland, is the chief executive officer. Their vision is “Pride in developing”, an expression that promotes big ambitions and versatile engagement in the 
                    local community. Therefore, J.B. Ugland Holding AS wishes to contribute 
                    to development that... """,
                "image" : 'images/NITO.svg',
                "alt" : "Molstad",
            },
            {
                "id" : 2,
                "name" : "molstad modell&form",
                "url" : "https://www.molstad.no/",
                "text" : """ J.B. Ugland Holding AS was established 18th of September 2000 and is the parent company of all the J.B. Ugland-companies. The company is located in Sørlandets Teknologipark in Grimstad (Norway) where Johan Benad Ugland is the owner and his son, Johan Martin Ugland, is the chief executive officer. Their vision is “Pride in developing”, an expression that promotes big ambitions and versatile engagement in the 
                    local community. Therefore, J.B. Ugland Holding AS wishes to contribute 
                    to development that... """,
                "image" : 'images/Molstad.svg',
                "alt" : "Molstad",
            },
        ],
        "gold" : [
            {
                "id" : 0,
                "name" : "molstad modell&form",
                "url" : "https://www.molstad.no/",
                "text" : """ Lorem ipsum dolor sit, amet consectetur adipisicing elit. 
                             Culpa perspiciatis consectetur quae explicabo labore inventore a enim dolorum laborum """,
                "image" : 'images/Molstad.svg',
                "alt" : "Molstad",
            },
            {
                "id" : 1,
                "name" : "molstad modell&form",
                "url" : "https://www.molstad.no/",
                "text" : """ Lorem ipsum dolor sit, amet consectetur adipisicing elit. 
                             Culpa perspiciatis consectetur quae explicabo labore inventore a enim dolorum laborum """,
                "image" : 'images/Molstad.svg',
                "alt" : "Molstad",
            },
            {
                "id" : 2,
                "name" : "molstad modell&form",
                "url" : "https://www.molstad.no/",
                "text" : """ Lorem ipsum dolor sit, amet consectetur adipisicing elit. 
                             Culpa perspiciatis consectetur quae explicabo labore inventore a enim dolorum laborum """,
                "image" : 'images/Molstad.svg',
                "alt" : "Molstad",
            },
        ],
        "silver" : [
            {
                "id" : 0,
                "name": "Molstad",
                "url" : "",
                "text": "",
                "image": 'images/Molstad.svg',
                "alt": "Molstad",
            },
            {
                "id" : 1,
                "name": "Molstad",
                "url" : "",
                "text": "",
                "image": 'images/Molstad.svg',
                "alt": "Molstad",
            },
            {
                "id" : 2,
                "name": "Molstad",
                "image": 'images/Molstad.svg',
                "alt": "Molstad",
            },
        ],
        "bronze" : [
            {
                "id" : 0,
                "name": "Molstad",
                "url" : "",
                "text": "",
                "image": 'images/Molstad.svg',
                "alt": "Molstad",
            },
            {
                "id" : 1,
                "name": "Molstad",
                "url" : "",
                "text": "",
                "image": 'images/Molstad.svg',
                "alt": "Molstad",
            },
            {
                "id" : 2,
                "name": "Molstad",
                "url" : "",
                "text": "",
                "image": 'images/Molstad.svg',
                "alt": "Molstad",
            },
            
        ]
    }

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