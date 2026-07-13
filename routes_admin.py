from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, Trek, Booking
from functools import wraps
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           total_treks=total_treks, 
                           total_users=total_users,
                           total_staff=total_staff,
                           total_bookings=total_bookings,
                           recent_bookings=recent_bookings)

@admin_bp.route('/treks')
@login_required
@admin_required
def manage_treks():
    search = request.args.get('search', '')
    query = Trek.query
    if search:
        query = query.filter(Trek.name.ilike(f'%{search}%') | Trek.location.ilike(f'%{search}%'))
    treks = query.all()
    return render_template('admin/manage_treks.html', treks=treks, search=search)

@admin_bp.route('/trek/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_trek():
    staff_members = User.query.filter_by(role='staff', status='approved').all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = int(request.form.get('duration'))
        slots = int(request.form.get('slots'))
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        description = request.form.get('description')
        staff_id = request.form.get('staff_id')
        
        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=slots,
            total_slots=slots,
            start_date=start_date,
            end_date=end_date,
            description=description,
            staff_id=staff_id if staff_id else None
        )
        
        db.session.add(new_trek)
        db.session.commit()
        flash('Trek created successfully!', 'success')
        return redirect(url_for('admin.manage_treks'))
        
    return render_template('admin/trek_form.html', staff_members=staff_members, trek=None)

@admin_bp.route('/trek/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trek(id):
    trek = db.get_or_404(Trek, id)
    staff_members = User.query.filter_by(role='staff', status='approved').all()
    
    if request.method == 'POST':
        trek.name = request.form.get('name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration = int(request.form.get('duration'))
        new_total_slots = int(request.form.get('slots'))
        
        # Calculate available slots difference
        diff = new_total_slots - trek.total_slots
        trek.total_slots = new_total_slots
        trek.available_slots = trek.available_slots + diff
        
        trek.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        trek.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        trek.description = request.form.get('description')
        trek.staff_id = request.form.get('staff_id') or None
        
        db.session.commit()
        flash('Trek updated successfully!', 'success')
        return redirect(url_for('admin.manage_treks'))
        
    return render_template('admin/trek_form.html', staff_members=staff_members, trek=trek)

@admin_bp.route('/trek/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_trek(id):
    trek = db.get_or_404(Trek, id)
    
    # Check if there are bookings before deleting
    if trek.bookings:
        flash('Cannot delete trek with existing bookings. You can set its status to Closed instead.', 'danger')
        return redirect(url_for('admin.manage_treks'))
        
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted successfully!', 'success')
    return redirect(url_for('admin.manage_treks'))

@admin_bp.route('/staff')
@login_required
@admin_required
def manage_staff():
    search = request.args.get('search', '')
    query = User.query.filter_by(role='staff')
    if search:
        query = query.filter(User.full_name.ilike(f'%{search}%') | User.email.ilike(f'%{search}%'))
    staff_members = query.all()
    return render_template('admin/manage_staff.html', staff_members=staff_members, search=search)

@admin_bp.route('/staff/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_staff_status(id):
    staff = db.get_or_404(User, id)
    new_status = request.form.get('status')
    
    if new_status in ['approved', 'blacklisted', 'pending']:
        staff.status = new_status
        db.session.commit()
        flash(f'Staff status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
        
    return redirect(url_for('admin.manage_staff'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    search = request.args.get('search', '')
    query = User.query.filter_by(role='user')
    if search:
        query = query.filter(User.full_name.ilike(f'%{search}%') | User.email.ilike(f'%{search}%'))
    users = query.all()
    return render_template('admin/manage_users.html', users=users, search=search)

@admin_bp.route('/users/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_user_status(id):
    user = db.get_or_404(User, id)
    new_status = request.form.get('status')
    
    if new_status in ['approved', 'blacklisted']:
        user.status = new_status
        db.session.commit()
        flash(f'User status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
        
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/bookings')
@login_required
@admin_required
def all_bookings():
    search = request.args.get('search', '')
    query = Booking.query.join(Trek).join(User)
    
    if search:
        query = query.filter(
            Trek.name.ilike(f'%{search}%') | 
            User.full_name.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%')
        )
        
    bookings = query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/all_bookings.html', bookings=bookings, search=search)
