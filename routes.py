
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Policy, db
from . import app

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Admin':
        policies = Policy.query.all()
        return render_template('admin_dashboard.html', policies=policies)
    else:
        policies = Policy.query.filter(~Policy.id.in_([a.policy_id for a in current_user.acknowledgments])).all()
        return render_template('staff_dashboard.html', policies=policies)

@app.route('/policy/create', methods=['GET', 'POST'])
@login_required
def create_policy():
    if current_user.role != 'Admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        policy = Policy(title=title, content=content)
        db.session.add(policy)
        db.session.commit()
        flash('Policy created successfully')
        return redirect(url_for('dashboard'))
    return render_template('create_policy.html')

@app.route('/policy/<int:policy_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_policy(policy_id):
    policy = Policy.query.get(policy_id)
    if not policy:
        flash('Policy not found')
        return redirect(url_for('dashboard'))
    acknowledgment = Acknowledgment(user_id=current_user.id, policy_id=policy_id)
    db.session.add(acknowledgment)
    db.session.commit()
    flash('Policy acknowledged successfully')
    return redirect(url_for('dashboard'))
