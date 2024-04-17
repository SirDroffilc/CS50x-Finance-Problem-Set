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
    """Show portfolio of stocks"""
    stocks = db.execute("SELECT symbol, SUM(num_shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    stocks_total = 0

    for stock in stocks:
        quote = lookup(stock["symbol"])
        stock["price"] = quote["price"]
        stock["total_value"] = quote["price"] * stock["total_shares"]
        stocks_total += stock["total_value"]

    grand_total = stocks_total + cash

    return render_template("index.html", stocks=stocks, cash=cash, grand_total=grand_total, stocks_total=stocks_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        quote = lookup(symbol)
        if not symbol or not shares:
            return apology("incomplete details")
        elif not quote:
            return apology("invalid symbol")
        elif not shares.isdigit() or int(shares) <= 0:
            return apology("invalid shares")

        shares = int(shares)
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
        total_price = shares * quote['price']

        if user['cash'] < total_price:
            return apology("not enough cash")

        db.execute("""INSERT INTO transactions (user_id, username, symbol, num_shares, total_price, date, type)
                   VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                   """, session["user_id"], user["username"], symbol, shares, total_price, "purchase")

        db.execute("UPDATE users SET cash = ? WHERE id = ?", user['cash'] - total_price, session['user_id'])

        flash(f"Successfully purchased {shares} shares of {symbol} for {usd(total_price)}")

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", session['user_id'])
    for transaction in transactions:
        if transaction["num_shares"] < 0:
            transaction["num_shares"] *= -1

    return render_template("history.html", transactions=transactions)


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
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol")
        return render_template("quoted.html", quote=quote, usd_func=usd)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")

        # validation
        if not username or len(username) < 3:
            return apology("invalid username", 400)
        elif not password1 or len(password1) < 3:
            return apology("invalid password", 400)
        elif not password2 or (password1 != password2):
            return apology("passwords don't match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username already exists", 400)

        hashed = generate_password_hash(password1)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    stocks = db.execute("SELECT symbol, SUM(num_shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    for stock in stocks:
        quote = lookup(stock["symbol"])
        stock["price"] = quote["price"]
        stock["total_value"] = quote["price"] * stock["total_shares"]

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        quote = lookup(symbol)
        if not symbol or not shares:
            return apology("incomplete details")
        elif not quote:
            return apology("invalid symbol")
        elif not shares.isdigit() or int(shares) <= 0:
            return apology("invalid shares")
        shares = int(shares)

        for stock in stocks:
            if stock["symbol"] == symbol:
                if shares > stock["total_shares"]:
                    return apology("not enough owned shares")
                else:
                    sale = shares * stock["price"]
                    db.execute("""INSERT INTO transactions (user_id, username, symbol, num_shares, total_price, date, type)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                    """, session["user_id"], user["username"], symbol, -shares, sale, "sale")
                    db.execute("UPDATE users SET cash = ? WHERE id = ?", user["cash"] + sale, session['user_id'])
                    flash(f"Successfully sold {shares} shares of {symbol} for {usd(sale)}")

                    return redirect("/")

    else:
        return render_template("sell.html", stocks=stocks)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])[0]

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not old_password or not new_password or not confirmation:
            return apology("incomplete details")
        elif not check_password_hash(user['hash'], old_password):
            return apology("incorrect old password")
        elif new_password != confirmation:
            return apology("new password and confirmation do not match")

        hashed = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed, user['id'])
        flash("Successfully changed password")

        return redirect("/account")

    else:
        return render_template("account.html", user=user)
