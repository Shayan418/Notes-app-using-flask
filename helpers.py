import datetime
import re

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    
    return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def longDateTime(input):
    date_time = list(map(int,re.split('-| |:', input)))
    dt_tm = datetime.datetime(date_time[0], date_time[1], date_time[2], date_time[3], date_time[4], date_time[5])
    return(dt_tm.strftime("%d %B %Y %I:%M%p"))

def shortDate(input):
    date_time = list(map(int,re.split('-| |:', input)))
    dt_tm = datetime.datetime(date_time[0], date_time[1], date_time[2], date_time[3], date_time[4], date_time[5])
    return(dt_tm.strftime("%d %b %y"))