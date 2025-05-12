from flask import Flask, render_template, url_for
from abc import ABC, abstractmethod
from enum import Enum
#import matplotlib.pyplot as plt

app = Flask(__name__, 
            static_url_path='',
            static_folder='static')

@app.route("/")
def home():
    print("Home route accessed")
    return render_template("services.html")

@app.route("/services")
def services():
    print("Services route accessed")
    return render_template("services.html")

@app.route("/tracking")
def tracking():
    print("Tracking route accessed")
    return render_template("tracking.html")

@app.route("/FAQ")
def faq():
    print("FAQ route accessed")
    return render_template("FAQ.html")

# add direct routes for HTML files
@app.route("/services.html")
def services_html():
    print("Services.html route accessed")
    return render_template("services.html")

@app.route("/tracking.html")
def tracking_html():
    print("Tracking.html route accessed")
    return render_template("tracking.html")

@app.route("/FAQ.html")
def faq_html():
    print("FAQ.html route accessed")
    return render_template("FAQ.html")

if __name__ == "__main__":
    app.debug = True
    print("Flask app routes:")
    print(app.url_map)
    app.run(debug=True)