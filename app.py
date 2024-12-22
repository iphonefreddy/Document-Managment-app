from flask import Flask, render_template_string, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong random string

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///policy_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Middleware to require login
@app.before_request
def require_login():
    if "user_id" not in session and request.endpoint not in ("login", "static"):
        return redirect(url_for("login"))

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # "Admin" or "Staff"

# Policy model
class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Acknowledgment model
class Acknowledgment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)

# Route: Home (redirects to login)
@app.route("/")
def home():
    return redirect(url_for("login"))

# Route: Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_role"] = user.role
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Login</title></head>
    <body>
        <h1>Login</h1>
        <form method="POST">
            <label>Email:</label>
            <input type="email" name="email" required><br>
            <label>Password:</label>
            <input type="password" name="password" required><br>
            <button type="submit">Login</button>
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul>
              {% for category, message in messages %}
                <li class="{{ category }}">{{ message }}</li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
    </body>
    </html>
    """)

# Route: Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# Route: Dashboard
@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)

    if user.role == "Admin":
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Admin Dashboard</title></head>
        <body>
            <h1>Welcome, {{ user.name }} (Admin)</h1>
            <ul>
                <li><a href="{{ url_for('manage_policies') }}">Manage Policies</a></li>
                <li><a href="{{ url_for('view_acknowledgments') }}">View Acknowledgments</a></li>
            </ul>
            <a href="{{ url_for('logout') }}">Logout</a>
        </body>
        </html>
        """, user=user)
    elif user.role == "Staff":
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Staff Dashboard</title></head>
        <body>
            <h1>Welcome, {{ user.name }} (Staff)</h1>
            <ul>
                <li><a href="{{ url_for('view_policies') }}">View Policies</a></li>
            </ul>
            <a href="{{ url_for('logout') }}">Logout</a>
        </body>
        </html>
        """, user=user)
    else:
        return "Unauthorized Access", 403

# Route: Manage Policies (Admin only)
@app.route("/manage_policies")
def manage_policies():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    if user.role != "Admin":
        return "Unauthorized Access", 403

    policies = Policy.query.all()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Manage Policies</title></head>
    <body>
        <h1>Manage Policies</h1>
        <ul>
            {% for policy in policies %}
                <li>
                    <strong>{{ policy.title }}</strong>
                    <a href="#">Edit</a>
                    <a href="#">Delete</a>
                </li>
            {% endfor %}
        </ul>
        <a href="#">Add New Policy</a><br>
        <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    </body>
    </html>
    """, policies=policies)

# Route: View Policies (Staff only)
@app.route("/view_policies")
def view_policies():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    if user.role != "Staff":
        return "Unauthorized Access", 403

    policies = Policy.query.all()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>View Policies</title></head>
    <body>
        <h1>View Policies</h1>
        <ul>
            {% for policy in policies %}
                <li>
                    <strong>{{ policy.title }}</strong>
                </li>
            {% endfor %}
        </ul>
        <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    </body>
    </html>
    """, policies=policies)

# Route: View Acknowledgments (Admin only)
@app.route("/view_acknowledgments")
def view_acknowledgments():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    if user.role != "Admin":
        return "Unauthorized Access", 403

    acknowledgments = db.session.query(Acknowledgment, User, Policy).join(User).join(Policy).all()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Acknowledgments</title></head>
    <body>
        <h1>Policy Acknowledgments</h1>
        <table border="1">
            <tr>
                <th>User</th>
                <th>Policy</th>
                <th>Status</th>
            </tr>
            {% for ack, user, policy in acknowledgments %}
            <tr>
