from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from backend import db
from backend.models.attendance import AttendanceSession, Attendance, SessionActivityLog
from backend.models.user import Subject, Teacher, Student
from sqlalchemy.exc import IntegrityError
from backend.utils.geolocation import is_within_radius

bp = Blueprint('attendance', __name__)

@bp.route('/attendance/start')
@login_required
def start_attendance_page():
    if current_user.role not in ('teacher', 'hod', 'admin'):
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    
    # Get subjects taught by this teacher
    teacher_profile = current_user.teacher_profile
    # Assuming subjects might need to be drawn from timetable or directly assigned,
    # let's just get all subjects for now (or a subset if specified in real app)
    # The requirement says "dropdown from teacher's subjects", so we can query 
    # subjects that the teacher is teaching via timetable, or just list all subjects 
    # in the department. For simplicity, we list subjects in their department.
    subjects = Subject.query.filter_by(department=current_user.department).all()
    if not subjects and teacher_profile:
        from backend.models.timetable import Timetable
        slots = Timetable.query.filter_by(teacher_id=teacher_profile.id).all()
        subj_ids = {s.subject_id for s in slots}
        subjects = Subject.query.filter(Subject.id.in_(subj_ids)).all()
    if not subjects:
        subjects = Subject.query.limit(10).all()  # Ultimate fallback to avoid empty screens
    
    return render_template('attendance/start.html', title='Start Attendance Session', subjects=subjects)


@bp.route('/attendance/mark')
@login_required
def mark_attendance_page():
    if current_user.role != 'student':
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    return render_template('attendance/mark.html', title='Mark Attendance')


@bp.route('/api/attendance/start-session', methods=['POST'])
@login_required
def api_start_session():
    if current_user.role not in ('teacher', 'hod', 'admin'):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    try:
        subject_id = data['subject_id']
        duration_minutes = int(data['duration_minutes'])
        classroom_name = data['classroom_name']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        radius_meters = float(data.get('radius_meters', 50.0))
        class_section = data.get('class_section', '').strip()
        
        # Set end time
        end_time_limit = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        session = AttendanceSession(
            teacher_id=current_user.teacher_profile.id,
            subject_id=subject_id,
            end_time_limit=end_time_limit,
            classroom_name=classroom_name,
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
            class_section=class_section if class_section else None,
            status='active'
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Session started successfully', 
            'session': session.to_dict()
        }), 201
        
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/attendance/active-sessions', methods=['GET'])
@login_required
def api_active_sessions():
    # First, expire any sessions that have passed their end limit
    now = datetime.utcnow()
    expired_sessions = AttendanceSession.query.filter(
        AttendanceSession.status == 'active',
        AttendanceSession.end_time_limit < now
    ).all()
    
    for sess in expired_sessions:
        sess.status = 'expired'
    if expired_sessions:
        db.session.commit()
        
    # Query active sessions
    query = AttendanceSession.query.filter_by(status='active')
    
    if current_user.role == 'teacher':
        # Teachers only see their own active sessions
        query = query.filter_by(teacher_id=current_user.teacher_profile.id)
        active_sessions = query.all()
        # Decorate with subject name
        results = []
        for s in active_sessions:
            d = s.to_dict()
            subject = Subject.query.get(s.subject_id)
            d['subject_name'] = subject.subject_name if subject else 'Unknown'
            # Check what "now" is in UTC for the timer
            d['server_time_utc'] = now.isoformat() + 'Z' if not now.tzinfo else now.isoformat()
            results.append(d)
        return jsonify(results)
        
    elif current_user.role == 'student':
        # Filter sessions by the student's class_section
        student_profile = current_user.student_profile
        student_section = student_profile.class_section if student_profile else None
        
        # Get all active sessions
        all_active = query.all()
        results = []
        for s in all_active:
            # If the session has a class_section set, only show it to matching students
            if s.class_section and student_section:
                if s.class_section.strip().lower() != student_section.strip().lower():
                    continue  # Skip: wrong section
            # If session has no class_section set, show to all students (no filter)
            d = s.to_dict()
            subject = Subject.query.get(s.subject_id)
            teacher_user = Teacher.query.get(s.teacher_id).user
            d['subject_name'] = subject.subject_name if subject else 'Unknown'
            d['teacher_name'] = teacher_user.name if teacher_user else 'Unknown'
            # Ensure Z is appended so JS knows it is UTC
            d['server_time_utc'] = now.isoformat() + 'Z' if not now.tzinfo else now.isoformat()
            results.append(d)
        return jsonify(results)
        
    return jsonify([])


@bp.route('/api/attendance/mark', methods=['POST'])
@login_required
def api_mark_attendance():
    if current_user.role != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    try:
        session_id = data['session_id']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        
        # 1. Session exists and status=active and not expired
        sess = AttendanceSession.query.get(session_id)
        if not sess:
            return _log_and_reject(session_id, current_user.student_profile.id, 'Session not found', latitude, longitude, 404)
            
        now = datetime.utcnow()
        # Fix offset-naive vs aware bug across databases
        end_time = sess.end_time_limit.replace(tzinfo=None) if sess.end_time_limit.tzinfo else sess.end_time_limit
        
        if end_time < now or sess.status != 'active':
            if sess.status == 'active':
                sess.status = 'expired'
                db.session.commit()
            return _log_and_reject(session_id, current_user.student_profile.id, 'Session has ended', latitude, longitude, 403)
            
        # 2. Student not already marked for this session
        existing = Attendance.query.filter_by(session_id=session_id, student_id=current_user.student_profile.id).first()
        if existing:
            return _log_and_reject(session_id, current_user.student_profile.id, 'Already marked for this session', latitude, longitude, 409)
            
        # 3. Student coordinates within radius using haversine
        within_radius, distance = is_within_radius(
            slat=latitude, slon=longitude,
            clat=sess.latitude, clon=sess.longitude,
            radius_m=sess.radius_meters
        )
        if not within_radius:
            reason = f'Outside radius ({int(distance)}m away. Must be within {int(sess.radius_meters)}m)'
            return _log_and_reject(session_id, current_user.student_profile.id, reason, latitude, longitude, 403)
            
        # 4. Student account is_active=True
        if not current_user.is_active:
             return _log_and_reject(session_id, current_user.student_profile.id, 'Account is inactive', latitude, longitude, 403)
             
        # All checks pass
        attendance = Attendance(
            session_id=session_id,
            student_id=current_user.student_profile.id,
            student_latitude=latitude,
            student_longitude=longitude,
            distance_from_class=distance,
            status='present',
            is_valid=True,
            ip_address=request.remote_addr
        )
        sess.total_present += 1
        
        log = SessionActivityLog(
            session_id=session_id,
            student_id=current_user.student_profile.id,
            action='marked',
            latitude=latitude,
            longitude=longitude,
            ip_address=request.remote_addr
        )
        
        db.session.add(attendance)
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Attendance marked successfully',
            'distance_from_class': distance
        })
        
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid coordinates provided'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def _log_and_reject(session_id, student_id, reason, lat, lon, status_code):
    try:
        log = SessionActivityLog(
            session_id=session_id,
            student_id=student_id,
            action='rejected',
            reason=reason,
            latitude=lat,
            longitude=lon,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
        
    return jsonify({'error': reason}), status_code


@bp.route('/api/attendance/close-session/<int:id>', methods=['POST'])
@login_required
def api_close_session(id):
    if current_user.role not in ('teacher', 'hod', 'admin'):
        return jsonify({'error': 'Unauthorized'}), 403
        
    sess = AttendanceSession.query.get_or_404(id)
    if sess.teacher_id != current_user.teacher_profile.id:
        return jsonify({'error': 'Forbidden'}), 403
        
    sess.status = 'closed'
    db.session.commit()
    return jsonify({'message': 'Session closed successfully'})

@bp.route('/api/attendance/report/<int:session_id>', methods=['GET'])
@login_required
def api_attendance_report(session_id):
    if current_user.role not in ['teacher', 'hod', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    sess = AttendanceSession.query.get_or_404(session_id)
    
    if current_user.role == 'teacher' and sess.teacher_id != current_user.teacher_profile.id:
        return jsonify({'error': 'Forbidden'}), 403
        
    records = Attendance.query.filter_by(session_id=session_id).all()
    
    report = []
    for r in records:
        student = Student.query.get(r.student_id)
        user = student.user if student else None
        
        report.append({
            'student_name': user.name if user else 'Unknown',
            'roll_number': student.roll_number if student else 'Unknown',
            'marked_at': r.marked_at.isoformat(),
            'distance_from_class': r.distance_from_class
        })
        
    return jsonify(report)


# ── Phase 2b: Analytics endpoints ──────────────────────────────────────────────

@bp.route('/api/attendance/student-stats/<int:student_id>', methods=['GET'])
@login_required
def api_student_stats(student_id):
    """Per-subject attendance breakdown for a single student."""
    # Students can only see their own stats; teachers/hod can see any
    if current_user.role == 'student':
        if not current_user.student_profile or current_user.student_profile.id != student_id:
            return jsonify({'error': 'Unauthorized'}), 403

    # Get all sessions that have any attendance record for this student,
    # grouped by subject
    from sqlalchemy import func

    # All sessions for subjects where this student has ever been marked present
    attended_rows = (
        db.session.query(
            AttendanceSession.subject_id,
            func.count(Attendance.id).label('attended')
        )
        .join(Attendance, Attendance.session_id == AttendanceSession.id)
        .filter(Attendance.student_id == student_id, Attendance.status == 'present')
        .group_by(AttendanceSession.subject_id)
        .all()
    )

    attended_map = {row.subject_id: row.attended for row in attended_rows}

    if not attended_map:
        return jsonify([])

    results = []
    for subject_id, attended in attended_map.items():
        subject = Subject.query.get(subject_id)
        if not subject:
            continue

        # Total sessions ever held for this subject
        total = AttendanceSession.query.filter_by(subject_id=subject_id).count()
        if total == 0:
            continue

        pct = round(attended / total * 100, 1)
        if pct >= 75:
            flag = 'green'
        elif pct >= 70:
            flag = 'yellow'
        else:
            flag = 'red'

        results.append({
            'subject_name': subject.subject_name,
            'subject_code': subject.subject_code,
            'total_sessions': total,
            'attended': attended,
            'percentage': pct,
            'flag': flag
        })

    results.sort(key=lambda x: x['subject_name'])
    return jsonify(results)


@bp.route('/api/attendance/class-stats', methods=['GET'])
@login_required
def api_class_stats():
    """Aggregated per-student, per-subject attendance. Teacher/HOD only."""
    if current_user.role not in ['teacher', 'hod', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403

    from sqlalchemy import func

    # All attendance records joined to sessions for subject names
    rows = (
        db.session.query(
            Attendance.student_id,
            AttendanceSession.subject_id,
            func.count(Attendance.id).label('attended')
        )
        .join(AttendanceSession, AttendanceSession.id == Attendance.session_id)
        .filter(Attendance.status == 'present')
        .group_by(Attendance.student_id, AttendanceSession.subject_id)
        .all()
    )

    # Build: {student_id: {subject_id: attended_count}}
    student_subject_map = {}
    for row in rows:
        student_subject_map.setdefault(row.student_id, {})[row.subject_id] = row.attended

    # Total sessions per subject
    session_totals = {
        r.subject_id: r.total
        for r in db.session.query(
            AttendanceSession.subject_id,
            func.count(AttendanceSession.id).label('total')
        ).group_by(AttendanceSession.subject_id).all()
    }

    results = []
    for student_id, subject_map in student_subject_map.items():
        student = Student.query.get(student_id)
        if not student:
            continue
        user = student.user

        subject_stats = []
        percentages = []

        for subject_id, attended in subject_map.items():
            subject = Subject.query.get(subject_id)
            total = session_totals.get(subject_id, 0)
            if total == 0:
                continue
            pct = round(attended / total * 100, 1)
            percentages.append(pct)
            subject_stats.append({
                'subject_name': subject.subject_name if subject else 'Unknown',
                'attended': attended,
                'total': total,
                'percentage': pct
            })

        overall = round(sum(percentages) / len(percentages), 1) if percentages else 0.0
        at_risk = overall < 75

        results.append({
            'student_name': user.name if user else 'Unknown',
            'college_user_id': user.college_user_id if user else '-',
            'class_section': student.class_section or '-',
            'subjects': subject_stats,
            'overall_percentage': overall,
            'at_risk': at_risk
        })

    results.sort(key=lambda x: x['student_name'])
    return jsonify(results)


@bp.route('/attendance/reports')
@login_required
def attendance_reports_page():
    if current_user.role not in ['teacher', 'hod', 'admin']:
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    return render_template('attendance/reports.html', title='Attendance Reports')

