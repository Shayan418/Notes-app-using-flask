import datetime
import requests
import re
import os
import urllib.parse
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

def getWeather(ipinfo):
    
    # Contact API
    try:
        api_key = os.environ.get("OPEN_WEATHER_API")
        city = ipinfo["city"]
        state = ipinfo["region"]
        country = ipinfo["country"]
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{state},{country}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        data = response.json()
        if data['dt'] < data['sys']['sunrise'] or data['dt'] > data['sys']['sunset']:
            day = 'false'
        return {
            "temp": data['main']['temp'],
            "city": city,
            "day": day
        }
    except (KeyError, TypeError, ValueError):
        return None