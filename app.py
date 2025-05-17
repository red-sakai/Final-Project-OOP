from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from models.admin import Admin
from abc import ABC, abstractmethod
from enum import Enum
from flask_mail import Mail, Message
import random
from transformers import pipeline
import os
import re

# Initialize DistilBERT QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Initialize Flask app and set static folder
app = Flask(__name__, 
            static_url_path='',
            static_folder='static')
app.secret_key = "your_secret_key"

# flask-mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hexahaulprojects@gmail.com'
app.config['MAIL_PASSWORD'] = 'ikai nagb zyna hjoc'

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

# Truck routes
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
#-----------------------------------------------
# Motorcycle routes
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
#------------------------------------------------
# Car routes
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
        # Send the issue to the support email
        msg = Message(
            subject="New Support Ticket",
            sender="hexahaulprojects@gmail.com",
            recipients=["hexahaulprojects@gmail.com"]
        )
        msg.body = f"Support ticket submitted by: {user_email}\n\nIssue Description:\n{issue}"
        mail.send(msg)
        # Pass a query parameter to trigger the modal on index.html
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

# predefined quick replies and their answers
QUICK_REPLY_ANSWERS = {
    "about hexahaul": "HexaHaul is a logistics company founded and operated by a passionate team of six people: Jhered, Carl, Patricia, Kris, Sandrine, and CJ. We provide efficient and reliable transportation solutions for businesses and individuals.",
    "who are you?": "I'm HexaBot, your helpful AI assistant for HexaHaul. Ask me anything about our company or services!",
    "what services do you offer?": "HexaHaul offers truck, motorcycle, and car logistics for deliveries of all sizes. We ensure timely deliveries, real-time tracking, and excellent customer service.",
    "how can i track my shipment?": "You can track your shipment using the tracking page on our website by entering your tracking number. If you have lost your tracking number, please contact our support team.",
    "how do i contact support?": "For support, contact us at hexahaulprojects@gmail.com or call 123-456-7890. Our office hours are 9am to 6pm, Monday to Saturday."
}

FAQ_CONTEXT = """
HexaHaul is a logistics company founded and operated by a passionate team of six people: Jhered, Carl, Patricia, Kris, Sandrine, and CJ. We provide efficient and reliable transportation solutions for businesses and individuals.
Our services include truck, motorcycle, and car logistics for deliveries of all sizes. You can track your shipment using the tracking page on our website by entering your tracking number.
For support, contact us at hexahaulprojects@gmail.com or call 123-456-7890. Our office hours are 9am to 6pm, Monday to Saturday.
We ensure timely deliveries, real-time tracking, and excellent customer service. We operate in major cities and offer both same-day and scheduled delivery options.
If you have lost your tracking number, please contact our support team. For partnership or business inquiries, email us at hexahaulprojects@gmail.com.
HexaHaul is committed to safe, secure, and on-time delivery of your goods.
"""

CONVERSATION_PATTERNS = {
    "greetings": [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "yo", "sup"
    ],
    "thanks": [
        "thank you", "thanks", "thx", "ty"
    ],
    "goodbye": [
        "bye", "goodbye", "see you", "see ya", "farewell"
    ]
}

CONVERSATION_RESPONSES = {
    "greetings": "Hello, I am HexaBot, your logistics assistant. What can I do for you today?",
    "thanks": "You're welcome! If you have more questions about HexaHaul, just ask.",
    "goodbye": "Goodbye! If you need anything else about HexaHaul, feel free to chat again."
}

# Add a list of profane words (expand as needed)
PROFANITY_LIST = [

    "fuck", "shit", "bitch", "asshole", "bastard", "dick", "pussy", "motherfucker", "fucker", "cunt", "slut", "penis", "dimwit" 

    "putangina", "tangina", "tanginamo", "taena", "taenamo", "gago", "ulol", "leche", "bwisit", "punyeta", "potangina", "pota",
    "pakshet", "puta", "pukinginamo", "kinginamo",
]

def contains_profanity(text):
    # normalize and check for profane words (word boundaries, case-insensitive)
    text = text.lower()
    for word in PROFANITY_LIST:
        # use regex to match whole words or common variations
        if re.search(rf"\b{re.escape(word)}\b", text):
            return True
    return False

@app.route("/faq-bot", methods=["POST"])
def faq_bot():
    user_question = request.form.get("question", "").strip()
    if not user_question:
        return jsonify({"answer": "Please provide a question."}), 400

    # Profanity check
    if contains_profanity(user_question):
        return jsonify({"answer": "Let's keep our conversation respectful. Please avoid using inappropriate language."})

    normalized = user_question.lower().strip(" ?!.")

    # easter egg: "who is our professor"
    if "who is our professor" in normalized or "sino professor" in normalized or "sino ang professor" in normalized:
        return jsonify({
            "answer": "Engr. Jerico Sarcillo, our outstanding professor! He inspires us to excel and brings out the best in every student. We are grateful for his dedication and guidance."
        })

    # 1. check for conversational patterns (greetings, thanks, goodbye)
    for pattern, keywords in CONVERSATION_PATTERNS.items():
        if any(normalized.startswith(word) or normalized == word for word in keywords):
            return jsonify({"answer": CONVERSATION_RESPONSES[pattern]})

    # 2. check for quick reply match (case-insensitive)
    for quick, answer in QUICK_REPLY_ANSWERS.items():
        if normalized == quick or normalized.rstrip("?!.") == quick.rstrip("?!."):
            return jsonify({"answer": answer})

    # 3. only answer if the question is about HexaHaul's services, tracking, or support
    allowed_keywords = [
        "hexahaul", "service", "services", "track", "tracking", "shipment", "support", "contact", "delivery", "truck", "motorcycle", "car", "logistics", "booking", "book", "parcel"
    ]
    if not any(word in normalized for word in allowed_keywords):
        return jsonify({"answer": "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."})

    # 4. use DistilBERT QA pipeline as fallback (only if in scope)
    result = qa_pipeline(question=user_question, context=FAQ_CONTEXT)
    answer = result["answer"].strip()

    if not answer or len(answer) < 5:
        answer = "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."
    return jsonify({"answer": answer})

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin-dashboard.html")

if __name__ == "__main__":
    app.debug = True
    print("Flask app routes:")
    print(app.url_map)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)