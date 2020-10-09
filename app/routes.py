from flask import render_template, flash, redirect, url_for, request, g, session, abort, Response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import app, limiter, login_manager
from app.forms import RegisterForm, LoginForm, UserEdit, UserOldPwd, UserChangePwd, AdminAddCar, AdminEditCar, AdminRemoveCar, AdminTeamAdd, AdminTeamRemove, AdminUser, AdminCreateUser, AdminPostCreate, AdminPostEdit, AdminPostDelete
from datetime import datetime
from app.pylib import win_user, StringTools
from app.pylib.ad_settings import get_ous, get_teams, get_ad_settings
from app.pylib.auth_user import User
from app.pylib.StringTools import getTableFields, getSingleResult, getMultipleResults, decodeJSONAndSplit
from app.pylib.FileOperations import delete_file
from pyad import pyad, adcontainer, aduser, adgroup, adobject
from flask_ldap import ldap
import os
import time
import pythoncom
import pywin32_system32
import re
import json
import mysql.connector
import shutil

def get_remote_info(request=request):
    '''
    Returns information about a remote host in a dict.\n
    Keys: \"ip\", \"method\", \"url\"\n
    Parameters:\n
    :request (flask.request): Request object from Flask\n
    get_remote_info(`request`) -> dict{\'ip\': str, \'method\': str, \'url\': url}
    '''
    if request.headers.getlist("X-Forwarded-For"): # Try to get ip if a proxy is used
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else: # Else try to get remote ip address
        if len(request.access_route) > 1:
            ip = request.access_route[-1]
        else:
            ip = request.access_route[0]
    method = request.method # Get request method
    url = request.url # Get the requested url
    return {"ip": ip, "method": method, "url": url}

def get_remote_addr(request=request):
    '''
    Returns the layer 3 address of a remote host.\n
    Parameters:\n
    :request (flask.request): Request object from Flask.\n
    get_remote_addr(`request`) -> str(ip)
    '''
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        if len(request.access_route) > 1:
            ip = request.access_route[-1]
        else:
            ip = request.access_route[0]
    return ip

def get_date_time():
    '''
    Return the current date and time in the format:\n
    [dd/mmm/yyyy hh:MM:SS]\n
    get_date_time() -> str(dd/mmm/yyy hh:MM:SS)
    '''
    int_to_str = {
        1: "JAN",
        2: "FEB",
        3: "MAR",
        4: "APR",
        5: "MAY",
        6: "JUN",
        7: "JUL",
        8: "AUG",
        9: "SEP",
        10: "OCT",
        11: "NOV",
        12: "DEC"
    }
    now = datetime.now()
    date_dict = {
    "day": str(now.day),
    "month": str(int_to_str[now.month]),
    "year": str(now.year),
    "hour": str(now.hour),
    "minu": str(now.minute),
    "sec": str(now.second)
    }
    for k in date_dict.keys():
        val = date_dict[k]
        if len(val) < 2:
            date_dict[k] = "0" + date_dict[k]
    return "[" + str(date_dict["day"]) + "/" + str(date_dict["month"]) + "/" + str(date_dict["year"]) + " " + str(date_dict["hour"]) + ":" + str(date_dict["minu"]) + ":" + str(date_dict["sec"]) + "]"

def build_log(data=None):
    '''
    Returns a logstring with data from a route that is appended to `app\\__logs__\\filename.txt`\n
    Parameters:\n
    :data (str): String of data from a route to be used in the log message.\n
    build_log(`data`) -> str(log_msg)
    '''
    remote_info = get_remote_info(request)
    req_time = get_date_time()
    res = remote_info["ip"] + " - - " + req_time + " " + remote_info["method"] + " " + remote_info["url"] + " "
    return res + str(data)

def route_log():
    '''
    Creates a log string and prints it to stdout and returns the log message.\n
    route_log() -> str(log_msg)
    '''
    remote_info = get_remote_info(request)
    req_time = get_date_time()
    res = remote_info["ip"] + " - - " + req_time + " " + remote_info["method"] + " " + remote_info["url"] + " Requested"
    print(res)
    return res

def get_db():
    '''
    Get database connects to the database and returns the connection.\n
    get_db() -> MySQLConnection
    '''
    if not hasattr(g, "_database"):
        g._database = mysql.connector.connect(
            host=app.config["DB_HOST"], user=app.config["DB_USER"],
            password=app.config["DB_PWD"], database=app.config["DB_DB"], port=app.config["DB_PORT"]
        )
    return g._database

@app.teardown_appcontext
def teardown_db(error):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def admin_check(current_user=current_user):
    '''
    Checks if the current user is either an admin or web_admin. Meant to be used on routes that require admin privileges.
    Unauthorized useres are redirected to `login`.\n
    Parameters:\n
    :current_user (app.pylib.auth_user.User): `current_user` of the session.\n
    admin_check(`current_user`) -> bool
    '''
    if not current_user.is_web_admin or not current_user.is_admin:
        flash("You are not authorized to access this page", 'warning')
        return True
    user_agent = request.user_agent
    if 'mobile' in str(user_agent).lower():
        flash("Admin interface is not available on mobile devices. Sorry you're SOL.", 'info')
        return True

def get_countries():
    '''
    Returns a list of tuples for use with wtforms SelectField.\n
    get_countries() -> tuple(str, str)
    '''
    db = get_db()
    cur = db.cursor()
    q = "SELECT * FROM c"
    cur.execute(q)
    l = []
    for c in cur.fetchall():
        l.append((c[0], c[-1]))
    return l

@login_manager.user_loader
def load_user(id):
    pythoncom.CoInitialize()
    return User(id)
@app.before_request
def get_current_user():
    g.user = current_user

@app.route("/")
def landing():
    route_log()
    return render_template("landing.html")

@app.route("/r/", methods=["POST"])
def r():
    route_log()
    time.sleep(3.2)
    return url_for("home")

#@app.route("/")
@app.route("/home/", methods=["GET", "POST"])
def home():
    route_log()
    db = get_db()
    cursor = db.cursor()
    q = "SELECT year, name, number, img, engine, torque, mass FROM car"
    cursor.execute(q)
    cars = {}
    for car in cursor.fetchall():
        cars[int(car[0])] = {
            'name': str(car[1]),
            'number': int(car[2]),
            'img': str(car[3]),
            'engine': str(car[4]),
            'speed': int(car[5]),
            'weight': int(car[6]),
            'year': int(car[0])
        }
    posts = {
        0 : {
            "author" : "Jens Hansen",
            "title" : "Live: Canadian Virtual",
            "date" : "24-06-2020",
            "time" : "21:16",
            "heading" : " It’s time for the Grand Finale of the F1 Virtual Grand Prix Series. This Sunday the race takes \
                            place on the Montreal track layout with our own Pierre Gasly teamed up with Simon Neil of Biffy Clyro! ",
            "text" : "  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
                        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure  \
                        dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
                        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "bgimg" : "bcimg1.jpg",
            "img" : "img1.jpg",

        },
        1 : {
            "author" : "Ola Nordman",
            "title" : "Thanks to our Virtual “Wild Cards”",
            "date" : "01-06-2020",
            "time" : "18:16",
            "heading" : " The chequered flag has been waved to end the F1 Virtual Grand Prix Series. \
                            After keeping millions of race fans entertained  \
                            during this long period when the sound of race engines was silenced, now it’s time to look back at it all. ",

            "text" : "  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
                        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure  \
                        dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
                        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "bgimg" : "bcimg2.png",
            "img" : "img1.jpg",

        },
        2 : {
            "author" : "Ali Reza",
            "title" : "2020 F1 latest news",
            "date" : "24-01-2020",
            "time" : "11:16",
            "heading" : " It’s time for the Grand Finale of the F1 Virtual Grand Prix Series. This Sunday the race takes \
                            place on the Montreal track layout with our own Pierre Gasly teamed up with Simon Neil of Biffy Clyro! ",

            "text" :"  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
                        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure  \
                        dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
                        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "bgimg" : "bcimg3.jpg",
            "img" : "img1.jpg",

        },
        3 : {
            "author" : "Ali Baba",
            "title" : "2015 F1 latest news",
            "date" : "24-01-2020",
            "time" : "11:16",
            "heading" : " It’s time for the Grand Finale of the F1 Virtual Grand Prix Series. This Sunday the race takes \
                            place on the Montreal track layout with our own Pierre Gasly teamed up with Simon Neil of Biffy Clyro! ",

            "text" :"  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
                        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure  \
                        dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
                        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "bgimg" : "bcimg4.jpg",
            "img" : "img1.jpg",

        },
        4 : {
            "author" : "Ola Nordman",
            "title" : "Thanks to our Virtual “Wild Cards”",
            "date" : "01-06-2020",
            "time" : "18:16",
            "heading" : " The chequered flag has been waved to end the F1 Virtual Grand Prix Series. \
                            After keeping millions of race fans entertained  \
                            during this long period when the sound of race engines was silenced, now it’s time to look back at it all. ",

            "text" : "  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
                        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure  \
                        dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
                        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "bgimg" : "bcimg5.jpg",
            "img" : "img1.jpg",

        }
    }
    return render_template("home.html", active=0, head_menu=app.config["head_menu"], cars=cars, posts=posts)

@app.route("/user_reg/")
@app.route("/user_reg/register", methods=["POST"])
def user_reg():
    route_log()
    '''
    Route for user register page.
    '''
    '''Regular expressions to allow all latin characthers and remove two or more sequential spaces.'''
    text_regexp = app.config["TEXT_REGEXP"]
    space_regexp = app.config["SPACE_REGEXP"]
    pythoncom.CoInitialize()
    form = RegisterForm(get_ous(), get_countries())
    pythoncom.CoUninitialize()
    if form.is_submitted() and form.validate() and form.submit.data:
        pythoncom.CoInitialize()
        fname = re.sub(space_regexp, "", re.sub(text_regexp, "", form.givenName.data))
        lname = re.sub(space_regexp, "", re.sub(text_regexp, "", form.sn.data))
        if len(fname) == 0 or len(lname) == 0:
            msg = "Invalid input data in first or last name."
            pythoncom.CoUninitialize()
            data = "Failed user registration due to wrong input data in either fname or lname."
            res = build_log(data)
            print(res)
            return render_template("regRes.html", active=1, head_menu=app.config["head_menu"], title="Unsuccessful", msg=msg)
        while fname[-1] == " ": # Remove trailing spaces at the end
            fname = fname[0:-1]
        while lname[-1] == " ": # Remove trailing spaces at the end
            lname = lname[0:-1]
        user_data={
        "department": form.ou.data,
        "role": form.description.data,
        "fname": fname,
        "lname": lname,
        "email": form.mail.data,
        "passw": form.password.data,
        "c": form.c.data,
        "st": form.st.data,
        "postalCode": form.postalCode.data,
        "l": form.l.data,
        "streetAddress": form.streetAddress.data,
        }
        user_settings = win_user.create_user_settings(user_data)
        if not win_user.name_check(user_settings["sAMAccountName"]):
            msg = "Your username: " + user_settings["sAMAccountName"]  + " already exists in the Active Directory database. Please contact a system administrator."
            pythoncom.CoUninitialize()
            data = "User registration failed, username: " + user_settings["sAMAccountName"] + " alread in active directory!"
            res = build_log(data)
            print(res) # Print to log file
            return render_template("regRes.html", active=1, head_menu=app.config["head_menu"], title="Unsuccessful", msg=msg)
        #os.system("python \"" + win_user.path + "\" \"" + user_data["fname"] + " " + user_data["lname"] + "\" \"" + user_data['passw'] + "\" \"" + user_data['department'] + "\" \"" + user_data['role'] + "\" \"" + user_data['email'] + "\"")
        #os.system("python \"" + win_user.path + "\" \"" + user_data["fname"] + " " + user_data["lname"] + "\" \"" + user_data["department"] + "\"")
        #win_user.create_user(user_settings, user_data["passw"])
        try:
            ou = adcontainer.ADContainer.from_cn(user_data["department"].upper())
        except:
            msg = "An error occoured when getting the organizational unit from the Domain Controller."
            res = build_log(msg + " Make sure that OUs have the cn attributes set.")
            print(res) # Print to log file
            pythoncom.CoUninitialize()            
            return render_template("regRes.html", active=1, head_menu=app.config["head_menu"], title="Unsuccessful", msg=msg)
        try:
            user = aduser.ADUser.create(user_settings["sAMAccountName"], ou, user_data["passw"])
            time.sleep(1.5)
            #user = aduser.ADUser.from_cn(user_settings["sAMAccountName"])
            print("New User:\t" + str(aduser.ADUser.from_cn(user_settings['sAMAccountName'])))
        except:
            #print("Unable to get user from AD, user non existent.")
            try:
                user.delete()
            except UnboundLocalError as e:
                pass
            msg = "An error occoured when creating the user account " + user_settings["sAMAccountName"] + ". If the problem persists, don't include your middle name. Max length is 20 characters including periods. If your username is within the limits, then your password do not meet the password policy."
            res = build_log("An error occured when creating the user account: " + user_settings["sAMAccountName"])
            print(res)
            pythoncom.CoUninitialize()
            return render_template("regRes.html", active=1, head_menu=app.config["head_menu"], title="Unsuccessful", msg=msg)
        win_user.update_attributes(user_settings['sAMAccountName'], user_settings, user_data['passw'])
        win_user.join_group(user_settings['sAMAccountName'])
        pythoncom.CoUninitialize()
        res = build_log("New User created: " + user_settings["sAMAccountName"] + " created successfully.")
        print(res)
        msg = user_data["fname"] + ", your user account: " + user_settings["sAMAccountName"] + " should be created. If not please contact the system administrator."
        return render_template("regRes.html", active=1, head_menu=app.config["head_menu"], title="Succes", msg=msg)
    else:
        return render_template("user_reg.html", active=1, head_menu=app.config["head_menu"], form=form)

@app.route("/systems")
def systems():
    route_log()
    return render_template("no.html", active=2, head_menu=app.config["head_menu"])

@app.route("/terms")
def terms():
    route_log()
    return render_template("no.html", active=3, head_menu=app.config["head_menu"])

@app.route("/contact")
def contact():
    route_log()
    return render_template("contact.html", active=4, head_menu=app.config["head_menu"], url=request.url)

@app.route("/contact/<hostname>")
def contacthost(hostname):
    route_log()
    content = render_template("comp_issue.html", hostname=hostname)
    return render_template("contact.html", active=4, head_menu=app.config["head_menu"], host=content)

@app.route("/contact/<form_type>", methods=["POST"])
def form_type(form_type):
    route_log()
    url = StringTools.removeBetween(request.url+str("/"), StringTools.secondLastIndexOf(request.url+str("/"), "/"), StringTools.lastIndexOf(request.url+str("/"), "/"))
    return render_template(form_type + ".html", url=url)

@app.route("/login", methods=["GET", "POST"])
def login():
    route_log()
    # print("Current_user: " + str(current_user))
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for("appuser_home"))
    form = LoginForm()
    pythoncom.CoInitialize()
    if request.method == "POST" and form.validate() and form.is_submitted():
        username = form.username.data
        password = form.password.data
        try: # Try to authenticate the user and handle exceptions if they occour
            res = build_log("Trying login for: " + username)
            print(res)
            User.try_login(username, password)
        except ldap.INVALID_CREDENTIALS as e: # Invalid username or password
            flash("Invalid username or password", "danger")
            res = build_log("Invalid user credentials for: " + username)
            print(res)
            print(str(e))
            return render_template("login.html", active=5, head_menu=app.config["head_menu"], form=form)
        except ldap.INVALID_DN_SYNTAX or ldap.INVALID_SYNTAX: # Syntax error
            flash("Invalid syntax for login", "danger")
            res = build_log("Invalid syntax for login, user: " + username)
            print(res)
            return render_template("login.html", active=5, head_menu=app.config["head_menu"], form=form)
        except pyad.invalidResults: # Unable to get the user from ldap_server
            flash("Invalid username or password", "danger")
            res = build_log("Invalid syntax for login, user: " + username)
            return render_template("login.html", active=5, head_menu=app.config["head_menu"], form=form)
        except ldap.SERVER_DOWN: # Unable to contact dc
            flash("The Domain Controller could not be contacted at this time, please try again later.")
            res = build_log("Domain Controller could no be contacted!")
            return render_template("login.html", active=5, head_menu=app.config["head_menu"], form=form)
        user = User(username)
        #print("User: " + str(user))
        login_user(user)
        #print("Current_user: " + str(current_user) + ", is_auth: " + str(current_user.is_authenticated))
        flash("You have been logged in.", 'success')
        res = build_log("Successful login for: " + username)
        print(res)
        return redirect(url_for("appuser_home"))
    if form.errors:
        flash(form.errors, 'danger')
        res = build_log("Form error.")
        print(res)
    return render_template("login.html", active=5, head_menu=app.config["head_menu"], form=form)

@app.route("/logout")
@login_required
def logout():
    route_log()
    if current_user.is_authenticated:
        flash("You are now logged out.", 'success')
    if current_user.is_admin or current_user.is_web_admin:
        logout_user()
        return redirect(url_for("admin"))
    logout_user()
    return redirect(url_for("login"))

@app.route("/appuser_home")
@login_required
def appuser_home():
    route_log()
    res = build_log("/appuser_home/ current_user: " + str(current_user) + ", is_auth? " + str(current_user.is_authenticated))
    return render_template("appuser_home.html", user=current_user)

@app.route("/gohome")
@login_required
def gohome():
    route_log()
    if current_user.is_authenticated:
        flash("You are now logged out.", 'success')
    logout_user()
    return redirect(url_for("home"))

@app.route("/appuser_edit", methods=["POST", "GET"])
@login_required
def appuser_edit():
    route_log()
    pythoncom.CoInitialize()
    adu = current_user.u
    #form = UserEdit(adu.givenName, adu.sn, adu.displayName, adu.description, adu.mail)
    form = UserEdit()
    if request.method == "POST" and form.validate() and form.is_submitted():
        givenName = form.givenName.data
        sn = form.sn.data
        displayName = form.displayName.data
        description = form.description.data
        mail = form.mail.data
        if givenName is not None and len(givenName) > 0:
            adu.update_attribute('givenName', givenName)
        if sn is not None and len(sn) > 0:
            adu.update_attribute('sn', sn)
        if displayName is not None and len(displayName) > 0:
            adu.update_attribute('displayName', displayName)
        if description is not None and len(description) > 0:
            adu.update_attribute('description', description)
        if mail is not None and len(mail) > 0:
            adu.update_attribute('mail', mail)
        return redirect(url_for("appuser_home"))
    form.givenName.data = adu.givenName
    form.sn.data = adu.sn
    form.displayName.data = adu.displayName
    form.description.data = adu.description
    form.mail.data = adu.mail
    return render_template("appuser_edit.html", user=current_user, form=form)

@app.route("/appuser_password", methods=["POST", "GET"])
@login_required
def appuser_password():
    route_log()
    #pythoncom.CoInitialize()
    adu = current_user.u
    old_form = UserOldPwd()
    new_form = UserChangePwd()
    '''try: 
        print("Change_Pwd_Stage: " + str(session["change_pwd_stage"]))
    except:
        print("Change_Pwd_stage: " + str(0))'''
    if request.method == "GET":
        session["change_pwd_stage"] = 0
        old_form.username.data = adu.cn
        return render_template("appuser_password.html", form=old_form, user=session["change_pwd_stage"])
    elif request.method == "POST":
        if new_form.is_submitted() and new_form.validate():
            password = new_form.password.data
            confirm_password = new_form.confirm_password.data
            if password == confirm_password:
                u = aduser.ADUser.from_cn(adu.cn)
                u.set_password(password)
                session["change_pwd_stage"] = 0
                flash("Your password has been changed!", "success")
                return redirect(url_for('appuser_home'))
            else:
                flash("The passwords does not match, please try again.", "error")
                return redirect(url_for('appuser_password'))
        elif old_form.is_submitted() and old_form.validate():
            username = old_form.username.data
            password = old_form.password.data
            try: 
                User.try_login(adu.cn, password)
            except ldap.INVALID_CREDENTIALS: # Invalid username or password
                flash("Invalid username or password: INVALID_CREDENTIALS", "danger")
                res = build_log("Invalid user credentials for: " + adu.cn)
                print(res)
                return redirect(url_for('appuser_password'))
            except ldap.INVALID_DN_SYNTAX or ldap.INVALID_SYNTAX: # Syntax error
                flash("Invalid syntax for login", "danger")
                res = build_log("Invalid syntax for login, user: " + adu.cn)
                print(res)
                return redirect(url_for('appuser_password'))
            except pyad.invalidResults: # Unable to get the user from ldap_server
                flash("Invalid username or password: invalidResults", "danger")
                res = build_log("Invalid syntax for login, user: " + adu.cn)
                return redirect(url_for('appuser_password'))
            except ldap.SERVER_DOWN: # Unable to contact dc
                flash("The Domain Controller could not be contacted at this time, please try again later.")
                res = build_log("Domain Controller could no be contacted!")
                return redirect(url_for('appuser_password'))
            session["change_pwd_stage"] = 1
            new_form.username.data = adu.cn
            return render_template("appuser_password.html", form=new_form, user=session["change_pwd_stage"])

@app.route("/appuser_reportedit")            
@login_required
def appuser_reportedit():
    route_log()
    return render_template("appuser_reportedit.html")

@app.route("/appuser_reportonchange", methods=["POST"])
def appuser_reportonchange():
    # print(data)
    return "Change Detected!"

@app.route("/admin", methods=["GET", "POST"])
def admin():
    route_log()
    #print("Current_user: " + str(current_user))
    if current_user.is_authenticated and (current_user.is_web_admin or current_user.is_admin):
        flash("You are already logged in.")
        return redirect(url_for("admin_home"))
    form = LoginForm()
    pythoncom.CoInitialize()
    if request.method == "POST" and form.validate() and form.is_submitted():
        username = form.username.data
        password = form.password.data
        try:
            res = build_log("Trying admin login for: " + username)
            print(res)
            User.try_admin_login(username, password)
        except ldap.INVALID_CREDENTIALS as e:
            flash("Invalid username or password", "danger")
            res = build_log("Invalid user credential for: " + username)
            print(res)
            return render_template("admin_login.html", head_menu=app.config["head_menu"], form=form)
        except ldap.INVALID_DN_SYNTAX or ldap.INVALID_SYNTAX:
            flash("Invalid syntax for login", "danger")
            res = build_log("Invalid syntax for login, user: ", "danger")
            print(res)
            return render_template("")
        except pyad.invalidResults:
            flash("Invalid username or password", "danger")
            res = build_log("Invalid username or password for user: " + username)
            return render_template("admin_login.html", head_menu=app.config["head_menu"], form=form)
        except ldap.SERVER_DOWN:
            flash("The Domain Controller could not be contacted at this time, please try again later.")
            res = build_log("Domain Controller could no be contacted!")
            return render_template("admin_login.html", head_menu=app.config["head_menu"], form=form)
        admin = User(username)
        login_user(admin)
        flash("You have been logged in.", "success")
        res = build_log("Successful login for: " + username)
        print(res)
        return redirect(url_for("admin_home"))
    if form.errors:
        flash(str(form.errors), 'danger')
        res = build_log("Form error: " + str(form.errors))
        print(res)
    return render_template("admin_login.html", head_menu=app.config["head_menu"], form=form)

@app.route("/admin_home")
@login_required
def admin_home():
    route_log()
    if admin_check(current_user):
        return redirect(url_for('login'))
    print("Current user: is_web_admin=%s, is_admin=%s" % (current_user.is_web_admin, current_user.is_admin))
    return render_template("admin_layout.html", user=current_user)

@app.route("/admin_car")
@login_required
def admin_car():
    route_log()
    if admin_check(current_user):
        return redirect(url_for('appuser_home'))
    db = get_db()
    cursor = db.cursor()
    cars = {}
    try:
        q = "SELECT * FROM car ORDER BY `year` ASC"
        cursor.execute(q)
        for (id, year, name, number, img, mass, engine, output, torque) in cursor.fetchall():
            cars[int(id)] = {
                'id': str(id),
                'year': int(year),
                'name': str(name),
                'number': str(number),
                'img': str(img),
                'mass': str(mass),
                'engine': str(engine),
                'output': str(output),
                'torque': str(torque)
            }
    except ValueError as e:
        flash("An error occurred when casting values from the database, please inform the dev team about the issue: " + str(e), 'error')
        return render_template("admin_layout.html", user=current_user)
    return render_template("admin_car.html", user=current_user, cars=cars)

@app.route("/admin_car/add", methods=["GET", "POST"])
@login_required
def admin_car_add():
    route_log()
    if admin_check(current_user):
        return redirect(url_for('appuser_home'))
    form = AdminAddCar()
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data:
        db = get_db()
        cursor = db.cursor()
        try:
            data = {
                'year': int(form.year.data),
                'name': str(form.name.data),
                'number': int(form.number.data),
                'mass': float(form.mass.data),
                'engine': str(form.engine.data),
                'output': str(form.output.data),
                'torque': float(form.torque.data)
            }
        except ValueError as e:
            flash("An error was encountered when parsing the data:\t" + str(e))
            res = build_log("ValueError when parsing data:\t" + str(e))
            print(res)
            return render_template("admin_car_add.html", user=current_user)
        if form.img.data:
            sec_filename = secure_filename(form.img.data.filename)
            data['img'] = str(app.config["CAR_IMG_PATH"] + sec_filename)
            path = os.path.join(app.config["CAR_IMAGES"], sec_filename)
            form.img.data.save(path)
            q = "INSERT INTO car (`year`, `name`, `number`, `img`, `mass`, `engine`, `output`, `torque`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute("START TRANSACTION")
            cursor.execute(q,  (data['year'], data['name'], data['number'], data['img'], data['mass'], data['engine'], data['output'], data['torque']))
            cursor.execute("COMMIT")
        else:
            q = "INSERT INTO car (`year`, `name`, `number`, `mass`, `engine`, `output`, `torque`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute("START TRANSACTION")
            cursor.execute(q,  (data['year'], data['name'], data['number'], data['mass'], data['engine'], data['output'], data['torque']))
            cursor.execute("COMMIT")
        flash("Car for the year: " + str(data['year']) + " named: " + data['name'] + " has been successfully added!", 'success')
        res = build_log("Car for the year: " + str(data['year']) + " named: "  + data['name'] + " has been added by: " + current_user.username)
        return redirect(url_for("admin_car"))
    return render_template("admin_car_add.html", user=current_user, form=form)

@app.route("/admin_car/<int:id>", methods=["GET", "POST"])
@login_required
def admin_car_i(id):
    if admin_check(current_user):
        return redirect(url_for('appuser_home'))
    form = AdminEditCar()
    try:
        i = int(id)
    except ValueError as e:
        flash("Error while parsing argument id as an integer:\t" + str(e))
        res = build_log("Error while parsing argument id as integer:\t" + str(e))
        print(res)
        return redirect(url_for("admin_car"))
    db = get_db()
    cursor = db.cursor()
    q = "SELECT * FROM car WHERE id=%s"
    cursor.execute(q, (i,))
    car = cursor.fetchone()
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data and (str(form.cid.data)==str(i)):
        try:
            data = {
                'id': int(form.cid.data),
                'year': int(form.year.data),
                'name': str(form.name.data),
                'number': str(form.number.data),
                'mass': float(form.mass.data),
                'engine': str(form.engine.data),
                'output': str(form.output.data),
                'torque': float(form.torque.data)
            }
        except ValueError as e:
            flash("An error was encountered when parsing the data:\t" + str(e))
            res = build_log("ValueError when parsing data:\t" + str(e))
            print(res)
        if form.img.data:
            if form.img.data.filename == car[4]:
                return redirect(url_for('admin_car'))
            sec_filename = secure_filename(form.img.data.filename)
            data['img'] = str(app.config["CAR_IMG_PATH"] + sec_filename)
            path = os.path.join(app.config["CAR_IMAGES"], sec_filename)
            if car[4]:
                old_img = os.path.join(app.config["CAR_IMAGES"], StringTools.getFileName(car[4]).replace("/", "\\"))
                try:
                    os.remove(old_img)
                except FileNotFoundError as e:
                    flash("Unable to delete the imgage file for the car: %s, file: %s does not exist" % (str(i), StringTools.getFileName(car[4].replace("/", "\\"))))
                    res = build_log("Unable to delete the imgage file for the car: %s, file: %s does not exist" % (str(i), StringTools.getFileName(car[4].replace("/", "\\"))))
                    print(res)
            form.img.data.save(path)
            q = "UPDATE car SET year=%s, name=%s, number=%s, img=%s, mass=%s, engine=%s, output=%s, torque=%s WHERE id=%s"
            cursor.execute("START TRANSACTION")
            cursor.execute(q, (data['year'], data['name'], data['number'], data['img'], data['mass'], data['engine'], data['output'], data['torque'], data['id']))
            cursor.execute("COMMIT")
        else:
            q = "UPDATE car SET year=%s, name=%s, number=%s, mass=%s, engine=%s, output=%s, torque=%s WHERE id=%s"
            cursor.execute("START TRANSACTION")
            cursor.execute(q, (data['year'], data['name'], data['number'], data['mass'], data['engine'], data['output'], data['torque'], data['id']))
            cursor.execute("COMMIT")
            res = build_log("Car updated! ID: " + str(data['id']) + " Year: " + str(data['year']) + " by: " + current_user.username)
            print(res)
            flash("Car ID: " + str(data['id']) + " year: " + str(data['year']) + " has successfully been updated!", 'success')
        return redirect(url_for("admin_car"))
    #print(str(car))
    form.cid.data = car[0]
    form.year.data = int(car[1])
    form.name.data = str(car[2])
    form.number.data = int(car[3])
    if str(car[4]) and len(str(car[4])) > 0:
        img = str(car[4])
    #form.img.data.filename = str(car[4])
    form.mass.data = float(car[5])
    form.engine.data = str(car[6])
    form.output.data = str(car[7])
    form.torque.data = float(car[8])
    return render_template("admin_car_edit.html", user=current_user, form=form, img=img)

@app.route("/admin_car/remove", methods=["GET", "POST"])
@login_required
def admin_car_remove():
    if admin_check(current_user):
        return redirect(url_for('appuser_home'))
    form = AdminRemoveCar()
    db = get_db()
    cursor = db.cursor()
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data:
        car_ids = form.cars.data
        if car_ids[-1] == ",":
            car_ids = car_ids[0:-1].split(',')
        for car_id in car_ids:
            q = "SELECT img, year FROM car WHERE id=%s"
            cursor.execute(q, (car_id,))
            img = cursor.fetchone()
            #print("q = " + str(q % car_id) + "; img: " + str(img))
            img = img[0]
            if img:
                img = StringTools.getFileName(img).replace("/", "\\")
                img = os.path.join(app.config["CAR_IMAGES"], img)
                try:
                    os.remove(img)
                except FileNotFoundError as e:
                    flash("Unable to delete the imgage file for the car: %s, file: %s does not exist" % (str(car_id), StringTools.getFileName(img.replace("/", "\\"))))
                    res = build_log("Unable to delete the imgage file for the car: %s, file: %s does not exist" % (str(car_id), StringTools.getFileName(img.replace("/", "\\"))))
                    print(res)
            cursor.execute("START TRANSACTION")
            q = "DELETE FROM car WHERE id=%s"
            cursor.execute(q, (car_id,))
            cursor.execute("SELECT @`id`:=MAX(`id`)+1 FROM car")
            auto_inc = cursor.fetchone()[0]
            cursor.execute("ALTER TABLE car AUTO_INCREMENT = %s", (auto_inc,))
            cursor.execute("COMMIT")
        return redirect(url_for("admin_car"))
    q = "SELECT id, year, name, number, img FROM car"
    cursor.execute(q)
    cars = {}
    for car in cursor.fetchall():
        cars[int(car[1])] = {
            'id': car[0],
            'year': car[1],
            'name': car[2],
            'number': car[3],
            'img': car[4]
        }
    return render_template("admin_car_remove.html", form=form, user=current_user, cars=cars)

@app.route("/admin_team")
@login_required
def admin_team():
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    teams_g = adcontainer.ADContainer.from_cn("Teams").get_children()
    teams = []
    for t in teams_g:
        teams.append(t.cn)
    return render_template("admin_team.html", user=current_user, teams=sorted(teams))

@app.route("/admin_team/<int:i>", methods=["POST"])
@login_required
def admin_team_i(i):
    team = []
    for m in adgroup.ADGroup.from_cn(str(i)).get_members():
        team.append(User(m.get_attribute('cn', False)))
    return render_template("admin_team_i.html", team=team, year=i)

@app.route("/admin_team/add", methods=["GET", "POST"])
@login_required
def admin_team_add():
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    form = AdminTeamAdd()
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data:
        team = str(form.year.data)
        g = adgroup.ADGroup.create(team, adcontainer.ADContainer.from_cn("Teams"), True, "GLOBAL", optional_attributes={'cn': team})
        basedir = app.config["MEMBER_IMAGES"]
        if not os.path.exists(os.path.join(basedir, str(team))):
            os.makedirs(os.path.join(basedir, str(team)))
        msg = "Team: %s added by %s" % (team, current_user.u.cn)
        flash(msg)
        res = build_log(msg)
        print(res)
        return redirect(url_for("admin_team"))
    teams_g = adcontainer.ADContainer.from_cn("Teams").get_children()
    teams = []
    for t in teams_g:
        teams.append(t.cn)
    return render_template("admin_team_add.html", user=current_user, teams=teams, form=form)

@app.route("/admin_team/delete", methods=["GET", "POST"])
@login_required
def admin_team_remove():
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    form = AdminTeamRemove()
    form.team.choices = get_teams()
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data:
        team = str(form.team.data)
        g = adgroup.ADGroup.from_cn(team)
        members = g.get_members()
        for m in members:
            attr = m.get_attribute("wbemPath", True)
            img = ""
            for a in attr:
                if a.split(':')[0] == str(team):
                    img = a
            m.remove_from_attribute("wbemPath", img)
            keys = ["department", "description", "title"]
            for k in keys:
                a = json.loads(m.get_attribute(k, False))
                a.pop(str(team))
                m.update_attribute(k, json.dumps(a))
        basedir = app.config["MEMBER_IMAGES"]
        if os.path.exists(os.path.join(basedir, team)):
            shutil.rmtree(os.path.join(basedir, team))
        g.delete()
        msg = "Team: %s deleted by %s" % (team, current_user.u.cn)
        flash(msg)
        res = build_log(msg)
        print(res)
        return redirect(url_for("admin_team"))
    teams_g = adcontainer.ADContainer.from_cn("Teams").get_children()
    teams = []
    for t in teams_g:
        teams.append(t.cn)
    return render_template("admin_team_remove.html", user=current_user, teams=teams, form=form)

@app.route("/query/<attrib>/<who>", methods=["POST"])
@login_required
def query(attrib, who="all"):
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    pythoncom.CoInitialize()
    result = {}
    i = 0
    ion_users = adgroup.ADGroup.from_cn(get_ad_settings()["usergroup"]).get_members()
    if who.lower() == "all":
        for u in ion_users:
            result[i] = u.get_attribute(str(attrib), False, 'LDAP')
            i = i + 1
    else:
        for u in ion_users:
            if who.lower() == str(u.parent_container.get_attribute('cn', False, 'LDAP')).lower():
                result[i] = u.get_attribute(str(attrib), False, 'LDAP')
                i = i + 1
    pythoncom.CoUninitialize()
    return result

@app.route("/group/<action>/<to_from>/<whom>", methods=["POST"])
@login_required
def group_whom(action, to_from, whom):
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    pythoncom.CoInitialize()
    try:
        g = adgroup.ADGroup.from_cn(str(to_from))
    except pyad.invalidResults as e:
        return str(e)
    try:
        u = aduser.ADUser.from_cn(str(whom))
    except pyad.invalidResults as e:
        return str(e)
    if action.lower() == "add":
        g.add_members([u])
    elif action.lower() == "remove":
        g.remove_members([u])
        attr = u.get_attribute("wbemPath", True)
        basedir = app.config["MEMBER_IMAGES"]
        for a in attr:
            if a.split(':')[0] == str(to_from):
                u.remove_from_attribute("wbemPath", a)
                filename = StringTools.getFileName(a)
                try:
                    os.remove(os.path.join(basedir, str(to_from), filename))
                except FileNotFoundError as e:
                    pass
        keys = ["department", "description", "title"]
        for k in keys:
            a = json.loads(user.get_attribute(k, False))
            a.pop(str(to_from))
            user.update_attribute(k, json.dumps(a))
    return str(u.get_attribute('cn', False, 'LDAP'))

@app.route("/group/<action>/<to_from>", methods=["POST"])
@login_required
def group(action, to_from):
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    pythoncom.CoInitialize()
    try:
        g = adgroup.ADGroup.from_cn(str(to_from))
    except pyad.invalidResults as e:
        return str(e)
    data = request.data.decode("utf-8", "strict").replace("%2C", ",")
    usernames = data.split("=")[-1].split(",")
    u = []
    for username in usernames:
        u.append(aduser.ADUser.from_cn(username))
        user = aduser.ADUser.from_cn(username)
        attr = user.get_attribute("wbemPath", True)
        if action.lower() == "remove":
            for a in attr:
                if a.split(':')[0] == str(to_from):
                    user.remove_from_attribute("wbemPath", a)
            keys = ["department", "description", "title"]
            for k in keys:
                a = json.loads(user.get_attribute(k, False))
                a.pop(str(to_from))
                user.update_attribute(k, json.dumps(a))
    if action.lower() == "remove":
        g.remove_members(u)
        return str(u)
    else:
        return ""

@app.route("/admin_user")
@login_required
def admin_user():
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    ionracing = adcontainer.ADContainer.from_cn(get_ad_settings()["base_ou"]).get_children()
    departments = []
    for c in ionracing:
        if type(c) is adcontainer.ADContainer and c.cn.lower() != "teams":
            departments.append(c)
    return render_template("admin_user.html", user=current_user, departments=departments)

@app.route("/admin_user/<department>")
@login_required
def admin_user_department(department):
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    ionracing = adcontainer.ADContainer.from_cn(get_ad_settings()["base_ou"]).get_children()
    departments = []
    for c in ionracing:
        if type(c) is adcontainer.ADContainer and c.cn.lower() != "teams":
            departments.append(c)
    dept = adcontainer.ADContainer.from_cn(str(department))
    members = dept.get_children(filter_=[aduser.ADUser])
    return render_template("admin_user_department.html", user=current_user, department=dept, members=members, departments=departments)

@app.route("/admin_user/user/<username>", methods=["GET", "POST"])
@login_required
def admin_user_username(username):
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    ion_users = adgroup.ADGroup.from_cn(get_ad_settings()["usergroup"]).get_members()
    pythoncom.CoInitialize()
    user = None
    for u in ion_users:
        if u.get_attribute('cn', False).split('.') == username.split('.'):
            username = u.get_attribute('distinguishedName', False)
            user = aduser.ADUser.from_dn(str(username))
    if user is None:
        flash("There is no user by the username: " + str(username))
        return redirect(url_for("admin_user"))
    teams = []
    choises = []
    country = user.get_attribute("c", False)
    for team in sorted(user.get_attribute("memberOf", True)):
        t = adgroup.ADGroup.from_dn(str(team))
        if t.get_attribute("cn", False).isnumeric():
            teams.append(t.get_attribute("cn", False))
            choises.append((t.get_attribute("cn", False), t.get_attribute("cn", False)))
    form = AdminUser(teams=choises, country=country)
    #print(choises)
    if request.method == "POST" and form.is_submitted() and form.validate() and form["submit"].data:
        basedir = app.config["MEMBER_IMAGES"]
        directory = app.config["MEMBER_IMG_PATH"]
        try:
            data = {
                'displayName': str(form.displayName.data),
                'givenName': str(form.givenName.data),
                'sn': str(form.sn.data)
            }
            year_select = str(form.year_select.data)
            other_data = {
                'department': str(form.department.data),
                'description': str(form.description.data),
                'title': str(form.title.data)
            }
        except ValueError as e:
            flash("There was an error during parsing of the data: " + str(e))
            return redirect(url_for("admin_user"))
        user.update_attributes(data)
        for k, v in other_data.items():
            d = json.loads(user.get_attribute(k, False))
            d[year_select] = v
            user.update_attribute(k, json.dumps(d))
        if form.wbemPath.data:
            imgPaths = user.get_attribute("wbemPath", True)
            for imgP in imgPaths:
                if imgP.split(':')[0] == str(year_select):
                    img = StringTools.getFileName(imgP.split(':')[-1])
                    try:
                        os.remove(os.path.join(basedir, year_select, img))
                    except FileNotFoundError as e:
                        flash("Unable to locate the image to delete.")
                    finally:
                        user.remove_from_attribute("wbemPath", imgP)
            filename = user.get_attribute("cn", False) + StringTools.getFileExt(form.wbemPath.data.filename)
            path = os.path.join(basedir, year_select, filename)
            form.wbemPath.data.save(path)
            user.append_to_attribute("wbemPath", year_select + ":" + directory + year_select + "/" + filename)
            msg = "User: %s has been updated by: %s" % (user.get_attribute("cn", False), current_user.username)
            flash(msg, 'info')
            res = build_log(msg)
            print(res)
            return redirect(url_for("admin_user"))
    for field in form:
        if field.id.lower() == "year_select":
            #field.choices = choises
            pass
        elif field.id in ["department", "description", "title", "wbemPath", "imgPath"]:
            if field.id not in ["wbemPath", "imgPath"]:
                data = json.loads(user.get_attribute(field.id, False))
                try:
                    field.data = data[str(teams[0])]
                except KeyError as e:
                    field.data = ""
                except IndexError as e:
                    field.data = ""
            else:
                if field.id == "imgPath":
                    for p in user.get_attribute("wbemPath", True):
                        if p.split(':')[0] == str(teams[0]):
                            imgPath = p.split(':')[-1]
                            field.data = imgPath
        elif field.id in ["confirm", "submit", "csrf_token"]:
            pass
        else:
            field.data = user.get_attribute(field.id, False)
    return render_template("admin_user_username.html", user=current_user, edit_user=user, form=form, teams=teams)

@app.route("/admin_user/add", methods=["GET", "POST"])
@login_required
def admin_user_add():
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    text_regexp = app.config["TEXT_REGEXP"]
    space_regexp = app.config["SPACE_REGEXP"]
    pythoncom.CoInitialize()
    form = AdminCreateUser(get_ous(), get_countries())
    pythoncom.CoUninitialize()
    if form.is_submitted() and form.validate() and form.submit.data:
        pythoncom.CoInitialize()
        fname = re.sub(space_regexp, "", re.sub(text_regexp, "", form.givenName.data))
        lname = re.sub(space_regexp, "", re.sub(text_regexp, "", form.sn.data))
        if len(fname) == 0 or len(lname) == 0:
            pythoncom.CoUninitialize()
            msg = "Failed user registration due to wrong input data in either fname or lname."
            res = build_log(msg)
            print(res)
            flash(msg)
            return render_template("admin_user_create.html", user=current_user, form=form)
        while fname[-1] == " ":
            fname = fname[0:-1]
        while lname[-1] == " ":
            lname = lname[0:-1]
        user_data = {
            "department": form.ou.data,
            "role": form.description.data,
            "fname": fname,
            "lname": lname,
            "email": form.mail.data,
            "passw": None,
            "c": form.c.data,
            "st": form.st.data,
            "postalCode": form.postalCode.data,
            "l": form.l.data,
            "streetAddress": form.streetAddress.data
        }
        user_settings = win_user.create_user_settings(user_data)
        if not win_user.name_check(user_settings["sAMAccountName"]):
            pythoncom.CoUninitialize()
            msg = "User registration failed, username: %s allready exists in the Active Directory database!" % (user_settings["sAMAccountName"])
            res = build_log(msg)
            print(res)
            flash(msg)
            return render_template("admin_user_create.html", user=current_user, form=form)
        try:
            ou = adcontainer.ADContainer.from_cn(user_data["department"].upper())
        except:
            msg = "An error occoured when getting the organizational unit from the Domain Controller."
            res = build_log(msg + " Make sure that OUs have the cn attributes set.")
            print(res) # Print to log file
            pythoncom.CoUninitialize()
            return render_template("admin_user_create.html", user=current_user, form=form)
        try:
            user = aduser.ADUser.create(user_settings["sAMAccountName"], ou, None)
            user.set_user_account_control_setting("ACCOUNTDISABLE", True)
            time.sleep(0.25)
            print("New User:\t%s" % str(aduser.ADUser.from_cn(user_settings["sAMAccountName"])))
        except:
            try:
                user.delete()
            except UnboundLocalError as e:
                pass
            msg = "An error occoured when creating the account %s. If the problem presists, don't include your middle name. Max length is 20 charaters including preiods. If your username is within the limits, the your password do not meet the password policy." % user_settings["sAMAccountName"]
            res = build_log(msg)
            print(res)
            pythoncom.CoUninitialize()
            flash(msg)
            return render_template("admin_user_create.html", user=current_user, form=form)
        win_user.update_attributes(user_settings["sAMAccountName"], user_settings, None)
        win_user.join_group(user_settings["sAMAccountName"])
        pythoncom.CoUninitialize()
        res = build_log("New User created successfully: %s." % user_settings["sAMAccountName"])
        print(res)
        msg = "%s, created successfully by %s" % (user_settings["sAMAccountName"], current_user.username)
        flash(msg)
        return redirect("/admin_user/user/%s" % user_settings["sAMAccountName"])
    return render_template("admin_user_create.html", user=current_user, form=form)

@app.route("/admin_user/remove", methods=["GET", "POST"])
@login_required
def admin_user_remove():
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    departments = []
    for cn, _ in get_ous():
        departments.append(adgroup.ADGroup.from_cn(cn))
    g = adgroup.ADGroup.from_cn(get_ad_settings()["usergroup"]).get_members()
    if request.method == "POST":
        usernames = decodeJSONAndSplit(request.data, ",")
        for username in usernames:
            print("Username=%s" % username)
            user = aduser.ADUser.from_cn(username)
            image_paths = user.get_attribute("wbemPath", True)
            base_dir = app.config["MEMBER_IMAGES"]
            for image_path in image_paths:
                del_file = delete_file(image_path.split(":")[-1], image_path.split(":")[0], base_dir)
            user.delete()
        msg = "User(s) %s have been deleted from ad by %s." % (usernames, current_user.username)
        flash(msg, "info")
        res = build_log(msg)
        print(res)
        return res
    return render_template("admin_user_delete.html", user=current_user, departments=departments, users=g)

@app.route("/get/<username>/<year>", methods=["POST"])
@login_required
def get_username_year(username, year):
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    route_log()
    user = aduser.ADUser.from_cn(username)
    attributes = ["department", "description", "title", "wbemPath"]
    kw = {}
    for a in attributes:
        if a == "wbemPath":
            kw[a] = ""
            for p in user.get_attribute("wbemPath", True):
                if p.split(':')[0] == str(year):
                    kw[a] = p.split(':')[-1]
        else:
            try:
                kw[a] = json.loads(user.get_attribute(a, False))[str(year)]
            except KeyError as e:
                kw[a] = ""
    return json.dumps(kw)

@app.route("/disable/<username>/<b>", methods=["POST"])
@login_required
def disable_username_b(username, b):
    if admin_check():
        return redirect(url_for("appuser_home"))
    route_log()
    user = aduser.ADUser.from_cn(username)
    if b.lower() == "true":
        msg = "User: %s has been disabled by %s" % (username, current_user.username)
        user.set_user_account_control_setting("ACCOUNTDISABLE", True)
    else:
        msg = "User: %s has been enabled by %s" % (username, current_user.username)
        user.set_user_account_control_setting("ACCOUNTDISABLE", False)
    res = build_log(msg)
    print(res)
    return str(b)

@app.route("/admin_post")
@login_required
def admin_post():
    if admin_check():
        return redirect(url_for("appuser_home"))
    route_log()
    db = get_db()
    cur = db.cursor()
    q = "SELECT pid, author, title, datetime FROM post"
    cur.execute(q)
    posts = {}
    for p in cur.fetchall():
        posts[int(p[0])] = {
            "author": p[1],
            "title": p[2],
            "datetime": p[3]
        }
    return render_template("admin_post.html", user=current_user, posts=posts)

@app.route("/admin_post/<int:pid>", methods=["GET", "POST"])
@login_required
def admin_post_i(pid):
    if admin_check():
        return redirect(url_for("appuser_home"))
    route_log()
    user = current_user
    db = get_db()
    cur = db.cursor()
    q = "SELECT * FROM post WHERE pid=%s"
    cur.execute(q, (pid,))
    r = getSingleResult(cur.fetchone(), cur, "post")
    #print("r:\t" + str(r))
    form = AdminPostEdit(pid=r["pid"], author=r["author"], title=r["title"], heading=r["heading"], text=r["text"], bgimgh=r["bgimg"], imgh=r["img"])
    #print("Form test (type(%s)%s==(type(%s)%s)): " % (type(form.pid.data), form.pid.data, type(pid), pid) + str(form.pid.data==pid))
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data and form.pid.data == pid:
        try:
            data = {
                'pid': str(form.pid.data),
                'author': str(form.author.data),
                'title': request.form["title"],
                'heading': request.form["heading"],
                'text': request.form["text"]
            }
        except ValueError as e:
            flash("An error was encountered when parsing the data:\t" + str(e))
            res = build_log("ValueError when parsing data:\t" + str(e))
            print(res)
        #print("form.img.data:\t%s\nform.bgim.data:\t%s" % (form.img.data, form.bgimg.data))
        if form.img.data and form.bgimg.data:
            img = form.img
            bgimg = form.bgimg
            data["img"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            data["bgimg"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            delete_file(StringTools.getFileName(r["img"]), "", app.config["POST_IMAGES"])
            delete_file(StringTools.getFileName(r["bgimg"]), "", app.config["POST_IMAGES"])
            img_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            print("img_path:\t" + str(img_path))
            form.img.data.save(img_path)
            bgimg_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            print("bgimg_path:\t" + str(bgimg_path))
            form.bgimg.data.save(bgimg_path)
            q = "UPDATE post SET author=%s, title=%s, heading=%s, text=%s, img=%s, bgimg=%s WHERE pid=%s"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], data["img"], data["bgimg"], data["pid"]))
            cur.execute("COMMIT")
        elif form.img.data:
            img = form.img
            data["img"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            delete_file(StringTools.getFileName(r["img"]), "", app.config["POST_IMAGES"])
            img_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            form.img.data.save(img_path)
            q = "UPDATE post SET author=%s, title=%s, heading=%s, text=%s, img=%s WHERE pid=%s"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], data["img"], data["pid"]))
            cur.execute("COMMIT")
        elif form.bgimg.data:
            bgimg = form.bgimg
            data["bgimg"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            delete_file(StringTools.getFileName(r["bgimg"]), "", app.config["POST_IMAGES"])
            bgimg_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            print("bgimg_path:\t" + str(bgimg_path))
            form.bgimg.data.save(bgimg_path)
            q = "UPDATE post SET author=%s, title=%s, heading=%s, text=%s, bgimg=%s WHERE pid=%s"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], data["img"], data["pid"]))
            cur.execute("COMMIT")
        else:
            q = "UPDATE post SET author=%s, title=%s, heading=%s, text=%s WHERE pid=%s"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], data["pid"]))
            cur.execute("COMMIT")
        res = build_log("Post updated! PID: " + str(data["pid"]) + " Title: " + str(data["title"]) + " by: " + current_user.username)
        print(res)
        flash("Post PID: " + str(data["pid"]) + " title: " + str(data["title"]) + " has successfully been updated!", 'success')
        return redirect(url_for("admin_post"))
    return render_template("admin_post_i.html", user=current_user, form=form, post=r)

@app.route("/admin_post/add", methods=["GET", "POST"])
@login_required
def admin_post_add():
    if admin_check():
        return redirect(url_for("appuser_home"))
    route_log()
    user = current_user
    db = get_db()
    cur = db.cursor()
    form = AdminPostCreate(user.username)
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data:
        q = "SELECT @`pid`:=MAX(`pid`)+1 FROM post"
        cur.execute(q)
        n_pid = cur.fetchone()[0]
        if not n_pid:
            n_pid = "1"
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        try:
            data = {
                'pid': str(n_pid),
                'author': str(form.author.data),
                'title': str(form.title.data),
                'heading': str(form.heading.data),
                'text': str(form.text.data)
            }
        except ValueError as e:
            flash("An error was encountered when parsing the data:\t" + str(e))
            res = build_log("ValueError when parsing data:\t" + str(e))
            print(res)
        print("form.img.data:\t%s\nform.bgim.data:\t%s" % (form.img.data, form.bgimg.data))
        if form.img.data and form.bgimg.data:
            img = form.img
            bgimg = form.bgimg
            data["img"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            data["bgimg"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            #delete_file(StringTools.getFileName(r["img"]), "", app.config["POST_IMAGES"])
            #delete_file(StringTools.getFileName(r["bgimg"]), "", app.config["POST_IMAGES"])
            img_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            print("img_path:\t" + str(img_path))
            form.img.data.save(img_path)
            bgimg_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            print("bgimg_path:\t" + str(bgimg_path))
            form.bgimg.data.save(bgimg_path)
            q = "INSERT INTO post (author, title, heading, text, img, bgimg, datetime) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], data["img"], data["bgimg"], date_time))
            cur.execute("COMMIT")
        elif form.img.data:
            img = form.img
            data["img"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            #delete_file(StringTools.getFileName(r["img"]), "", app.config["POST_IMAGES"])
            img_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-img" + StringTools.getFileExt(img.data.filename))
            print("img_path:\t" + str(img_path))
            form.img.data.save(img_path)
            q = "INSERT INTO post (author, title, heading, text, img, datetime) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], data["img"], date_time))
            cur.execute("COMMIT")
        elif form.bgimg.data:
            bgimg = form.bgimg
            data["bgimg"] = str(app.config["POST_IMG_PATH"] + str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            #delete_file(StringTools.getFileName(r["bgimg"]), "", app.config["POST_IMAGES"])
            bgimg_path = os.path.join(app.config["POST_IMAGES"], str(data["pid"]) + "-bgimg" + StringTools.getFileExt(bgimg.data.filename))
            print("bgimg_path:\t" + str(bgimg_path))
            form.bgimg.data.save(bgimg_path)
            q = "INSERT INTO post (author, title, heading, text, bgimg, datetime) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], data["bgimg"], date_time))
            cur.execute("COMMIT")
        else:
            q = "INSERT INTO post (author, title, heading, text, datetime) VALUES (%s, %s, %s, %s, %s)"
            cur.execute("START TRANSACTION")
            cur.execute(q, (data["author"], data["title"], data["heading"], data["text"], date_time))
            cur.execute("COMMIT")
        res = build_log("Post created! PID: " + str(data["pid"]) + " Title: " + str(data["title"]) + " by: " + current_user.username)
        print(res)
        flash("Post PID: " + str(data["pid"]) + " title: " + str(data["title"]) + " has successfully been created!", 'success')
        return redirect(url_for("admin_post"))
    return render_template("admin_post_add.html", user=current_user, form=form)

@app.route("/admin_post/delete", methods=["GET", "POST"])
@login_required
def admin_post_delete():
    if admin_check(current_user):
        return redirect(url_for("appuser_home"))
    db = get_db()
    cur = db.cursor()
    q = "SELECT pid, author, title, datetime FROM post"
    cur.execute(q)
    form = AdminPostDelete()
    if request.method == "POST" and form.is_submitted() and form.validate() and form.submit.data:
        pass
    posts = {}
    for post in cur.fetchall():
        posts[int(post[0])] = {
            'author': post[1],
            'title': post[2],
            'datetime': post[3]
        }
    return render_template("admin_post_delete.html", user=current_user, posts=posts, form=form)

@app.route("/test/json", methods=["POST"])
def test_json():
    data = request.data.decode("utf-8", "strict").replace("%2C", ",")
    username = data.split("=")[-1].split(",")
    print(str(username))
    return str(username)

@app.route("/show/<template_file>")
def show_template(template_file):
    route_log()
    return render_template(str(template_file)+".html")
