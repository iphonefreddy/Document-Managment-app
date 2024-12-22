from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///policies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database models
class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
class Acknowledgment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)

with app.app_context():
    if not Policy.query.first():  # Add sample policies if none exist
        sample_policies = [
            Policy(title="Policy A", content="This is the content of Policy A."),
            Policy(title="Policy B", content="This is the content of Policy B."),
            Policy(title="Policy C", content="This is the content of Policy C.", read=True),
        ]
        db.session.add_all(sample_policies)
        db.session.commit()
with app.app_context():
    # Add sample users if the database is empty
    if not User.query.first():
        sample_users = [
            User(name="Alice"),
            User(name="Bob"),
            User(name="Charlie"),
        ]
        db.session.add_all(sample_users)
        db.session.commit()

        # Add sample acknowledgments
        user1 = User.query.filter_by(name="Alice").first()
        user2 = User.query.filter_by(name="Bob").first()
        user3 = User.query.filter_by(name="Charlie").first()
        policy1 = Policy.query.filter_by(title="Policy A").first()
        policy2 = Policy.query.filter_by(title="Policy B").first()
        policy3 = Policy.query.filter_by(title="Policy C").first()

        sample_acknowledgments = [
            Acknowledgment(user_id=user1.id, policy_id=policy1.id, read=True),
            Acknowledgment(user_id=user1.id, policy_id=policy2.id, read=False),
            Acknowledgment(user_id=user2.id, policy_id=policy1.id, read=False),
            Acknowledgment(user_id=user3.id, policy_id=policy3.id, read=True),
        ]
        db.session.add_all(sample_acknowledgments)
        db.session.commit()


# Initialize the database
with app.app_context():
    db.create_all()

# User dashboard
@app.route("/dashboard")
def dashboard():
    policies = Policy.query.all()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Policy Dashboard</title>
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

# View policy content
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
        <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    </body>
    </html>
    """, policy=policy)

# Mark policy as read
@app.route("/mark_as_read/<int:policy_id>", methods=["POST"])
def mark_as_read(policy_id):
    policy = Policy.query.get_or_404(policy_id)
    policy.read = True
    db.session.commit()
    return redirect(url_for("dashboard"))
@app.route("/")
def home():
    return redirect(url_for("dashboard"))
# Add sample policies (only if the database is empty)
with app.app_context():
    if not Policy.query.first():
        sample_policies = [
            Policy(title="Policy A", content="This is the content of Policy A."),
            Policy(title="Policy B", content="This is the content of Policy B."),
            Policy(title="Policy C", content="This is the content of Policy C.", read=True),
        ]
        db.session.add_all(sample_policies)
        db.session.commit()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
