from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, Blueprint, send_from_directory, session
from models.admin import Admin
from models.analytics_backend import plot_employee_statuses, plot_vehicles_deployed
from models.vehicle_database import VehicleDatabase, Vehicle
from models.employee_database import EmployeeDatabase, Employee
from models.hexaboxes_database import HexaBoxesDatabase, Order
from models.user_login_database import init_db, load_users_from_csv, authenticate_user
from models.admin_database import init_admin_db, get_db_session, Admin, get_default_admin
from models.utilities_database import UtilitiesDatabase
from models.salary_database import SalaryDatabase, EmployeeSalary
from models.products_database import ProductsDatabase, Product
from models.sales_database import SalesDatabase
from abc import ABC, abstractmethod
from enum import Enum
from flask_mail import Mail, Message
from flask_moment import Moment
from transformers import pipeline
from services.hexabot import hexabot_bp
from models.activity_database import ActivityDatabase
from models.customers_database import CustomerDatabase
import csv
import time
import os
import json
import random
import pandas as pd
from werkzeug.utils import secure_filename
import requests
from datetime import datetime, timedelta
import uuid
from markupsafe import Markup
from sqlalchemy import create_engine, text
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_mysql_connection():
    """Create and return a MySQL connection for hh_user_login_db table access using .env credentials."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT"))
    )

def get_qa_pipeline():
    """Lazily load and cache the QA pipeline to avoid OOM on startup."""
    # Lazy Load - delaying the initialization to save memory
    if not hasattr(get_qa_pipeline, "_pipeline"):
        get_qa_pipeline._pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
    return get_qa_pipeline._pipeline

class BaseManager(ABC):
    @abstractmethod
    def generate_otp(self, email):
        pass

    @abstractmethod
    def send_otp(self, email, otp):
        pass

    @abstractmethod
    def verify_otp(self, email, otp):
        pass

    @abstractmethod
    def clear_otp(self, email):
        pass

class PasswordResetManager(BaseManager):
    def __init__(self, mail):
        self.__user_otps = {}
        self.mail = mail

    def get_otp(self, email):
        return self.__user_otps.get(email)

    def set_otp(self, email, otp):
        self.__user_otps[email] = otp

    def generate_otp(self, email):
        otp = str(random.randint(100000, 999999))
        self.__user_otps[email] = otp
        return otp

    def send_otp(self, email, otp):
        logo_url = "https://i.imgur.com/upLAusA.png"
        msg = Message("Forgot Password Code: " + otp,
                      sender="hexahaulprojects@gmail.com",
                      recipients=[email])
        msg.html = f"""
        <div style="background:#f7f7f7;padding:40px 0;">
          <div style="max-width:480px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="background:#e6e9ef;padding:24px 0;text-align:center;">
              <img src="{logo_url}" alt="HexaHaul Logo" style="width:64px;height:64px;margin-bottom:8px;">
              <h2 style="margin:0;font-family:sans-serif;color:#03335e;">Forgot Password Code</h2>
            </div>
            <div style="padding:32px 24px;text-align:center;">
              <p style="font-family:sans-serif;color:#333;font-size:16px;margin-bottom:24px;">
                Here's your forgot password code:
              </p>
              <div style="font-size:36px;letter-spacing:12px;font-family:monospace;color:#03335e;font-weight:bold;margin-bottom:16px;">
                {otp}
              </div>
              <p style="font-family:sans-serif;color:#888;font-size:14px;">
                This code will expire soon.
              </p>
            </div>
            <div style="padding:16px 24px 24px 24px;font-family:sans-serif;font-size:13px;color:#888;text-align:center;">
              If this request did not come from you, change your account password immediately to prevent unauthorized access.
            </div>
          </div>
        </div>
        """
        self.mail.send(msg)

    def send_admin_otp(self, email, otp):
        logo_url = "https://i.imgur.com/upLAusA.png"
        msg = Message("Admin Password Reset Code: " + otp,
                      sender="hexahaulprojects@gmail.com",
                      recipients=[email])
        msg.html = f"""
        <div style="background:#f7f7f7;padding:40px 0;">
          <div style="max-width:480px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="background:#e6e9ef;padding:24px 0;text-align:center;">
              <img src="{logo_url}" alt="HexaHaul Logo" style="width:64px;height:64px;margin-bottom:8px;">
              <h2 style="margin:0;font-family:sans-serif;color:#03335e;">Admin Password Reset Code</h2>
            </div>
            <div style="padding:32px 24px;text-align:center;">
              <p style="font-family:sans-serif;color:#333;font-size:16px;margin-bottom:24px;">
                Here is your admin password reset code:
              </p>
              <div style="font-size:36px;letter-spacing:12px;font-family:monospace;color:#03335e;font-weight:bold;margin-bottom:16px;">
                {otp}
              </div>
              <p style="font-family:sans-serif;color:#888;font-size:14px;">
                This code is for admin use only and will expire soon.
              </p>
            </div>
            <div style="padding:16px 24px 24px 24px;font-family:sans-serif;font-size:13px;color:#888;text-align:center;">
              If you did not request this, please contact HexaHaul support immediately.
            </div>
          </div>
        </div>
        """
        self.mail.send(msg)

    def verify_otp(self, email, otp):
        return self.__user_otps.get(email) == otp

    def clear_otp(self, email):
        self.__user_otps.pop(email, None)

class UserPasswordResetManager(PasswordResetManager):
    def send_otp(self, email, otp):
        super().send_otp(email, otp)

class AdminPasswordResetManager(PasswordResetManager):
    def send_otp(self, email, otp):
        self.send_admin_otp(email, otp)

class HexaHaulApp:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        self.app = Flask(__name__, 
                         static_url_path='', 
                         static_folder='static',
                         template_folder=template_dir)
        
        self.app.secret_key = "your_secret_key"
        self.configure_mail()
        self.user_password_reset_manager = UserPasswordResetManager(self.mail)
        self.admin_password_reset_manager = AdminPasswordResetManager(self.mail)
        
        # Initialize admin database
        init_admin_db()
        
        # Get or create default admin account
        self.admin_account = get_default_admin()
        
        self.vehicle_db = VehicleDatabase()
        self.employee_db = EmployeeDatabase()
        self.hexabox_db = HexaBoxesDatabase()
        self.salary_db = SalaryDatabase()
        self.product_db = ProductsDatabase()
        self.activity_db = ActivityDatabase()
        
        print(f"Template folder: {template_dir}")
        print(f"Template folder exists: {os.path.exists(template_dir)}")
        
        with self.app.app_context():
            init_db()
            load_users_from_csv()
            
        self.register_routes()
        self.register_blueprints()
        self.register_template_filters()
        self.moment = Moment(self.app)

    def configure_mail(self):
        self.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        self.app.config['MAIL_PORT'] = 587
        self.app.config['MAIL_USE_TLS'] = True
        self.app.config['MAIL_USERNAME'] = 'hexahaulprojects@gmail.com'
        self.app.config['MAIL_PASSWORD'] = 'ikai nagb zyna hjoc'
        self.mail = Mail(self.app)

    def register_template_filters(self):
        """Register custom template filters for the application"""
        
        @self.app.template_filter('number_format')
        def number_format_filter(value):
            if isinstance(value, (int, float)):
                return "{:,}".format(value)
            return value

    def register_routes(self):
        app = self.app
        user_password_reset_manager = self.user_password_reset_manager
        admin_password_reset_manager = self.admin_password_reset_manager
        admin_account = self.admin_account
        vehicle_db = self.vehicle_db

        @app.route("/user-login", methods=["GET", "POST"])
        @app.route("/user-login.html", methods=["GET", "POST"])
        def user_login_html():
            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")

                # Only use MySQL authentication
                user = authenticate_user_mysql(username, password)

                if user:
                    session["logged_in"] = True
                    session["user_name"] = user["full_name"]  # For backwards compatibility
                    session["full_name"] = user["full_name"]  # Make sure this is set
                    session["user_email"] = user["email"]
                    session["username"] = user["username"]
                    session["user_image"] = user.get("user_image", "images/pfp.png")
                    
                    # Log the login activity
                    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
                    user_agent = request.environ.get('HTTP_USER_AGENT', '')
                    
                    self.activity_db.log_activity(
                        username=user["username"],
                        email=user["email"],
                        activity_type="LOGIN",
                        description=f"User logged in successfully",
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    
                    return redirect(url_for("index_html"))
                else:
                    error_message = "Invalid username or password. Please try again."
                    return render_template("user-login.html", error=error_message)
            
            return render_template("user-login.html")

        def authenticate_user_mysql(username, password):
            """
            Authenticate user against MySQL hh_user_login_db table.
            Returns user dict if found, else None.
            """
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT * FROM hh_user_login
                    WHERE (Username = %s OR username = %s) AND Password = %s
                    LIMIT 1
                """
                cursor.execute(query, (username, username, password))
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row:
                    return {
                        'full_name': row.get('full_name') or row.get('Full Name') or row.get('Full_Name') or username,
                        'email': row.get('email_address') or row.get('Email_Address') or row.get('email'),
                        'username': row.get('Username') or row.get('username'),
                        'user_image': row.get('profile_image') or row.get('Profile Image') or row.get('Profile_Image') or row.get('user_image', 'images/pfp.png')
                    }
            except Exception as e:
                print(f"Error authenticating user from MySQL: {e}")
            return None

        @app.route("/logout")
        def logout():
            # Log the logout activity before clearing session
            if "username" in session and "user_email" in session:
                self.activity_db.log_activity(
                    username=session["username"],
                    email=session["user_email"],
                    activity_type="LOGOUT",
                    description="User logged out",
                    ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '')),
                    user_agent=request.environ.get('HTTP_USER_AGENT', '')
                )
            
            session.clear()
            return redirect(url_for("user_login_html"))

        @app.route("/api/user-activities")
        def get_user_activities():
            """API endpoint to get user activities for the sidebar"""
            if "logged_in" not in session or not session["logged_in"]:
                return jsonify({"error": "Not logged in"}), 401
            
            username = session.get("username")
            email = session.get("user_email")
            
            if not username and not email:
                return jsonify({"error": "No user identifier found"}), 400
            
            # Get recent activities for the user
            activities = self.activity_db.get_recent_activities(
                username=username, 
                email=email, 
                limit=10
            )
            
            # Format activities for display
            formatted_activities = []
            for activity in activities:
                formatted = self.activity_db.format_activity_for_display(activity)
                formatted_activities.append(formatted)
            
            return jsonify({"activities": formatted_activities})

        @app.route("/user-dashboard")
        def user_dashboard():
            if "logged_in" not in session or not session["logged_in"]:
                return redirect(url_for("user_login_html"))

            return render_template("user-dashboard.html", user_name=session.get("user_name"))

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

        @app.route("/tracking", methods=["GET", "POST"])
        @app.route("/tracking.html", methods=["GET", "POST"])
        def tracking_html():
            error_message = None
            if request.method == "POST":
                order_item_id = request.form.get("tracking_id", "").strip()
                # Validate order_item_id in MySQL
                try:
                    conn = get_mysql_connection()
                    cursor = conn.cursor()
                    query = "SELECT 1 FROM hh_order WHERE order_item_id = %s LIMIT 1"
                    cursor.execute(query, (order_item_id,))
                    exists = cursor.fetchone() is not None
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Error validating order_item_id in MySQL: {e}")
                    exists = False
                if exists:
                    return redirect(url_for("parceltracking", tracking_id=order_item_id))
                else:
                    error_message = "Invalid Tracking ID. Please enter a valid Order Item Id."
            return render_template("tracking.html", error=error_message)

        @app.route("/validate-order-item-id", methods=["POST"])
        def validate_order_item_id():
            data = request.get_json()
            order_item_id = data.get("order_item_id", "").strip()
            exists = False
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                query = "SELECT 1 FROM hh_order WHERE order_item_id = %s LIMIT 1"
                cursor.execute(query, (order_item_id,))
                exists = cursor.fetchone() is not None
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error validating order_item_id in MySQL: {e}")
            return jsonify({"exists": exists})

        @app.route("/FAQ")
        @app.route("/FAQ.html")
        def faq_html():
            print("FAQ route accessed")
            return render_template("FAQ.html")

        @app.route("/sidebar")
        @app.route("/sidebar.html")
        def sidebar_html():
            print("Sidebar route accessed")
            return render_template("sidebar.html")

        @app.route("/admin-login")
        @app.route("/admin-login.html")
        def admin_login_redirect():
            """Redirect from /admin-login to /admin/login"""
            return redirect(url_for('admin_login'))

        @app.route("/admin/login", methods=["GET", "POST"])
        def admin_login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                # Try to authenticate with MySQL first
                found_admin = authenticate_admin_mysql(username, password)

                if found_admin:
                    # Set admin session
                    session['admin_id'] = found_admin.get('admin_username')
                    session['admin_username'] = found_admin.get('admin_username')
                    session['admin_name'] = f"{found_admin.get('admin_fname', '')} {found_admin.get('admin_lname', '')}".strip()
                    return redirect(url_for('admin_dashboard'))
                else:
                    # Fallback to SQLAlchemy authentication if not found in MySQL
                    db_session = get_db_session()
                    try:
                        admin = Admin.authenticate(db_session, username, password)
                        if admin:
                            session['admin_id'] = admin.id
                            session['admin_username'] = admin.admin_username
                            session['admin_name'] = f"{admin.admin_fname} {admin.admin_lname}"
                            return redirect(url_for('admin_dashboard'))
                        else:
                            flash('Invalid username or password', 'error')
                    finally:
                        db_session.close()

            return render_template('admin-login.html')

        def authenticate_admin_mysql(username, password):
            """
            Authenticate admin against MySQL hh_admins table.
            Returns admin dict if found, else None.
            """
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT * FROM hh_admins
                    WHERE (admin_username = %s) AND (admin_password = %s)
                    LIMIT 1
                """
                cursor.execute(query, (username, password))
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row:
                    return {
                        'admin_username': row.get('admin_username'),
                        'admin_fname': row.get('admin_fname'),
                        'admin_lname': row.get('admin_lname'),
                        'admin_email': row.get('admin_email')
                    }
            except Exception as e:
                print(f"Error authenticating admin from MySQL: {e}")
            return None

        @app.route("/admin/dashboard")
        def admin_dashboard():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
                
            # Get admin info from session
            admin_name = session.get('admin_name')
            
            return render_template('admin-dashboard.html', admin_name=admin_name)

        @app.route("/admin/forgot-password")
        def admin_forgot_password_page():
            """Route for admin forgot password page"""
            return render_template("admin-forgot-password.html")
            
        @app.route("/admin/forgot-password/submit", methods=["POST"])
        def admin_forgot_password_submit():
            """Handle admin forgot password form submission"""
            email = request.form.get("email")
            
            # Check if email exists in admin database (MySQL hh_admins table)
            email_found = False
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                
                # Query to check if email exists in admin_email column
                query = "SELECT 1 FROM hh_admins WHERE admin_email = %s LIMIT 1"
                cursor.execute(query, (email,))
                email_found = cursor.fetchone() is not None
                
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error checking admin email in MySQL: {e}")
            
            if email_found:
                # Generate and send OTP
                otp = admin_password_reset_manager.generate_otp(email)
                admin_password_reset_manager.send_otp(email, otp)
                return redirect(url_for('admin_verification_code', email=email))
            else:
                # Email not found
                flash("Email not found in admin records", "error")
                return render_template("admin-forgot-password.html", error="Email not found in admin records")

        @app.route("/admin/logout")
        def admin_logout():
            # Clear admin session
            session.pop('admin_id', None)
            session.pop('admin_username', None)
            session.pop('admin_name', None)
            
            flash('You have been logged out', 'success')
            return redirect(url_for('admin_login'))

        @app.route("/user-signup")
        @app.route("/user-signup.html")
        def user_signup_html():
            print("User signup route accessed")
            return render_template("user-signup.html")

        @app.route('/register', methods=['GET'])
        def register_form():
            return render_template('user-signup.html')

        @app.route("/forgot-password", methods=["GET", "POST"])
        def forgot_password():
            if request.method == "POST":
                email = request.form.get("email")
                
                # Check if email exists in MySQL hh_user_login table
                email_found = False
                try:
                    conn = get_mysql_connection()
                    cursor = conn.cursor()
                    
                    # Query to check if email exists in email_address column
                    query = "SELECT 1 FROM hh_user_login WHERE email_address = %s LIMIT 1"
                    cursor.execute(query, (email,))
                    email_found = cursor.fetchone() is not None
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Error checking email in MySQL: {e}")
                
                if not email_found:
                    flash("Email not found. Please use a registered email address.", "error")
                    return render_template("forgot-password.html", error="Email not found in user records")
                
                # If email is found, proceed with OTP generation and sending
                otp = user_password_reset_manager.generate_otp(email)
                user_password_reset_manager.send_otp(email, otp)
                flash("OTP sent to your email. Please check your inbox.")
                return redirect(url_for("verify_otp", email=email))
                
            return render_template("forgot-password.html")

        @app.route("/verify-otp", methods=["GET", "POST"])
        def verify_otp():
            email = request.args.get("email")
            if request.method == "POST":
                otp = ''.join([
                    request.form.get('otp1', ''),
                    request.form.get('otp2', ''),
                    request.form.get('otp3', ''),
                    request.form.get('otp4', ''),
                    request.form.get('otp5', ''),
                    request.form.get('otp6', ''),
                ])
                new_password = request.form.get("new_password")
                if user_password_reset_manager.verify_otp(email, otp):
                    user_password_reset_manager.clear_otp(email)
                    return redirect(url_for("change_password", email=email))
                else:
                    flash("Invalid OTP. Please try again.")
            return render_template("verify-otp.html", email=email)

        @app.route('/verification-code')
        def verification_code():
            email = request.args.get('email')
            return render_template('verification-code.html', email=email)

        @app.route('/admin-verification-code', methods=['GET', 'POST'])
        def admin_verification_code():
            email = request.values.get('email')
            if request.method == 'POST':
                otp = ''.join([request.form.get(f'otp{i}', '') for i in range(1, 7)])
                if admin_password_reset_manager.verify_otp(email, otp):
                    admin_password_reset_manager.clear_otp(email)
                    return redirect(url_for('admin_new_password', email=email))
                else:
                    flash("Invalid verification code. Please try again.")
            return render_template('verification-code.html', email=email, is_admin=True)

        @app.route('/admin-new-password', methods=['GET', 'POST'])
        def admin_new_password():
            email = request.values.get('email')
            if request.method == 'POST':
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                if new_password == confirm_password and len(new_password) >= 8:
                    # Update admin password in MySQL database
                    try:
                        conn = get_mysql_connection()
                        cursor = conn.cursor()
                        
                        # Update password in hh_admins table where admin_email matches
                        update_query = "UPDATE hh_admins SET admin_password = %s WHERE admin_email = %s"
                        cursor.execute(update_query, (new_password, email))
                        conn.commit()
                        
                        # Check if any rows were affected
                        if cursor.rowcount > 0:
                            flash("Password reset successful. Please login.", "success")
                        else:
                            flash("No account found with that email address.", "error")
                            
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        flash(f"Error updating admin password: {e}", "error")
                    return redirect(url_for('admin_login'))
                else:
                    flash("Passwords do not match or do not meet requirements.")
            return render_template('admin-new-password.html', email=email)

        @app.route('/admin-resend-otp', methods=['POST'])
        def admin_resend_otp():
            email = request.form.get('email')
            if email:
                otp = admin_password_reset_manager.generate_otp(email)
                admin_password_reset_manager.send_otp(email, otp)
                return jsonify({'success': True, 'message': 'Verification code resent.'})
            return jsonify({'success': False, 'message': 'Email not found.'}), 400

        @app.route("/truck")
        def truck_html():
            return render_template("truck.html")

        @app.route("/truck-book")
        def truck_book_html():
            return render_template("truck-book.html")

        @app.route("/truck-book2")
        def truck_book2_html():
            return render_template("truck-book2.html")

        @app.route("/truck-book3")
        def truck_book3_html():
            return render_template("truck-book3.html")

        @app.route("/motorcycle")
        def motorcycle_html():
            return render_template("motorcycle.html")

        @app.route("/motorcycle-book")
        def motorcycle_book_html():
            return render_template("motorcycle-book.html")

        @app.route("/motorcycle-book2")
        def motorcycle_book2_html():
            return render_template("motorcycle-book2.html")

        @app.route("/motorcycle-book3")
        def motorcycle_book3_html():
            return render_template("motorcycle-book3.html")

        @app.route("/car")
        def car_html():
            return render_template("car.html")

        @app.route("/carbook")
        def carbook_html():
            return render_template("carbook.html")

        @app.route("/carbook2")
        def carbook2_html():
            return render_template("carbook2.html")

        @app.route("/carbook3")
        def carbook3_html():
            return render_template("carbook3.html")

        @app.route("/parcel-tracker")
        def parcel_tracker():
            tracking_id = request.args.get("tracking_id", "")
            return render_template("parcel-tracker.html", tracking_id=tracking_id)

        def reverse_geocode(lat, lon):
            """Reverse geocode using Nominatim (OpenStreetMap)"""
            try:
                url = f"https://nominatim.openstreetmap.org/reverse"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "zoom": 12,
                    "addressdetails": 1
                }
                headers = {
                    "User-Agent": "HexaHaulParcelTracker/1.0"
                }
                resp = requests.get(url, params=params, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    address = data.get("address", {})
                    for key in ("city", "town", "village", "municipality", "county"):
                        if key in address:
                            return address[key]
                    return data.get("display_name", "Unknown Location")
            except Exception as e:
                print(f"Reverse geocoding failed: {e}")
            return "Unknown Location"

        @app.route("/parceltracking")
        def parceltracking():
            tracking_id = request.args.get("tracking_id", "")
            courier = None
            order_data = None
            
            if tracking_id:
                # Get order data from MySQL instead of CSV
                try:
                    conn = get_mysql_connection()
                    cursor = conn.cursor(dictionary=True)
                    
                    # Get product name from hh_product_info table
                    product_name = None
                    product_query = "SELECT `product_name` FROM hh_product_info WHERE `order_item_id` = %s LIMIT 1"
                    cursor.execute(product_query, (tracking_id,))
                    product_row = cursor.fetchone()
                    if product_row:
                        product_name = product_row['product_name'].strip()
                    
                    # Get order info from hh_order table
                    order_query = """
                        SELECT `order_item_id`, `delivery_status`, `origin_branch`, 
                        `branch_latitude`, `branch_longitude`, `customer_latitude`, `customer_longitude`,
                        `driver_id`, `order date (DateOrders)` 
                        FROM hh_order
                        WHERE `order_item_id` = %s
                        LIMIT 1
                    """
                    cursor.execute(order_query, (tracking_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        driver_id = int(row['driver_id']) if row['driver_id'] else None
                        order_date_str = row['order date (DateOrders)']
                        try:
                            order_date = datetime.strptime(order_date_str, "%Y-%m-%d")
                        except Exception:
                            order_date = None
                        offset_days = 5
                        expected_delivery_date = order_date + timedelta(days=offset_days) if order_date else None
                        expected_delivery_str = expected_delivery_date.strftime("%Y-%m-%d") if expected_delivery_date else "Unknown"
                        cust_lat = float(row['customer_latitude'])
                        cust_lon = float(row['customer_longitude'])
                        branch_lat = float(row['branch_latitude'])
                        branch_lon = float(row['branch_longitude'])
                        # reverse geocode
                        customer_place = reverse_geocode(cust_lat, cust_lon)
                        branch_place = reverse_geocode(branch_lat, branch_lon)
                        
                        order_data = {
                            'orderItemId': row['order_item_id'],
                            'deliveryStatus': row['delivery_status'],
                            'originBranch': row['origin_branch'],
                            'branchLatitude': branch_lat,
                            'branchLongitude': branch_lon,
                            'customerLatitude': cust_lat,
                            'customerLongitude': cust_lon,
                            'orderDate': order_date_str,
                            'expectedDeliveryDate': expected_delivery_str,
                            'customerPlace': customer_place,
                            'branchPlace': branch_place,
                            'driverId': driver_id,
                            'productName': product_name
                        }
                        
                        # Get courier (driver) info if driver_id is available
                        if driver_id:
                            courier_query = """
                                SELECT `employee_id`, `first_name`, `last_name`, `gender`, 
                                `age`, `birth_date`, `contact_number` 
                                FROM hh_employee_biography 
                                WHERE `employee_id` = %s
                                LIMIT 1
                            """
                            cursor.execute(courier_query, (driver_id,))
                            courier_row = cursor.fetchone()
                            if courier_row:
                                courier = {
                                    'employee_id': int(courier_row['employee_id']),
                                    'first_name': courier_row['first_name'],
                                    'last_name': courier_row['last_name'],
                                    'gender': courier_row['gender'],
                                    'age': int(courier_row['age']),
                                    'birthdate': courier_row['birth_date'],
                                    'contact_number': courier_row['contact_number']
                                }
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Error fetching order data from MySQL: {e}")

            return render_template("parceltracking.html", tracking_id=tracking_id, courier=courier, order_data=order_data)
            
        @app.route("/submit-ticket", methods=["GET", "POST"])
        def submit_ticket():
            if request.method == "POST":
                # Get form data
                ticket_title = request.form.get("ticket_title")
                ticket_description = request.form.get("ticket_description")
                error_code = request.form.get("error_code")
                tracking_id = request.form.get("tracking_id")
                user_email = request.form.get("user_email", "Unknown user")
                
                # Check if there are file attachments
                attachments = []
                attachment_paths = []  # <-- New: to store file paths
                if 'attachments' in request.files:
                    files = request.files.getlist('attachments')
                    for file in files:
                        if file and file.filename:
                            # Use werkzeug for secure and unique filenames
                            filename = secure_filename(
                                f"{str(uuid.uuid4())}_{int(time.time())}_{file.filename}"
                            )
                            upload_dir = os.path.join('static', 'support_attachments')
                            os.makedirs(upload_dir, exist_ok=True)
                            filepath = os.path.join(upload_dir, filename)
                            file.save(filepath)
                            # Store relative path for web access
                            rel_path = os.path.join('support_attachments', filename).replace('\\', '/')
                            attachment_paths.append(rel_path)
                            attachments.append(file)
                # Create email message
                msg = Message(
                    subject=f"Support Ticket: {ticket_title}",
                    sender="hexahaulprojects@gmail.com",
                    recipients=["hexahaulprojects@gmail.com"]
                )
                
                # Create HTML email body with styled formatting
                logo_url = "https://i.imgur.com/upLAusA.png"
                msg.html = f"""
                <div style="background:#f7f7f7;padding:40px 0;">
                  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    <div style="background:#03335e;padding:24px 0;text-align:center;">
                      <img src="{logo_url}" alt="HexaHaul Logo" style="width:64px;height:64px;margin-bottom:8px;">
                      <h2 style="margin:0;font-family:sans-serif;color:#fff;">New Support Ticket</h2>
                    </div>
                    
                    <div style="padding:32px 24px;">
                      <table style="width:100%;border-collapse:collapse;font-family:sans-serif;">
                        <tr>
                          <th style="text-align:left;padding:8px 12px;background:#eaf6fb;color:#03335e;border-radius:4px;">From:</th>
                          <td style="padding:8px 12px;">{user_email}</td>
                        </tr>
                        <tr>
                          <th style="text-align:left;padding:8px 12px;background:#eaf6fb;color:#03335e;border-radius:4px;">Subject:</th>
                          <td style="padding:8px 12px;font-weight:600;">{ticket_title}</td>
                        </tr>
                        <tr>
                          <th style="text-align:left;padding:8px 12px;background:#eaf6fb;color:#03335e;border-radius:4px;vertical-align:top;">Description:</th>
                          <td style="padding:8px 12px;white-space:pre-wrap;">{ticket_description}</td>
                        </tr>
                        <tr>
                          <th style="text-align:left;padding:8px 12px;background:#eaf6fb;color:#03335e;border-radius:4px;">Error Code:</th>
                          <td style="padding:8px 12px;font-family:monospace;">{error_code or 'Not provided'}</td>
                        </tr>
                        <tr>
                          <th style="text-align:left;padding:8px 12px;background:#eaf6fb;color:#03335e;border-radius:4px;">Tracking ID:</th>
                          <td style="padding:8px 12px;font-family:monospace;">{tracking_id or 'Not provided'}</td>
                        </tr>
                      </table>
                      
                      <div style="margin-top:24px;padding:16px;background:#f9f9f9;border-radius:4px;border-left:4px solid #1579c0;">
                        <h3 style="margin:0 0 12px 0;font-family:sans-serif;color:#03335e;">Attachments</h3>
                        <p style="margin:0;font-family:sans-serif;color:#555;font-size:14px;">
                          {f"{len(attachments)} file(s) attached" if attachments else "No attachments provided"}
                        </p>
                      </div>
                    </div>
                    
                    <div style="padding:16px 24px 24px 24px;background:#f0f7ff;text-align:center;font-family:sans-serif;font-size:14px;color:#555;">
                      <p style="margin:0;">This ticket was submitted through the HexaHaul support system.</p>
                      <p style="margin:6px 0 0 0;">Please handle according to support protocol.</p>
                    </div>
                  </div>
                </div>
                """
                
                # Add plain text alternative for email clients that don't support HTML
                msg.body = f"""
                New support ticket submitted:
                
                From: {user_email}
                Title: {ticket_title}
                
                Description:
                {ticket_description}
                
                Error Code: {error_code or 'Not provided'}
                Tracking ID: {tracking_id or 'Not provided'}
                """
                
                # Add attachments if any
                for file in attachments:
                    msg.attach(file.filename, 
                              'application/octet-stream', 
                              file.read())
                
                # Send the email
                self.mail.send(msg)
                
                # --- Append ticket to CSV ---
                ticket_id = str(uuid.uuid4())
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                csv_path = os.path.join('hexahaul_db', 'hh_support_tickets.csv')
                # Add attachments column (comma-separated paths)
                attachments_str = ",".join(attachment_paths) if attachment_paths else ""
                ticket_row = [
                    ticket_id,
                    user_email,
                    ticket_title,
                    ticket_description,
                    error_code,
                    tracking_id,
                    timestamp,
                    "",  # admin_reply
                    "",  # reply_timestamp
                    attachments_str  # <-- New column
                ]
                # Write header if file is empty
                write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
                try:
                    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        if write_header:
                            writer.writerow([
                                "ticket_id","user_email","ticket_title","ticket_description",
                                "error_code","tracking_id","timestamp","admin_reply","reply_timestamp","attachments"
                            ])
                        writer.writerow(ticket_row)
                except Exception as e:
                    print(f"Error writing support ticket to CSV: {e}")
                
                # Flash success message
                flash('Your support ticket has been submitted. Our team will get back to you shortly.', 'success')
                
                # Redirect back to sidebar page
                return redirect(url_for("sidebar_html", _anchor="ticket"))
                
            # GET request - just show the form
            return render_template("sidebar.html")

        @app.route("/personal-info")
        def personal_info():
            return render_template("personal-info.html")

        @app.route("/change-password", methods=["GET", "POST"])
        def change_password():
            if request.method == "POST":
                email = request.args.get("email") or request.form.get("email")
                new_password = request.form.get("new_password")
                if email and new_password:
                    # Update password in MySQL database
                    try:
                        conn = get_mysql_connection()
                        cursor = conn.cursor()
                        
                        # Update password in hh_user_login table where email_address matches
                        update_query = "UPDATE hh_user_login SET password = %s WHERE email_address = %s"
                        cursor.execute(update_query, (new_password, email))
                        conn.commit()
                        
                        # Check if any rows were affected
                        if cursor.rowcount > 0:
                            flash("Password updated successfully. Please login.", "success")
                        else:
                            flash("No account found with that email address.", "error")
                            
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        flash(f"Error updating password: {e}", "error")
                return redirect(url_for("user_login_html"))
            return render_template("change-password.html", email=request.args.get("email", ""))

        @app.route("/update-email")
        def update_email():
            return render_template("update-email.html")

        @app.route("/privacy-settings")
        def privacy_settings():
            return render_template("privacy-settings.html")

        @app.route("/language-region")
        def language_region():
            return render_template("language-region.html")

        @app.route("/recent-logins")
        def recent_logins():
            return render_template("recent-logins.html")

        @app.route("/recent-bookings")
        def recent_bookings():
            return render_template("recent-bookings.html")

        @app.route('/admin/employees')
        def admin_employees():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))

            # --- NEW: Read employees from MySQL hh_employee_biography ---
            employees = []
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM hh_employee_biography
                """)
                rows = cursor.fetchall()
                for row in rows:
                    emp_id = row.get('employee_id')
                    # Assign role based on employee_id
                    if emp_id is not None:
                        try:
                            emp_id_int = int(emp_id)
                        except Exception:
                            emp_id_int = None
                    else:
                        emp_id_int = None

                    # Default to DB value
                    role = row.get('role')
                    # Override role based on employee_id
                    if emp_id_int is not None:
                        if 1 <= emp_id_int <= 200:
                            # Alternate between Dispatcher and Manager for variety
                            role = 'Dispatcher' if emp_id_int % 2 == 0 else 'Manager'
                        elif 201 <= emp_id_int <= 240:
                            role = 'Driver'

                    # Generate random hire date in yyyy-mm-dd format
                    start_date = datetime(2018, 1, 1)
                    end_date = datetime(2023, 12, 31)
                    random_days = random.randint(0, (end_date - start_date).days)
                    random_hire_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

                    # Generate random status: mostly 'Active', some 'On Leave'
                    status = 'Active' if random.random() < 0.85 else 'On Leave'

                    employees.append({
                        'employee_id': emp_id,
                        'first_name': row.get('first_name'),
                        'last_name': row.get('last_name'),
                        'full_name': f"{row.get('first_name', '')} {row.get('last_name', '')}".strip(),
                        'gender': row.get('gender'),
                        'age': row.get('age'),
                        'birthdate': row.get('birth_date'),
                        'contact_number': row.get('contact_number'),
                        'email': row.get('email'),
                        'department': row.get('department'),
                        'role': role,
                        'hire_date': random_hire_date,
                        'license_number': row.get('license'),
                        'assigned_vehicle': row.get('assigned_vehicle'),
                        'status': status,
                    })
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error fetching employees from MySQL: {e}")

            # --- Fix: Convert date/datetime objects to string for JSON serialization ---
            def serialize_employee(emp):
                for key in ['birthdate', 'hire_date', 'license_expiry']:
                    if emp.get(key) is not None and hasattr(emp[key], 'isoformat'):
                        emp[key] = emp[key].isoformat()
                    elif emp.get(key) is not None and not isinstance(emp[key], str):
                        emp[key] = str(emp[key])
                return emp

            employees_json = json.dumps([serialize_employee(dict(e)) for e in employees])

            total_count = len(employees)
            manager_count = sum(1 for e in employees if e['role'] == 'Manager')
            driver_count = sum(1 for e in employees if e['role'] == 'Driver')
            active_count = sum(1 for e in employees if e['status'] == 'Active')

            # Get available vehicles from SQLAlchemy as before
            session2 = self.vehicle_db.connect()
            available_vehicles = session2.query(Vehicle).filter_by(status='Available').all()

            # Get admin name from Flask session
            admin_name = session.get('admin_name', 'Admin User')

            return render_template('admin_employees.html',
                                  employees=employees,
                                  total_count=total_count,
                                  manager_count=manager_count,
                                  driver_count=driver_count,
                                  active_count=active_count,
                                  available_vehicles=available_vehicles,
                                  employees_json=employees_json,
                                  admin_name=admin_name)

        @app.route('/admin/employees/add', methods=['POST'])
        def add_employee():
            data = {
                'employee_id': int(request.form.get('employee_id', 0)),
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'gender': request.form.get('gender', 'Male'),
                'age': int(request.form.get('age', 0)),
                'birthdate': request.form.get('birthdate'),
                'contact_number': request.form.get('phone_number'),
                'email': request.form.get('email'),
                'department': request.form.get('department'),
                'role': request.form.get('role'),
                'hire_date': request.form.get('hire_date'),
                'license_number': request.form.get('license_number'),
                'assigned_vehicle': int(request.form.get('assigned_vehicle')) if request.form.get('assigned_vehicle') else None,
                'status': request.form.get('status', 'Active')
            }
            
            self.employee_db.add_employee(**data)
            
            return redirect(url_for('admin_employees'))

        @app.route('/admin/employees/update', methods=['POST'])
        def update_employee():
            employee_id = int(request.form.get('employee_id'))
            
            data = {
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'gender': request.form.get('gender', 'Male'),
                'age': int(request.form.get('age', 0)),
                'birthdate': request.form.get('birthdate'),
                'contact_number': request.form.get('phone_number'),
                'email': request.form.get('email'),
                'department': request.form.get('department'),
                'role': request.form.get('role'),
                'hire_date': request.form.get('hire_date'),
                'license_number': request.form.get('license_number'),
                'assigned_vehicle': int(request.form.get('assigned_vehicle')) if request.form.get('assigned_vehicle') else None,
                'status': request.form.get('status')
            }
            
            self.employee_db.update_employee(employee_id, **data)
            
            return redirect(url_for('admin_employees'))

        @app.route('/admin/employees/delete', methods=['POST'])
        def delete_employee():
            employee_id = int(request.form.get('employee_id'))
            
            self.employee_db.delete_employee(employee_id)
            
            return redirect(url_for('admin_employees'))

        @app.route('/admin/hexaboxes')
        def admin_hexaboxes():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
                
            session_db = self.hexabox_db.connect()
            packages = session_db.query(Order).all()
            
            total_count = len(packages)
            transit_count = sum(1 for p in packages if p.delivery_status == "Shipping on time" or 
                                p.delivery_status == "Late delivery" or p.delivery_status == "Advance shipping")
            delivered_count = sum(1 for p in packages if p.order_status == "COMPLETE" or p.order_status == "CLOSED")
            pending_count = sum(1 for p in packages if p.order_status == "PENDING" or p.order_status == "PENDING_PAYMENT" or 
                                 p.order_status == "PAYMENT_REVIEW" or p.order_status == "ON_HOLD")
            
            vehicle_session = self.vehicle_db.connect()
            available_vehicles = vehicle_session.query(Vehicle).filter_by(status='Available').all()
            
            packages_json = json.dumps([{
                'tracking_id': p.order_item_id if p.order_item_id and p.order_item_id.strip() else p.tracking_id,
                'original_tracking_id': p.tracking_id,
                'order_id': p.order_id,
                'order_item_id': p.order_item_id,
                'sender': p.sender,
                'recipient': p.recipient,
                'origin': p.origin,
                'destination': p.destination,
                'package_size': p.package_size,
                'weight': p.weight,
                'date_shipped': p.date_shipped,
                'eta': p.eta,
                'assigned_vehicle': p.assigned_vehicle,
                'delivery_status': p.delivery_status,
                'order_status': p.order_status,
                'late_delivery_risk': p.late_delivery_risk,
                'notes': p.notes
            } for p in packages])
            
            self.hexabox_db.disconnect()
            self.vehicle_db.disconnect()
            
            # Get admin name from Flask session
            admin_name = session.get('admin_name', 'Admin User')
            
            return render_template('admin_hexaboxes.html', 
                                  packages=packages,
                                  total_count=total_count,
                                  transit_count=transit_count,
                                  delivered_count=delivered_count,
                                  pending_count=pending_count,
                                  available_vehicles=available_vehicles,
                                  packages_json=packages_json,
                                  admin_name=admin_name)

        @app.route('/admin/hexaboxes/add', methods=['POST'])
        def add_package():
            data = {
                'tracking_id': request.form.get('tracking_id'),
                'sender': request.form.get('sender'),
                'recipient': request.form.get('recipient'),
                'origin': request.form.get('origin'),
                'destination': request.form.get('destination'),
                'package_size': request.form.get('size'),
                'weight': float(request.form.get('weight')),
                'date_shipped': request.form.get('date_shipped'),
                'eta': request.form.get('eta'),
                'assigned_vehicle': request.form.get('assigned_vehicle_text'),
                'order_status': 'PENDING',
                'delivery_status': 'Shipping on time',
                'late_delivery_risk': False,
                'notes': request.form.get('notes', '')
            }
            
            self.hexabox_db.add_order(**data)
            
            return redirect(url_for('admin_hexaboxes'))

        @app.route('/admin/hexaboxes/update', methods=['POST'])
        def update_package():
            tracking_id = request.form.get('tracking_id')
            
            data = {
                'sender': request.form.get('sender'),
                'recipient': request.form.get('recipient'),
                'origin': request.form.get('origin'),
                'destination': request.form.get('destination'),
                'package_size': request.form.get('size'),
                'weight': float(request.form.get('weight')),
                'date_shipped': request.form.get('date_shipped'),
                'eta': request.form.get('eta'),
                'assigned_vehicle': request.form.get('assigned_vehicle_text'),
                'notes': request.form.get('notes', '')
            }
            
            status = request.form.get('status')
            if status == 'Delivered':
                data['order_status'] = 'COMPLETE'
                data['delivery_status'] = 'Shipping on time'
            elif status == 'In Transit':
                data['order_status'] = 'PROCESSING'
                data['delivery_status'] = 'Shipping on time'
            elif status == 'Pending':
                data['order_status'] = 'PENDING'
                data['delivery_status'] = 'Shipping on time'
            elif status == 'Returned':
                data['order_status'] = 'CANCELED'
                data['delivery_status'] = 'Shipping canceled'
            
            self.hexabox_db.update_order(tracking_id, **data)
            
            return redirect(url_for('admin_hexaboxes'))

        @app.route('/admin/hexaboxes/delete', methods=['POST'])
        def delete_package():
            tracking_id = request.form.get('tracking_id')
            
            self.hexabox_db.delete_order(tracking_id)
            
            return redirect(url_for('admin_hexaboxes'))

        @app.route('/admin/utilities')
        def admin_utilities():
            # Check if user is logged in as admin
            if 'admin_id' not in session:
                return redirect(url_for('admin_login'))
            
            # Get admin name from session
            admin_name = session.get('admin_name', 'Admin')
            
            # Use an absolute path for the database
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'hexahaul.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Initialize utilities database
            utilities_db = UtilitiesDatabase(db_path)
            
            # Get dashboard stats
            dashboard_stats = utilities_db.get_dashboard_stats()
            
            # Get initial chart data
            sales_data = utilities_db.get_sales_data()
            vehicle_status_data = utilities_db.get_vehicle_status_data()
            employee_performance_data = utilities_db.get_employee_performance_data()
            customer_growth_data = utilities_db.get_customer_growth_data()
            
            # Get table data
            sales_detail = utilities_db.get_sales_detail_data()
            vehicle_detail = utilities_db.get_vehicle_detail_data()
            employee_detail = utilities_db.get_employee_detail_data()
            
            # Convert chart data to JSON for JavaScript
            chart_data = {
                'sales': sales_data,
                'vehicles': vehicle_status_data,
                'employees': employee_performance_data,
                'customers': customer_growth_data
            }
            
            return render_template(
                'admin_utilities.html',
                admin_name=admin_name,
                stats=dashboard_stats,
                chart_data=json.dumps(chart_data),
                sales_detail=sales_detail,
                vehicle_detail=vehicle_detail,
                employee_detail=employee_detail
            )

        @app.route('/api/utilities/chart-data')
        def utilities_chart_data():
            # Check if user is logged in as admin
            if 'admin_id' not in session:
                return jsonify({'error': 'Unauthorized'}), 401
            
            chart_type = request.args.get('type', 'sales')
            time_range = request.args.get('timeRange', 'month')
            
            # Use an absolute path for the database
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'hexahaul.db')
            
            # Initialize utilities database
            utilities_db = UtilitiesDatabase(db_path)
            
            if chart_type == 'sales':
                data = utilities_db.get_sales_data(time_range)
            elif chart_type == 'vehicles':
                data = utilities_db.get_vehicle_status_data()
            elif chart_type == 'employees':
                data = utilities_db.get_employee_performance_data()
            elif chart_type == 'customers':
                data = utilities_db.get_customer_growth_data(time_range)
            else:
                return jsonify({'error': 'Invalid chart type'}), 400
            
            return jsonify(data)

        @app.route('/api/utilities/generate-report', methods=['POST'])
        def generate_report():
            # Check if user is logged in as admin
            if 'admin_id' not in session:
                return jsonify({'error': 'Unauthorized'}), 401
            
            report_type = request.form.get('reportType')
            time_range = request.form.get('reportTimeRange')
            report_format = request.form.get('reportFormat')
            
            # Use an absolute path for the database
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'hexahaul.db')
            
            # Initialize utilities database
            utilities_db = UtilitiesDatabase(db_path)
            result = utilities_db.generate_report(report_type, time_range, report_format)
            
            return jsonify(result)

        def generate_order_id(vehicle_type=None):
            """
            Generate an order ID with a prefix based on vehicle_type:
            - 'MC' for motorcycle, 'CR' for car, 'TK' for truck.
            Followed by 6-7 random digits.
            """
            import random
            prefix = 'CR'
            if vehicle_type == 'motorcycle':
                prefix = 'MC'
            elif vehicle_type == 'truck':
                prefix = 'TK'
            # 6 or 7 digits
            digits = str(random.randint(100000, 9999999))
            return f"{prefix}{digits}"

        @app.route("/payment-wall", methods=['GET', 'POST'])
        def payment_wall():
            # Get the source booking page from query param or form
            source = request.args.get('source') or request.form.get('source') or ''
            # Default prices (car based)
            price_data = {
                'base_fare': 200.00,
                'shipping_fee': 79.00,
                'service_fee': 20.00,
                'vehicle_name': 'Car'
            }
            vehicle_type = 'car'
            # Set prices based on source
            if source in ['motorcycle-book', 'motorcycle-book2', 'motorcycle-book3']:
                price_data = {
                    'base_fare': 80.00,
                    'shipping_fee': 39.00,
                    'service_fee': 10.00,
                    'vehicle_name': 'Motorcycle'
                }
                vehicle_type = 'motorcycle'
            elif source in ['carbook', 'carbook2', 'carbook3']:
                price_data = {
                    'base_fare': 200.00,
                    'shipping_fee': 79.00,
                    'service_fee': 20.00,
                    'vehicle_name': 'Car'
                }
                vehicle_type = 'car'
            elif source in ['truck-book', 'truck-book2', 'truck-book3']:
                price_data = {
                    'base_fare': 400.00,
                    'shipping_fee': 159.00,
                    'service_fee': 40.00,
                    'vehicle_name': 'Truck'
                }
                vehicle_type = 'truck'

            # --- Insert order into MySQL on POST ---
            if request.method == 'POST':
                # Extract order details from form
                order_item_id = request.form.get('order_item_id') or generate_order_id(vehicle_type)
                origin_branch = request.form.get('dropoff') or 'Manila'  # Default fallback
                schedule_date = request.form.get('schedule')
                
                # Get geocoded coordinates from the payment form based on payment method
                payment_method = request.form.get('method', 'credit')
                customer_latitude = 0.0
                customer_longitude = 0.0
                
                # Get coordinates from the appropriate address field based on payment method
                if payment_method == 'credit':
                    customer_latitude = request.form.get('credit_latitude', 0.0)
                    customer_longitude = request.form.get('credit_longitude', 0.0)
                elif payment_method == 'gcash':
                    customer_latitude = request.form.get('gcash_latitude', 0.0)
                    customer_longitude = request.form.get('gcash_longitude', 0.0)
                elif payment_method == 'paypal':
                    customer_latitude = request.form.get('paypal_latitude', 0.0)
                    customer_longitude = request.form.get('paypal_longitude', 0.0)
                elif payment_method == 'cod':
                    customer_latitude = request.form.get('cod_latitude', 0.0)
                    customer_longitude = request.form.get('cod_longitude', 0.0)
                
                # Defensive: convert to float if not already
                try:
                    customer_latitude = float(customer_latitude)
                except (ValueError, TypeError):
                    customer_latitude = 0.0
                try:
                    customer_longitude = float(customer_longitude)
                except (ValueError, TypeError):
                    customer_longitude = 0.0

                # Map origin_branch to lat/lon
                branch_lat_map = {
                    'Parañaque': '14.479300',
                    'Caloocan': '14.650700',
                    'Quezon': '14.676000',
                    'Manila': '14.599500'
                }
                branch_lon_map = {
                    'Parañaque': '121.019800',
                    'Caloocan': '120.966700',
                    'Quezon': '121.043700',
                    'Manila': '120.984200'
                }
                branch_latitude = branch_lat_map.get(origin_branch, '14.599500')  # Default to Manila
                branch_longitude = branch_lon_map.get(origin_branch, '120.984200')  # Default to Manila

                # Assign random driver_id between 201 and 240
                driver_id = random.randint(201, 240)

                # Use the user-selected schedule date if provided, else fallback to now
                if schedule_date:
                    order_date_value = schedule_date
                else:
                    order_date_value = datetime.now().strftime('%Y-%m-%d')

                # Insert into hh_order
                try:
                    conn = get_mysql_connection()
                    cursor = conn.cursor()
                    insert_query = """
                        INSERT INTO hh_order (
                            order_item_id, delivery_status, late_delivery_risk, origin_branch,
                            branch_latitude, branch_longitude, customer_latitude, customer_longitude,
                            `order date (DateOrders)`, driver_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        order_item_id,
                        'Shipping on time',
                        0,
                        origin_branch,
                        branch_latitude,
                        branch_longitude,
                        customer_latitude,
                        customer_longitude,
                        order_date_value,
                        driver_id
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    print(f"Order inserted successfully: {order_item_id}")
                except Exception as e:
                    print(f"Error inserting order into hh_order: {e}")

                return render_template(
                    'payment-wall.html',
                    price_data=price_data,
                    vehicle_type=vehicle_type,
                    order_id=order_item_id,
                    current_date=datetime.now(),
                    order_success=True
                )

            # GET request - just show the form
            return render_template(
                'payment-wall.html',
                price_data=price_data,
                vehicle_type=vehicle_type,
                order_id=generate_order_id(vehicle_type),
                current_date=datetime.now(),
            )

        @app.route('/admin/vehicles')
        def admin_vehicles():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
                
            # Get vehicles from MySQL database instead of SQLAlchemy
            vehicles = []
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT * FROM hh_vehicle
                """
                cursor.execute(query)
                vehicles = cursor.fetchall()
                cursor.close()
                conn.close()
                
                # Convert any Decimal objects to float for JSON serialization
                # Import random module if it's not already imported at the top of the file
                import random

                for vehicle in vehicles:
                    for key, value in vehicle.items():
                        # Check if value is Decimal and convert to float
                        if hasattr(value, 'as_tuple') and hasattr(value, 'quantize'):
                            vehicle[key] = float(value)
                    
                    # Randomly assign a status if not already set
                    if not vehicle.get('status'):
                        vehicle['status'] = random.choice(['Available', 'In Use', 'Maintenance'])
                    
                    # Assign category based on min_weight rules
                    min_weight = vehicle.get('min_weight', 0)
                    if min_weight == 0.1:
                        vehicle['category'] = 'Motorcycle'
                    elif min_weight == 20:
                        vehicle['category'] = 'Car'
                    elif min_weight == 25:
                        if 'NMAX' in vehicle.get('unit_name', '') or 'Yamaha' in vehicle.get('unit_brand', ''):
                            vehicle['category'] = 'Motorcycle'
                        else:
                            vehicle['category'] = 'Car'
                    elif min_weight >= 350:
                        vehicle['category'] = 'Truck'
                    # If none of the above, keep existing category or set to 'Unknown'
                    elif not vehicle.get('category'):
                        vehicle['category'] = 'Unknown'
                
            except Exception as e:
                print(f"Error fetching vehicles from MySQL: {e}")
                
            # Calculate counts for stats based on assigned categories
            motorcycle_count = sum(1 for v in vehicles if v.get('category') == 'Motorcycle')
            car_count = sum(1 for v in vehicles if v.get('category') == 'Car')
            truck_count = sum(1 for v in vehicles if v.get('category') == 'Truck')
            available_count = sum(1 for v in vehicles if v.get('status') == 'Available')
            
            # Convert to JSON for JavaScript
            vehicles_json = json.dumps(vehicles)
            
            # Get admin name from Flask session
            admin_name = session.get('admin_name', 'Admin User')
            
            return render_template('admin_vehicles.html', 
                                  vehicles=vehicles,
                                  motorcycle_count=motorcycle_count,
                                  car_count=car_count,
                                  truck_count=truck_count,
                                  available_count=available_count,
                                  vehicles_json=vehicles_json,
                                  admin_name=admin_name)

        @app.route('/admin/vehicles/add', methods=['POST'])
        def admin_add_vehicle():
            data = {
                'employee_id': request.form.get('employee_id') if request.form.get('employee_id') else None,
                'unit_name': request.form.get('unit_name'),
                'unit_brand': request.form.get('unit_brand'),
                'year': int(request.form.get('year')),
                'km_driven': int(request.form.get('km_driven', 0)),
                'min_weight': float(request.form.get('min_weight', 0)),
                'max_weight': float(request.form.get('max_weight')),
                'status': request.form.get('status', 'Available'),
                'category': request.form.get('category')
            }
            
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                
                # Create INSERT statement dynamically based on data keys
                columns = ', '.join(f"`{key}`" for key in data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                query = f"""
                    INSERT INTO hh_vehicle ({columns})
                    VALUES ({placeholders})
                """
                
                # Execute the query with data values
                cursor.execute(query, list(data.values()))
                conn.commit()
                
                cursor.close()
                conn.close()
                
                flash('Vehicle added successfully', 'success')
            except Exception as e:
                flash(f'Error adding vehicle: {str(e)}', 'error')
            
            return redirect(url_for('admin_vehicles'))

        @app.route('/admin/vehicles/update', methods=['POST'])
        def admin_update_vehicle():
            vehicle_id = int(request.form.get('vehicle_id'))
            
            data = {
                'employee_id': request.form.get('employee_id') if request.form.get('employee_id') else None,
                'unit_name': request.form.get('unit_name'),
                'unit_brand': request.form.get('unit_brand'),
                'year': int(request.form.get('year')),
                'km_driven': int(request.form.get('km_driven', 0)),
                'min_weight': float(request.form.get('min_weight', 0)),
                'max_weight': float(request.form.get('max_weight')),
                'status': request.form.get('status'),
                'category': request.form.get('category')
            }
            
            # ...existing code...
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                
                # Create UPDATE statement dynamically based on data
                set_clause = ', '.join(f"`{key}` = %s" for key in data.keys())
                query = f"""
                    UPDATE hh_vehicle 
                    SET {set_clause}
                    WHERE id = %s
                """
                
                # Add the vehicle_id to the data values for the WHERE clause
                values = list(data.values()) + [vehicle_id]
                
                # Execute the query
                cursor.execute(query, values)
                conn.commit()
                
                cursor.close()
                conn.close()
                
                flash('Vehicle updated successfully', 'success')
            except Exception as e:
                flash(f'Error updating vehicle: {str(e)}', 'error')
            
            return redirect(url_for('admin_vehicles'))

        @app.route('/admin/vehicles/delete', methods=['POST'])
        def admin_delete_vehicle():
            vehicle_id = int(request.form.get('vehicle_id'))
            
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                
                # Delete the vehicle with the given ID
                query = "DELETE FROM hh_vehicle WHERE id = %s"
                cursor.execute(query, (vehicle_id,))
                conn.commit()
                
                cursor.close()
                conn.close()
                
                flash('Vehicle deleted successfully', 'success')
            except Exception as e:
                flash(f'Error deleting vehicle: {str(e)}', 'error')
            
            return redirect(url_for('admin_vehicles'))

        @app.route('/admin/employee-salary')
        def admin_employee_salary():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
            
            session_db = self.salary_db.connect()
            salaries = session_db.query(EmployeeSalary).all()
            
            # Calculate statistics
            total_count = len(salaries)
            
            total_salary = sum(s.salary_yearly for s in salaries)
            avg_salary = total_salary / total_count if total_count > 0 else 0
            
            total_bonus = sum(s.bonus_amount for s in salaries)
            avg_bonus = total_bonus / total_count if total_count > 0 else 0
            
            high_performers = sum(1 for s in salaries if s.performance_rating >= 4)
            
            # Get list of all departments
            departments = set()
            for salary in salaries:
                if salary.department:
                    departments.add(salary.department)
                else:
                    departments.add('Other')
            
            # Get the top 5 most frequent departments for tabs
            department_counts = {}
            for salary in salaries:
                dept = salary.department if salary.department else 'Other'
                if dept in department_counts:
                    department_counts[dept] += 1
                else:
                    department_counts[dept] = 1
            
            sorted_departments = sorted(department_counts.items(), key=lambda x: x[1], reverse=True)
            main_departments = [dept for dept, count in sorted_departments[:5]]
            
            # Get department statistics
            department_stats = self.salary_db.get_department_stats()
            
            # Get performance statistics
            performance_stats = self.salary_db.get_performance_stats()
            
            # Convert data to JSON for JavaScript
            salaries_json = json.dumps([s.to_dict() for s in salaries])
            department_stats_json = json.dumps(department_stats)
            performance_stats_json = json.dumps(performance_stats)
            
            self.salary_db.disconnect(session_db)
            
            # Get admin name from Flask session
            admin_name = session.get('admin_name', 'Admin User')
            
            return render_template('admin_employee_salary.html', 
                                  salaries=salaries,
                                  departments=sorted(departments),
                                  main_departments=main_departments,
                                  total_count=total_count,
                                  avg_salary=avg_salary,
                                  avg_bonus=avg_bonus,
                                  high_performers=high_performers,
                                  department_stats=department_stats_json,
                                  performance_stats=performance_stats_json,
                                  salaries_json=salaries_json,
                                  admin_name=admin_name)

        @app.route('/admin/employee-salary/add', methods=['POST'])
        def add_salary():
            try:
                data = {
                    'employee_id': int(request.form.get('employee_id')),
                    'job_title': request.form.get('job_title'),
                    'department': request.form.get('department'),
                    'salary_yearly': float(request.form.get('salary_yearly')),
                    'salary_monthly': float(request.form.get('salary_monthly')),
                    'hire_date': request.form.get('hire_date'),
                    'years_of_experience': int(request.form.get('years_of_experience')),
                    'years_of_experience_company': float(request.form.get('years_of_experience_company')),
                    'performance_rating': int(request.form.get('performance_rating')),
                    'bonus_amount': float(request.form.get('bonus_amount')),
                    'total_compensation': float(request.form.get('total_compensation'))
                }
                
                self.salary_db.add_salary(**data)
                flash('Salary record added successfully', 'success')
                
            except Exception as e:
                flash(f'Error adding salary record: {str(e)}', 'error')
            
            return redirect(url_for('admin_employee_salary'))

        @app.route('/admin/employee-salary/update', methods=['POST'])
        def update_salary():
            try:
                employee_id = int(request.form.get('employee_id'))
                
                data = {
                    'job_title': request.form.get('job_title'),
                    'department': request.form.get('department'),
                    'salary_yearly': float(request.form.get('salary_yearly')),
                    'salary_monthly': float(request.form.get('salary_monthly')),
                    'hire_date': request.form.get('hire_date'),
                    'years_of_experience': int(request.form.get('years_of_experience')),
                    'years_of_experience_company': float(request.form.get('years_of_experience_company')),
                    'performance_rating': int(request.form.get('performance_rating')),
                    'bonus_amount': float(request.form.get('bonus_amount')),
                    'total_compensation': float(request.form.get('total_compensation'))
                }
                
                self.salary_db.update_salary(employee_id, **data)
                flash('Salary record updated successfully', 'success')
                
            except Exception as e:
                flash(f'Error updating salary record: {str(e)}', 'error')
            
            return redirect(url_for('admin_employee_salary'))

        @app.route('/admin/employee-salary/delete', methods=['POST'])
        def delete_salary():
            try:
                employee_id = int(request.form.get('employee_id'))
                
                self.salary_db.delete_salary(employee_id)
                flash('Salary record deleted successfully', 'success')
                
            except Exception as e:
                flash(f'Error deleting salary record: {str(e)}', 'error')
            
            return redirect(url_for('admin_employee_salary'))

        @app.route('/admin/products')
        def admin_products():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
            
            session_db = self.product_db.connect()
            products = session_db.query(Product).all()
            
            total_count = len(products)
            
            # Get unique departments and categories
            departments = set()
            categories = set()
            for product in products:
                departments.add(product.department_name)
                categories.add(product.product_category_name)
            
            department_count = len(departments)
            category_count = len(categories)
            
            # Get department statistics
            department_stats = self.product_db.get_department_stats()
            
            # Get category statistics
           
            category_stats = self.product_db.get_category_stats()
            
            # Find top department
            top_department = max(department_stats.items(), key=lambda x: x[1]['count'])[0] if department_stats else "None"
            
            # Get the top 5 most frequent departments for tabs
            department_counts = {dept: department_stats[dept]['count'] for dept in department_stats}
            sorted_departments = sorted(department_counts.items(), key=lambda x: x[1], reverse=True)
            main_departments = [dept for dept, count in sorted_departments[:5]]
            
            # Convert data to JSON for JavaScript
            products_json = json.dumps([p.to_dict() for p in products])
            department_stats_json = json.dumps(department_stats)
            category_stats_json = json.dumps(category_stats)
            
            self.product_db.disconnect(session_db)
            
            # Get admin name from Flask session
            admin_name = session.get('admin_name', 'Admin User')
            
            return render_template('admin_products.html', 
                                  products=products,
                                                                   departments=sorted(departments),
                                  categories=sorted(categories),
                                  main_departments=main_departments,
                                  total_count=total_count,
                                  department_count=department_count,
                                  category_count=category_count,
                                  top_department=top_department,
                                  department_stats=department_stats_json,
                                  category_stats=category_stats_json,
                                  products_json=products_json,
                                  admin_name=admin_name)

        @app.route('/admin/products/add', methods=['POST'])
        def add_product():
            try:
                data = {
                    'product_name': request.form.get('product_name'),
                    'order_item_id': request.form.get('order_item_id'),
                    'product_category_id': int(request.form.get('product_category_id')),
                    'product_category_name': request.form.get('product_category_name'),
                    'department_id': int(request.form.get('department_id')),
                    'department_name': request.form.get('department_name')
                }
                
                self.product_db.add_product(**data)
                flash('Product added successfully', 'success')
                
            except Exception as e:
                flash(f'Error adding product: {str(e)}', 'error')
            
            return redirect(url_for('admin_products'))

        @app.route('/admin/products/update', methods=['POST'])
        def update_product():
            try:
                product_id = int(request.form.get('id'))
                
                data = {
                    'product_name': request.form.get('product_name'),
                    'order_item_id': request.form.get('order_item_id'),
                    'product_category_id': int(request.form.get('product_category_id')),
                    'product_category_name': request.form.get('product_category_name'),
                    'department_id': int(request.form.get('department_id')),
                    'department_name': request.form.get('department_name')
                }
                
                self.product_db.update_product(product_id, **data)
                flash('Product updated successfully', 'success')
                
            except Exception as e:
                flash(f'Error updating product: {str(e)}', 'error')
            
            return redirect(url_for('admin_products'))

        @app.route('/admin/products/delete', methods=['POST'])
        def delete_product():
            try:
                product_id = int(request.form.get('id'))
                
                self.product_db.delete_product(product_id)
                flash('Product deleted successfully', 'success')
                
            except Exception as e:
                flash(f'Error deleting product: {str(e)}', 'error')
            
            return redirect(url_for('admin_products'))

        @app.route('/admin/sales')
        def admin_sales():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
            # Initialize sales database and get sales data
            sales_db = SalesDatabase()
            sales = sales_db.get_all_sales()
            
            # Get sales statistics
            stats = sales_db.get_sales_stats()
            
            # Get admin name from Flask session
            admin_name = session.get('admin_name', 'Admin User')
            
            return render_template('admin_sales.html',
                                  sales=sales,
                                  total_sales=stats['total_sales'],
                                  total_revenue=stats['total_revenue'],
                                  total_profit=stats['total_profit'],
                                  admin_name=admin_name)
                                  
        @app.route('/admin/customers')
        def admin_customers():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
            # Initialize customer database and get customer data
            customer_db = CustomerDatabase()
            customers = customer_db.get_all_customers()
            
            # Get customer statistics
            stats = customer_db.get_customer_stats()
            
            # Get unique cities for the filter
            cities = list(set(customer.city for customer in customers if customer.city))
            
            # Get admin name from Flask session
            admin_name = session.get('admin_name', 'Admin User')
            
            # Convert customer data to JSON for JavaScript use
            customers_json = json.dumps([customer.to_dict() for customer in customers])
            
            return render_template('admin_customers.html',
                                  customers=customers,
                                  customers_json=customers_json,
                                  total_count=stats['total_count'],
                                  corporate_count=stats['corporate_count'],
                                  consumer_count=stats['consumer_count'],
                                  home_office_count=stats['home_office_count'],
                                  top_city=stats['top_city'],
                                  cities=cities,
                                  admin_name=admin_name)

        @app.route('/admin/customers/add', methods=['POST'])
        def admin_add_customer():
            try:
                # Generate a unique customer ID (in a real app, this would be more systematic)
                customer_id = f"CUST-{random.randint(10000, 99999)}"
                
                data = {
                    'customer_id': customer_id,
                    'order_item_id': request.form.get('order_item_id'),
                    'first_name': request.form.get('first_name'),
                    'last_name': request.form.get('last_name'),
                    'city': request.form.get('city'),
                    'country': request.form.get('country'),
                    'segment': request.form.get('segment')
                }
                
                # Initialize customer database
                customer_db = CustomerDatabase()
                
                # Add new customer
                customer_db.add_customer(**data)
                
                flash('Customer added successfully', 'success')
                
            except Exception as e:
                flash(f'Error adding customer: {str(e)}', 'error')
                
            return redirect(url_for('admin_customers'))
        
        @app.route('/admin/customers/update', methods=['POST'])
        def admin_update_customer():
            try:
                customer_id = request.form.get('customer_id')
                
                data = {
                    'order_item_id': request.form.get('order_item_id'),
                    'first_name': request.form.get('first_name'),
                    'last_name': request.form.get('last_name'),
                    'city': request.form.get('city'),
                    'country': request.form.get('country'),
                    'segment': request.form.get('segment')
                }
                
                # Initialize customer database
                customer_db = CustomerDatabase()
                
                # Update customer
                customer_db.update_customer(customer_id, **data)
                
                flash('Customer updated successfully', 'success')
                
            except Exception as e:
                flash(f'Error updating customer: {str(e)}', 'error')
                
            return redirect(url_for('admin_customers'))
        
        @app.route('/admin/customers/delete', methods=['POST'])
        def admin_delete_customer():
            try:
                customer_id = request.form.get('customer_id')
                
                # Initialize customer database
                customer_db = CustomerDatabase()
                
                # Delete customer
                customer_db.delete_customer(customer_id)
                
                flash('Customer deleted successfully', 'success')
                
            except Exception as e:
                flash(f'Error deleting customer: {str(e)}', 'error')
                
            return redirect(url_for('admin_customers'))
        
        @app.route('/admin/sales/add', methods=['POST'])
        def admin_add_sale():
            
            try:
                data = {
                    'order_item_id': request.form.get('order_item_id'),
                    'payment_type': request.form.get('payment_type'),
                    'benefit_per_order': float(request.form.get('benefit_per_order', 0)),
                    'sales_per_customer': float(request.form.get('sales_per_customer', 0)),
                    'order_item_discount_rate': float(request.form.get('discount_rate', 0)) / 100,
                    'order_item_product_price': float(request.form.get('product_price', 0)),
                    'order_item_profit_ratio': float(request.form.get('profit_ratio', 0)),
                    'order_item_quantity': int(request.form.get('quantity', 1)),
                    'sales': float(request.form.get('product_price', 0)) * int(request.form.get('quantity', 1)),
                    'order_item_total': float(request.form.get('product_price', 0)) * int(request.form.get('quantity', 1)) * (1 - float(request.form.get('discount_rate', 0)) / 100),
                    'order_profit_per_order': float(request.form.get('product_price', 0)) * int(request.form.get('quantity', 1)) * (1 - float(request.form.get('discount_rate', 0)) / 100) * float(request.form.get('profit_ratio', 0)),
                    'product_price': float(request.form.get('product_price', 0)),
                    'order_date': request.form.get('order_date'),
                }
                
                # Initialize sales database
                sales_db = SalesDatabase()
                
                # Add new sale
                sales_db.add_sale(**data)
                
                flash('Sale added successfully', 'success')
                
            except Exception as e:
                flash(f'Error adding sale: {str(e)}', 'error')
                
            return redirect(url_for('admin_sales'))
        
        @app.route('/admin/sales/update', methods=['POST'])
        def admin_update_sale():
            try:
                sale_id = int(request.form.get('sale_id'))
                
                data = {
                    'order_item_id': request.form.get('order_item_id'),
                    'payment_type': request.form.get('payment_type'),
                    'order_item_discount_rate': float(request.form.get('discount_rate', 0)) / 100,
                    'order_item_product_price': float(request.form.get('product_price', 0)),
                    'order_item_profit_ratio': float(request.form.get('profit_ratio', 0)),
                    'order_item_quantity': int(request.form.get('quantity', 1)),
                    'product_price': float(request.form.get('product_price', 0)),
                    'order_date': request.form.get('order_date'),
                }
                
                # Calculate derived fields
                data['sales'] = data['order_item_product_price'] * data['order_item_quantity']
                data['order_item_total'] = data['sales'] * (1 - data['order_item_discount_rate'])
                data['order_profit_per_order'] = data['order_item_total'] * data['order_item_profit_ratio']
                
                # Initialize sales database
                sales_db = SalesDatabase()
                
                # Update sale
                sales_db.update_sale(sale_id, **data)
                
                flash('Sale updated successfully', 'success')
                
            except Exception as e:
                flash(f'Error updating sale: {str(e)}', 'error')
                
            return redirect(url_for('admin_sales'))
        
        @app.route('/admin/sales/delete', methods=['POST'])
        def admin_delete_sale():    
            try:
                sale_id = int(request.form.get('sale_id'))
                
                # Initialize sales database
                sales_db = SalesDatabase()
                
                # Delete sale
                sales_db.delete_sale(sale_id)
                
                
                flash('Sale deleted successfully', 'success')
                
            except Exception as e:
                flash(f'Error deleting sale: {str(e)}', 'error')
                
            return redirect(url_for('admin_sales'))

        @app.route('/add-user', methods=['POST'])
        def add_user():
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')

            print("DEBUG - Received data:", full_name, email, username, password)

            # Validate all fields are provided
            if not all([full_name, email, username, password]):
                flash('All fields are required.', 'error')
                return redirect(url_for('user_signup_html'))

            # Always include default profile picture path
            default_profile_pic = 'images/pfp.png'
            
            # Insert user into MySQL database instead of CSV file
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                
                # Check if username already exists
                check_query = "SELECT 1 FROM hh_user_login WHERE username = %s LIMIT 1"
                cursor.execute(check_query, (username,))
                if cursor.fetchone():
                    flash('Username already exists. Please choose another username.', 'error')
                    cursor.close()
                    conn.close()
                    return redirect(url_for('user_signup_html'))
                
                # Insert the new user
                insert_query = """
                    INSERT INTO hh_user_login 
                    (`full_name`, `email_address`, `username`, `password`, `profile_image`) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (full_name, email, username, password, default_profile_pic))
                conn.commit()
                cursor.close()
                conn.close()
                
                print("DEBUG - Successfully added user to MySQL database")
                flash('User added successfully!', 'success')
                return redirect(url_for('user_signup_html'))

            except Exception as e:
                print(f"ERROR adding user to MySQL: {e}")
                flash(f'Error adding user: {str(e)}', 'error')

            return redirect(url_for('user_login_html'))
                
        # New route to handle profile updates
        @app.route('/update-profile', methods=['POST'])
       
        def update_profile():
            # Make sure user is logged in
            if 'user_email' not in session:
                return jsonify({'success': False, 'message': 'User not logged in'})
            
            data = request.get_json()
            field = data.get('field')
            value = data.get('value')
            current_email = session.get('user_email')
            
            # Only allow name update here (email handled separately)
            try:
                if field == 'name':
                    # Update full name in MySQL
                    conn = get_mysql_connection()
                    cursor = conn.cursor()
                    user_username = session.get('username')
                    update_query = """
                        UPDATE hh_user_login
                        SET `full_name` = %s
                        WHERE (`email_address` = %s OR `Username` = %s OR `username` = %s)
                    """
                    cursor.execute(update_query, (value, current_email, user_username, user_username))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    session['user_name'] = value
                    session['full_name'] = value
                    return jsonify({'success': True})
                elif field == 'email':
                    # Email update is handled by /update_email route
                    return jsonify({'success': False, 'message': 'Use /update_email for email changes'})
                else:
                    return jsonify({'success': False, 'message': 'Invalid field'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        # New route to update the user's contact email in MySQL and session
        @app.route('/update_email', methods=['POST'])
        def update_email_route():
            if 'user_email' not in session:
                return jsonify({'success': False, 'message': 'User not logged in'}), 401
            data = request.get_json()
            new_email = data.get('email', '').strip()
            if not new_email:
                return jsonify({'success': False, 'message': 'No email provided'}), 400

            user_email = session.get('user_email')
            user_username = session.get('username')
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                # Update email_address in MySQL
                update_query = """
                    UPDATE hh_user_login
                    SET `email_address` = %s
                    WHERE (`email_address` = %s OR `Username` = %s OR `username` = %s)
                """
                cursor.execute(update_query, (new_email, user_email, user_username, user_username))
                conn.commit()
                cursor.close()
                conn.close()
                # Update session
                session['user_email'] = new_email
                return jsonify({'success': True, 'email': new_email})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        @app.route('/admin/support-tickets')
        def admin_support_tickets():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))

            tickets = []
            csv_path = os.path.join('hexahaul_db', 'hh_support_tickets.csv')
            try:
                with open(csv_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        # Ensure 'attachments' key exists for template
                        if 'attachments' not in row:
                            row['attachments'] = ""
                        tickets.append(row)
            except Exception as e:
                print(f"Error reading support tickets CSV: {e}")

            admin_name = session.get('admin_name', 'Admin User')
            return render_template('admin_support_tickets.html', tickets=tickets, admin_name=admin_name)

        @app.route('/admin/support-tickets/reply', methods=['POST'])
        def admin_support_ticket_reply():
            ticket_id = request.form.get('ticket_id')
            reply_message = request.form.get('reply_message')
            if not ticket_id or not reply_message:
                flash('Missing ticket ID or reply message.', 'error')
                return redirect(url_for('admin_support_tickets'))

            csv_path = os.path.join('hexahaul_db', 'hh_support_tickets.csv')
            updated_rows = []
            user_email = None
            ticket_title = None
            ticket_description = None

            # Read and update the CSV
            try:

                df = pd.read_csv(csv_path)
                idx = df.index[df['ticket_id'] == ticket_id].tolist()
                if not idx:
                    flash('Ticket not found.', 'error')
                    return redirect(url_for('admin_support_tickets'))
                row_idx = idx[0]
                user_email = df.at[row_idx, 'user_email']
                ticket_title = df.at[row_idx, 'ticket_title']
                ticket_description = df.at[row_idx, 'ticket_description']
                df.at[row_idx, 'admin_reply'] = reply_message
                reply_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.at[row_idx, 'reply_timestamp'] = reply_timestamp
                df.to_csv(csv_path, index=False)
            except Exception as e:
                flash(f'Error updating ticket: {e}', 'error')
                return redirect(url_for('admin_support_tickets'))

            # Send reply email using existing styled template
            try:
                logo_url = "https://i.imgur.com/upLAusA.png"
                msg = Message(
                    subject=f"HexaHaul Support Reply: {ticket_title}",
                    sender="hexahaulprojects@gmail.com",
                    recipients=[user_email]
                )
                msg.html = f"""
                <div style="background:#f7f7f7;padding:40px 0;">
                  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    <div style="background:#03335e;padding:24px 0;text-align:center;">
                      <img src="{logo_url}" alt="HexaHaul Logo" style="width:64px;height:64px;margin-bottom:8px;">
                      <h2 style="margin:0;font-family:sans-serif;color:#fff;">Support Ticket Reply</h2>
                    </div>
                    <div style="padding:32px 24px;">
                      <p style="font-family:sans-serif;color:#333;font-size:16px;">
                        <strong>Your Ticket:</strong> {ticket_title}<br>
                        <span style="color:#888;font-size:14px;">{{ ticket_id }}</span>
                      </p>
                      <div style="margin:16px 0;padding:16px;background:#f9f9f9;border-radius:4px;">
                        <strong>Description:</strong><br>
                        <span style="white-space:pre-line;">{ticket_description}</span>
                      </div>
                      <div style="margin:16px 0;padding:16px;background:#eaf6fb;border-radius:4px;">
                        <strong>Admin Reply:</strong><br>
                        <span style="white-space:pre-line;">{reply_message}</span>
                      </div>
                    </div>
                    <div style="padding:16px 24px 24px 24px;background:#f0f7ff;text-align:center;font-family:sans-serif;font-size:14px;color:#555;">
                      <p style="margin:0;">If you have further questions, please reply to this email or submit a new ticket.</p>
                    </div>
                  </div>
                </div>
                """
                msg.body = f"""Your support ticket has received a reply.

Ticket: {ticket_title}
Description: {ticket_description}

Admin Reply:
{reply_message}
"""
                self.mail.send(msg)
                flash('Reply sent successfully!', 'success')
            except Exception as e:
                flash(f'Error sending reply email: {e}', 'error')

            return redirect(url_for('admin_support_tickets'))

        @app.route('/admin/support-tickets/reply/<ticket_id>', methods=['GET'])
        def admin_support_ticket_reply_page(ticket_id):
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))

            csv_path = os.path.join('hexahaul_db', 'hh_support_tickets.csv')
            ticket = None
            try:
                df = pd.read_csv(csv_path)
                row = df[df['ticket_id'] == ticket_id]
                if not row.empty:
                    ticket = row.iloc[0].to_dict()
            except Exception as e:
                print(f"Error reading support ticket for reply: {e}")

            if not ticket:
                flash('Ticket not found.', 'error')
                return redirect(url_for('admin_support_tickets'))

            return render_template('admin_support_ticket_reply.html', ticket=ticket)

        @app.route('/admin/support/ticket/done/<ticket_id>', methods=['POST'])
        def admin_support_ticket_done(ticket_id):
            """
            Mark a support ticket as done by updating its status in the CSV.
            """
            csv_path = os.path.join('hexahaul_db', 'hh_support_tickets.csv')
            try:
                df = pd.read_csv(csv_path)
                idx = df.index[df['ticket_id'] == ticket_id].tolist()
                if not idx:
                    return jsonify({'success': False, 'message': 'Ticket not found'}), 404
                row_idx = idx[0]
                # If status column does not exist, add it and default all to 'new'
                if 'status' not in df.columns:
                    df['status'] = 'new'
                df.at[row_idx, 'status'] = 'done'
                df.to_csv(csv_path, index=False)
                return '', 204
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        # Add this route to update the user's full name in MySQL and session
        @app.route('/update-full-name', methods=['POST'])
        def update_full_name():
            if 'user_email' not in session:
                return jsonify({'success': False, 'message': 'User not logged in'}), 401
            data = request.get_json()
            new_full_name = data.get('full_name', '').strip()
            if not new_full_name:
                return jsonify({'success': False, 'message': 'No name provided'}), 400

            user_email = session.get('user_email')
            user_username = session.get('username')
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                # Try to update by email or username
                update_query = """
                    UPDATE hh_user_login
                    SET `full_name` = %s
                    WHERE (`email_address` = %s OR `Username` = %s OR `username` = %s)
                """
                cursor.execute(update_query, (new_full_name, user_email, user_username, user_username))
                conn.commit()
                cursor.close()
                conn.close()
                # Update session
                session['full_name'] = new_full_name
                session['user_name'] = new_full_name
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        # --- Ensure this route is present and correct ---
        @app.route('/upload-profile-image', methods=['POST'])
        def upload_profile_image():
            if 'user_email' not in session or 'username' not in session:
                return jsonify({'success': False, 'message': 'User not logged in'}), 401

            if 'profile_image' not in request.files:
                return jsonify({'success': False, 'message': 'No file uploaded'}), 400

            file = request.files['profile_image']
            if not file or file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'}), 400

            # Save the file to static/profile_images/
            filename = secure_filename(f"{session['username']}_{int(time.time())}_{file.filename}")
            upload_dir = os.path.join('static', 'profile_images')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)

            # Store relative path for web access
            rel_path = os.path.join('profile_images', filename).replace('\\', '/')

            # Update the user's profile image in MySQL
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                update_query = """
                    UPDATE hh_user_login
                    SET profile_image = %s
                    WHERE (email_address = %s OR Username = %s OR username = %s)
                """
                cursor.execute(update_query, (rel_path, session['user_email'], session['username'], session['username']))
                conn.commit()
                cursor.close()
                conn.close()
                # Update session
                session['user_image'] = rel_path
                image_url = url_for('static', filename=rel_path)
                return jsonify({'success': True, 'image_url': image_url})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

    def register_blueprints(self):
        self.app.register_blueprint(analytics_bp)
        self.app.register_blueprint(hexabot_bp)

    def run(self):
        self.app.debug = True
        self.app.run(host="0.0.0.0", port=5000)
        print("Flask app routes:")
        print(self.app.url_map)
        
        
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        if os.path.exists(template_dir):
            print("Available templates:")
            for file in os.listdir(template_dir):
                print(f"  - {file}")
            
            @self.app.route('/test-template/<template_name>')
            def test_template(template_name):
                try:
                    return render_template(template_name)
                except Exception as e:
                    return f"Error rendering template {template_name}: {str(e)}"
        else:
            print("Template directory not found!")
            
        port = int(os.environ.get("PORT", 5000))
        self.app.run(host='0.0.0.0', port=port, debug=True)

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/employee_statuses.png')
def employee_statuses_graph():
    save_path = os.path.join('static', 'graphs', 'employee_statuses.png')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plot_employee_statuses(save_path)
    return send_from_directory('static/graphs', 'employee_statuses.png')

@analytics_bp.route('/analytics/vehicles_deployed.png')
def vehicles_deployed_graph():
    save_path = os.path.join('static', 'graphs', 'vehicles_deployed.png')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plot_vehicles_deployed(save_path)
    return send_from_directory('static/graphs', 'vehicles_deployed.png')

if __name__ == "__main__":
    app_instance = HexaHaulApp()
    app_instance.run()

# This allows Gunicorn to find 'app' when running 'gunicorn app:app'
app_instance = HexaHaulApp()
app = app_instance.app