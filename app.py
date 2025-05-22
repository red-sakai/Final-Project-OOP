from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, Blueprint, send_from_directory, session
from models.admin import Admin
from models.analytics_backend import plot_employee_statuses, plot_vehicles_deployed
from models.vehicle_database import VehicleDatabase, Vehicle
from models.employee_database import EmployeeDatabase, Employee
from models.hexaboxes_database import HexaBoxesDatabase, Order
from models.user_login_database import init_db, load_users_from_csv, authenticate_user
from models.admin_database import init_admin_db, get_db_session, Admin, get_default_admin
from models.utilities_database import UtilitiesDatabase
from abc import ABC, abstractmethod
from enum import Enum
from flask_mail import Mail, Message
import random
from transformers import pipeline
import os
import re
import json
from services.hexabot import hexabot_bp

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
            error = None
            print(f"User login route accessed, method: {request.method}")
            try:
                if request.method == "POST":
                    username = request.form["username"]
                    password = request.form["password"]

                    user = authenticate_user(username, password)

                    if user:
                        # Set user session data
                        session["user_id"] = user.customer_id
                        session["username"] = user.username
                        # Format the full name properly
                        session["user_name"] = f"{user.customer_fname} {user.customer_lname}"

                        # Redirect to index.html instead of user-dashboard
                        return redirect(url_for("index_html"))
                    else:
                        error = "Invalid username or password. Please try again."
                
                return render_template("user-login.html", error=error)
            except Exception as e:
                print(f"Error in user_login_html route: {e}")
                return f"Error loading template: {str(e)}", 500

        @app.route("/user-dashboard")
        def user_dashboard():
            if "user_id" not in session:
                return redirect(url_for("user_login_html"))

            return render_template("user-dashboard.html", user_name=session.get("user_name"))

        @app.route("/logout")
        def logout():
            session.clear()
            return redirect(url_for("user_login_html"))

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
                if new_password == confirm_password and len(new_password) >= 8:
                    flash("Password reset successful. Please login.")
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

        @app.route("/parceltracking")
        def parceltracking():
            tracking_id = request.args.get("tracking_id", "")
            return render_template("parceltracking.html", tracking_id=tracking_id)

        @app.route("/submit-ticket", methods=["GET", "POST"])
        def submit_ticket():
            if request.method == "POST":
                user_email = request.form.get("email")
                issue = request.form.get("issue")
                msg = Message(
                    subject="New Support Ticket",
                    sender="hexahaulprojects@gmail.com",
                    recipients=["hexahaulprojects@gmail.com"]
                )
                msg.body = f"Support ticket submitted by: {user_email}\n\nIssue Description:\n{issue}"
                self.mail.send(msg)
                return redirect(url_for("index_html", ticket_submitted="1"))
            return render_template("submit-ticket.html")

        @app.route("/personal-info")
        def personal_info():
            return render_template("personal-info.html")

        @app.route("/change-password")
        def change_password():
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