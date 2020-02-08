# Canticum Repertoire List

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
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
db = SQL("sqlite:///canticum-repertoire.db")


# Get full list of composer names to display
def list_composers():
    rows = db.execute("SELECT * FROM composers ORDER BY composer_name")
    l_composers = []
    for person in rows:
        person_info = {}
        person_info['composer_id'] = person['composer_id']
        person_info['composer_name'] = person['composer_name']
        l_composers.append(person_info)
    return l_composers


# Get full list of composer composition combos to display
def list_composercompositions():
    rows = db.execute("SELECT * FROM compositions n JOIN composers r on n.composer_id = r.composer_id ORDER BY r.composer_name, n.composition_name")
    l_composercompositions = []
    for work in rows:
        work_info = {}
        work_info['composition_id'] = work['composition_id']
        work_info['composer_name'] = work['composer_name']
        work_info['composition_name'] = work['composition_name']
        l_composercompositions.append(work_info)
    return l_composercompositions


# Get full list of composition names to display
def list_compositions():
    rows = db.execute("SELECT * FROM composers r JOIN compositions n ON r.composer_id = n.composer_id ORDER BY r.composer_name, n.composition_name")
    l_compositions = []
    for piece in rows:
        piece_info = {}
        piece_info['composition_id'] = piece['composition_id']
        piece_info['composer_id'] = piece['composer_id']
        piece_info['composer_name'] = piece['composer_name']
        piece_info['composition_name'] = piece['composition_name']
        l_compositions.append(piece_info)
    return l_compositions


# Get full list of concerts to display
def list_concerts():
    rows = db.execute("SELECT * FROM concerts t JOIN venues v ON t.venue_id = v.venue_id ORDER BY t.concert_date DESC")
    l_concerts = []
    for appearance in rows:
        appearance_info = {}
        appearance_info['concert_id'] = appearance['concert_id']
        appearance_info['concert_date'] = appearance['concert_date']
        appearance_info['concert_name'] = appearance['concert_name']
        appearance_info['venue_name'] = appearance['venue_name']
        l_concerts.append(appearance_info)
    return l_concerts


# Get full list of date concert combos to display
def list_dateconcerts():
    rows = db.execute("SELECT * FROM concerts ORDER BY concert_date DESC")
    l_dateconcerts = []
    for date in rows:
        date_info = {}
        date_info['concert_id'] = date['concert_id']
        date_info['concert_date'] = date['concert_date']
        date_info['concert_name'] = date['concert_name']
        l_dateconcerts.append(date_info)
    return l_dateconcerts


# Get full list of performances to display
def list_performances():
    rows = db.execute("SELECT * FROM performances e JOIN concerts t ON e.concert_id = t.concert_id JOIN compositions n ON e.composition_id = n.composition_id JOIN composers r ON n.composer_id = r.composer_id ORDER BY t.concert_date DESC, r.composer_name ASC, n.composition_name ASC")
    l_performances = []
    for occasion in rows:
        occasion_info = {}
        occasion_info['performance_id'] = occasion['performance_id']
        occasion_info['concert_date'] = occasion['concert_date']
        occasion_info['concert_name'] = occasion['concert_name']
        occasion_info['composer_name'] = occasion['composer_name']
        occasion_info['composition_name'] = occasion['composition_name']
        l_performances.append(occasion_info)
    return l_performances


# Get list of repertoire with latest performance date to display
def list_reps():
    rows = db.execute("SELECT r.composer_name AS composer, n.composition_name AS composition, MAX(t.concert_date) AS latest_date FROM performances e LEFT JOIN compositions n ON e.composition_id = n.composition_id LEFT JOIN composers r ON n.composer_id = r.composer_id LEFT JOIN concerts t ON e.concert_id = t.concert_id GROUP BY n.composition_id ORDER BY r.composer_name, n.composition_name")
    l_reps = []
    for repert in rows:
        repert_info = {}
        repert_info['composer_name'] = repert['composer']
        repert_info['composition_name'] = repert['composition']
        repert_info['latest_date'] = repert['latest_date']
        l_reps.append(repert_info)
    return l_reps


# Get full list of user names to display
def list_users():
    rows = db.execute("SELECT * FROM users ORDER BY username")
    l_users = []
    for person in rows:
        person_info = {}
        person_info['user_id'] = person['user_id']
        person_info['user_name'] = person['username']
        l_users.append(person_info)
    return l_users


# Get full list of venue names to display
def list_venues():
    rows = db.execute("SELECT * FROM venues ORDER BY venue_name")
    l_venues = []
    for place in rows:
        place_info = {}
        place_info['venue_id'] = place['venue_id']
        place_info['venue_name'] = place['venue_name']
        l_venues.append(place_info)
    return l_venues


@app.route("/")
def index():
    """Show full repertoire with latest performance date"""
    reps = list_reps()
    return render_template("index.html", reps=reps)


@app.route("/composers")
def composers():
    """Show composers in read-only mode"""
    composers = list_composers()
    return render_template("composers.html", composers=composers)


@app.route("/composeradd", methods=["GET", "POST"])
@login_required
def composeradd():
    """Show composers and allow entry of new composer"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new composer name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new composer name in database
        composer_name = request.form.get("name")
        db.execute("INSERT INTO composers (composer_name) VALUES (:composer_name)", composer_name=composer_name)
        composers = list_composers()
        flash("Composer added!")
        return render_template("composeradd.html", composers=composers)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        composers = list_composers()
        return render_template("composeradd.html", composers=composers)


@app.route("/composeredit", methods=["GET", "POST"])
@login_required
def composeredit():
    """Update composer name"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new composer name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new composer name in database
        composer_id = request.form.get("id")
        name = request.form.get("name")
        db.execute("UPDATE composers SET composer_name = :name WHERE composer_id = :composer_id", name=name, composer_id=composer_id)
        composers = list_composers()
        flash("Composer name updated!")
        return render_template("composers.html", composers=composers)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        composer_id = request.args.get('id')
        rows = db.execute("SELECT composer_name FROM composers WHERE composer_id = :composer_id", composer_id=composer_id)
        composer_name = rows[0]["composer_name"]
        return render_template("composeredit.html", composer_id=composer_id, composer_name=composer_name)


@app.route("/composerdelete")
@login_required
def composerdelete():
    delete_id = request.args.get('id')
    # Check if any compositions use this composer and only delete if result is zero
    rows = db.execute("SELECT * FROM compositions WHERE composer_id = :delete_id", delete_id=delete_id)
    if len(rows) == 0:
        db.execute("DELETE FROM composers WHERE composer_id = :delete_id", delete_id=delete_id)
        composers = list_composers()
        flash("Composer deleted!")
        return render_template("composers.html", composers=composers)
    else:
        composers = list_composers()
        flash("Cannot delete this composer, because at least one composition is by this composer. Delete the composition first.")
        return render_template("composers.html", composers=composers)


@app.route("/composercompositions")
def composercompositions():
    """Display compositions of a composer"""
    composer_id = request.args.get('id')
    rows = db.execute("SELECT * FROM composers WHERE composer_id = :composer_id", composer_id=composer_id)
    composer_name = rows[0]["composer_name"]
    rows = db.execute("SELECT * FROM compositions WHERE composer_id = :composer_id ORDER BY composition_name", composer_id=composer_id)
    composerworks = []
    for work in rows:
        work_info = {}
        work_info['composition_id'] = work['composition_id']
        work_info['composition_name'] = work['composition_name']
        composerworks.append(work_info)
    return render_template("composercompositions.html", composer_name=composer_name, composerworks=composerworks)


@app.route("/compositions")
def compositions():
    """Show compositions in read-only mode"""
    compositions = list_compositions()
    composers = list_composers()
    return render_template("compositions.html", composers=composers, compositions=compositions)


@app.route("/compositionadd", methods=["GET", "POST"])
@login_required
def compositionadd():
    """Show compositions with their composers and allow entry of new composition"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new composition name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new composition name in database with composer ID
        composition_name = request.form.get("name")
        composer_name = request.form.get("composer")
        rows = db.execute("SELECT composer_id FROM composers WHERE composer_name = :composer_name", composer_name=composer_name)
        composer_id = rows[0]["composer_id"]
        db.execute("INSERT INTO compositions (composition_name, composer_id) VALUES (:composition_name, :composer_id)",
                composition_name=composition_name, composer_id=composer_id)
        compositions = list_compositions()
        composers = list_composers()
        flash("Composition added!")
        return render_template("compositionadd.html", composers=composers, compositions=compositions)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        compositions = list_compositions()
        composers = list_composers()
        return render_template("compositionadd.html", composers=composers, compositions=compositions)


@app.route("/compositionedit", methods=["GET", "POST"])
@login_required
def compositionedit():
    """Update composition name"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new composition name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new composition name in database
        composition_id = request.form.get("id")
        name = request.form.get("name")
        db.execute("UPDATE compositions SET composition_name = :name WHERE composition_id = :composition_id", name=name, composition_id=composition_id)
        compositions = list_compositions()
        composers = list_composers()
        flash("Composition name updated!")
        return render_template("compositions.html", composers=composers, compositions=compositions)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        composition_id = request.args.get('id')
        rows = db.execute("SELECT composition_name FROM compositions WHERE composition_id = :composition_id", composition_id=composition_id)
        composition_name = rows[0]["composition_name"]
        return render_template("compositionedit.html", composition_id=composition_id, composition_name=composition_name)


@app.route("/compositiondelete")
@login_required
def compositiondelete():
    delete_id = request.args.get('id')
    # Check if any performances use this composition and only delete if result is zero
    rows = db.execute("SELECT * FROM performances WHERE composition_id = :delete_id", delete_id=delete_id)
    if len(rows) == 0:
        db.execute("DELETE FROM compositions WHERE composition_id = :delete_id", delete_id=delete_id)
        compositions = list_compositions()
        composers = list_composers()
        flash("Composition deleted!")
        return render_template("compositions.html", composers=composers, compositions=compositions)
    else:
        compositions = list_compositions()
        composers = list_composers()
        flash("Cannot delete this composition, because at least one performance includes this composition. Delete the performance first.")
        return render_template("compositions.html", composers=composers, compositions=compositions)


@app.route("/compositionperformances")
def compositionperformances():
    """Display performances of a composition"""
    composition_id = request.args.get('id')
    rows = db.execute("SELECT * FROM compositions n JOIN composers r ON n.composer_id = r.composer_id WHERE n.composition_id = :composition_id", composition_id=composition_id)
    composition_name = rows[0]["composition_name"]
    composer_name = rows[0]["composer_name"]
    rows = db.execute("SELECT * FROM performances e JOIN concerts t ON e.concert_id = t.concert_id JOIN venues v ON t.venue_id = v.venue_id JOIN compositions n ON e.composition_id = n.composition_id JOIN composers r ON n.composer_id = r.composer_id WHERE n.composition_id = :composition_id ORDER BY t.concert_date DESC", composition_id=composition_id)
    performances = []
    for perf in rows:
        perf_info = {}
        perf_info['concert_id'] = perf['concert_id']
        perf_info['concert_date'] = perf['concert_date']
        perf_info['concert_name'] = perf['concert_name']
        perf_info['venue_name'] = perf['venue_name']
        performances.append(perf_info)
    return render_template("compositionperformances.html", composition_name=composition_name, composer_name=composer_name, performances=performances)


@app.route("/concerts")
def concerts():
    """Show history of concerts in read-only mode"""
    concerts = list_concerts()
    venues = list_venues()
    return render_template("concerts.html", concerts=concerts, venues=venues)


@app.route("/concertadd", methods=["GET", "POST"])
@login_required
def concertadd():
    """Show history of concerts and allow entry of new concert"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new concert date was submitted
        if not request.form.get("date"):
            return apology("must provide date", 403)
        # Ensure new concert name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new concert name in database
        concert_date = request.form.get("date")
        concert_name = request.form.get("name")
        venue_name = request.form.get("venue")
        rows = db.execute("SELECT venue_id FROM venues WHERE venue_name = :venue_name", venue_name=venue_name)
        venue_id = rows[0]["venue_id"]
        db.execute("INSERT INTO concerts (concert_date, concert_name, venue_id) VALUES (:concert_date, :concert_name, :venue_id)",
                concert_date=concert_date, concert_name=concert_name, venue_id=venue_id)
        concerts = list_concerts()
        venues = list_venues()
        flash("Concert added!")
        return render_template("concertadd.html", concerts=concerts, venues=venues)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        concerts = list_concerts()
        venues = list_venues()
        return render_template("concertadd.html", concerts=concerts, venues=venues)


@app.route("/concertdelete")
@login_required
def concertdelete():
    delete_id = request.args.get('id')
    # Check if any performances use this concert and only delete if result is zero
    rows = db.execute("SELECT * FROM 'performances' WHERE concert_id = :delete_id", delete_id=delete_id)
    if len(rows) == 0:
        db.execute("DELETE FROM concerts WHERE concert_id = :delete_id", delete_id=delete_id)
        concerts = list_concerts()
        venues = list_venues()
        flash("Concert deleted!")
        return render_template("concerts.html", concerts=concerts, venues=venues)
    else:
        concerts = list_concerts()
        venues = list_venues()
        flash("Cannot delete this concert, because at least one performance includes this concert. Delete the performance first.")
        return render_template("concerts.html", concerts=concerts, venues=venues)


@app.route("/concertedit", methods=["GET", "POST"])
@login_required
def concertedit():
    """Update concert date and name"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new concert name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new concert date and name in database
        concert_id = request.form.get("id")
        date = request.form.get("date")
        name = request.form.get("name")
        venue_name = request.form.get("venue")
        rows = db.execute("SELECT venue_id FROM venues WHERE venue_name = :venue_name", venue_name=venue_name)
        venue_id = rows[0]["venue_id"]
        db.execute("UPDATE concerts SET concert_date = :date, concert_name = :name, venue_id = :venue_id WHERE concert_id = :concert_id", date=date, name=name, venue_id=venue_id, concert_id=concert_id)
        concerts = list_concerts()
        venues = list_venues()
        flash("Concert updated!")
        return render_template("concerts.html", concerts=concerts, venues=venues)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        concert_id = request.args.get('id')
        rows = db.execute("SELECT * FROM concerts t JOIN venues v ON t.venue_id = v.venue_id WHERE concert_id = :concert_id", concert_id=concert_id)
        concert_date = rows[0]["concert_date"]
        concert_name = rows[0]["concert_name"]
        current_venue_id = rows[0]["venue_id"]
        venue_name = rows[0]["venue_name"]
        venues = list_venues()
        return render_template("concertedit.html", concert_id=concert_id, concert_date=concert_date, concert_name=concert_name, current_venue_id=current_venue_id, venue_name=venue_name, venues=venues)


@app.route("/concertprogramme")
def concertprogramme():
    """Display compositions in a concert"""
    concert_id = request.args.get('id')
    rows = db.execute("SELECT * FROM concerts t JOIN venues v ON t.venue_id = v.venue_id WHERE t.concert_id = :concert_id", concert_id=concert_id)
    concert_name = rows[0]["concert_name"]
    concert_date = rows[0]["concert_date"]
    concert_venue = rows[0]["venue_name"]
    rows = db.execute("SELECT * FROM performances e JOIN concerts t ON e.concert_id = t.concert_id JOIN compositions n ON e.composition_id = n.composition_id JOIN composers r ON n.composer_id = r.composer_id WHERE t.concert_id = :concert_id ORDER BY r.composer_name, n.composition_name", concert_id=concert_id)
    programme = []
    for prog in rows:
        prog_info = {}
        prog_info['composition_id'] = prog['composition_id']
        prog_info['composer_name'] = prog['composer_name']
        prog_info['composition_name'] = prog['composition_name']
        programme.append(prog_info)
    return render_template("concertprogramme.html", concert_name=concert_name, concert_date=concert_date, concert_venue=concert_venue, programme=programme)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/password", methods=["GET", "POST"])
def password():
    """Change password"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure old password was submitted
        if not request.form.get("oldpassword"):
            return apology("must provide old password", 400)
        # Ensure new password was submitted
        elif not request.form.get("newpassword"):
            return apology("must provide new password", 400)
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        # Ensure password and confirmation match
        elif (request.form.get("newpassword") != request.form.get("confirmation")):
            return apology("new passwords must match", 400)
        # Query database for current password
        user_name = request.form.get("user")
        rows = db.execute("SELECT * FROM users WHERE username = :user_name", user_name=user_name)
        user_id = rows[0]["user_id"]
        # Ensure old password was correct
        if not check_password_hash(rows[0]["hash"], request.form.get("oldpassword")):
            return apology("invalid old password", 403)
        # Hash password
        hash = generate_password_hash(request.form.get("newpassword"))
        # Store value
        stored = db.execute("UPDATE users SET hash = :hash WHERE user_id = :user_id", hash=hash, user_id=user_id)
        flash("Password changed!")
        users = list_users()
        return render_template("users.html", users=users)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        users = list_users()
        return render_template("users.html", users=users)


@app.route("/performances")
def performances():
    """Show history of performances in read-only mode"""
    performances = list_performances()
    dateconcerts = list_dateconcerts()
    composercompositions = list_composercompositions()
    return render_template("performances.html", performances=performances, dateconcerts=dateconcerts, composercompositions=composercompositions)


@app.route("/performanceadd", methods=["GET", "POST"])
@login_required
def performanceadd():
    """Show history of performances of each composition"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Store new performance record in database with composition ID and concert ID
        concert_id = request.form.get("dateconcert")
        composition_id = request.form.get("composercomposition")
        db.execute("INSERT INTO performances (concert_id, composition_id) VALUES (:concert_id, :composition_id)",
                concert_id=concert_id, composition_id=composition_id)
        performances = list_performances()
        dateconcerts = list_dateconcerts()
        composercompositions = list_composercompositions()
        flash("Performance added!")
        return render_template("performanceadd.html", performances=performances, dateconcerts=dateconcerts, composercompositions=composercompositions)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        performances = list_performances()
        dateconcerts = list_dateconcerts()
        composercompositions = list_composercompositions()
        return render_template("performanceadd.html", performances=performances, dateconcerts=dateconcerts, composercompositions=composercompositions)


@app.route("/performancedelete")
@login_required
def performancedelete():
    delete_id = request.args.get('id')
    db.execute("DELETE FROM performances WHERE performance_id = :delete_id", delete_id=delete_id)
    performances = list_performances()
    dateconcerts = list_dateconcerts()
    composercompositions = list_composercompositions()
    flash("Performance deleted!")
    return render_template("performances.html", performances=performances, dateconcerts=dateconcerts, composercompositions=composercompositions)


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    """Register new user - only permitted by already-logged-in user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        # Ensure password and confirmation match
        elif (request.form.get("password") != request.form.get("confirmation")):
            return apology("passwords must match", 400)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username does not already exist
        if len(rows) == 1:
            return apology("username taken", 400)
        # Hash password
        hash = generate_password_hash(request.form.get("password"))
        # Store values
        stored = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                            username=request.form.get("username"), hash=hash)
        flash("New user added! Tell them their username and password.")
        users = list_users()
        return render_template("users.html", users=users)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        users = list_users()
        return render_template("users.html", users=users)


@app.route("/users")
@login_required
def users():
    users = list_users()
    return render_template("users.html", users=users)


@app.route("/venues")
def venues():
    """Show venues in read-only mode"""
    venues = list_venues()
    return render_template("venues.html", venues=venues)


@app.route("/venueadd", methods=["GET", "POST"])
@login_required
def venueadd():
    """Show venues of concerts and allow entry of new venue"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new venue name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new venue name in database
        name = request.form.get("name")
        db.execute("INSERT INTO venues (venue_name) VALUES (:name)", name=name)
        venues = list_venues()
        flash("Venue added!")
        return render_template("venueadd.html", venues=venues)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        venues = list_venues()
        return render_template("venueadd.html", venues=venues)


@app.route("/venuedelete")
@login_required
def venuedelete():
    delete_id = request.args.get('id')
    # Check if any concerts use this venue and only delete if result is zero
    rows = db.execute("SELECT * FROM concerts WHERE venue_id = :delete_id", delete_id=delete_id)
    if len(rows) == 0:
        db.execute("DELETE FROM venues WHERE venue_id = :delete_id", delete_id=delete_id)
        venues = list_venues()
        flash("Venue deleted!")
        return render_template("venues.html", venues=venues)
    else:
        venues = list_venues()
        flash("Cannot delete this venue, because at least one concert is in this venue. Delete the concert first.")
        return render_template("venues.html", venues=venues)


@app.route("/venueedit", methods=["GET", "POST"])
@login_required
def venueedit():
    """Update venue name"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure new venue name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        # Store new venue name in database
        venue_id = request.form.get("id")
        name = request.form.get("name")
        db.execute("UPDATE venues SET venue_name = :name WHERE venue_id = :venue_id", name=name, venue_id=venue_id)
        venues = list_venues()
        flash("Venue name updated!")
        return render_template("venues.html", venues=venues)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        venue_id = request.args.get('id')
        rows = db.execute("SELECT venue_name FROM venues WHERE venue_id = :venue_id", venue_id=venue_id)
        venue_name = rows[0]["venue_name"]
        return render_template("venueedit.html", venue_id=venue_id, venue_name=venue_name)


@app.route("/venueconcerts")
def venueconcerts():
    """Display concerts in a venue"""
    venue_id = request.args.get('id')
    rows = db.execute("SELECT * FROM venues WHERE venue_id = :venue_id", venue_id=venue_id)
    venue_name = rows[0]["venue_name"]
    rows = db.execute("SELECT * FROM concerts WHERE venue_id = :venue_id ORDER BY concert_date DESC", venue_id=venue_id)
    venueconcerts = []
    for concert in rows:
        concert_info = {}
        concert_info['concert_id'] = concert['concert_id']
        concert_info['concert_date'] = concert['concert_date']
        concert_info['concert_name'] = concert['concert_name']
        venueconcerts.append(concert_info)
    return render_template("venueconcerts.html", venue_name=venue_name, venueconcerts=venueconcerts)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
