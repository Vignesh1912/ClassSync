from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from backend import db
from backend.models.user import Student

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role != role:
                flash("You don't have permission to access that page.")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
@bp.route('/student', methods=['GET', 'POST'])
@role_required('student')
def student():
    if request.method == 'POST':
        new_section = request.form.get('class_section')
        if new_section and current_user.student_profile:
            current_user.student_profile.class_section = new_section
            db.session.commit()
            flash('Class section updated successfully!', 'success')
        return redirect(url_for('dashboard.student'))
    return render_template('dashboard/student.html', title='Student Dashboard')

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        if current_user.role == 'student':
            new_section = request.form.get('class_section')
            if new_section and current_user.student_profile:
                current_user.student_profile.class_section = new_section
                db.session.commit()
                flash('Class section updated successfully!')
        return redirect(url_for('dashboard.settings'))
        
    return render_template('dashboard/settings.html', title='Settings')

@bp.route('/teacher')
@role_required('teacher')
def teacher():
    return render_template('dashboard/teacher.html', title='Teacher Dashboard')

@bp.route('/hod')
@role_required('hod')
def hod():
    return render_template('dashboard/teacher.html', title='HOD Dashboard')

@bp.route('/admin')
@role_required('admin')
def admin():
    return render_template('dashboard/teacher.html', title='Admin Dashboard')

@bp.route('/')
@login_required
def index():
    return redirect(url_for(f'dashboard.{current_user.role}'))
