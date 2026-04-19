from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from datetime import datetime
from backend import db
from backend.models.timetable import Timetable
from backend.models.user import Teacher, Subject
from sqlalchemy import or_, and_

bp = Blueprint('timetable', __name__)

@bp.route('/timetable')
@login_required
def view_timetable_page():
    return render_template('timetable/view.html', title='Timetable')

@bp.route('/timetable/manage')
@login_required
def manage_timetable_page():
    if current_user.role not in ['teacher', 'admin', 'hod']:
        from flask import flash, redirect, url_for
        flash('Access denied')
        return redirect(url_for('timetable.view_timetable_page'))
    
    # Pass subjects for the dropdowns
    subjects = Subject.query.all()
    teachers = Teacher.query.all()
    return render_template('timetable/manage.html', title='Manage Timetable', subjects=subjects, teachers=teachers)

def check_conflict(teacher_id, class_section, day_of_week, start_time, end_time, current_slot_id=None):
    """
    Returns a conflict reason string if a conflict exists, or None if clear.
    Checks two independent rules:
      1. Same teacher cannot teach two classes at the same time.
      2. Same class section cannot have two subjects at the same time.
    """
    base_filter = dict(day_of_week=day_of_week, is_active=True)

    def _make_query(**extra):
        q = Timetable.query.filter_by(**base_filter, **extra).filter(
            Timetable.start_time < end_time,
            Timetable.end_time > start_time,
        )
        if current_slot_id:
            q = q.filter(Timetable.id != current_slot_id)
        return q

    # Rule 1: teacher double-booking
    if _make_query(teacher_id=teacher_id).first():
        return "Teacher already has a class at this time"

    # Rule 2: section double-booking
    if class_section and _make_query(class_section=class_section).first():
        return f"Section '{class_section}' already has a class at this time"

    return None  # No conflict

@bp.route('/api/timetable/create', methods=['POST'])
@login_required
def api_timetable_create():
    if current_user.role not in ['teacher', 'admin', 'hod']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    try:
        teacher_id = data['teacher_id'] if current_user.role in ['admin', 'hod'] else current_user.teacher_profile.id
        subject_id = data['subject_id']
        day_of_week = data['day_of_week']
        start_time_str = data['start_time']
        end_time_str = data['end_time']
        room_number = data['room_number']
        class_section = data['class_section']
        
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        if start_time >= end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400
            
        conflict_reason = check_conflict(teacher_id, class_section, day_of_week, start_time, end_time)
        if conflict_reason:
            return jsonify({'error': f'Schedule conflict: {conflict_reason}'}), 409
            
        slot = Timetable(
            teacher_id=teacher_id,
            subject_id=subject_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room_number=room_number,
            class_section=class_section
        )
        db.session.add(slot)
        db.session.commit()
        
        return jsonify({'message': 'Timetable slot created successfully', 'slot': slot.to_dict()}), 201
        
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/timetable/view', methods=['GET'])
@login_required
def api_timetable_view():
    class_section = request.args.get('class_section')
    day = request.args.get('day')
    teacher_id = request.args.get('teacher_id')
    
    query = Timetable.query.filter_by(is_active=True)
    
    # Auto-filter for students
    if current_user.role == 'student':
        if current_user.student_profile and current_user.student_profile.class_section:
            query = query.filter_by(class_section=current_user.student_profile.class_section)
        else:
            return jsonify([]) # Student without a class_section assigned
    else:
        # For non-students, apply optional query parameters
        if class_section:
            query = query.filter_by(class_section=class_section)
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
            
    if day:
        query = query.filter_by(day_of_week=day)
        
    slots = query.order_by(Timetable.start_time).all()
    return jsonify([slot.to_dict() for slot in slots])

@bp.route('/api/timetable/update/<int:id>', methods=['PUT'])
@login_required
def api_timetable_update(id):
    if current_user.role not in ['teacher', 'admin', 'hod']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    slot = Timetable.query.get_or_404(id)
    
    # Only Admin/HOD or the owning Teacher can update
    if current_user.role == 'teacher' and slot.teacher_id != current_user.teacher_profile.id:
        return jsonify({'error': 'Forbidden'}), 403
        
    data = request.json
    try:
        # Check for updates and conflicts
        new_day = data.get('day_of_week', slot.day_of_week)
        new_start_str = data.get('start_time', slot.start_time.strftime('%H:%M'))
        new_end_str = data.get('end_time', slot.end_time.strftime('%H:%M'))
        
        start_time = datetime.strptime(new_start_str, '%H:%M').time()
        end_time = datetime.strptime(new_end_str, '%H:%M').time()
        
        new_class_section = data.get('class_section', slot.class_section)

        if start_time >= end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400

        conflict_reason = check_conflict(slot.teacher_id, new_class_section, new_day, start_time, end_time, current_slot_id=id)
        if conflict_reason:
            return jsonify({'error': f'Schedule conflict: {conflict_reason}'}), 409

        slot.subject_id = data.get('subject_id', slot.subject_id)
        slot.day_of_week = new_day
        slot.start_time = start_time
        slot.end_time = end_time
        slot.room_number = data.get('room_number', slot.room_number)
        slot.class_section = data.get('class_section', slot.class_section)
        
        db.session.commit()
        return jsonify({'message': 'Timetable slot updated successfully', 'slot': slot.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/timetable/delete/<int:id>', methods=['DELETE'])
@login_required
def api_timetable_delete(id):
    if current_user.role not in ['teacher', 'admin', 'hod']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    slot = Timetable.query.get_or_404(id)
    
    if current_user.role == 'teacher' and slot.teacher_id != current_user.teacher_profile.id:
        return jsonify({'error': 'Forbidden'}), 403
        
    slot.is_active = False # Soft delete
    db.session.commit()
    return jsonify({'message': 'Timetable slot deleted successfully'})

@bp.route('/api/timetable/today', methods=['GET'])
@login_required
def api_timetable_today():
    today_name = datetime.now().strftime('%A')
    
    query = Timetable.query.filter_by(is_active=True, day_of_week=today_name)

    # Automatically filter by student's class_section if logged in as student
    if current_user.role == 'student':
        if current_user.student_profile and current_user.student_profile.class_section:
             query = query.filter_by(class_section=current_user.student_profile.class_section)
        else:
             return jsonify([]) # Student without a class_section assigned
             
    elif current_user.role == 'teacher':
         query = query.filter_by(teacher_id=current_user.teacher_profile.id)
    
    slots = query.order_by(Timetable.start_time).all()
    return jsonify([slot.to_dict() for slot in slots])
