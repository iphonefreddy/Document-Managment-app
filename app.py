from flask import Flask, render_template_string, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template_string, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os

@app.before_request
def require_login():
    if "user_id" not in session and request.endpoint not in ("login", "static"):
        return redirect(url_for("login"))
        
# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "BigFall#2024"
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///policy_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., "Admin" or "Staff"

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)

class Acknowledgment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)

# Initialize the database
with app.app_context():
    db.create_all()
    with app.app_context():
    if not User.query.filter_by(email="admin@example.com").first():
        hashed_password = generate_password_hash("admin123", method="sha256")
        admin = User(name="Admin User", email="admin@example.com", password=hashed_password, role="Admin")
        db.session.add(admin)
        db.session.commit()
with app.app_context():
    # Check if any policies exist
    if not Policy.query.first():
        # Add sample policies
        sample_policies = [
            Policy(title="Policy A", content="This is the content of Policy A."),
            Policy(title="Policy B", content="This is the content of Policy B."),
            Policy(title="Policy C", content="This is the content of Policy C.")
        ]
        db.session.add_all(sample_policies)
        db.session.commit()

# Route: Home (redirects to user dashboard)
@app.route("/")
def home():
    return redirect(url_for("user_dashboard"))

# Route: User Dashboard
@app.route("/dashboard")
def user_dashboard():
    policies = Policy.query.all()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Dashboard</title>
    </head>
    <body>
        <h1>Policy Acknowledgment</h1>
        <ul>
            {% for policy in policies %}
                <li>
                    <a href="{{ url_for('view_policy', policy_id=policy.id) }}">{{ policy.title }}</a>
                    {% if policy.read %}
                        - <strong>Read</strong>
                    {% else %}
                        - <em>Pending</em>
                    {% endif %}
                </li>
            {% endfor %}
        </ul>
    </body>
    </html>
    """, policies=policies)

# Route: View Policy
@app.route("/policy/<int:policy_id>")
def view_policy(policy_id):
    policy = Policy.query.get_or_404(policy_id)
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ policy.title }}</title>
    </head>
    <body>
        <h1>{{ policy.title }}</h1>
        <p>{{ policy.content }}</p>
        {% if not policy.read %}
        <form action="{{ url_for('mark_as_read', policy_id=policy.id) }}" method="post">
            <button type="submit">Mark as Read</button>
        </form>
        {% else %}
        <p><strong>Policy already marked as read.</strong></p>
        {% endif %}
        <a href="{{ url_for('user_dashboard') }}">Back to Dashboard</a>
    </body>
    </html>
    """, policy=policy)

# Route: Mark Policy as Read
@app.route("/mark_as_read/<int:policy_id>", methods=["POST"])
def mark_as_read(policy_id):
    policy = Policy.query.get_or_404(policy_id)
    policy.read = True
    db.session.commit()
    return redirect(url_for("user_dashboard"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
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
    <h1>Login</h1>
    <form method="POST">
        <label>Email:</label>
        <input type="email" name="email" required><br>
        <label>Password:</label>
        <input type="password" name="password" required><br>
        <button type="submit">Login</button>
    </form>
    """)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
