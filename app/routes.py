from flask import render_template, flash, redirect, url_for, request, g, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import app, limiter, login_manager
from app.forms import RegisterForm, LoginForm
from datetime import datetime
from app.pylib import win_user, StringTools
from app.pylib.auth_user import User
from pyad import pyad, adcontainer, aduser, adgroup, adobject
from flask_ldap import ldap
import os
import time
import pythoncom
import pywin32_system32
import re

def get_remote_info(request=request):
    '''
    Returns information about a remote host in a dict.\n
    Keys: \"ip\", \"method\", \"url\"\n
    Arguments:\n
    :param request: Request object from Flask <type:flask.request>
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
    Arguments:\n
    :param request: Request object from Flask <type:flask.request>
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
    [dd/mmm/yyyy hh:MM:SS]
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
    Arguments:\n
    :param data: String of data from a route to be used in the log message <type:str>
    '''
    remote_info = get_remote_info(request)
    req_time = get_date_time()
    res = remote_info["ip"] + " - - " + req_time + " " + remote_info["method"] + " " + remote_info["url"] + " "
    return res + str(data)

def route_log():
    remote_info = get_remote_info(request)
    req_time = get_date_time()
    res = remote_info["ip"] + " - - " + req_time + " " + remote_info["method"] + " " + remote_info["url"] + " Requested"
    print(res)
    return res

@login_manager.user_loader
def load_user(id):
    pythoncom.CoInitialize()
    return User(id)
@app.before_request
def get_current_user():
    g.user = current_user.get_id()

@app.route("/")
def landing():
    route_log()
    return render_template("landing.html")

@app.route("/r/", methods=["POST"])
def r():
    route_log()
    time.sleep(3.2)
    return url_for("home")

@app.route("/home/", methods=["GET", "POST"])
def home():
    route_log()
    return render_template("home.html", active=0, head_menu=app.config["head_menu"])

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


@app.route("/show/<template_file>")
def show_template(template_file):
    route_log()
    return render_template(str(template_file)+".html")

from app import user