import os
from datetime import datetime, timedelta, timezone

from flask import (Blueprint, request, jsonify, render_template,
                   redirect, url_for, flash, send_from_directory, current_app)
from flask_login import login_required, current_user

from backend import db
from backend.models.assignment import Assignment, Submission, NotificationPrefs
from backend.models.user import Subject, Teacher, Student, User
from backend.utils.helpers import allowed_file, save_uploaded_file

bp = Blueprint('assignment', __name__)


# ──────────────────────────────────────────────────────────────────────────────
# Page routes
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/assignments')
@login_required
def student_assignments_page():
    if current_user.role != 'student':
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    return render_template('assignments/student.html', title='My Assignments')


@bp.route('/assignments/<int:id>')
@login_required
def assignment_detail_page(id):
    if current_user.role not in ('student', 'admin'):
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
        
    assignment = Assignment.query.get_or_404(id)
    sub = None
    if current_user.role == 'student':
        from backend.models.assignment import Submission
        sub = Submission.query.filter_by(assignment_id=id, student_id=current_user.student_profile.id).first()
        if not sub:
            # Defensive auto-create for newly added/missing students
            sub = Submission(assignment_id=id, student_id=current_user.student_profile.id, status='pending')
            db.session.add(sub)
            db.session.commit()
            
    # Load manual relation properties to prevent UndefinedError in template
    from backend.models.user import Subject, Teacher
    subject = Subject.query.get(assignment.subject_id)
    teacher = Teacher.query.get(assignment.teacher_id) if assignment.teacher_id else None
            
    return render_template('assignments/detail.html', 
                           title=assignment.title, 
                           assignment=assignment, 
                           submission=sub,
                           subject=subject,
                           teacher=teacher,
                           datetime_now=datetime.utcnow())


@bp.route('/assignments/create')
@login_required
def create_assignment_page():
    if current_user.role not in ('teacher', 'hod', 'admin'):
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    if current_user.role == 'admin':
        subjects = Subject.query.all()
    else:
        subjects = Subject.query.filter_by(department=current_user.department).all()
    return render_template('assignments/create.html', title='Create Assignment', subjects=subjects)


@bp.route('/assignments/dashboard')
@login_required
def assignment_dashboard_page():
    if current_user.role not in ('teacher', 'hod', 'admin'):
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    return render_template('assignments/dashboard.html', title='Assignment Dashboard')


@bp.route('/profile')
@login_required
def profile_page():
    prefs = NotificationPrefs.query.filter_by(user_id=current_user.id).first()
    return render_template('profile.html', title='Profile & Preferences', prefs=prefs)


# ──────────────────────────────────────────────────────────────────────────────
# File serving
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename, as_attachment=False)


# ──────────────────────────────────────────────────────────────────────────────
# API – Create assignment (teacher)
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/api/assignments/create', methods=['POST'])
@login_required
def api_create_assignment():
    if current_user.role not in ('teacher', 'hod', 'admin'):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        title = request.form.get('title', '').strip()
        subject_id = int(request.form.get('subject_id'))
        description = request.form.get('description', '').strip() or None
        deadline_str = request.form.get('deadline')
        classroom_link = request.form.get('classroom_link', '').strip() or None

        if not title or not deadline_str:
            return jsonify({'error': 'title and deadline are required'}), 400

        deadline = datetime.fromisoformat(deadline_str)

        resource_path = None
        file = request.files.get('question_paper')
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({'error': 'Only PDF files are allowed'}), 400
            resource_path = save_uploaded_file(file)

        assignment = Assignment(
            teacher_id=current_user.teacher_profile.id if current_user.teacher_profile else None,
            subject_id=subject_id,
            title=title,
            description=description,
            deadline=deadline,
            classroom_link=classroom_link,
            resource_path=resource_path
        )
        db.session.add(assignment)
        db.session.flush()  # get assignment.id

        # Auto-create pending submission records for ALL students
        subject = Subject.query.get(subject_id)
        if subject:
            students = (
                Student.query
                .join(User, User.id == Student.user_id)
                .filter(User.department == subject.department)
                .all()
            )
            for student in students:
                sub = Submission(
                    assignment_id=assignment.id,
                    student_id=student.id,
                    status='pending'
                )
                db.session.add(sub)

        db.session.commit()
        return jsonify(assignment.to_dict(include_subject=True, include_submission_count=True)), 201

    except (ValueError, KeyError) as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid input: {e}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# API – List assignments
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/api/assignments/list', methods=['GET'])
@login_required
def api_list_assignments():
    status_filter = request.args.get('status')
    subject_filter = request.args.get('subject_id', type=int)

    if current_user.role in ('teacher', 'hod', 'admin'):
        if current_user.role == 'admin':
            query = Assignment.query
            dept_filter = request.args.get('department')
            if dept_filter:
                query = query.join(Subject, Subject.id == Assignment.subject_id).filter(Subject.department == dept_filter)
        else:
            query = Assignment.query.filter_by(teacher_id=current_user.teacher_profile.id)
            
        if subject_filter:
            query = query.filter_by(subject_id=subject_filter)
        assignments = query.order_by(Assignment.deadline.asc()).all()
        result = [a.to_dict(include_subject=True, include_submission_count=True) for a in assignments]
        return jsonify(result)

    elif current_user.role == 'student':
        student = current_user.student_profile
        if not student:
            return jsonify([])

        subs_query = Submission.query.filter_by(student_id=student.id)
        if status_filter:
            subs_query = subs_query.filter_by(status=status_filter)
        subs = subs_query.all()

        result = []
        for sub in subs:
            a = Assignment.query.get(sub.assignment_id)
            if not a:
                continue
            if subject_filter and a.subject_id != subject_filter:
                continue
            d = a.to_dict(include_subject=True)
            d['submission_status'] = sub.status
            d['submitted_at'] = sub.submitted_at.isoformat() if sub.submitted_at else None
            result.append(d)
        result.sort(key=lambda x: x['deadline'])
        return jsonify(result)

    return jsonify([])


# ──────────────────────────────────────────────────────────────────────────────
# API – Student marks as submitted
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/api/assignments/mark-submitted', methods=['POST'])
@login_required
def api_mark_submitted():
    if current_user.role != 'student':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    assignment_id = data.get('assignment_id')
    if not assignment_id:
        return jsonify({'error': 'assignment_id required'}), 400

    student = current_user.student_profile
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    sub = Submission.query.filter_by(
        assignment_id=assignment_id, student_id=student.id
    ).first()

    if not sub:
        return jsonify({'error': 'Submission record not found'}), 404

    sub.status = 'submitted'
    sub.self_reported = True
    sub.submitted_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'message': 'Marked as submitted', 'submitted_at': sub.submitted_at.isoformat()})


# ──────────────────────────────────────────────────────────────────────────────
# API – Submission status for an assignment (teacher)
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/api/assignments/submission-status/<int:assignment_id>', methods=['GET'])
@login_required
def api_submission_status(assignment_id):
    if current_user.role not in ('teacher', 'hod', 'admin'):
        return jsonify({'error': 'Unauthorized'}), 403

    assignment = Assignment.query.get_or_404(assignment_id)
    if current_user.role != 'admin' and assignment.teacher_id != current_user.teacher_profile.id:
        return jsonify({'error': 'Forbidden'}), 403

    subs = Submission.query.filter_by(assignment_id=assignment_id).all()
    result = []
    for sub in subs:
        student = Student.query.get(sub.student_id)
        user = student.user if student else None
        result.append({
            'student_name': user.name if user else 'Unknown',
            'college_user_id': user.college_user_id if user else '-',
            'status': sub.status,
            'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else None
        })
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────────
# API – Upcoming assignments (student)
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/api/assignments/upcoming', methods=['GET'])
@login_required
def api_upcoming_assignments():
    if current_user.role != 'student':
        return jsonify({'error': 'Unauthorized'}), 403

    student = current_user.student_profile
    if not student:
        return jsonify([])

    now = datetime.utcnow()
    cutoff = now + timedelta(days=7)

    subs = (
        Submission.query
        .filter_by(student_id=student.id, status='pending')
        .all()
    )

    result = []
    for sub in subs:
        a = Assignment.query.get(sub.assignment_id)
        if not a or a.deadline < now or a.deadline > cutoff:
            continue
        d = a.to_dict(include_subject=True)
        days_remaining = (a.deadline.date() - now.date()).days
        d['days_remaining'] = days_remaining
        d['submission_id'] = sub.id
        result.append(d)

    result.sort(key=lambda x: x['deadline'])
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────────
# API – Notification preferences
# ──────────────────────────────────────────────────────────────────────────────

@bp.route('/api/notification-prefs/update', methods=['PUT'])
@login_required
def api_update_notification_prefs():
    data = request.get_json() or {}

    prefs = NotificationPrefs.query.filter_by(user_id=current_user.id).first()
    if not prefs:
        prefs = NotificationPrefs(user_id=current_user.id)
        db.session.add(prefs)

    prefs.email_enabled = bool(data.get('email_enabled', prefs.email_enabled))
    prefs.remind_3days = bool(data.get('remind_3days', prefs.remind_3days))
    prefs.remind_2days = bool(data.get('remind_2days', prefs.remind_2days))
    prefs.remind_1day = bool(data.get('remind_1day', prefs.remind_1day))
    prefs.remind_deadline = bool(data.get('remind_deadline', prefs.remind_deadline))

    db.session.commit()
    return jsonify({'message': 'Preferences saved'})
