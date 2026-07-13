from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Trek, Booking
from functools import wraps

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'staff' or current_user.status != 'approved':
            flash('You do not have permission to access this page or your account is pending.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    my_treks = Trek.query.filter_by(staff_id=current_user.id).all()
    
    # Calculate some basic stats for the staff dashboard
    total_assigned = len(my_treks)
    total_participants = sum(trek.total_slots - trek.available_slots for trek in my_treks)
    
    return render_template('staff/dashboard.html', 
                           treks=my_treks,
                           total_assigned=total_assigned,
                           total_participants=total_participants)

@staff_bp.route('/trek/<int:id>/manage', methods=['GET', 'POST'])
@login_required
@staff_required
def manage_trek(id):
    trek = db.get_or_404(Trek, id)
    
    # Ensure this staff member manages this trek
    if trek.staff_id != current_user.id:
        flash('You are not assigned to manage this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
        
    if request.method == 'POST':
        new_status = request.form.get('status')
        new_available_slots = int(request.form.get('available_slots'))
        
        # Basic validation
        if new_available_slots < 0 or new_available_slots > trek.total_slots:
            flash('Invalid available slots value.', 'danger')
        else:
            trek.status = new_status
            trek.available_slots = new_available_slots
            db.session.commit()
            flash('Trek updated successfully.', 'success')
            
        return redirect(url_for('staff.manage_trek', id=trek.id))
        
    # Get bookings for this trek
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    
    return render_template('staff/manage_trek.html', trek=trek, bookings=bookings)

@staff_bp.route('/booking/<int:id>/status', methods=['POST'])
@login_required
@staff_required
def update_booking_status(id):
    booking = db.get_or_404(Booking, id)
    
    # Ensure this staff manages the trek the booking is for
    if booking.trek.staff_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('staff.dashboard'))
        
    new_status = request.form.get('status')
    if new_status in ['Booked', 'Completed', 'Cancelled']:
        booking.status = new_status
        db.session.commit()
        flash('Booking status updated.', 'success')
    else:
        flash('Invalid status.', 'danger')
        
    return redirect(url_for('staff.manage_trek', id=booking.trek_id))
