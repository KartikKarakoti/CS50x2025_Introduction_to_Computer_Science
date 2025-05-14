import os

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


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    # Get all stocks the user owns
    rows = db.execute("""
        SELECT symbol, SUM(shares) AS total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING total_shares > 0
    """, user_id)

    holdings = []
    total_stocks_value = 0

    # For each stock, look up the current price and calculate total value
    for row in rows:
        stock = lookup(row["symbol"])
        if stock:
            shares = row["total_shares"]
            price = stock["price"]
            total = shares * price
            total_stocks_value += total

            holdings.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "shares": shares,
                "price": price,
                "total": total
            })

    # Get user's remaining cash
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    grand_total = cash + total_stocks_value

    return render_template("index.html", holdings=holdings, cash=cash, total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        # Get the stock symbol and shares from the form
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate symbol
        if not symbol:
            return apology("must provide stock symbol", 400)

        # Validate shares
        try:
            shares = int(shares)
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except ValueError:
            return apology("shares must be a number", 400)

        # Look up the stock information
        stock = lookup(symbol)
        if not stock:
            return apology("invalid stock symbol", 400)

        # Get the price of the stock
        price = stock["price"]
        total_cost = price * shares

        # Get user’s current cash balance
        user_id = session["user_id"]
        user = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]

        if user["cash"] < total_cost:
            return apology("not enough cash", 400)

        # Update the user’s cash balance
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)

        # Record the transaction in the transactions table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES (?, ?, ?, ?, ?)",
            user_id, stock["symbol"], shares, price, "buy"
        )

        # Flash a success message and redirect to the index page
        flash("Bought!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]

    # Fetch all transactions for the user, newest first
    rows = db.execute("""
        SELECT symbol, shares, price, timestamp
        FROM transactions
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, user_id)

    return render_template("history.html", transactions=rows)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

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
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("must provide symbol", 400)

        stock = lookup(symbol.upper())

        if not stock:
            return apology("invalid symbol", 400)

        return render_template("quote.html", quote=stock)

    else:
        return render_template("quote.html")


@login_required
def quote():
    """Get stock quote."""
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        if not password:
            return apology("must provide password", 400)
        if password != confirmation:
            return apology("passwords do not match", 400)

        hash_pw = generate_password_hash(password)

        try:
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw
            )
        except:
            return apology("username already exists", 400)

        session["user_id"] = new_user
        return redirect("/")
    else:
        return render_template("register.html")


def register():
    """Register user"""
    return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate inputs
        if not symbol:
            return apology("must select stock", 400)
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("invalid share amount", 400)

        shares = int(shares)

        # Get current user's ID
        user_id = session["user_id"]

        # Check how many shares the user owns of that stock
        rows = db.execute("""
            SELECT SUM(shares) as total_shares FROM transactions
            WHERE user_id = ? AND symbol = ?
            GROUP BY symbol
        """, user_id, symbol)

        if not rows or rows[0]["total_shares"] < shares:
            return apology("not enough shares", 400)

        # Lookup current price
        quote = lookup(symbol)
        if not quote:
            return apology("invalid stock", 400)

        price = quote["price"]
        total_value = price * shares

        # Update user's cash
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_value, user_id)

        # Record the sale (negative shares)
        db.execute("""
            INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES (?, ?, ?, ?)
        """, user_id, symbol, -shares, price)

        return redirect("/")

    else:
        # For GET: show stocks user owns
        user_id = session["user_id"]
        rows = db.execute("""
            SELECT symbol, SUM(shares) as total_shares
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING total_shares > 0
        """, user_id)

        return render_template("sell.html", stocks=rows)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount"))
        except:
            return apology("Invalid amount", 400)

        if amount <= 0:
            return apology("Amount must be positive", 400)

        user_id = session["user_id"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, user_id)
        return redirect("/")

    else:
        return render_template("add_cash.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current = request.form.get("current_password")
        new = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        if not current or not new or not confirm:
            return apology("Must fill out all fields", 400)

        if new != confirm:
            return apology("Passwords don't match", 400)

        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(user[0]["hash"], current):
            return apology("Incorrect current password", 400)

        new_hash = generate_password_hash(new)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, session["user_id"])

        return redirect("/")

    else:
        return render_template("change_password.html")
