from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Trek, Booking
from functools import wraps

user_bp = Blueprint('user', __name__)

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'user':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    search_query = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    
    query = Trek.query.filter(Trek.status.in_(['Open', 'Approved']))
    
    if search_query:
        query = query.filter(Trek.name.ilike(f'%{search_query}%') | Trek.location.ilike(f'%{search_query}%'))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
        
    treks = query.all()
    
    return render_template('user/dashboard.html', treks=treks, search=search_query, difficulty=difficulty)

@user_bp.route('/trek/<int:id>')
@login_required
@user_required
def trek_details(id):
    trek = db.get_or_404(Trek, id)
    
    # Check if user already booked this trek
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).first()
    
    return render_template('user/trek_details.html', trek=trek, existing_booking=existing_booking)

@user_bp.route('/trek/<int:id>/book', methods=['POST'])
@login_required
@user_required
def book_trek(id):
    trek = db.get_or_404(Trek, id)
    
    if trek.status != 'Open':
        flash('This trek is not open for booking.', 'danger')
        return redirect(url_for('user.trek_details', id=trek.id))
        
    if trek.available_slots <= 0:
        flash('Sorry, this trek is fully booked.', 'danger')
        return redirect(url_for('user.trek_details', id=trek.id))
        
    # Check if already booked
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).first()
    if existing_booking:
        flash('You have already booked this trek.', 'warning')
        return redirect(url_for('user.trek_details', id=trek.id))
        
    # Process booking
    try:
        new_booking = Booking(user_id=current_user.id, trek_id=trek.id)
        trek.available_slots -= 1
        
        db.session.add(new_booking)
        db.session.commit()
        flash('Trek booked successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while booking. Please try again.', 'danger')
        
    return redirect(url_for('user.my_bookings'))

@user_bp.route('/my_bookings')
@login_required
@user_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).filter(Booking.status.in_(['Booked', 'Confirmed'])).all()
    return render_template('user/my_bookings.html', bookings=bookings)

@user_bp.route('/history')
@login_required
@user_required
def history():
    bookings = Booking.query.filter_by(user_id=current_user.id).filter(Booking.status.in_(['Completed', 'Cancelled'])).all()
    return render_template('user/history.html', bookings=bookings)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@user_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        contact = request.form.get('contact')
        
        # Only simple fields are updated to avoid complex password resets for now,
        # but password can be added if needed.
        if full_name:
            current_user.full_name = full_name
        if contact:
            current_user.contact = contact
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
        
    return render_template('user/profile.html', user=current_user)
