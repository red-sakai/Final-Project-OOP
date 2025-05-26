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

# Initialize DistilBERT QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

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
            return render_template("tracking.html")

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
                
                # Get database session
                db_session = get_db_session()
                
                try:
                    # Authenticate admin
                    admin = Admin.authenticate(db_session, username, password)
                    
                    if admin:
                        # Set admin session
                        session['admin_id'] = admin.id
                        session['admin_username'] = admin.admin_username
                        session['admin_name'] = f"{admin.admin_fname} {admin.admin_lname}"
                        
                        # Redirect to admin dashboard
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
                    flash("Password changed successfully. Please login.")
                    return redirect(url_for("user_login_html"))
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
                
                # Check if this is an AJAX request
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                         request.headers.get('Accept', '').find('application/json') != -1 or \
                         'application/json' in request.headers.get('Content-Type', '')
                
                # Validate passwords match and meet requirements
                if new_password != confirm_password:
                    if is_ajax:
                        return jsonify({'success': False, 'message': 'Passwords do not match.'})
                    flash("Passwords do not match.")
                    return render_template('admin-new-password.html', email=email)
                
                # Validate password requirements
                if len(new_password) < 8:
                    if is_ajax:
                        return jsonify({'success': False, 'message': 'Password must be at least 8 characters long.'})
                    flash("Password must be at least 8 characters long.")
                    return render_template('admin-new-password.html', email=email)
                
                # Check for symbol, uppercase, and lowercase
                import re
                if not re.search(r'[^A-Za-z0-9]', new_password):
                    if is_ajax:
                        return jsonify({'success': False, 'message': 'Password must contain at least one symbol.'})
                    flash("Password must contain at least one symbol.")
                    return render_template('admin-new-password.html', email=email)
                
                if not re.search(r'[a-z]', new_password) or not re.search(r'[A-Z]', new_password):
                    if is_ajax:
                        return jsonify({'success': False, 'message': 'Password must contain both uppercase and lowercase letters.'})
                    flash("Password must contain both uppercase and lowercase letters.")
                    return render_template('admin-new-password.html', email=email)
                
                # Update password in CSV file
                try:
                    csv_path = os.path.join('hexahaul_db', 'hh_admins.csv')
                    
                    # Check if file exists
                    if not os.path.exists(csv_path):
                        if is_ajax:
                            return jsonify({'success': False, 'message': 'Admin database file not found.'})
                        flash("Admin database file not found.")
                        return render_template('admin-new-password.html', email=email)
                    
                    updated = False
                    
                    # Read the CSV file
                    rows = []
                    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        fieldnames = reader.fieldnames
                        for row in reader:
                            if row['admin_email'] == email:
                                row['admin_password'] = new_password
                                updated = True
                            rows.append(row)
                    
                    if not updated:
                        if is_ajax:
                            return jsonify({'success': False, 'message': 'Admin email not found.'})
                        flash("Admin email not found.")
                        return render_template('admin-new-password.html', email=email)
                    
                    # Write the updated data back to CSV
                    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)
                    
                    # Return success response
                    if is_ajax:
                        return jsonify({'success': True, 'message': 'Password updated successfully.'})
                    
                    flash("Password reset successful. Please login.")
                    return redirect(url_for('admin_login'))
                    
                except Exception as e:
                    print(f"Error updating admin password: {e}")
                    import traceback
                    traceback.print_exc()
                    if is_ajax:
                        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
                    flash("An error occurred while updating the password.")
                    return render_template('admin-new-password.html', email=email)
                    
            return render_template('admin-new-password.html', email=email)

        @app.route('/admin-resend-otp', methods=['POST'])
        def admin_resend_otp():
            email = request.form.get('email')
            if email:
                otp = admin_password_reset_manager.generate_otp(email)
                admin_password_reset_manager.send_otp(email, otp)
                return jsonify({'success': True, 'message': 'Verification code resent.'})
            return jsonify({'success': False, 'message': 'Email not found.'}), 400

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