from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

# Mock database (in reality, this would be a proper database)
policies = [
    {"id": 1, "title": "Policy A", "content": "This is the content of Policy A.", "read": False},
    {"id": 2, "title": "Policy B", "content": "This is the content of Policy B.", "read": False},
    {"id": 3, "title": "Policy C", "content": "This is the content of Policy C.", "read": True},  # Example of an already read policy
]

# User dashboard
@app.route("/dashboard")
def dashboard():
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
    policy = next((p for p in policies if p["id"] == policy_id), None)
    if not policy:
        return "Policy not found", 404
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
    policy = next((p for p in policies if p["id"] == policy_id), None)
    if policy:
        policy["read"] = True
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
