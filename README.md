# CS50x Finance
by Ford Torion

## Description
A web app that simulates a user who can register and log in an account, get stock quotes, buy stocks, sell stocks, view transaction history, and view his stock portfolio.

## Distribution Code
Like other problem sets in CS50x, the Finance distribution code comes with pre-written code by the CS50 staff like the helpers.py which has the lookup() function that uses Yahoo API to get stock information from the Yahoo stock market. As the student taking this course, my task was to create the necessary HTML templates, create the necessary tables in the database, and most importantly, develop the back-end routes of the web app.

## Technologies Used
#### Front-End: HTML (with Jinja), CSS (with Bootstrap)
#### Back-End: Python with Flask
#### Database: SQL from cs50 library
#### API: Yahoo Finance API

## SQL Tables
This section shows the database tables implemented in the web app.
#### TABLE users
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00);
#### TABLE transactions
CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, username TEXT NOT NULL,
symbol TEXT NOT NULL, num_shares INTEGER NOT NULL, total_price DECIMAL NOT NULL, date DATETIME NOT NULL, type TEXT NOT NULL DEFAULT "purchase", FOREIGN KEY(user_id) REFERENCES users(id));

## Features and Routes
This section explains how the features of the web app works.

#### Register an Account (username and password)
@app.route("/register") | In this route, first, the session is cleared to forget the previous logged in user id. 
If requested via GET, it returns 'register.html', which has a form that collects username, password, and password confirmation. This form is submitted with the action '/register' and method 'post'.
If requested via POST, the the route validates the details and if valid, it adds the new account to the database in the 'users' table, with the password being hashed.
Then, session['user_id'] is set to the database id of the account to remember the user. Finally, they are automatically logged in and redirected to the homepage (stock portfolio).

#### Log In 
@app.route("/login") | First, the session is cleared.
If requested via GET, it returns 'login.html', which has a form that collects username and password, submitted with action '/login' and method 'post'.
If requested via POST, it checks if the details are in the database 'users' table. If it is, then the session remembers the user's id and redirected to the homepage (stock portfolio)
Additionally, this is the default page of the web app if there is no currently logged in user. This is defined in the login_required() function in helpers.py.

#### Log Out
@app.route("/logout")
The session clears (forgets) the user's id then redirected to '/' route, but the '/' route has been decorated with the login_required() function, so this essentially redirectes to the login page.

#### Quote Stocks

#### Buy Stocks

#### View Stock Portfolio (Homepage)

#### Sell Stocks

#### View Transaction History
