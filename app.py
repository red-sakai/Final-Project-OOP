from flask import Flask, render_template, url_for, request, redirect, flash
from models.admin import Admin
from abc import ABC, abstractmethod
from enum import Enum
from flask_mail import Mail, Message
import random

# Initialize Flask app and set static folder
app = Flask(__name__, 
            static_url_path='',
            static_folder='static')
app.secret_key = "your_secret_key"

# flask-mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jheredmiguelrepublica14@gmail.com'
app.config['MAIL_PASSWORD'] = 'mehf kygg amjr kedv'

mail = Mail(app)

# encapsulated password reset manager
class PasswordResetManager:
    def __init__(self):
        self.__user_otps = {}  # double underscore for strong encapsulation

    def generate_otp(self, email):
        otp = str(random.randint(100000, 999999))
        self.__user_otps[email] = otp
        return otp

    def send_otp(self, email, otp):
        msg = Message("HexaHaul Password Reset OTP",
                      sender="hexahaulprojects@gmail.com",
                      recipients=[email])
        msg.body = f"Your OTP for password reset is: {otp}"
        mail.send(msg)

    def verify_otp(self, email, otp):
        return self.__user_otps.get(email) == otp

    def clear_otp(self, email):
        self.__user_otps.pop(email, None)

password_reset_manager = PasswordResetManager()

# hard coded admin acccount; use database soon
admin_account = Admin(username="admin", password="admin123", otp_authentication=False)

@app.route("/")
def home():
    print("Home route accessed")
    return render_template("user-login.html")

@app.route("/index")
@app.route("/index.html")
def index_html():
    print("Index route accessed")
    return render_template("index.html")

@app.route("/services")
@app.route("/services.html")
def services_html():
    print("Services route accessed")
    return render_template("services.html")

@app.route("/tracking")
@app.route("/tracking.html")
def tracking_html():
    print("Tracking route accessed")
    return render_template("tracking.html")

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

@app.route("/user-login", methods=["GET", "POST"])
@app.route("/user-login.html", methods=["GET", "POST"])
def user_login_html():
    print("User login route accessed")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if admin_account.login(username, password):
            print("Admin login successful")
            return redirect(url_for("index_html"))
        else:
            flash("Wrong username or password.")
            return render_template("user-login.html")
    return render_template("user-login.html")

@app.route("/user-signup")
@app.route("/user-signup.html")
def user_signup_html():
    print("User signup route accessed")
    return render_template("user-signup.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        # TODO: Check if email exists in your user database
        otp = password_reset_manager.generate_otp(email)
        password_reset_manager.send_otp(email, otp)
        flash("OTP sent to your email. Please check your inbox.")
        return redirect(url_for("verify_otp", email=email))
    return render_template("forgot-password.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = request.args.get("email")
    if request.method == "POST":
        input_otp = request.form.get("otp")
        new_password = request.form.get("new_password")
        if password_reset_manager.verify_otp(email, input_otp):
            # TODO: Update user's password in your database
            password_reset_manager.clear_otp(email)
            flash("Password changed successfully. Please login.")
            return redirect(url_for("user_login_html"))
        else:
            flash("Invalid OTP. Please try again.")
    return render_template("verify-otp.html", email=email)

if __name__ == "__main__":
    app.debug = True
    print("Flask app routes:")
    print(app.url_map)
    app.run(host='0.0.0.0', port=5000, debug=True)