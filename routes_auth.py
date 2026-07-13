from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard')) # To be created
        elif current_user.role == 'staff':
            return redirect(url_for('staff.dashboard')) # To be created
        else:
            return redirect(url_for('user.dashboard')) # To be created
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))

        if user.status == 'blacklisted':
            flash('Your account has been blacklisted. Please contact admin.', 'danger')
            return redirect(url_for('auth.login'))

        if user.role == 'staff' and user.status == 'pending':
            flash('Your staff account is pending approval by the admin.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        
        # Role-based redirection
        if user.role == 'admin':
            return redirect('/admin/dashboard') # Update when routes exist
        elif user.role == 'staff':
            return redirect('/staff/dashboard')
        else:
            return redirect('/dashboard')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if role not in ['user', 'staff']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('auth.register'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('auth.register'))

        # Staff users are pending by default
        status = 'pending' if role == 'staff' else 'approved'

        new_user = User(
            email=email,
            full_name=name,
            password_hash=generate_password_hash(password),
            role=role,
            status=status
        )

        db.session.add(new_user)
        db.session.commit()

        if role == 'staff':
            flash('Registration successful! Please wait for admin approval.', 'success')
        else:
            flash('Registration successful! You can now log in.', 'success')
        
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
