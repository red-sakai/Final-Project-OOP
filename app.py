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
from abc import ABC, abstractmethod
from enum import Enum
from flask_mail import Mail, Message
from transformers import pipeline
from services.hexabot import hexabot_bp
from models.activity_database import ActivityDatabase
import csv
import os
import json
import random
import pandas as pd
from werkzeug.utils import secure_filename
import requests
from datetime import datetime, timedelta
import uuid

def get_qa_pipeline():
    """Lazily load and cache the QA pipeline to avoid OOM on startup."""
    # Lazy Load - delaying the initialization to save memory
    if not hasattr(get_qa_pipeline, "_pipeline"):
        from transformers import pipeline
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
                
                user = authenticate_user_csv(username, password)
                
                if user:
                    session["logged_in"] = True
                    session["user_name"] = user["full_name"]
                    session["user_email"] = user["email"]
                    session["username"] = user["username"]
                    session["user_image"] = user.get("user_image", "images/pfp.png")  # <-- Add this line
                    
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

        def authenticate_user_csv(username, password):
            """Authenticate user against CSV file"""
            csv_path = os.path.join('hexahaul_db', 'hh_user-login.csv')
            try:
                with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row['Username'] == username and row['Password'] == password:
                            return {
                                'full_name': row['Full Name'],
                                'email': row['Email Address'],
                                'username': row['Username'],
                                'user_image': row.get('Profile Image', 'images/pfp.png')  # <-- Add this line
                            }
            except FileNotFoundError:
                print(f"CSV file not found: {csv_path}")
            except Exception as e:
                print(f"Error reading CSV: {e}")
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

        @app.route("/tracking")
        @app.route("/tracking.html")
        def tracking_html():
            print("Tracking route accessed")
            # Read Order Item Ids from CSV
            csv_path = os.path.join('hexahaul_db', 'hh_order.csv')
            order_item_ids = []
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        order_item_ids.append(row['Order Item Id'])
            except Exception as e:
                print(f"Error reading hh_order.csv: {e}")
            return render_template("tracking.html", order_item_ids=order_item_ids)

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

                # --- PATCH: Read from CSV directly for admin authentication ---
                csv_path = os.path.join('hexahaul_db', 'hh_admins.csv')
                found_admin = None
                try:
                    with open(csv_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            # Compare with whitespace trimmed, case-sensitive
                            if (row['admin_username'].strip() == username.strip() and
                                row['admin_password'].strip() == password.strip()):
                                found_admin = row
                                break
                except Exception as e:
                    print(f"Error reading admin CSV: {e}")

                if found_admin:
                    # Set admin session
                    session['admin_id'] = found_admin.get('admin_username')
                    session['admin_username'] = found_admin.get('admin_username')
                    session['admin_name'] = f"{found_admin.get('admin_fname', '')} {found_admin.get('admin_lname', '')}".strip()
                    return redirect(url_for('admin_dashboard'))
                else:
                    # Fallback to SQLAlchemy authentication if not found in CSV
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
            
            # Check if email exists in admin database (hh_admins.csv)
            admin_emails = []
            try:
                with open('hexahaul_db/hh_admins.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    admin_emails = [row['admin_email'] for row in reader]
            except Exception as e:
                print(f"Error reading admin CSV: {e}")
            
            if email in admin_emails:
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
                # --- Check if email exists in CSV ---
                csv_path = os.path.join('hexahaul_db', 'hh_user-login.csv')
                email_found = False
                try:
                    with open(csv_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row.get('Email Address', '').strip().lower() == email.strip().lower():
                                email_found = True
                                break
                except Exception as e:
                    print(f"Error reading user CSV: {e}")
                if not email_found:
                    flash("Email not found in user records", "error")
                    return render_template("forgot-password.html", error="Email not found in user records")
                # --- If found, proceed as before ---
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
                    # --- Update admin password in CSV ---
                    csv_path = os.path.join('hexahaul_db', 'hh_admins.csv')
                    try:
                        df = pd.read_csv(csv_path)
                        # Update the password for the row with matching email
                        df.loc[df['admin_email'].str.strip().str.lower() == email.strip().lower(), 'admin_password'] = new_password
                        df.to_csv(csv_path, index=False)
                        flash("Password reset successful. Please login.")
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
                order_csv_path = os.path.join('hexahaul_db', 'hh_order.csv')
                product_csv_path = os.path.join('hexahaul_db', 'hh_product_info.csv')
                driver_id = None
                product_name = None
                # --- Read product info into a dict for fast lookup ---
                product_lookup = {}
                try:
                    with open(product_csv_path, 'r', newline='', encoding='utf-8') as prodfile:
                        prod_reader = csv.DictReader(prodfile)
                        for prod_row in prod_reader:
                            # Normalize key for lookup
                            product_lookup[prod_row['Order Item Id']] = prod_row['Product Name'].strip()
                except Exception as e:
                    print(f"Error reading product info CSV: {e}")
                # --- Read order info and merge product name ---
                try:
                    with open(order_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row['Order Item Id'] == tracking_id:
                                driver_id = int(row['driver_id'])
                                order_date_str = row['order date (DateOrders)']
                                try:
                                    order_date = datetime.strptime(order_date_str, "%Y-%m-%d")
                                except Exception:
                                    order_date = None
                                offset_days = 5
                                expected_delivery_date = order_date + timedelta(days=offset_days) if order_date else None
                                expected_delivery_str = expected_delivery_date.strftime("%Y-%m-%d") if expected_delivery_date else "Unknown"
                                cust_lat = float(row['Customer Latitude'])
                                cust_lon = float(row['Customer Longitude'])
                                branch_lat = float(row['Branch Latitude'])
                                branch_lon = float(row['Branch Longitude'])
                                # reverse geocode
                                customer_place = reverse_geocode(cust_lat, cust_lon)
                                branch_place = reverse_geocode(branch_lat, branch_lon)
                                # Lookup product name
                                product_name = product_lookup.get(row['Order Item Id'], None)
                                order_data = {
                                    'orderItemId': row['Order Item Id'],
                                    'deliveryStatus': row['Delivery Status'],
                                    'originBranch': row['Origin Branch'],
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
                                break
                except Exception as e:
                    print(f"Error reading order CSV: {e}")

                if driver_id:
                    emp_csv_path = os.path.join('hexahaul_db', 'hh_employee_biography.csv')
                    try:
                        with open(emp_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                            reader = csv.DictReader(csvfile)
                            for row in reader:
                                if int(row['Employee Id']) == driver_id:
                                    courier = {
                                        'employee_id': int(row['Employee Id']),
                                        'first_name': row['First Name'],
                                        'last_name': row['Last Name'],
                                        'gender': row['Gender'],
                                        'age': int(row['Age']),
                                        'birthdate': row['birth_date'],
                                        'contact_number': row['Contact Number']
                                    }
                                    break
                    except Exception as e:
                        print(f"Error reading employee CSV: {e}")

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
                if 'attachments' in request.files:
                    files = request.files.getlist('attachments')
                    for file in files:
                        if file and file.filename:
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
                ticket_row = [
                    ticket_id,
                    user_email,
                    ticket_title,
                    ticket_description,
                    error_code,
                    tracking_id,
                    timestamp,
                    "",  # admin_reply
                    ""   # reply_timestamp
                ]
                # Write header if file is empty
                write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
                try:
                    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        if write_header:
                            writer.writerow([
                                "ticket_id","user_email","ticket_title","ticket_description",
                                "error_code","tracking_id","timestamp","admin_reply","reply_timestamp"
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
                    csv_path = os.path.join('hexahaul_db', 'hh_user-login.csv')
                    try:
                        df = pd.read_csv(csv_path)
                        # Update the password for the row with matching email
                        df.loc[df['Email Address'].str.strip().str.lower() == email.strip().lower(), 'Password'] = new_password
                        df.to_csv(csv_path, index=False)
                        flash("Password updated successfully. Please login.", "success")
                    except Exception as e:
                        flash(f"Error updating password: {e}", "error")
                return redirect(url_for("user_login_html"))
            return render_template("change-password.html")

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
                
            session_db = self.employee_db.connect()
            employees = session_db.query(Employee).all()
            
            total_count = len(employees)
            manager_count = sum(1 for e in employees if e.role == 'Manager')
            driver_count = sum(1 for e in employees if e.role == 'Driver')
            active_count = sum(1 for e in employees if e.status == 'Active')
            
            session2 = self.vehicle_db.connect()
            available_vehicles = session2.query(Vehicle).filter_by(status='Available').all()
            
            employees_json = json.dumps([{
                'id': e.id,
                'employee_id': e.employee_id,
                'first_name': e.first_name,
                'last_name': e.last_name,
                'full_name': e.full_name,
                'gender': e.gender,
                'age': e.age,
                'birthdate': e.birthdate,
                'contact_number': e.contact_number,
                'email': e.email,
                'department': e.department,
                'role': e.role,
                'hire_date': e.hire_date,
                'license_number': e.license_number,
                'license_expiry': e.license_expiry,
                'assigned_vehicle': e.assigned_vehicle,
                'status': e.status
            } for e in employees])
            
            self.employee_db.disconnect()
            self.vehicle_db.disconnect()
            
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
                'license_expiry': request.form.get('license_expiry'),
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
                'license_expiry': request.form.get('license_expiry'),
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

        @app.route("/payment-wall")
        def payment_wall():
            return render_template("payment-wall.html")

        @app.route('/admin/vehicles')
        def admin_vehicles():
            # Check if admin is logged in
            if 'admin_id' not in session:
                flash('Please login to access the admin dashboard', 'error')
                return redirect(url_for('admin_login'))
                
            # Get database session (SQLAlchemy)
            db_session = vehicle_db.connect()
            vehicles = db_session.query(Vehicle).all()
            
            motorcycle_count = sum(1 for v in vehicles if v.category == 'Motorcycle')
            car_count = sum(1 for v in vehicles if v.category == 'Car')
            truck_count = sum(1 for v in vehicles if v.category == 'Truck')
            available_count = sum(1 for v in vehicles if v.status == 'Available')
            
            vehicles_json = json.dumps([{
                'id': v.id,
                'unit_brand': v.unit_brand,
                'unit_model': v.unit_model,
                'unit_type': v.unit_type,
                'category': v.category,
                'distance': v.distance,
                'driver_employee_id': v.driver_employee_id,
                'license_expiration_date': v.license_expiration_date,
                'order_id': v.order_id,
                'max_weight': v.max_weight,
                'min_weight': v.min_weight,
                'status': v.status,
                'year': v.year
            } for v in vehicles])
            
            vehicle_db.disconnect()
            
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
                'unit_brand': request.form.get('unit_brand'),
                'unit_model': request.form.get('unit_model'),
                'unit_type': request.form.get('unit_type'),
                'category': request.form.get('category'),
                'distance': int(request.form.get('distance', 0)),
                'driver_employee_id': int(request.form.get('driver_employee_id')) if request.form.get('driver_employee_id') else None,
                'license_expiration_date': request.form.get('license_expiration_date'),
                'order_id': int(request.form.get('order_id')) if request.form.get('order_id') else None,
                'max_weight': float(request.form.get('max_weight')),
                'min_weight': float(request.form.get('min_weight', 0)),
                'status': request.form.get('status', 'Available'),
                'year': int(request.form.get('year'))
            }
            
            vehicle_db.add_vehicle(**data)
            
            return redirect(url_for('admin_vehicles'))

        @app.route('/admin/vehicles/update', methods=['POST'])
        def admin_update_vehicle():
            vehicle_id = int(request.form.get('vehicle_id'))
            
            data = {
                'unit_brand': request.form.get('unit_brand'),
                'unit_model': request.form.get('unit_model'),
                'unit_type': request.form.get('unit_type'),
                'category': request.form.get('category'),
                'distance': int(request.form.get('distance', 0)),
                'driver_employee_id': int(request.form.get('driver_employee_id')) if request.form.get('driver_employee_id') else None,
                'license_expiration_date': request.form.get('license_expiration_date'),
                'order_id': int(request.form.get('order_id')) if request.form.get('order_id') else None,
                'max_weight': float(request.form.get('max_weight')),
                'min_weight': float(request.form.get('min_weight', 0)),
                'status': request.form.get('status'),
                'year': int(request.form.get('year'))
            }
            
            vehicle_db.update_vehicle(vehicle_id, **data)
            
            return redirect(url_for('admin_vehicles'))

        @app.route('/admin/vehicles/delete', methods=['POST'])
        def admin_delete_vehicle():
            vehicle_id = int(request.form.get('vehicle_id'))
            
            vehicle_db.delete_vehicle(vehicle_id)
            
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
            
            from models.sales_database import SalesDatabase
            
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
            
            from models.customers_database import CustomerDatabase
            
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
            from models.customers_database import CustomerDatabase
            
            try:
                # Generate a unique customer ID (in a real app, this would be more systematic)
                import random
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
            from models.customers_database import CustomerDatabase
            
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
            from models.customers_database import CustomerDatabase
            
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
            from models.sales_database import SalesDatabase
            
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
            from models.sales_database import SalesDatabase
            
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
            from models.sales_database import SalesDatabase
            
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
            new_user = [full_name, email, username, password, default_profile_pic]

            import os
            csv_path = os.path.join('hexahaul_db', 'hh_user-login.csv')

            try:
                # Ensure file ends with newline before appending
                with open(csv_path, 'r+', encoding='utf-8') as f:
                    f.seek(0, 2)  # Go to end of file
                    if f.tell() > 0:  # If file is not empty
                        f.seek(f.tell() - 1)  # Go back one character
                        last_char = f.read(1)
                        if last_char != '\n':  # If last character is not newline
                            f.write('\n')  # Add newline

                # Now append the new user with profile picture path
                with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(new_user)

                print("DEBUG - Successfully wrote to CSV")
                flash('User added successfully!', 'success')
                return redirect(url_for('user_signup_html')) 

            except Exception as e:
                print(f"ERROR writing to CSV: {e}")
                flash(f'Error adding user: {str(e)}', 'error')

            return redirect(url_for('user_login_html'))
                
        # New route to handle profile updates
        @app.route('/update-profile', methods=['POST'])
        def update_profile():
            # Make sure user is logged in
            if 'user_email' not in session:
                return jsonify({'success': False, 'message': 'User not logged in'})
            
            # Get the data from request
            data = request.get_json()
            field = data.get('field')
            value = data.get('value')
            
            # Get current email from session
            current_email = session.get('user_email')
            
            try:
                # Path to CSV file
                csv_path = os.path.join('hexahaul_db', 'hh_user-login.csv')
                
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(csv_path)
                
                # Find the row with the current email
                user_row = df[df['Email Address'] == current_email]
                
               
                if len(user_row) == 0:
                    return jsonify({'success': False, 'message': 'User not found'})
                
                # Update the appropriate field
                if field == 'name':
                    df.loc[df['Email Address'] == current_email, 'Full Name'] = value
                    # Update the session name
                    session['user_name'] = value
                elif field == 'email':
                    # First save the current email to find the user row
                    old_email = current_email
                    # Update the email in the DataFrame
                    df.loc[df['Email Address'] == old_email, 'Email Address'] = value
                    # Update the session email
                    session['user_email'] = value
                else:
                    return jsonify({'success': False, 'message': 'Invalid field'})
                
                # Save the updated DataFrame back to CSV
                df.to_csv(csv_path, index=False)
                
                return jsonify({'success': True})
            
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        UPLOAD_FOLDER = os.path.join('static', 'user_images')
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        # Add this route to handle uploads
        @app.route('/upload-profile-image', methods=['POST'])
        def upload_profile_image():
            if 'user_email' not in session:
                if request.is_json or request.accept_mimetypes['application/json']:
                    return jsonify(success=False, message="Not logged in"), 401
                return redirect(url_for('user_login_html'))

            file = request.files.get('profile_image')
            if file and allowed_file(file.filename):
                filename = secure_filename(session['user_email'].replace('@', '').replace('.', '') + '_' + file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(filepath)
                # Always use forward slashes for web paths
                relative_path = os.path.join('user_images', filename).replace('\\', '/')
                session['user_image'] = relative_path

                # Update CSV
                csv_path = os.path.join('hexahaul_db', 'hh_user-login.csv')
                try:
                    df = pd.read_csv(csv_path)
                    user_email = session['user_email']
                    df.loc[df['Email Address'] == user_email, 'Profile Image'] = relative_path
                    df.to_csv(csv_path, index=False)
                except Exception as e:
                    print(f"Error updating profile image in CSV: {e}")

                image_url = url_for('static', filename=relative_path)
               
                if request.is_json or request.accept_mimetypes['application/json']:
                    return jsonify(success=True, image_url=image_url)
                flash('Profile image updated!', 'success')
            else:
                if request.is_json or request.accept_mimetypes['application/json']:
                    return jsonify(success=False, message="Invalid file type")
                flash('Invalid file type.', 'error')
            return redirect(request.referrer or url_for('sidebar_html'))

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
                        tickets.append(row)
            except Exception as e:
                print(f"Error reading support tickets CSV: {e}")

            admin_name = session.get('admin_name', 'Admin User')
            return render_template('admin_support_tickets.html', tickets=tickets, admin_name=admin_name)

    def register_blueprints(self):
        self.app.register_blueprint(analytics_bp)
        self.app.register_blueprint(hexabot_bp)

    def run(self):
        self.app.debug = True
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