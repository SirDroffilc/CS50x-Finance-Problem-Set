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
@app.route("/logout") | 
The session clears (forgets) the user's id then redirected to '/' route, but the '/' route has been decorated with the login_required() function, so this essentially redirects to the login page, as per the login_required() in helpers.py

#### Quote Stocks
@app.route("/quote") | 
If requested via GET, it returns 'quote.html' which has a form that collects a stock symbol, submitted with action '/quote' and method 'post'.
If requested via POST, the symbol is passed into the lookup() function, which returns a dictionary with keys 'symbol' and 'price'. Then, it returns 'quoted.html' that shows the stock's symbol and price.

#### Buy Stocks
@app.route("/buy") | 
If requested via GET, it returns 'buy.html' which has a form that collects stock symbol and number of shares the user wants to buy, submitted with action '/buy' and method 'post'.
If requested via POST, the lookup() function is called on the symbol, the logged in user's cash is collected from the database, and the total price of the purchase is calculated. Then, the transaction is inserted into the database and the cash is updated in the database as well to reflect the purchase.

#### View Stock Portfolio (Homepage)
@app.route("/") | 
The current user's transactions is collected from the database, as well as his cash. Then, a for loop is used to assign new keys to each stock that represent different information about it such as price, total value of each stock, and to get the total value of all stocks. Then, this route returns 'index.html' that shows all of these information in a table. 

#### Sell Stocks
@app.route("/sell" | 
First, the user's stocks are collected from the database 'transactions' table and all of his information from the 'users' table. Then, a for loop is used to assign informative keys to each stock. 
If requested via GET, this route returns 'sell.html', which has a form that lets the user choose what stock he wants to sell from all of his currently owned stocks, as well as the number of shares he want to sell. This is submitted with action '/sell' and method 'post'.
If requested via POST, the sale is inserted into the 'transactions' table in the database. Then the cash is updated to reflect the sale. The user is then redirected to the homepage.


#### View Transaction History
@app.route("/history")
All transactions are collected from the database. Then, this simply returns 'history.html', which has a table that displays all the user's previous transactions.

#### Change Password
@app.route("/account")
(This is the feature that I implemented myself, separate from the required features by CS50).
If requested via GET, it returns 'account.html', which has a form that collects the old password, new password, and confirmation password. This is submitted with the action 'account' and method 'post'. 
If requested via POST, the new password is hashed. Then, the database is updated to change the user's password with this new password. The user is then redirected to the same route.

## How to run?
Simply download the whole repository and install the necessary imported libraries by using the terminal and executing 'pip install <library>'. Then, you can execute 'flask run' in the terminal to run a server for the web app. Just click the link in the terminal to use the web app. 
