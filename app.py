import uuid
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, make_response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, longDateTime, shortDate, getWeather


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filters
app.jinja_env.filters["longDateTime"] = longDateTime
app.jinja_env.filters["shortDate"] = shortDate

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///notes.db")

if not os.environ.get("OPEN_WEATHER_API"):
    raise RuntimeError("OPEN_WEATHER_API not set")

#route for index
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html')
 

@app.route("/register", methods=["GET", "POST"])
def register():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password and confirmation was submitted
        elif not request.form.get("password"):
            if not request.form.get("confirmation"):
                return apology("missing passwords")

        # Return apology if password and confirmation does not match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords does not match")

        # Ensure same username does not already exist in database
        exist_u = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(exist_u) == 1:
            #print("username not available")
            flash(u'Username not available', 'error')
            return render_template("register.html")
        
        # Insert user into databse along with hashed password 
        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password"))
        )
        
        #Extract registered user row
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        #Pass userid and username to session variable for 
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        return redirect("/dashboard")
    
    # User reached route via GET or no POST input was provided
    else:
        session.clear()
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    
    """Log user in"""

    # Forget any user_id
    session.clear()

    #` User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]


        # Redirect user to dashboard
        return redirect("/dashboard")

    # User reached route via GET or no POST input was provided
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/dashboard")


#route for dashboard
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    
    #executes when input recieved from form
    #add / view / delete button is pressed
    if request.method == "POST":
        
        # redirects to /add if add button is clicked
        if "add_note" in request.form:
            if request.form['add_note'] == 'True':
                return redirect("/add")
        
        #redirects to /view with note id if view is clicked
        if "view_button" in request.form:
            return redirect(url_for('.view', noteid = request.form['view_button'] ))
        
        # executes delete command when delete button is pressed validating with user_id
        db.execute(
            "DELETE FROM notes WHERE userid=? and noteid=?;", 
            session["user_id"],
            request.form['submit_button']
        )
        
        #flash delete alert and reloads the page
        flash(u'Note Deleted','alert')
        return redirect("/dashboard")

    # User reached route via GET or no POST input was provided
    else:
        
        # tuple for headers for table in dashbord
        headings = ("Sno.", "Title", "last edited", "view" , "delete ")

        # extracting data to send for rendering table in dashboard 
        data = db.execute(
            "SELECT noteid, title, edited FROM notes WHERE Userid = ?",
            session["user_id"]
        )
        
        # adding serial number in data for display
        if len(data) > 0:
            i = 0
            for row in data:
                i += 1 
                row['count'] = i
        
        # render dashempty if there is no data
        if (len(data)) == 0:
            return render_template("dashempty.html")
        
        # otherwise render dash.html passing heading and data
        return render_template("dash.html", headings=headings, data=data)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    
    #executes when input recieved from user
    #add button is pressed
    if request.method == "POST":
        
        #validating form input are not empty
        if not request.form.get('noteTitle'):
            flash(u'Empty title not Allowed', 'error')
            return render_template("add.html")
        
        if not request.form.get('NoteContent'):
            flash(u'Empty note not Allowed', 'error')
            return render_template("add.html")
        
        # creating uuid for note 
        uuid_note_id = str(uuid.uuid4())
          
        # insert into database 
        db.execute(
            "INSERT INTO notes (noteid ,userid, title, note) VALUES(?, ?, ?, ?)",
            uuid_note_id,
            session["user_id"],
            request.form.get('noteTitle'),
            request.form.get('NoteContent')
        )
        
        # flash confirmation and retirect to dashboard
        flash(u'Note Added', 'info')
        return redirect("/dashboard")
    
    # User reached route via GET or no POST input was provided
    else:
        #renders page to add note
        return render_template("add.html")


@app.route("/view", methods=["GET", "POST"])
@login_required
def view():
   
    # User reached route via POST (as by submitting a form via POST)
    # edit button is pressed
    if request.method == "POST":
        
        # validating note id is same as the one in url
        if request.form['noteid_edit'] != request.args['noteid']:
            return apology("Bad Request")
        
        # update record and flash alert
        db.execute(
            "UPDATE notes SET title = ? ,note = ?,edited = (DATETIME('now','localtime')) WHERE noteid = ?",
            request.form.get('noteTitle'),
            request.form.get('NoteContent'),
            request.form.get('noteid_edit')
        )
        flash(u'Note Edited', 'info')
       
        # reload view page to see updated changes
        return redirect(request.url)
    
    # User reached route via GET or no POST input was provided
    else:
        noteid = request.args['noteid']

        # extract notes for current user
        data = db.execute(
                "SELECT noteid, title, note, creation, edited FROM notes WHERE Userid = ?",
                session["user_id"]
            )
       
        # validating noteid exists in database with same user        
        flag = False
        for row in data:
            if noteid == row['noteid']:
                fdata = row
                flag = True
        
        # return bad request on url tampering
        if flag == False:
            return apology("Bad Request")
        
        #pass note data to view.html
        return render_template("view.html", fdata = fdata)



@app.route("/api/ip", methods=["POST"])
def api():
    if request.method == 'POST':
        ipinfo = request.json
        print(ipinfo['city'])
        
        weatherdata = getWeather(ipinfo)
        print(weatherdata)
        res = make_response(jsonify(weatherdata), 200)
        return res
        
    
    
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True, port = 5000)