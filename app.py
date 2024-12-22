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

# User model with roles
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # "Admin" or "Staff"

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
    <head>
        <title>Login</title>
    </head>
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

# Route: Dashboard with Role-Specific Views
@app.route("/dashboard")
def dashboard():
    # Check if user is logged in
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # Get the logged-in user
    user = User.query.get(user_id)

    # Admin Dashboard
    if user.role == "Admin":
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard</title>
        </head>
        <body>
            <h1>Welcome, {{ user.name }} (Admin)</h1>
            <ul>
                <li><a href="#">Manage Policies</a></li>
                <li><a href="#">View Acknowledgment Status</a></li>
                <li><a href="#">View Notifications</a></li>
            </ul>
            <a href="{{ url_for('logout') }}">Logout</a>
        </body>
        </html>
        """, user=user)

    # Staff Dashboard
    elif user.role == "Staff":
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Staff Dashboard</title>
        </head>
        <body>
            <h1>Welcome, {{ user.name }} (Staff)</h1>
            <ul>
                <li><a href="#">View Policies</a></li>
                <li><a href="#">Acknowledge Policies</a></li>
            </ul>
            <a href="{{ url_for('logout') }}">Logout</a>
        </body>
        </html>
        """, user=user)

    # If role is unknown
    else:
        return "Unauthorized Access", 403

# Initialize the database and add a sample admin user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@example.com").first():
        hashed_password = generate_password_hash("admin123", method="sha256")
        admin = User(name="Admin User", email="admin@example.com", password=hashed_password, role="Admin")
        staff = User(name="Staff User", email="staff@example.com", password=generate_password_hash("staff123", method="sha256"), role="Staff")
        db.session.add_all([admin, staff])
        db.session.commit()

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
