import os
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if not request.form.get("fund"):
            return apology("must provide funds", 403)
        amt = float(request.form.get("fund"))
        if not (amt > 0):
            return apology("must provide a valid amount of cash", 403)

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amt, session["user_id"])

        return redirect("/")
    else:
        """Show portfolio of stocks"""
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        data = db.execute("SELECT * FROM owned WHERE u_id = ?", session["user_id"])
        values = []
        sum = 0
        for row in data:
            values.append({"symbol": row["symbol"], "qty": row["qty"], "price": usd(
                lookup(row["symbol"])["price"]), "total": usd((lookup(row["symbol"])["price"] * row["qty"]))})
            sum += (lookup(row["symbol"])["price"] * row["qty"])

        sum += rows[0]["cash"]
        return render_template("index.html", values=values, cash=usd(rows[0]["cash"]), sum=usd(sum))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide # of shares", 400)
        if not request.form.get("shares").isdigit():
            return apology("must provide # of shares", 400)

        qty = int(request.form.get("shares"))
        if not (qty > 0):
            return apology("must provide a valid amount of stocks to buy", 400)

        if lookup(request.form.get("symbol")) == None:
            return apology("requested stock not found", 400)

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        data = db.execute("SELECT symbol FROM owned WHERE u_id = ?", session["user_id"])
        symbols = [row["symbol"] for row in data]

        amount = lookup(request.form.get("symbol"))["price"] * qty
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        if amount > rows[0]["cash"]:
            return apology("not enough funds", 403)
        else:
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", amount, rows[0]["id"])
            db.execute("INSERT INTO transactions(u_id, symbol, qty, type, time, price) VALUES (?, ?, ?, ?, ?, ?)",
                       rows[0]["id"], request.form.get("symbol"), qty, "buy", timestamp, (amount/qty))

            if request.form.get("symbol") in symbols:
                db.execute("UPDATE owned SET qty = qty + ? WHERE symbol = ?",
                           qty, request.form.get("symbol"))
            else:
                db.execute("INSERT INTO owned (u_id, symbol, qty) VALUES (?, ?, ?)",
                           rows[0]["id"], request.form.get("symbol"), qty)

            return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    data = db.execute("SELECT * FROM transactions WHERE u_id = ?", session["user_id"])
    values = []
    for row in data:
        values.append({"symbol": row["symbol"], "qty": row["qty"],
                      "price": usd(row["price"]), "time": row["time"]})
    return render_template("history.html", values=values)


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
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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
    return redirect("/login")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide a stock", 400)

        if lookup(request.form.get("symbol")) == None:
            return apology("requested stock not found", 400)

        return render_template("quoted.html", name=lookup(request.form.get("symbol"))["name"], price=usd(lookup(request.form.get("symbol"))["price"]))

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must re-type password for verification", 400)

        if request.form.get("confirmation") != request.form.get("password"):
            return apology("retyped password didn't match", 400)

        # Query database for username
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       request.form.get("username"), generate_password_hash(request.form.get("password")))
        except ValueError:
            return apology("username already taken", 400)
        finally:
            rows = db.execute("SELECT * FROM users WHERE username = ?",
                              request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide # of shares", 400)

        q = int(request.form.get("shares"))
        if not (q > 0):
            return apology("must provide a valid amount of stocks to sell", 400)

        if lookup(request.form.get("symbol")) == None:
            return apology("requested stock not found", 400)

        data = db.execute("SELECT symbol, qty FROM owned WHERE u_id = ?", session["user_id"])
        symbols = [row["symbol"] for row in data]
        if not request.form.get("symbol") in symbols:
            return apology("you dont own that stock")

        qty = 0
        for row in data:
            if row["symbol"] == request.form.get("symbol"):
                qty = row["qty"]

        amount = lookup(request.form.get("symbol"))["price"] * q
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        if qty >= q:

            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, session["user_id"])
            db.execute("INSERT INTO transactions(u_id, symbol, qty, type, time, price) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], request.form.get("symbol"), q, "sell", timestamp, (amount/q))
            db.execute("UPDATE owned SET qty = qty - ? WHERE symbol = ?",
                       q, request.form.get("symbol"))

        else:
            return apology("you dont own enough shares of the stock", 400)

        return redirect("/")

    else:
        data = db.execute("SELECT * FROM owned WHERE u_id = ?", session["user_id"])
        return render_template("sell.html", data=data)
