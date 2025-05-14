from flask import Flask, render_template, url_for, request, redirect, flash
from models.admin import Admin
from abc import ABC, abstractmethod
from enum import Enum
# import matplotlib.pyplot as plt

# Initialize Flask app and set static folder
app = Flask(__name__, 
            static_url_path='',
            static_folder='static')
app.secret_key = "your_secret_key"

# hard coded admin acccount; use database soon
admin_account = Admin(username="admin", password="admin123", otp_authentication=False)

# root route redirects to index page
@app.route("/")
def home():
    print("Home route accessed")
    return render_template("user-login.html")

@app.route("/index")
@app.route("/index.html")
def index_html():
    print("Index route accessed")
    return render_template("index.html")

# Services route
@app.route("/services")
@app.route("/services.html")
def services_html():
    print("Services route accessed")
    return render_template("services.html")

# Tracking route
@app.route("/tracking")
@app.route("/tracking.html")
def tracking_html():
    print("Tracking route accessed")
    return render_template("tracking.html")

# FAQ route
@app.route("/FAQ")
@app.route("/FAQ.html")
def faq_html():
    print("FAQ route accessed")
    return render_template("FAQ.html")

@app.route("/admin-login")
@app.route("/admin-login.html")
def admin_login():
    print("Admin login route accessed")
    return render_template("admin-login.html")

# User login route - add this to handle the direct link in navbar
@app.route("/user-login", methods=["GET", "POST"])
@app.route("/user-login.html", methods=["GET", "POST"])
def user_login_html():
    print("User login route accessed")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # check if admin credentials
        if admin_account.login(username, password):
            print("Admin login successful")
            return redirect(url_for("index_html"))
        else:
            flash("Wrong username or password.")
            return render_template("user-login.html")
    return render_template("user-login.html")

# user signup route
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