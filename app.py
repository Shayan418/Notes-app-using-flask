import uuid

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required


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


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///notes.db")


@app.route("/", methods=["GET", "POST"])
def index():
    return apology("HOME Under Construction")
    


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    
    if request.method == "POST":
        
        if "add_note" in request.form:
            if request.form['add_note'] == 'True':
                return redirect("/add")
        
        if "view_button" in request.form:
            return redirect(url_for('.view', noteid = request.form['view_button'] ))
        
        db.execute(
            "DELETE FROM notes WHERE userid=? and noteid=?;", 
            session["user_id"],
            request.form['submit_button']
        )
        
        print(request.form['submit_button'])
        flash(u'Note Deleted','alert')
        return redirect("/dashboard")

    else:
        headings = ("Sno.", "Title", "last edited", "view" , "delete ")

        data = db.execute(
            "SELECT noteid, title, edited FROM notes WHERE Userid = ?",
            session["user_id"]
        )
        
        
        if len(data) > 0:
            i = 0
            for row in data:
                i += 1 
                row['count'] = i
        
        if (len(data)) ==0:
            return render_template("dashempty.html")
        
        return render_template("dash.html", headings=headings, data=data)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    
    if request.method == "POST":
        
        if not request.form.get('noteTitle'):
            flash(u'Empty title not Allowed', 'error')
            return render_template("add.html")
        
        if not request.form.get('NoteContent'):
            flash(u'Empty note not Allowed', 'error')
            return render_template("add.html")
        
        
        uuid_note_id = str(uuid.uuid4())
               
        db.execute(
            "INSERT INTO notes (noteid ,userid, title, note) VALUES(?, ?, ?, ?)",
            uuid_note_id,
            session["user_id"],
            request.form.get('noteTitle'),
            request.form.get('NoteContent')
        )
        
        flash(u'Note Added', 'info')
        return redirect("/dashboard")
        
    else:
        return render_template("add.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
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


        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/dashboard")


@app.route("/view", methods=["GET", "POST"])
@login_required
def view():
   
    
    if request.method == "POST":
        
        if request.form['noteid_edit'] != request.args['noteid']:
            return apology("not allowed")
        
        db.execute(
            "UPDATE notes SET title = ? ,note = ?,edited = (DATETIME('now','localtime')) WHERE noteid = ?",
            request.form.get('noteTitle'),
            request.form.get('NoteContent'),
            request.form.get('noteid_edit')
        )
        flash(u'Note Edited', 'info')
       
        return redirect(request.url)
    
    else:
        noteid = request.args['noteid']
    
        data = db.execute(
                "SELECT noteid, title, note, creation, edited FROM notes WHERE Userid = ?",
                session["user_id"]
            )
        
        flag = False
        for row in data:
            if noteid == row['noteid']:
                fdata = row
                flag = True
            
        if flag == False:
            return apology("not allowed")
        
        print(fdata)
        return render_template("view.html", fdata = fdata)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username")

        elif not request.form.get("password"):
            if not request.form.get("confirmation"):
                return apology("missing passwords")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords does not match")

        exist_u = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(exist_u) == 1:
            #print("username not available")
            flash(u'Username not available', 'error')
            return apology("passwords does not match")

        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password"))
        )
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        return redirect("/dashboard")

    else:
        session.clear()
        return render_template("register.html")



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