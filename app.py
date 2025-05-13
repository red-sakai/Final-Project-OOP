from flask import Flask, render_template, url_for
from abc import ABC, abstractmethod
from enum import Enum
# import matplotlib.pyplot as plt

# Initialize Flask app and set static folder
app = Flask(__name__, 
            static_url_path='',
            static_folder='static')

# Root route redirects to index page
@app.route("/")
def home():
    print("Home route accessed")
    return render_template("index.html")

# Index route (handles both '/index' and '/index.html')
@app.route("/index")
@app.route("/index.html")
def index_html():  # Changed to match the function name used in navbar
    print("Index route accessed")
    return render_template("index.html")

# Services route
@app.route("/services")
@app.route("/services.html")
def services_html():  # Using consistent naming that matches navbar
    print("Services route accessed")
    return render_template("services.html")

# Tracking route
@app.route("/tracking")
@app.route("/tracking.html")
def tracking_html():  # Using consistent naming that matches navbar
    print("Tracking route accessed")
    return render_template("tracking.html")

# FAQ route
@app.route("/FAQ")
@app.route("/FAQ.html")  # Be consistent with capitalization
def faq_html():  # Using consistent naming that matches navbar
    print("FAQ route accessed")
    return render_template("FAQ.html")

@app.route("/admin-login")
@app.route("/admin-login.html")
def admin_login():
    print("Admin login route accessed")
    return render_template("admin-login.html")

# User login route - add this to handle the direct link in navbar
@app.route("/user-login")
@app.route("/user-login.html")
def user_login_html():
    print("User login route accessed")
    return render_template("user-login.html")

# User signup route
@app.route("/user-signup")
@app.route("/user-signup.html")
def user_signup_html():
    print("User signup route accessed")
    return render_template("user-signup.html")

if __name__ == "__main__":
    app.debug = True
    print("Flask app routes:")
    print(app.url_map)
    app.run(host='0.0.0.0', port=5000, debug=True)